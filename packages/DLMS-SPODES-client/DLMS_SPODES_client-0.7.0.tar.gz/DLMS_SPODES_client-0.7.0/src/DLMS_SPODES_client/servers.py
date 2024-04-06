from threading import Thread, Event
from functools import cached_property
import asyncio
from .client import Client, Errors, cdt
from . import task
from DLMS_SPODES.enums import Transmit, Application
from DLMS_SPODES import exceptions as exc
from .enums import LogLevel as logL


class Result:
    client: Client
    complete: bool
    errors: Errors
    value: cdt.CommonDataType | None

    def __init__(self, client: Client):
        self.client = client
        self.complete = False
        """complete exchange"""
        self.errors = Errors()
        self.value = None
        """response if available"""


class Results:
    __values: tuple[Result, ...]
    name: str
    tsk: task.ExTask

    def __init__(self, clients: tuple[Client],
                 tsk: task.ExTask,
                 name: str = None):
        self.__values = tuple(Result(c) for c in clients)
        self.tsk = tsk
        self.name = name
        """common operation name"""

    def __getitem__(self, item):
        return self.__values[item]

    @cached_property
    def clients(self) -> set[Client]:
        return {res.client for res in self.__values}

    @cached_property
    def ok_results(self) -> set[Result]:
        """without errors exchange clients"""
        ret = set()
        for res in self.__values:
            if all(map(lambda err_code: err_code.is_ok(), res.errors)):
                ret.add(res)
        return ret

    @cached_property
    def nok_results(self) -> set[Result]:
        """ With errors exchange clients """
        return set(self.__values).difference(self.ok_results)

    def is_complete(self) -> bool:
        return all((res.complete for res in self))


class TransactionServer:
    __t: Thread
    results: Results

    def __init__(self,
                 clients: list[Client] | tuple[Client],
                 tsk: task.ExTask,
                 name: str = None,
                 abort_timeout: int = 1):
        self.results = Results(clients, tsk, name)
        # self._tg = None
        self.__stop = Event()
        self.__t = Thread(
            target=self.__start_coro,
            args=(self.results, abort_timeout))

    def start(self):
        self.__t.start()

    def abort(self):
        self.__stop.set()

    def __start_coro(self, results, abort_timeout):
        asyncio.run(self.coro_loop(results, abort_timeout))

    async def coro_loop(self, results: Results, abort_timeout: int):
        async def check_stop(tg: asyncio.TaskGroup):
            while True:
                await asyncio.sleep(abort_timeout)
                if results.is_complete():
                    break
                elif self.__stop.is_set():
                    tg._abort()
                    break

        async with asyncio.TaskGroup() as tg:
            for res in results:
                tg.create_task(
                    coro=session(
                        c=res.client,
                        t=results.tsk,
                        result=res))
            tg.create_task(
                coro=check_stop(tg),
                name="wait abort task")


async def session(c: Client,
                  t: task.ExTask,
                  result: Result = None,
                  is_public: bool = False):
    if not result:  # if not use TransActionServer
        result = Result(c)
    c.lock.acquire(timeout=10)  # 10 second, todo: keep parameter anywhere
    # try media open
    assert c.media is not None, F"media is absense"
    if not c.media.is_open():
        try:
            await c.media.open()
            c.set_error(Transmit.OK, "Open port")
            c.log(logL.INFO, F"Open port communication channel: {c.media}")
        except (ConnectionRefusedError, TimeoutError) as e:
            c.set_error(Transmit.NO_PORT, e.args[0])
            result.complete = True
            result.errors = c.errors
            return result
        except Exception as e:
            c.set_error(Transmit.NO_TRANSPORT, F"При соединении{e}")
            result.complete = True
            result.errors = c.errors
            return result
    #
    try:
        if c.objects is None:
            await c.connect(True)
            await task.InitType().exchange(c)
            await c.close()  # todo: change to DiscRequest
        await c.connect(is_public)
        result.value = await t.exchange(c)
        await c.close()  # todo: change to DiscRequest
    except TimeoutError as e:
        c.set_error(Transmit.TIMEOUT, 'Таймаут при обмене')
    except exc.DLMSException as e:
        c.set_error(e.error, e.args[0])
    except Exception as e:
        c.log(logL.INFO, F'UNKNOWN ERROR: {e}...')
        c.set_error(Transmit.UNKNOWN, F'При обмене{e}')
    except asyncio.CancelledError as e:
        c.set_error(Transmit.ABORT, "ручная остановка")
        await c.close()  # todo: change to DiscRequest
    finally:
        c.received_frames.clear()  # for next exchange need clear all received frames. todo: this bag, remove in future
        c.lock.release()
        result.complete = True
        result.errors = c.errors
        # media close
        if not c.lock.locked():
            c.lock.acquire(timeout=1)
            if c.media.is_open():
                await c.media.close()
                c.log(logL.DEB, F'Close media: {c.media}')
            c.lock.release()
        else:
            """opened media use in other session"""
        return result

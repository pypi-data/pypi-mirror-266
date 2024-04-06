import asyncio
import time
import unittest
from DLMS_SPODES.cosem_interface_classes import collection
from DLMS_SPODES.types import cdt
from src.DLMS_SPODES_client.client import Client, SerialPort, Network, AsyncNetwork, Collection, AppVersion, AsyncSerial
from src.DLMS_SPODES_client.servers import TransactionServer
from src.DLMS_SPODES_client import task


class TestType(unittest.TestCase):
    def test_connect(self):
        t_server = TransactionServer(
            clients=[
                client := Client(addr_size=1)
            ],
            tsk=task.Dummy()
        )
        client.device_address.set(0)
        client.media = AsyncSerial(
            port="COM13",
            inactivity_timeout=3
        )
        t_server.start()

    def test_Loop(self):
        def foo(res):
            return res == cdt.Long(4)

        t_server = TransactionServer(
            clients=[
                client := Client(addr_size=1)
            ],
            tsk=task.Loop(
                task=task.ReadAttribute(
                    ln="0.0.1.0.0.255",
                    index=3),
                func=lambda res: res == cdt.Long(4),
                delay=2,
                attempt_amount=5
            )
        )
        client.device_address.set(0)
        client.media = AsyncSerial(
            port="COM13",
            inactivity_timeout=3
        )
        t_server.start()

    def test_async_network(self):
        client = Client(
            secret="00 00 00 00 00 00 00 00",
            addr_size=1,
            conformance="010000000001111000011101")
        type_ = "4d324d5f31"
        ver = "1.5.7"
        man = b"KPZ"
        # client.objects = collection.get(
        #     m=man,
        #     t=cdt.OctetString(type_),
        #     ver=AppVersion.from_str(ver))
        client.m_id.set(0)
        client.device_address.set(0)
        client.media = AsyncSerial(
            port="COM3"
        )
        client2 = Client(
            secret="00 00 00 00 00 00 00 00",
            addr_size=1,
            conformance="010000000001111000011101")
        client2.m_id.set(1)
        client2.device_address.set(0)
        client2.media = AsyncSerial(
            port="COM13"
        )
        client3 = Client(
            secret="00 00 00 00 00 00 00 00",
            addr_size=1,
            conformance="010000000001111000011101")
        client3.m_id.set(0)
        client3.device_address.set(0)
        client3.media = AsyncNetwork(
            host="127.0.0.1",
            port=10000
        )
        t_server = TransactionServer(
            clients=[client3],
            # clients=[client, client2, client3],
            tsk=(s := task.Sequence(
                task.InitType(),
                task.WriteAttribute("0.0.1.0.0.255", 3, "100"),
                task.ReadAttribute("0.0.1.0.0.255", 2),
                task.WriteTime()
            )))
        t_server.start()
        # s.append(task.InitType())
        # print(f"{t_server.is_complete()=}")
        # time.sleep(1)
        # print(f"{t_server.is_complete()=}")
        # time.sleep(1)
        # print(f"{t_server.is_complete()=}")
        # t_s2 = TransactionServer2(
        #     clients=[client2, client3],
        #     exchanges=(tasks.ReadAttribute("0.0.42.0.0.255", 2),))
        # t_se.start()
        time.sleep(.3)
        for r in t_server.results:
            print(F'{r.complete=}')
        print("end")
        print(f"{t_server.results.is_complete()=}")
        time.sleep(3)
        print(t_server.results.ok_results)

    def test_server_stop(self):
        client = Client(
            secret="30 30 30 30 30 30 30 30",
            addr_size=1,
            conformance="010000000001111000011101")
        client.SAP.set(0x20)
        client.m_id.set(1)
        client.device_address.set(0)
        client.media = AsyncSerial(
            port="COM13",
            inactivity_timeout=3
        )
        t_server = TransactionServer(
            clients=[client],
            tsk=(s := task.Sequence(
                task.InitType(),
                # task.WriteAttribute("0.0.1.0.0.255", 3, "100"),
                # task.ReadAttribute("1.0.99.1.0.255", 2),
                task.ReadAttribute("0.0.99.98.2.255", 2),
                task.ReadAttribute("0.0.99.98.3.255", 2),
                # task.WriteTime()
            )))
        t_server.start()

        time.sleep(.3)
        for r in t_server.results:
            print(F'{r.complete=}')
        print(f"{t_server.results.is_complete()=}")
        # time.sleep(4)
        # t_server.abort()
        # time.sleep(1)
        # t_server.abort()
        print(t_server.results.ok_results)
        while not t_server.results.is_complete():
            time.sleep(1)
        a = t_server.results[0]
        print(t_server)

    def test_write(self):
        client = Client(
            secret="30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30",
            addr_size=1,
            conformance="010000000001111000011101")
        # type_ = "4d324d5f31"
        # ver = "1.5.7"
        # man = b"KPZ"
        # client.objects = collection.get(
        #     m=man,
        #     t=cdt.OctetString(type_),
        #     ver=AppVersion.from_str(ver))
        client.SAP.set(0x30)
        client.m_id.set(2)
        client.device_address.set(0)
        client.media = AsyncSerial(
            port="COM13",
            inactivity_timeout=3
        )
        t_server = TransactionServer(
            clients=[client],
            tsk=(s := task.Sequence(
                task.InitType(),
                task.WriteAttribute("0.0.1.0.0.255", 3, "100"),
            )))
        t_server.start()

        time.sleep(.3)
        for r in t_server.results:
            print(F'{r.complete=}')
        print(f"{t_server.results.is_complete()=}")
        # time.sleep(4)
        # t_server.abort()
        # time.sleep(1)
        # t_server.abort()
        print(t_server.results.ok_results)
        while not t_server.results.is_complete():
            time.sleep(1)
        a = t_server.results[0]
        print(t_server)

    def test_firmware_update(self):
        client = Client(
            secret="30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30",
            addr_size=1,
            conformance="010000000001111000011101")
        client.SAP.set(0x30)
        client.m_id.set(2)
        client.device_address.set(0)
        client.media = AsyncSerial(
            port="COM13",
            inactivity_timeout=3
        )
        t_server = TransactionServer(
            clients=[client],
            tsk=task.UpdateFirmware())
        t_server.start()

        while not t_server.results.is_complete():
            time.sleep(1)
            print(f"{t_server.results.is_complete()=}")
        a = t_server.results[0]
        print(t_server)

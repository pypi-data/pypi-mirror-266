import asyncio
import hashlib
from dataclasses import dataclass, field
from typing import Callable, Any
from itertools import count
import datetime
import time
from abc import ABC, abstractmethod
from DLMS_SPODES.types.implementations import enums, long_unsigneds, bitstrings, octet_string, structs
from DLMS_SPODES import exceptions as exc
from DLMS_SPODES.cosem_interface_classes import collection, overview
from DLMS_SPODES.types import cdt, ut
from DLMS_SPODES.enums import Transmit, Application
from DLMS_SPODES.obis import media_id
from DLMS_SPODES.firmwares import get_firmware
from DLMS_SPODES.cosem_interface_classes.image_transfer import image_transfer_status as i_t_status
from .client import Client, pdu, logL, AppVersion


class ExTask(ABC):
    """Exchange task for DLMS client"""
    @abstractmethod
    async def exchange(self, c: Client):
        """common exchange in session"""


class Dummy(ExTask):
    """dummy task"""

    async def exchange(self, c: Client):
        """"""
        c.log(logL.INFO, "dummy task")


@dataclass
class Loop(ExTask):
    task: ExTask
    func: Callable[[Any], bool]
    delay: int
    attempt_amount: int = 0
    """0 is never end loop"""

    async def exchange(self, c: Client):
        attempt = count()
        while not self.func(await self.task.exchange(c)):
            if next(attempt) == self.attempt_amount:
                return False
            await asyncio.sleep(self.delay)
        return True


class Sequence(ExTask):
    """for exchange task sequence"""
    tasks: list[ExTask]
    __is_exchange: bool

    def __init__(self, *tasks: ExTask):
        assert all((isinstance(t, ExTask) for t in tasks))
        self.tasks = list(tasks)
        self.__is_exchange = False

    def append(self, task: ExTask):
        if not self.__is_exchange:
            self.tasks.append(task)
        else:
            raise RuntimeError(F"append to {self.__class__.__name__} not allowed, already exchange started")

    async def exchange(self, c: Client) -> list[cdt.CommonDataType | None]:
        ret = list()
        self.__is_exchange = True
        for t in self.tasks:
            # ret.append(await t.exchange(c))
            # TODO: remove in future try-except block with pleasure return value => ret.append(await t.exchange())
            try:
                res = await t.exchange(c)
            except exc.ResultError as e:
                res = e
            ret.append(res)
        return ret


class InitType(ExTask):
    """nothing params"""
    async def exchange(self, c: Client):
        # read LDN
        data = await c.read_attr(collection.AttrDesc.LDN_VALUE)
        ldn = octet_string.LDN(data)
        # find device_id(type for Russia)
        type_value, _ = cdt.get_instance_and_pdu_from_value(await c.read_attr(ut.CosemAttributeDescriptor((1, "0.0.96.1.1.255", 2))))
        # find version data
        for desc in (ut.CosemAttributeDescriptor((1, "0.0.0.2.1.255", 2)), ut.CosemAttributeDescriptor((1, "0.0.96.1.2.255", 2))):
            try:
                ver_value, _ = cdt.get_instance_and_pdu_from_value(await c.read_attr(desc))
                break
            except exc.ResultError as e:
                if e.result == pdu.DataAccessResult.OBJECT_UNDEFINED:
                    """try search in old object and set to new"""
                    continue
                else:
                    raise e
            except exc.NeedUpdate as e:
                c.log(logL.WARN, F"{e}. I do it...")
                break
        else:
            raise exc.NoObject(F"not find version object in server")
        try:
            c.objects = collection.get_collection(
                manufacturer=ldn.manufacturer(),
                server_type=type_value,
                server_ver=AppVersion.from_str(ver_value.to_str()))
            c.objects.LDN.set_attr(2, ldn)
        except exc.NoConfig as e:
            c.log(logL.WARN, F"false init type procedure: {e}, start create objects from device")
            new_collection = collection.Collection(ldn=ldn)
            # read association
            object_list: cdt.Array = cdt.Array(await c.read_attr(collection.AttrDesc.OBJECT_LIST), type_=structs.ObjectListElement)
            for c_id, ver, ln, _ in object_list:
                new_obj = new_collection.add_if_missing(
                    class_id=ut.CosemClassId(int(c_id)),
                    version=ver,
                    logical_name=ln)
                if new_obj.CLASS_ID == overview.ClassID.ASSOCIATION_LN:  # search association for keep object_list into
                    await c.read_attr(new_obj.get_attr_descriptor(3))
                    if new_obj.associated_partners_id.client_SAP == c.SAP:
                        new_obj.set_attr(2, object_list)
            new_collection.get_class_version()
            c.objects = new_collection
            # read all DeviceIDObjects
            for d_id in collection.get_filtered(
                objects=new_collection.filter_by_ass(new_collection.get_association_id(c.SAP)),
                keys=(media_id.DEVICE_ID_OBJECTS,
                      media_id.OTHER_ABSTRACT_GENERAL_PURPOSE_OBIS_CODES)):
                await c.read_attribute(d_id, 2)

            # TODO: handle 6.2.42 DLMS UA 1000-1 Ed. 14 - Device ID objects, 6.2.4 Other abstract general purpose OBIS codes(Program entries for version)
            # TODO: keep in Types
        c.log(logL.INFO, F"added {len(c.objects)} DLMS objects")


@dataclass
class ReadAttribute(ExTask):
    ln: collection.LNContaining
    index: int

    async def exchange(self, c: Client) -> cdt.CommonDataType:
        # TODO: check is_readable
        obj = c.objects.get_object(self.ln)
        return await self.read_from_obj(c, obj, self.index)

    @staticmethod
    async def read_from_obj(c: Client, obj: collection.InterfaceClass, index: int) -> cdt.CommonDataType | ValueError:
        c.get_get_request_normal(
            attr_desc=obj.get_attr_descriptor(
                value=index,
                with_selection=bool(c.negotiated_conformance.selective_access)))
        start_read_time: float = time.perf_counter()
        await c.read_data_block()
        c.last_transfer_time = datetime.timedelta(seconds=time.perf_counter()-start_read_time)
        try:
            obj.set_attr(index, c.reply.data.get_data())
            return obj.get_attr(index)
        except ValueError as e:
            return e


@dataclass
class ReadEmptyAttribute(ExTask):
    """read if attribute is empty"""
    ln: collection.LNContaining
    index: int

    async def exchange(self, c: Client):
        # TODO: check is_readable
        if c.objects.get_object(self.ln).get_attr(self.index) is None:
            data = await ReadAttribute(
                ln=self.ln,
                index=self.index).exchange(c)


@dataclass
class ReadAttributes(ExTask):
    ln: collection.LNContaining
    indexes: tuple[int, ...]

    async def exchange(self, c: Client) -> tuple[cdt.CommonDataType | ValueError]:
        obj = c.objects.get_object(self.ln)
        ret: list[cdt.CommonDataType | ValueError] = list()
        # TODO: check for Get-Request-With-List
        for i in self.indexes:
            ret.append(await ReadAttribute.read_from_obj(c, obj, i))
        return tuple(ret)


@dataclass
class WriteAttribute(ExTask):
    ln: collection.LNContaining
    index: int
    value: bytes | str | int | list | tuple | datetime.datetime

    async def exchange(self, c: Client):
        obj = c.objects.get_object(self.ln)
        if isinstance(self.value, (str, int, list, tuple, datetime.datetime)):
            value2 = await c.encode(
                obj=obj,
                index=self.index,
                value=self.value)
            enc = value2.encoding
        else:
            enc = self.value
        data = c.get_set_request_normal(
            obj=obj,
            attr_index=self.index,
            value=enc)
        return await c.read_data_block()


@dataclass
class WriteAttributesOld(ExTask):
    """todo: use for write without value(from object) replace all to WriteAttribute in future."""
    ln: collection.LNContaining
    indexes: tuple[int, ...]

    async def exchange(self, c: Client):
        for i in self.indexes:
            if c.objects.is_writable(
                    ln=(obj := c.objects.get_object(self.ln)).logical_name,
                    index=i,
                    association_id=c.objects.get_association_id(c.SAP)):
                data = c.get_set_request_normal(
                    obj=obj,
                    attr_index=i)
                await c.read_data_block()
            else:
                raise exc.ITEApplication(F"Access Error. From current association: {obj}: {i} is not writable")


@dataclass
class ExecuteByDesc(ExTask):
    """execute method by method descriptor # TODO: rewrite this"""
    desc: ut.CosemMethodDescriptor

    async def exchange(self, c: Client):
        try:
            await c.execute_method(self.desc)
            c.set_error(Transmit.OK, F'Execute {self.desc}.')
        except Exception as e:
            c.log(logL.INFO, F'ERROR: Исполнение {self.desc}')
            c.set_error(Transmit.EXECUTE_ERROR, F'Исполнение {self.desc}')


@dataclass
class Execute(ExTask):
    """execute method by method descriptor # TODO: rewrite this with <value>"""
    ln: collection.LNContaining
    index: int
    value: str

    async def exchange(self, c: Client):
        obj = c.objects.get_object(self.ln)
        try:
            await c.execute_method(ut.CosemMethodDescriptor(
                (obj.CLASS_ID,
                 ut.CosemObjectInstanceId(obj.logical_name.contents),
                 ut.CosemObjectMethodId(self.index))
            ))
            c.set_error(Transmit.OK, F'Execute {self.ln}: {self.index}.')
        except Exception as e:
            c.log(logL.INFO, F'ERROR: Исполнение {self.ln}: {self.index}')
            c.set_error(Transmit.EXECUTE_ERROR, F'Исполнение {self.ln}: {self.index}')


class WriteTime(ExTask):
    """write Clock.time depend from transfer time"""

    async def exchange(self, c: Client):
        try:
            obj = c.objects.clock
            c.get_get_request_normal(obj.get_attr_descriptor(3))
            await c.read_data_block()
            tz = obj.get_attr_element(3).DATA_TYPE(c.reply.data.get_data())
            await WriteAttribute(
                ln=obj.logical_name,
                index=2,
                value=(datetime.datetime.utcnow() + datetime.timedelta(minutes=tz.decode()) + c.last_transfer_time)
            ).exchange(c)
            # obj.set_attr(2, (cst.OctetStringDateTime(datetime.datetime.utcnow() + datetime.timedelta(minutes=obj.time_zone.decode()) + dev.last_transfer_time)))
            # dev.write_attr(obj, 2)
            # logger.info(F'Write attribute: 2 success')
            c.errors[Transmit.OK] = 'Запись времени'
        except Exception as e:
            # logger.info(F'ERROR: write Clock: attribute 2 {e}')
            c.errors[Transmit.WRITE_ERROR] = F"write time: {e}"


@dataclass
class UpdateFirmware(ExTask):
    """only for KPZ now"""
    # firmwares: field(default=dict)

    async def exchange(self, c: Client) -> bool:
        # read properties for update
        read_seq = Sequence()
        match c.objects.collection_ver:
            case AppVersion(0, 0, patch) if 25 <= patch < 26:
                read_seq.append(ReadAttribute(
                    ln=c.objects.firmwares_description.logical_name,
                    index=2))
                read_seq.append(ReadAttribute(
                    ln=c.objects.firmware_version.logical_name,
                    index=2))
                read_seq.append(ReadAttribute(
                    ln=c.objects.firmware_image_transfer.logical_name,
                    index=2))
            case AppVersion(0, 0, patch) if 26 <= patch <= 52:  # to max available version
                read_seq.append(ReadAttribute(
                    ln=c.objects.firmwares_description.logical_name,
                    index=2))
                read_seq.append(ReadAttribute(
                    ln=c.objects.firmware_version.logical_name,
                    index=2))
                read_seq.append(ReadAttribute(
                    ln=c.objects.firmware_image_transfer.logical_name,
                    index=2))
                read_seq.append(ReadAttribute(
                    ln=c.objects.boot_image_transfer.logical_name,
                    index=2))
            case AppVersion(0, 0, 53) | AppVersion(1, 1 | 2 | 3) | AppVersion(1, 4, 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7):  # to max available version
                read_seq.append(ReadAttribute(
                    ln=c.objects.firmwares_description.logical_name,
                    index=2))
                read_seq.append(ReadAttribute(
                    ln=c.objects.firmware_version.logical_name,
                    index=2))
                read_seq.append(ReadAttributes(
                    ln=c.objects.firmware_image_transfer.logical_name,
                    indexes=(2, 6)))
                read_seq.append(ReadAttribute(
                    ln=c.objects.boot_image_transfer.logical_name,
                    index=2))
            case AppVersion(1, 4 | 5 | 6):  # to max available version
                read_seq.append(ReadAttribute(
                    ln=c.objects.firmwares_description.logical_name,
                    index=2))
                read_seq.append(ReadAttributes(
                    ln=c.objects.firmware_image_transfer.logical_name,
                    indexes=(2, 6)))
                read_seq.append(ReadAttribute(
                    ln=c.objects.boot_image_transfer.logical_name,
                    index=2))
            case AppVersion(-1):
                read_seq.append(ReadAttribute(
                    ln=c.objects.firmware_version.logical_name,
                    index=2))
                c.set_error(Application.VERSION_ERROR, 'Need reread')
            case AppVersion(0, 0, 0):
                c.set_error(Application.VERSION_ERROR, 'Unknown metrology Version')
                return False
            case AppVersion():
                c.set_error(Application.VERSION_ERROR, F'Version {c.objects.server_ver} don\'t read update properties')
                return False
            case _:
                c.set_error(Transmit.READ_ERROR, 'Wrong AppVersion')
                return False
        # add optional object if its values absence
        ret = await read_seq.exchange(c)
        # todo: check exchange result
        c.objects.firmware_image_transfer.clear_image()  # TODO: check for missing objects !!
        firmwares_description_obj = c.objects.firmwares_description
        boot_version: int = int(firmwares_description_obj.value.decode()[:4])
        firmwares_description = firmwares_description_obj.value.decode()[4:]
        suitable_firmware: AppVersion = AppVersion(0, 0, 1)
        suitable_boot: int = 0
        temp_key: tuple | None = None
        """ key of image for update """
        if not (firms := get_firmware(manufacturer := c.objects.manufacturer)):
            c.log(logL.ERR, F"not find firmwares for {manufacturer=}")
            return False  # not find
        firmwares, boots = firms
        # search firmware image
        for key in firmwares:
            match key:
                case (int(), int(), int()) as app_args, str() as desc:
                    match compare_version := AppVersion(*app_args):
                        case AppVersion(0) if firmwares_description in desc:
                            """good"""
                        case AppVersion(1, minor) if minor <= 2 and firmwares_description in desc:
                            """good"""
                        case AppVersion(1, minor) if (minor in (3, 4, 5, 6)) and desc.split("_", maxsplit=5)[1:5] == firmwares_description.split("_", maxsplit=5)[:4]:
                            """good"""
                        case AppVersion(0 | 1, minor) if minor <= 6:
                            continue
                        case error:
                            c.log(logL.ERR, F"Неизвестная версия ПО: {error}")
                            return False
                case error_key_type:
                    c.log(logL.ERR, F"Неизвестный тип {error_key_type} в *.dat файле")
                    return False
            if compare_version > suitable_firmware:
                suitable_firmware = compare_version
                temp_key = key
        if suitable_firmware != c.objects.server_ver[0] and temp_key is not None:
            image: bytes = firmwares.get(temp_key)
            c.objects.firmware_image_transfer.set_image_for_update(
                value=image,
                identifier=bytearray(hashlib.md5(image).digest()))
        # search boot image
        temp_key = None
        for key in boots:
            match key:
                case 1 | 2 | 3 | 4 | 5 | 6 as compare_version, desc if firmwares_description in desc:
                    """good"""
                case 7 | 8 | 9 | 10 | 11 as compare_version, desc if desc.split("_", maxsplit=5)[1:5] == firmwares_description.split("_", maxsplit=5)[:4]:
                    """good"""
                # case 9 | 10 as invalid:
                #     messagebox.showerror("Внутренняя ошибка", F"Невалидная версия загрузчика {invalid}")
                case int() as version, _ if version <= 11:
                    continue
                case error:
                    c.log(logL.ERR, F"Неизвестная версия загрузчика {error[0]}")
                    return False
            if compare_version > suitable_boot:
                suitable_boot = compare_version
                temp_key = key
        c.objects.boot_image_transfer.clear_image()
        if suitable_boot != boot_version and temp_key is not None:
            image: bytes = boots.get(temp_key)
            c.objects.boot_image_transfer.set_image_for_update(
                value=image,
                identifier=bytearray(hashlib.md5(image).digest()))

        # update
        match c.objects.server_ver[0]:
            case AppVersion(0, 0, 53 | 54) | AppVersion(1, 1 | 2 | 3 | 4 | 5 | 6):
                if await self.__is_updated_image_3(c=c, obj=c.objects.boot_image_transfer):
                    await ReadAttribute(
                        ln=c.objects.firmwares_description.logical_name,
                        index=2).exchange(c)
                    return await self.__is_updated_image_3(c=c, obj=c.objects.firmware_image_transfer)
            case AppVersion(0, 0, patch) if 48 <= patch <= 52:
                if await self.__is_updated_image_2(c=c, obj=c.objects.boot_image_transfer):
                    await ReadAttribute(
                        ln=c.objects.firmwares_description.logical_name,
                        index=2
                    ).exchange(c)
                    return await self.__is_updated_image_2(c=c, obj=c.objects.firmware_image_transfer)
            case AppVersion(0, 0, patch) if 39 <= patch <= 47:
                if await self.__is_updated_image(c=c, obj=c.objects.boot_image_transfer):
                    await ReadAttribute(
                        ln=c.objects.firmwares_description.logical_name,
                        index=2
                    ).exchange(c)
                    return await self.__is_updated_image(c=c, obj=c.objects.firmware_image_transfer)
            case AppVersion(0, 0, patch) if 25 <= patch <= 38:
                return await self.__is_updated_image(c=c, obj=c.objects.firmware_image_transfer)
            case AppVersion(0, 0, 0):
                c.set_error(Transmit.EXECUTE_ERROR, F'Не могу установить номер версии счетчика')
                return False
            case AppVersion():
                c.set_error(Transmit.EXECUTE_ERROR, F'Невозможно обновить версию {c.objects.server_ver}')
                return False
        return False

    async def __is_updated_image(self, c: Client, obj: collection.ImageTransfer) -> bool:
        """ update image if blocks is fulls """
        if obj.is_image_exist:
            is_activating: bool = False
            c.current_obj = obj
            try:
                await c.execute_method(obj.get_meth_descriptor(1))
                c.log(logL.INFO, "Start initiate Image Transfer")
                while True:
                    if c.is_stop_request:
                        c.set_error(Transmit.ABORT, '')
                        return False
                    await c.execute_method(obj.get_meth_descriptor(2))
                    c.log(logL.INFO, F"start block: {obj.current_block_transfer} transferred")
                    try:
                        obj.set_next_block()
                    except StopIteration:
                        c.log(logL.INFO, "All blocks transferred")
                        break
                # c.execute_method(obj.get_meth_descriptor(3))  # Start Verify Transfer. todo: removed Verification because don't work with change to 1.3
                is_activating = True
                await c.execute_method(obj.get_meth_descriptor(4))
                c.log(logL.INFO, "Start Activate Transfer")
                is_activating = False
                c.set_error(Application.OK, F'Activated')
                return True
            except Exception as e:
                c.set_error(Transmit.EXECUTE_ERROR, F'unhandled update error. {e.args[0]}')
                return False
            finally:
                if is_activating:
                    c.set_error(Transmit.EXECUTE_ERROR, 'Activating')
                c.current_obj = None
        else:
            return True

    async def __is_updated_image_2(self, c: Client, obj: collection.ImageTransfer, with_abort: bool = True) -> bool:
        """ update image if blocks is fulls ver 2"""
        if obj.is_image_exist:
            is_activating: bool = False
            c.current_obj = obj
            try:
                # TODO: copypast from __is_updated_image_3
                await ReadAttributes(
                    ln=obj.logical_name,
                    indexes=(6, 7)
                ).exchange(c)
                if obj.image_transfer_status in (i_t_status.TRANSFER_NOT_INITIATED, i_t_status.VERIFICATION_FAILED, i_t_status.ACTIVATION_FAILED) \
                        or len(obj.image_to_activate_info) == 0 \
                        or obj.image_to_activate_info[0].image_to_activate_identification != obj.image_transfer_initiate.image_identifier:
                    await c.execute_method(obj.get_meth_descriptor(1))
                    c.log(logL.INFO, "Start initiate Image Transfer")
                    obj.set_block_for_transfer(0)
                else:
                    c.log(logL.INFO, "already INITIATED")
                    await ReadAttribute(
                        ln=obj.logical_name,
                        index=4
                    ).exchange(c)
                    try:
                        block_number = int(obj.image_first_not_transferred_block_number)
                        obj.set_block_for_transfer(block_number if block_number != 1 else 0)  # bag in SERVER: always start from 1
                    except IndexError:
                        """pass. not set"""
                # END copypast
                while True:
                    if c.is_stop_request:
                        c.set_error(Transmit.ABORT, '')
                        return False
                    await c.execute_method(obj.get_meth_descriptor(2))
                    c.log(logL.INFO, "start block: {obj.current_block_transfer} transferred")
                    try:
                        obj.set_next_block()
                    except StopIteration:
                        c.log(logL.INFO, "All blocks transferred")
                        break
                await c.execute_method(obj.get_meth_descriptor(4))
                c.log(logL.INFO, "Start Activate Transfer. Timeout 22 second. Waiting verification")
                time.sleep(22)
                is_activating = False
                c.set_error(Transmit.ABORT, F'Expected device Reboot')
                c.set_error(Application.OK, F'Activated')
                return True
            except Exception as e:
                c.set_error(Transmit.EXECUTE_ERROR, F'{e.args[0]}')
                return False
            finally:
                if is_activating:
                    c.set_error(Transmit.EXECUTE_ERROR, 'Activating')
                c.current_obj = None
        else:
            return True

    async def __is_updated_image_3(self, c: Client, obj: collection.ImageTransfer) -> bool:
        """ update image if blocks is fulls ver 3"""
        if obj.is_image_exist:
            # TODO: need common counter for exit from infinity loop
            c.current_obj = obj
            self.previous_status: int | None = None
            await ReadAttributes(
                ln=obj.logical_name,
                indexes=(6, 7)
            ).exchange(c)
            current_status = obj.image_transfer_status
            if obj.image_transfer_status in (i_t_status.TRANSFER_NOT_INITIATED, i_t_status.VERIFICATION_FAILED, i_t_status.ACTIVATION_FAILED) \
                    or len(obj.image_to_activate_info) == 0 \
                    or obj.image_to_activate_info[0].image_to_activate_identification != obj.image_transfer_initiate.image_identifier:
                await c.execute_method(obj.get_meth_descriptor(1))
                c.log(logL.INFO, "Start initiate Image Transfer")
                await ReadAttribute(
                    ln=obj.logical_name,
                    index=6
                ).exchange(c)
            elif obj.image_transfer_status == i_t_status.ACTIVATION_SUCCESSFUL:
                # image in outside memory and already activated early, but erased by hard programming. Need again go to activation
                obj.image_transfer_status.set(i_t_status.VERIFICATION_SUCCESSFUL)
            else:
                c.log(logL.INFO, "already INITIATED")
                await ReadAttribute(
                    ln=obj.logical_name,
                    index=4
                ).exchange(c)
                try:
                    obj.set_block_for_transfer(int(obj.image_first_not_transferred_block_number))
                except IndexError as e:
                    """Skip set block"""
                    await c.execute_method(obj.get_meth_descriptor(3))
                    c.log(logL.INFO, "Start Verify Transfer")
            while True:
                c.log(logL.INFO, F"{obj.image_transfer_status=}")
                try:
                    match current_status:
                        case self.previous_status if self.previous_status == i_t_status.VERIFICATION_FAILED:
                            c.set_error(Application.VERIFY_ERROR, 'Twice ERROR')
                            return False
                        case self.previous_status if self.previous_status == i_t_status.TRANSFER_INITIATED:
                            c.set_error(Application.VERIFY_ERROR, F"Expected Switch to Verification Initiated status, got Initiated")
                        case i_t_status.TRANSFER_NOT_INITIATED:
                            c.set_error(Application.ACTIVATION_ERROR, 'Got Not initiated status after call Initiation')
                        case i_t_status.TRANSFER_INITIATED:
                            while True:
                                if c.is_stop_request:
                                    c.set_error(Transmit.ABORT, '')
                                    return False
                                await c.execute_method(obj.get_meth_descriptor(2))  # start block: {obj.current_block_transfer} transferred
                                try:
                                    obj.set_next_block()
                                except StopIteration:
                                    c.log(logL.INFO, "All blocks transferred")
                                    break
                            await c.execute_method(obj.get_meth_descriptor(3))  # Start Verify Transfer
                        case i_t_status.VERIFICATION_INITIATED:
                            c.log(logL.INFO, "read bitstring. It must grow")
                            # TODO: calculate time for waiting or read growing bitstring ?
                            await ReadAttribute(
                                ln=obj.logical_name,
                                index=3
                            ).exchange(c)
                            if len(obj.image_transferred_blocks_status) < int(obj.image_block_transfer.image_block_number):
                                c.log(logL.INFO, F"Got blocks[{len(obj.image_transferred_blocks_status)}]: {obj.image_transferred_blocks_status}")
                            else:
                                c.log(logL.INFO, "All Bits solved")
                        case i_t_status.VERIFICATION_FAILED:
                            await ReadAttribute(
                                ln=obj.logical_name,
                                index=3
                            ).exchange(c)
                            valid = obj.image_transferred_blocks_status.decode()
                            c.log(logL.INFO, F"Got blocks[{len(obj.image_transferred_blocks_status)}]: {obj.image_transferred_blocks_status}")
                            for index in filter(lambda it: valid[it] == 0, range(len(valid))):
                                obj.set_block_for_transfer(index)
                                await c.execute_method(obj.get_meth_descriptor(2))
                                c.log(logL.INFO, F"start block: {obj.current_block_transfer} transferred")
                            await c.execute_method(obj.get_meth_descriptor(3))
                            c.log(logL.INFO, "Start Verify Transfer")
                        case i_t_status.VERIFICATION_SUCCESSFUL:
                            await ReadAttributes(
                                ln=obj.logical_name,
                                indexes=(7, 4, 3)
                            ).exchange(c)
                            valid = obj.image_transferred_blocks_status.decode()
                            c.log(logL.INFO, F"md5:{obj.image_to_activate_info[0].image_to_activate_signature}")
                            if any(map(lambda it: it == 0, valid)):
                                c.set_error(Application.VERIFY_ERROR, 'Exist 0 blocks')
                                await c.execute_method(obj.get_meth_descriptor(1))
                                c.log(logL.INFO, "Start initiate Image Transfer, after wrong verify. Exist 0 blocks")
                                return False
                            elif int(obj.image_first_not_transferred_block_number) < len(valid):
                                c.set_error(Application.VERIFY_ERROR, F'Got {obj.image_first_not_transferred_block_number} not transferred block')
                                await c.execute_method(obj.get_meth_descriptor(1))
                                c.log(logL.INFO, "Start initiate Image Transfer, after wrong verify. Got not transferred block")
                                return False
                            elif obj.image_to_activate_info[0].image_to_activate_signature != obj.image_to_activate_info[0].image_to_activate_identification:
                                message: str = F"Signature not match to Identification: got {obj.image_to_activate_info[0].image_to_activate_signature}, " \
                                               F"expected {obj.image_to_activate_info[0].image_to_activate_identification}"
                                c.set_error(Application.VERIFY_ERROR, message)
                                await c.execute_method(obj.get_meth_descriptor(1))
                                c.log(logL.INFO, F"Start initiate Image Transfer, after wrong verify. {message}")
                                return False
                            else:
                                await c.execute_method(obj.get_meth_descriptor(4))
                                c.log(logL.INFO, "Start Activate Transfer")
                        case i_t_status.ACTIVATION_INITIATED:
                            c.set_error(Application.OK, F'Activated')
                            await c.disconnect_request()
                            time.sleep(5)
                            return True
                        case i_t_status.ACTIVATION_SUCCESSFUL:
                            await ReadAttribute(
                                ln=obj.logical_name,
                                index=7
                            ).exchange(c)
                            if obj.image_to_activate_info[0].image_to_activate_identification == obj.image_transfer_initiate.image_identifier:
                                c.set_error(Application.OK, F'Activated')
                                c.log(logL.INFO, "already activated this image")
                                return True
                            else:
                                await c.execute_method(obj.get_meth_descriptor(1))
                                c.log(logL.INFO, "Start initiate Image Transfer")
                                # TODO: need wait clearing memory in device ~5 sec
                        case i_t_status.ACTIVATION_FAILED:
                            c.set_error(Application.ACTIVATION_ERROR, 'Ошибка активации...')
                            return False
                        case _: raise exc.DLMSException('Unknown image transfer status')
                    self.previous_status = current_status
                except Exception as e:
                    c.set_error(Transmit.EXECUTE_ERROR, F'{e.args[0]}')
                    return False
                finally:
                    c.current_obj = None
                time.sleep(1)  # TODO: tune it
                await ReadAttribute(
                    ln=obj.logical_name,
                    index=6
                ).exchange(c)
        else:
            return True

#
#  Copyright (c) 2018-2023 Renesas Inc.
#  Copyright (c) 2018-2023 EPAM Systems Inc.
#
import time
from contextlib import contextmanager

import grpc
from aos_prov.utils.common import print_message, print_left, print_done, print_success
from colorama import Fore, Style
from google.protobuf import empty_pb2

from aos_prov.communication.unit.v3.generated import iamanagercommon_pb2 as iam_manager_common
from aos_prov.communication.unit.v3.generated import iamanagerprotected_pb2 as iam_manager
from aos_prov.communication.unit.v3.generated import iamanagerprotected_pb2_grpc as api_iam_manager_grpc
from aos_prov.communication.unit.v3.generated import iamanagerpublic_pb2_grpc as iam_manager_public_grpc
from aos_prov.utils.errors import UnitError, GrpcUnimplemented
from aos_prov.utils.unit_certificate import UnitCertificate

UNIT_DEFAULT_PORT = 8089


class UnitCommunicationV3:
    def __init__(self, address: str = 'localhost:8089', set_users=True):
        self._need_set_users = True

        if address is None:
            address = 'localhost:8089'
        parts = address.split(':')
        if len(parts) == 2:
            try:
                port = int(parts[1])
                if not 1 <= port <= 65535:
                    raise UnitError("Unit port is invalid")
            except ValueError:
                raise UnitError("Unit port is invalid")
        else:
            address = address + ':' + str(UNIT_DEFAULT_PORT)
        self.__unit_address = address

    @property
    def need_set_users(self):
        return self._need_set_users

    @need_set_users.setter
    def need_set_users(self, value):
        self._need_set_users = value

    @contextmanager
    def unit_stub(self, catch_inactive=False, wait_for_close=False):
        try:
            with grpc.insecure_channel(self.__unit_address) as channel:
                stub = api_iam_manager_grpc.IAMProtectedServiceStub(channel)
                if wait_for_close:
                    def _stop_wait(state):
                        print(str(state))
                        if state is grpc.ChannelConnectivity.SHUTDOWN:
                            channel.unsubscribe(_stop_wait)
                            return
                    channel.subscribe(_stop_wait, try_to_connect=False)
                yield stub

        except grpc.RpcError as e:
            if catch_inactive and \
                    not (e.code() == grpc.StatusCode.UNAVAILABLE.value and e.details() == 'Socket closed'):
                return
            elif wait_for_close and (e.code() == grpc.StatusCode.UNKNOWN.value and e.details() == 'Stream removed'):
                return
            raise UnitError(f"FAILED! Error occurred: \n{e.code()}: {e.details()}")

    @contextmanager
    def unit_public_stub(self):
        try:
            with grpc.insecure_channel(self.__unit_address) as channel:
                stub = iam_manager_public_grpc.IAMPublicServiceStub(channel)
                yield stub

        except grpc.RpcError as e:
            if e.code().value == grpc.StatusCode.UNIMPLEMENTED.value:
                raise GrpcUnimplemented(f'Protocol V3 is not supported: \n{e.code()}: {e.details()}')
            else:
                raise UnitError(f"Error occurred: \n{e.code()}: {e.details()}")

    def get_protocol_version(self) -> int:
        with self.unit_public_stub() as stub:
            print_left('Getting protocol version...')
            response = stub.GetAPIVersion(empty_pb2.Empty())
            print_success(str(response.version))
            return int(response.version)

    def get_system_info(self) -> (str, str):
        with self.unit_public_stub() as stub:
            print_left('Getting System Info...')
            response = stub.GetSystemInfo(empty_pb2.Empty())
            print_done()
            print_left('System ID:')
            print_success(response.system_id)
            print_left('Model name:')
            print_success(response.board_model)
            return response.system_id, response.board_model

    def clear(self, certificate_type: str) -> None:
        with self.unit_stub() as stub:
            print_left('Clear certificate: ' + certificate_type)
            response = stub.Clear(iam_manager.ClearRequest(type=certificate_type))
            print_done()
            return response

    def set_cert_owner(self, certificate_type: str, password: str) -> None:
        with self.unit_stub() as stub:
            print_left('Set owner: ' + certificate_type)
            response = stub.SetOwner(iam_manager.SetOwnerRequest(type=certificate_type, password=password))
            print_done()
            return response

    def get_cert_types(self) -> [str]:
        with self.unit_public_stub() as stub:
            print_left('Getting certificate types to renew')
            response = stub.GetCertTypes(empty_pb2.Empty())
            print_done()
            return response.types

    def create_keys(self, cert_type: str, password: str) -> UnitCertificate:
        with self.unit_stub() as stub:
            print_left('Generating key type:' + cert_type)
            response = stub.CreateKey(iam_manager.CreateKeyRequest(type=cert_type, password=password))
            uc = UnitCertificate()
            uc.cert_type = response.type
            uc.csr = response.csr
            print_done()
            return uc

    def apply_certificate(self, unit_cert: UnitCertificate):
        with self.unit_stub() as stub:
            print_left('Applying type:' + unit_cert.cert_type)
            stub.ApplyCert(iam_manager.ApplyCertRequest(type=unit_cert.cert_type, cert=unit_cert.certificate))
            print_done()

    def set_users(self, users: [str]):
        with self.unit_stub() as stub:
            print_left('Setting users...')
            stub.SetUsers(iam_manager_common.Users(users=users))
            print_done()

    def encrypt_disk(self, password: str):
        print_left('Starting disk encryption...')
        with self.unit_stub(wait_for_close=True) as stub:
            stub.EncryptDisk(iam_manager.EncryptDiskRequest(password=password))
            print_done()

    def finish_provisioning(self):
        with self.unit_stub(True) as stub:
            print_left('Finishing provisioning')
            stub.FinishProvisioning(empty_pb2.Empty())
            print_done()

    def wait_for_connection(self):
        try:
            print_message('Sleep for 5 seconds...')
            time.sleep(5)
            print_message('Waiting for Unit reboot...')
            grpc.channel_ready_future(grpc.insecure_channel(self.__unit_address)).result(timeout=300)
            print_message('Unit is online')
        except grpc.FutureTimeoutError:
            raise UnitError('Unit did not go online')

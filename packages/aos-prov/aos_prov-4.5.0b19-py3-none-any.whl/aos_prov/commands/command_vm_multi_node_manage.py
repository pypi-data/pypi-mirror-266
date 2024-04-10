#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
# pylint: disable=R0913,R0914,R0915
import os
import platform
import socket
import subprocess
import uuid
from pathlib import Path
from random import randint
from shutil import copyfile

from aos_prov.commands.download import download_and_save_multinode
from aos_prov.utils.common import (
    AOS_DISKS_PATH,
    DISK_IMAGE_DOWNLOAD_URL,
    DOWNLOADS_PATH,
    IMAGE_WITHOUT_NODES_FILENAME,
    NODE0_IMAGE_FILENAME,
    NODE1_IMAGE_FILENAME,
    print_done,
    print_error,
    print_left,
    print_message,
    print_success,
)
from aos_prov.utils.errors import AosProvError

_MIN_PORT = 8090
_MAX_PORT = 8999
_PROVISION_PORT = 8089
_SSH_PORT = 22


def _is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_handler:
        return socket_handler.connect_ex(('localhost', port)) == 0


def _delete_controller(vm_uuid: str, controller_name: str):
    command = [
        'VBoxManage',
        'storagectl',
        vm_uuid,
        f'--name={controller_name}',
        '--controller=',
        '--remove',
    ]
    execute_command(command, catch_error=False)


def _create_storage_controller_ahci(vm_uuid: str, controller_name: str):
    """Create SATA controller for VM.

    Args:
        vm_uuid (str): UUID or Name of VM to attach controller.
         controller_name (str): Name of the controller.
    """
    command = [
        'VBoxManage',
        'storagectl',
        vm_uuid,
        f'--name={controller_name}',
        '--add=sata',
        '--controller=IntelAhci',
        '--portcount=1',
        '--hostiocache=on',
        '--bootable=on',
    ]
    execute_command(command)


def _create_storage_controller_piix4(vm_uuid: str, controller_name: str):
    """Create SATA controller for VM.

    Args:
         vm_uuid (str): UUID or Name of VM to attach controller.
         controller_name (str): Name of the controller.
    """
    # TODO: remove in case support of old version R3.0.1 is not required
    command = [
        'VBoxManage',
        'storagectl',
        vm_uuid,
        f'--name={controller_name}',
        '--add=ide',
        '--controller=PIIX4',
        '--portcount=2',
        '--hostiocache=on',
        '--bootable=on',
    ]
    execute_command(command)


def _attach_disk(vm_uuid: str, attach_to_controller_name: str, disk_location: str, add_disk=False):
    """Attach disk file to the controller.

    Args:
         vm_uuid (str): UUID or Name of VM to attach controller.
         attach_to_controller_name (str): Name of the controller where disk will be attached.
         disk_location (str): path to the disk file.
         add_disk (bool): If true, add disk file to the VM
    """
    command = [
        'VBoxManage',
        'storageattach',
        vm_uuid,
        '--storagectl',
        attach_to_controller_name,
        '--port',
        '0',
        '--type',
        'hdd',
        '--medium',
        disk_location,
    ]

    if add_disk:
        command.append('--device')
        command.append('0')

    execute_command(command)


def _create_network(network_name: str):
    print_left('Creating a network for the units...')
    command = [
        'VBoxManage',
        'natnetwork',
        'add',
        '--netname',
        network_name,
        '--network',
        '10.0.0.0/24',
        '--enable',
        '--dhcp',
        'on',
    ]
    execute_command(command)
    print_success(f'Network {network_name} has been created')


def _remove_network(network_name: str):
    print_left(f'Removing a network: {network_name} for the units...')
    command = [
        'VBoxManage',
        'natnetwork',
        'remove',
        '--netname',
        network_name,
    ]
    execute_command(command, catch_error=True)
    print_message('Network has been removed')


def _forward_port_nat_network(network_name: str, forward_name: str, from_ip: str, from_port: int, to_port=None) -> int:
    if to_port is None:
        to_port = randint(_MIN_PORT, _MAX_PORT)  # noqa: S311
        while _is_port_in_use(to_port):
            to_port = randint(_MIN_PORT, _MAX_PORT)  # noqa: S311

    command = [
        'VBoxManage',
        'natnetwork',
        'modify',
        '--netname',
        network_name,
        '--port-forward-4',
        f'{forward_name}:tcp:[]:{to_port}:[{from_ip}]:{from_port}',
    ]

    execute_command(command)
    return to_port


def _forward_port_nat(forward_name: str, from_port: int, to_port=None, vm_uuid: str = '') -> int:
    # TODO: remove in case support of old version R3.0.1 is not required
    if to_port is None:
        to_port = randint(_MIN_PORT, _MAX_PORT)  # noqa: S311
        while _is_port_in_use(to_port):
            to_port = randint(_MIN_PORT, _MAX_PORT)  # noqa: S311
    command_nat = [
        'VBoxManage',
        'modifyvm',
        vm_uuid,
        '--nic1',
        'nat',
        '--nic-type1',
        '82545EM',
    ]
    execute_command(command_nat)

    command_forward = [
        'VBoxManage',
        'modifyvm',
        vm_uuid,
        '--natpf1',
        f'{forward_name},tcp,,{to_port},,{from_port}',
    ]

    execute_command(command_forward)

    return to_port


def check_virtual_box():
    print_left('Checking VirtualBox...')

    if platform.machine().lower() not in {'amd64', 'x86_64'}:
        raise AosProvError('Only amd64 architecture is supported.')

    try:
        response = execute_command(['VBoxManage', '--version'], catch_error=False)
    except AosProvError as exc:
        raise AosProvError('VirtualBox is not installed or it is not in the PATH') from exc

    if 'WARNING: The vboxdrv kernel module is not loaded' in response:
        raise AosProvError('VirtualBox kernel modules is not installed.')

    if not response.startswith('7'):
        raise AosProvError('VirtualBox 7 is only supported')

    print_success(response)


def new_vms(vm_name: str, disk_location: str, nodes_count=2, check_virtualbox=True) -> ():
    if check_virtualbox:
        check_virtual_box()
    print_message('Creating a new virtual machines...')

    disk_location_path = Path(disk_location)
    is_image_without_nodes = False

    if (disk_location_path / IMAGE_WITHOUT_NODES_FILENAME).exists():
        # TODO: remove in case support of old version R3.0.1 is not required
        print_message('Found VM image (v3.0.1) without supporting Nodes functionality. Use it as one node VM.')
        nodes_count = 1
        nodes = [
            {
                'name': 'node0',
                'uuid': str(uuid.uuid4()),
                'disk_name': IMAGE_WITHOUT_NODES_FILENAME,
                'disk_location': Path(disk_location_path / IMAGE_WITHOUT_NODES_FILENAME),
            },
        ]
        is_image_without_nodes = True
    else:
        node0_exists = (disk_location_path / NODE0_IMAGE_FILENAME).exists()
        node1_exists = (disk_location_path / NODE1_IMAGE_FILENAME).exists()
        if not node0_exists or not node1_exists:
            if disk_location_path != AOS_DISKS_PATH:
                raise AosProvError(f'Disk images not found in directory {disk_location}. Cannot proceed!')
            print_message('Local images not found. Downloading...')
            download_and_save_multinode(DISK_IMAGE_DOWNLOAD_URL, DOWNLOADS_PATH, force_overwrite=False)
            print_success('Download finished. You may find Unit images in: ' + str(DOWNLOADS_PATH.resolve()))
        nodes = [
            {
                'name': 'node0',
                'uuid': str(uuid.uuid4()),
                'disk_name': NODE0_IMAGE_FILENAME,
                'disk_location': Path(disk_location_path / NODE0_IMAGE_FILENAME),
            },
        ]

        if nodes_count != 1:
            nodes.append(
                {
                    'name': 'node1',
                    'uuid': str(uuid.uuid4()),
                    'disk_name': NODE1_IMAGE_FILENAME,
                    'disk_location': Path(disk_location_path / NODE1_IMAGE_FILENAME),
                },
            )

    units_network_name = f'aos-network-{vm_name}'
    units_vm_group = f'/AosUnits/{vm_name}'
    try:
        provisioning_port, node0_ssh_port, node1_ssh_port = None, None, None
        if not is_image_without_nodes:
            _create_network(units_network_name)
            print_left('Forwarding provisioning port...')
            provisioning_port = _forward_port_nat_network(
                units_network_name,
                forward_name='provisioningPortForward',
                from_ip='10.0.0.100',
                from_port=_PROVISION_PORT,
            )
            print_success(provisioning_port)

            print_left('Forwarding ssh port to node0...')
            node0_ssh_port = _forward_port_nat_network(
                units_network_name,
                forward_name='node0ssh',
                from_ip='10.0.0.100',
                from_port=_SSH_PORT,
            )
            print_success(node0_ssh_port)

            node1_ssh_port = None
            if nodes_count > 1:
                print_left('Forwarding ssh port to node1...')
                node1_ssh_port = _forward_port_nat_network(
                    units_network_name,
                    forward_name='node1ssh',
                    from_ip='10.0.0.101',
                    from_port=_SSH_PORT,
                )
                print_success(node1_ssh_port)

        for node in nodes:
            print_left(f'Creating a new VM for {node["name"]}...')
            create_node_vm(
                node['name'],
                node['uuid'],
                units_vm_group,
                node['disk_location'],
                node['disk_name'],
                units_network_name,
                is_image_without_nodes,
            )
            print_done()

            if is_image_without_nodes:
                # TODO: remove in case support of old version R3.0.1 is not required
                print_left('Forwarding provisioning port...')
                provisioning_port = _forward_port_nat(
                    forward_name='provisioningPortForward',
                    from_port=_PROVISION_PORT,
                    vm_uuid=node['uuid'],
                )
                print_success(provisioning_port)

                print_left('Forwarding ssh port to node0...')
                node0_ssh_port = _forward_port_nat(
                    forward_name='node0ssh',
                    from_port=_SSH_PORT,
                    vm_uuid=node['uuid'],
                )
                print_success(node0_ssh_port)

        return provisioning_port, node0_ssh_port, node1_ssh_port
    except AosProvError as error:
        print_error('Cannot create VM. Clean up all related resources. Try again.')
        remove_vms_in_group(vm_name)
        raise error


def create_node_vm(  # noqa: WPS211
    vm_name: str,
    vm_uuid: str,
    group: str,
    original_disk_path: Path,
    disk_name: str,
    network_name,
    is_image_without_nodes: bool,
):
    create_vm_command = [
        'VBoxManage',
        'createvm',
        f'--name={vm_name}',
        '--ostype=Linux_64',
        f'--uuid={vm_uuid}',
        f'--groups={group}',
        '--default',
        '--register',
    ]

    cpu_count = 1
    if platform.system() in {'Windows', 'Darwin'}:
        cpu_count = 4

    set_vm_params = [
        'VBoxManage',
        'modifyvm',
        vm_uuid,
        '--memory=1024',
        '--firmware=efi',
        f'--cpus={cpu_count}',
    ]

    set_vm_net = [
        'VBoxManage',
        'modifyvm',
        vm_uuid,
        '--nic1=natnetwork',
        f'--nat-network1={network_name}',
    ]

    # Set paravirtualization to KVM
    set_vm_kvm = [
        'VBoxManage',
        'modifyvm',
        vm_uuid,
        '--paravirt-provider=kvm',
    ]

    disable_time_sync = [
        'VBoxManage',
        'setextradata',
        vm_uuid,
        '"VBoxInternal/Devices/VMMDev/0/Config/GetHostTimeDisabled" 1',
    ]

    execute_command(create_vm_command)
    execute_command(set_vm_params)
    if not is_image_without_nodes:
        execute_command(set_vm_net)
    execute_command(set_vm_kvm)
    execute_command(disable_time_sync)
    _delete_controller(vm_uuid, 'SATA')
    _delete_controller(vm_uuid, 'IDE')

    if is_image_without_nodes:
        # TODO: remove in case support of old version R3.0.1 is not required
        _create_storage_controller_piix4(vm_uuid, 'SATA')
    else:
        _create_storage_controller_ahci(vm_uuid, 'SATA')

    destination_image = str((_find_vm_location(vm_uuid) / disk_name).resolve())
    copyfile(original_disk_path.absolute(), destination_image)

    try:
        _attach_disk(vm_uuid, 'SATA', disk_location=destination_image, add_disk=is_image_without_nodes)
    except AosProvError as error:
        print_error(f'Cannot attach disk {destination_image} to VM. Clean up all related resources. Try again.')
        os.remove(destination_image)
        raise error


def remove_vms_in_group(vm_name: str):
    units_network_name = f'aos-network-{vm_name}'
    vm_group = f'/AosUnits/{vm_name}'

    print_message(f'Removing VMs in Groups: {vm_group} for the units...')

    # find uuids of all VMs into the required Group
    detailed_list_vms_command = [
        'VBoxManage',
        'list',
        'vms',
        '--long',
    ]
    detailed_list_vms_out = execute_command(detailed_list_vms_command, catch_error=True)
    detailed_list_vms = {}
    processed_group_vm = ''
    for output_line in detailed_list_vms_out.splitlines():
        if output_line.startswith('Groups:'):
            # line format is: 'Groups:                      /AosUnits/my-test-vm1'
            if len(output_line.split()) == 2:
                processed_group_vm = output_line.split()[1]
        elif output_line.startswith('UUID:'):
            # line format is: 'UUID:                        49f87eef-838b-43cb-b6eb-604989b15f9f'
            if len(output_line.split()) == 2:
                vm_uuid = output_line.split()[1]
                list_of_uuids = []
                if detailed_list_vms.get(processed_group_vm):
                    list_of_uuids = detailed_list_vms[processed_group_vm]
                if vm_uuid not in list_of_uuids:
                    list_of_uuids.append(vm_uuid)
                    detailed_list_vms[processed_group_vm] = list_of_uuids

    _remove_network(units_network_name)

    if not detailed_list_vms.get(vm_group):
        print_error(f'VM Group: {vm_group} is not presented on system.')
        return

    for vm_uuid in detailed_list_vms[vm_group]:  # noqa: WPS440
        delete_vm_command = [
            'VBoxManage',
            'unregistervm',
            vm_uuid,
            '--delete',
        ]
        execute_command(delete_vm_command, catch_error=False)
    print_message('VMs have been deleted')


def _find_vm_location(vm_uuid) -> Path:
    set_vm_params = [
        'VBoxManage',
        'showvminfo',
        vm_uuid,
        '--machinereadable',
    ]

    response = execute_command(set_vm_params)

    for row in response.splitlines():
        param_from_row = row.split('=')
        if param_from_row[0] == 'CfgFile':
            return Path(param_from_row[1].replace('"', '')).parent
    return Path()


def start_vms(group: str, check_virtualbox: bool = False, headless=False):
    """Start all VMs in the group.

    Args:
        group (str): Name of the group to start
        check_virtualbox (bool): Check VirtualBox status before execution
        headless (bool): Start VM in headless mode if True

    Raises:
        AosProvError: If no VMs to start found.
    """
    if check_virtualbox:
        check_virtual_box()

    message = f'Starting VMs in group [bold]{group}[/bold]'

    if headless:
        message += ' in headless mode'

    print_message(message)
    vms_to_start = []
    vms = execute_command(['VBoxManage', 'list', 'vms'])

    for virtual_machines in vms.splitlines():
        guid = virtual_machines[virtual_machines.find('{') + 1:virtual_machines.find('}')]
        info_out = request_vm_info(guid)

        for row in info_out.splitlines():
            if row.startswith('groups='):
                vm_group = row.replace('"', '').split('=')[1]
                if group == vm_group:
                    vms_to_start.append(guid)
                    break

    if not vms_to_start:
        raise AosProvError(f'No VMs found in group {group} to start!')

    start_type = 'headless' if headless else 'gui'

    for vm_guid in vms_to_start:
        start_command = ['VBoxManage', 'startvm', vm_guid, f'--type={start_type}']
        print_left(f'Starting VM {vm_guid}...')
        try:
            execute_command(start_command, catch_error=True)
        except AosProvError as exc:
            if 'is already locked by a session' in str(exc):
                print_message('[YELLOW]SKIPPING due to lock')
            else:
                print_message('[RED]ERROR')
                print_error(str(exc))
        print_done()


def request_vm_info(vm_guid):
    return execute_command(['VBoxManage', 'showvminfo', vm_guid, '--machinereadable'])


def execute_command(command, catch_error=False) -> str:
    execution_status = subprocess.run(command, shell=False, env=os.environ.copy(), capture_output=True, check=False)
    if execution_status.returncode == 0:
        return execution_status.stdout.decode('utf-8')

    if not catch_error:
        raise AosProvError(execution_status.stderr.decode('utf-8'))

    return ''

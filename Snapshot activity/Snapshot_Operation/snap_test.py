from pyVmomi import vim
from pyVim.connect import SmartConnect
import ssl
from pyVim.connect import Disconnect
import getpass

def take_snap():

    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_NONE
    # vCenter Server credentials
    vcenter_host = input("Provide the vCenter FQDN/IP : ")
    vcenter_user = input("Provide the username which has enough previlege for managing VM snapshot : ")
    vcenter_password = getpass.getpass("Provide the credential : ")

    # Connect to vCenter Server
    si = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password, sslContext=context)

    # Get the ServiceInstance's content property
    content = si.RetrieveContent()

    def find_vm_by_name(vm_name):
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        for vm in container.view:
            if vm.name == vm_name:
                return vm
        return None

    def create_vm_snapshot(vm, snapshot_name, snapshot_description=""):
        if not isinstance(vm, vim.VirtualMachine):
            print("Error: 'vm' is not a valid VirtualMachine object.")
            return None

        snapshot_task = vm.CreateSnapshot_Task(name=snapshot_name, description=snapshot_description,
                                            memory=True, quiesce=False)
        return snapshot_task

    # Specify the name of the virtual machine
    vm_name = input("Provide the VM name : ")

    # Find the virtual machine by name
    vm = find_vm_by_name(vm_name)
    if vm is None:
        print(f"Virtual Machine '{vm_name}' not found.")
        Disconnect(si)
        exit(1)

    # Specify the snapshot name and description
    snapshot_name = 'Snapshot_Name'
    snapshot_description = 'Snapshot_Description (Optional)'

    # Create the snapshot
    snapshot_task = create_vm_snapshot(vm, snapshot_name, snapshot_description)
    if snapshot_task is not None:
        print(f"Creating snapshot '{snapshot_name}' for VM '{vm.name}'...")
    else:
        print("Failed to create the snapshot.")

    # Disconnect from vCenter Server
    Disconnect(si)
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import ssl
import getpass
from urllib.parse import unquote

def list_snapshots(vm):
    if not isinstance(vm, vim.VirtualMachine):
        print("Error: 'vm' is not a valid VirtualMachine object.")
        return

    snapshot_tree = vm.snapshot.rootSnapshotList
    print(f"Available snapshots for VM '{vm.name}':")
    list_snapshots_recursive(snapshot_tree)

def list_snapshots_recursive(snapshots):
    for snapshot in snapshots:
        decoded_snapshot_name = unquote(snapshot.name)  # Decode the snapshot name
        print(f" - {decoded_snapshot_name}")
        print(f"   Timestamp: {snapshot.createTime}")
        print(f"   Description: {snapshot.description}")
        if snapshot.childSnapshotList:
            list_snapshots_recursive(snapshot.childSnapshotList)

def delete_all_snapshots(vm):
    if not isinstance(vm, vim.VirtualMachine):
        print("Error: 'vm' is not a valid VirtualMachine object.")
        return False

    # Check if the VM has any snapshots
    if not vm.snapshot:
        print(f"Virtual Machine '{vm.name}' has no snapshots.")
        return False

    # Remove all snapshots in the VM using the "Delete All" option
    task = vm.RemoveAllSnapshots_Task()
    task_result = task.info.state
    print(f"All snapshots in VM '{vm.name}' deletion result: {task_result}")

    return True


def delete_all_snap():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_NONE

    # vCenter Server credentials
        

    def get_valid_input(prompt, is_password=False):
        while True:
            if is_password:
                user_input = getpass.getpass(prompt)
            else:
                user_input = input(prompt).strip()

            if user_input:
                return user_input
            else:
                print("Invalid input. Please provide a valid value.")
    
    while True:
        vcenter_host = None
        vcenter_user = None
        vcenter_password = None
        
        vcenter_host = get_valid_input("Provide the vCenter FQDN/IP: ")
        vcenter_user = get_valid_input("Provide the username: ")
        vcenter_password = get_valid_input("Provide the credential: ", is_password=True)
  
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.verify_mode = ssl.CERT_NONE
            context.set_ciphers("DEFAULT@SECLEVEL=1")
            
            si = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password, sslContext=context)
            
            
            print("Connected to vCenter Server successfully!")
            # You can perform further actions using 'si' here
            break  # Break out of the loop since connection succeeded

        except Exception as e:
            print("Connection to vCenter Server failed. Please check your credentials or vCenter system availability and try again.")
            retry = input("Do you want to retry? (yes/no): ")
            if retry.lower() != "yes":
                print("Exiting...")
                exit()  # Exit the script if user doesn't want to retry

    # Get the ServiceInstance's content property
    content = si.RetrieveContent()

    def find_vm_by_name(vm_name):
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        for vm in container.view:
            if vm.name == vm_name:
                return vm
        return None

    vm_name = input("Provide the VM name : ")

    # Find the virtual machine by name
    vm = find_vm_by_name(vm_name)
    if vm is None:
        print(f"Virtual Machine '{vm_name}' not found.")
        Disconnect(si)
        exit(1)

    # List all available snapshots for the VM
    list_snapshots(vm)

    # Delete all snapshots
    delete_all_snapshots(vm)

    # Disconnect from vCenter Server
    Disconnect(si)

"""For now commenting the below lines to use this code in VM_Snapshot_Tool.py part of packaging it"""

# if __name__ == "__main__":
#     delete_all_snap()

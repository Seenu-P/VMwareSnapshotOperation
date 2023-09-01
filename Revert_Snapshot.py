from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import ssl
import getpass
from urllib.parse import unquote
from urllib.parse import unquote, quote


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

def find_snapshot_by_name(snapshot, snapshot_name_lower):
    if unquote(snapshot.name.lower()) == snapshot_name_lower:
        return snapshot

    for child in snapshot.childSnapshotList:
        child_snapshot_name_encoded = unquote(child.name.lower())
        if child_snapshot_name_encoded == snapshot_name_lower:
            return child

        found_snapshot = find_snapshot_by_name(child, snapshot_name_lower)
        if found_snapshot:
            return found_snapshot

    return None

def revert_vm_snapshot(vm, snapshot_name):
    if not isinstance(vm, vim.VirtualMachine):
        print("Error: 'vm' is not a valid VirtualMachine object.")
        return False

    # Convert the snapshot name to lowercase for case-insensitive comparison
    snapshot_name_lower = unquote(snapshot_name.lower())

    snapshot_to_revert = None
    for snapshot in vm.snapshot.rootSnapshotList:
        found_snapshot = find_snapshot_by_name(snapshot, snapshot_name_lower)
        if found_snapshot:
            snapshot_to_revert = found_snapshot.snapshot
            break

    if not snapshot_to_revert:
        print(f"Snapshot '{snapshot_name}' not found for VM '{vm.name}'.")
        return False

    task = snapshot_to_revert.RevertToSnapshot_Task()
    task_result = task.info.state
    print(f"Reverting to snapshot '{snapshot_name}' result: {task_result}")
    return True

def revert_snap():
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

    vm_name = input("Provide the VM name to revert it's snapshot : ")

    # Find the virtual machine by name
    vm = find_vm_by_name(vm_name)
    if vm is None:
        print(f"Virtual Machine '{vm_name}' not found.")
        Disconnect(si)
        exit(1)

    # List all available snapshots for the VM
    list_snapshots(vm)

    # Prompt user to provide the snapshot name to revert
    snapshot_name = input("Provide the snapshot name to revert : ")

    # Revert the snapshot
    if revert_vm_snapshot(vm, snapshot_name):
        print(f"Reverted to snapshot '{snapshot_name}' for VM '{vm.name}'.")

    # Disconnect from vCenter Server
    Disconnect(si)


"""For now commenting the below lines to use this code in VM_Snapshot_Tool.py part of packaging it"""
# if __name__ == "__main__":
#     revert_snap()

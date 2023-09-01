from pyVmomi import vim
from pyVim.connect import SmartConnect
import ssl
from pyVim.connect import Disconnect
import getpass
import datetime

def take_snap():

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

    def create_vm_snapshot(vm, snapshot_name, snapshot_description=""):
        if not isinstance(vm, vim.VirtualMachine):
            print("Error: 'vm' is not a valid VirtualMachine object.")
            return None
        vm_memory = input("Do you want take snap with memory ? yes/no : ")
        if vm_memory.lower() == "yes":
            mem = True
        else:
            mem = False
        snapshot_task = vm.CreateSnapshot_Task(name=snapshot_name, description=snapshot_description,
                                            memory=mem, quiesce=False)
        return snapshot_task

    # Specify the name of the virtual machine
    vm_name = input("Provide the VM name to take Snapshot : ")
    

    # Find the virtual machine by name
    vm = find_vm_by_name(vm_name)
    if vm is None:
        print(f"Virtual Machine '{vm_name}' not found.")
        Disconnect(si)
        exit(1)

    current_datetime = datetime.datetime.now()
    formatted_date_time = current_datetime.strftime("%Y-%m-%d, %H:%M:%S")  # Customize the format as needed
    # Specify the snapshot name and description
    snapshot_name = 'Created via Python Tool_' + formatted_date_time
    snapshot_description = 'VMware best practice "Try to clean snaps within 3 days after system validation"'

    # Create the snapshot
    snapshot_task = create_vm_snapshot(vm, snapshot_name, snapshot_description)
    if snapshot_task is not None:
        print(f"Creating snapshot '{snapshot_name}' for VM '{vm.name}'...Check the same after couple of minutes")
    else:
        print("Failed to create the snapshot.")

    # Disconnect from vCenter Server
    Disconnect(si)
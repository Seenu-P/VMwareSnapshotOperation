from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import ssl
import csv
import getpass
import datetime
import os

def get_vm_snapshot_report(si):
      

    # Get the ServiceInstance's content property
    content = si.RetrieveContent()

    # Create a container view to get all VMs in the vCenter
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)

    # Get a list of all VMs
    vm_list = container.view

    
    # Create a list to store the snapshot reports
    snapshot_reports = []

    # Loop through each VM and collect snapshot information
    for vm in vm_list:
        try:
            snapshot_reports.extend(collect_vm_snapshot_info(vm))
        except vim.fault.NotAuthenticated as e:
            print(f"Failed to collect snapshot information for VM '{vm.name}': {str(e)}")

    return snapshot_reports

def collect_vm_snapshot_info(vm):
    snapshot_info = []
    if vm.snapshot:
        snapshot_tree = vm.snapshot.rootSnapshotList
        collect_snapshot_info_recursive(snapshot_tree, snapshot_info)
    return snapshot_info

def collect_snapshot_info_recursive(snapshots, snapshot_info):
    for snapshot in snapshots:
        
        snapshot_info.append({
            'VM Name': snapshot.vm.name,
            'Snapshot Name': snapshot.name,
            'Timestamp': snapshot.createTime,
            'Description': snapshot.description,
        })

        if snapshot.childSnapshotList:
            collect_snapshot_info_recursive(snapshot.childSnapshotList, snapshot_info)
# Disconnect from vCenter Server
#Disconnect(si)

def snap_report():
        # vCenter Server credentials
       
    # Connect to vCenter Server
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
    
    
    

    # Get snapshot reports from all VMs
    snapshot_reports = get_vm_snapshot_report(si)
    
    current_datetime = datetime.datetime.now()
    formatted_date_time = current_datetime.strftime("%Y_%m_%d_T_%H_%M_%S")  # Customize the format as needed
    # Specify the Report name
    report_name = '/Snapshot_Report_D_' + formatted_date_time

    current_directory = os.getcwd()

    # Save the snapshot reports to a CSV file
    csv_file = os.path.join(current_directory + report_name + '.csv')
    
    

    try:
        with open(csv_file, mode='w', newline='') as file:
            fieldnames = ['VM Name', 'Snapshot Name', 'Timestamp', 'Description']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(snapshot_reports)

        print(f"Snapshot reports saved to '{csv_file}'.")
    except FileNotFoundError:
        print("Report file not found.")


"""For now commenting the below lines to use this code in VM_Snapshot_Tool.py part of packaging it"""
# if __name__ == "__main__":
#     snap_report()

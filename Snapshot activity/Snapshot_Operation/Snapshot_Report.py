from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import ssl
import csv
import getpass

def get_vm_snapshot_report(vcenter_host, vcenter_user, vcenter_password):
    # Disable SSL certificate verification (only use this in a test environment)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_NONE

    # Connect to vCenter Server
    si = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password, sslContext=context)

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
    vcenter_host = input("Provide the vCenter FQDN/IP: ")
    vcenter_user = input("Provide the username: ")
    vcenter_password = getpass.getpass("Provide the credential : ")

    # Get snapshot reports from all VMs
    snapshot_reports = get_vm_snapshot_report(vcenter_host, vcenter_user, vcenter_password)
    
    

    # Save the snapshot reports to a CSV file
    csv_file = 'C:\\Users\\Seenu_Perumal\\Python Learning\\snapshot_reports.csv'
    with open(csv_file, mode='w', newline='') as file:
        fieldnames = ['VM Name', 'Snapshot Name', 'Timestamp', 'Description']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(snapshot_reports)

    print(f"Snapshot reports saved to '{csv_file}'.")

"""For now commenting the below lines to use this code in VM_Snapshot_Tool.py part of packaging it"""
# if __name__ == "__main__":
#     snap_report()

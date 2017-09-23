
import ConfigParser
import VmCreator
import yaml
import time
import os
import sys


Config = ConfigParser.SafeConfigParser()


def main():

    """
    This is the main function of the code.
    It parses the configuration file and also contains the calls to the following functions:
    - setupAndStartVMs()
    - startAllVMs()
    - poweroffAllVMs()
    - deleteAllVMs()
    """

    global homeFolder, genericVM, hostUser, osVersion, osVersion, vmStartIP, vmUser, client, domain, ipaddress
    global vmsList, hosts, vms, vmsOnServerList
    global serverUserid, serverPass, vmUserid, vmPass

    # Replace with personal credentials the following variables: serverUserid, serverPass, vmUserid, vmPass
    serverUserid=''
    serverPass=''
    vmUserid=''
    vmPass=''

    # Verify existence of configuration file
    if not os.path.isfile("config.yaml"):
        print "The Config file specified does not exist "
        sys.exit(-1)

    # Open configuration file
    with open('config.yaml', 'r') as f:
        my_config = yaml.load(f)

    # Create the objects to manipulate the configuration file
    defaultsVM = my_config["virtual_machines_defaults"]
    vms = my_config["virtual_machines"]

    # Obtain the default values for the virtual machine
    homeFolder = defaultsVM['HOME_FOLDER']
    genericVM = defaultsVM['GENERIC_VM']
    hostUser = defaultsVM['HOSTUSER']
    osVersion = defaultsVM['OS_VERSION']
    vmStartIP = defaultsVM['VM_START_IP']
    vmUser = defaultsVM['VM_USER']
    domain = defaultsVM['DOMAIN']

    # Create the list of servers (used only for startAllVMs, poweroffAllVMs and deleteAllVMs functions)
    serversList = []
    for a_vm_name in vms:
        a_vm = vms[a_vm_name]
        serversList.append(a_vm["server"])
    server_list = list(set(serversList))

    # Create the list of virtual machines grouped on server (used only for startAllVMs, poweroffAllVMs and
    # deleteAllVMs functions)
    vmsOnServerList = []
    for a_server in server_list:
        data = [vms[a_vm_name] for a_vm_name in vms if vms[a_vm_name]["server"] == a_server]
        vmsOnServerList.append(data)

    # Create a list with the virtual machines to be created
    vmsList = []
    for a_vm in vms:
        data = vms[a_vm]
        vmsList.append(data)

    # Call the method to import and update all virtual machines
    # setupAndStartVMs()

    # Call the method to start all created virtual machines
    # startAllVMs()

    # Call method to poweroff all created virtual machines
    # poweroffAllVMs()

    # Call method to delete all created virtual machines
    deleteAllVMs()


def setupAndStartVMs():

    """
    This function imports all the virtual machines specified in the configuration file.
    After creation, the virtual machines are updated
    """

    # Create hosts file
    createHostsFile(vmsList)

    # For each virtual machine in the list, create and execute commands of import, update and start
    for a_vm in vmsList:
        vmName = a_vm['name']
        myServer = a_vm['server']
        memory = a_vm['ram']
        cores = a_vm['core']
        diskName = homeFolder + vmName + "/" + vmName + "-disk1.vmdk"
        ipaddress = a_vm['ip_address']

        # Connect to server on which the virtual machine will be imported and updated
        creator = VmCreator.Deployer(myServer, serverUserid, serverPass)

        # Define the import and update commands
        commandImport = "VBoxManage import " + homeFolder + genericVM + " --vsys 0 " + " --vmname " + vmName + \
                        " --vsys 0 " + " --cpus " + str(cores) + " --vsys 0 " + " --memory " + str(memory) + \
                        " --vsys 0 " + " --unit 11 " + " --disk " + diskName
        commandUpdateMacAdd = "VBoxManage modifyvm " + vmName + " --macaddress1 auto"
        commandUpdateAudio = "VBoxManage modifyvm " + vmName + " --audio none"
        commandStart = "VBoxManage startvm " + vmName + " --type headless"

        # Create a list with the commands to be executed
        commandList = [commandImport, commandUpdateMacAdd, commandUpdateAudio, commandStart]

        # Execute the list of commands
        for command in commandList:
            creator.run_command(command)

        # Verify virtual machine is started and running
        flag = 0
        counter = 0
        while flag == 0 and counter < 12:
            try:
                creator = VmCreator.Deployer(vmStartIP, vmUserid, vmPass)
                flag = 1
            except:
                counter += 1
                time.sleep(5)
        if counter == 12:
            print "Unable to connect to virtual machine"
            exit(-1)

        # Modify hostname for the created and started virtual machine
        command = "sudo nmcli g hostname " + vmName + "." + domain
        creator.run_command(command)

        # Modify ipaddress for the created and started virtual machine
        command = "sudo nmcli con mod enp0s3 ipv4.addresses " + ipaddress + "/24"
        creator.run_command(command)

        # Copy hosts file in home folder for the current virtual machine
        creator.copy_file("/tmp/hosts", "/tmp/hosts")

        # Move hosts file in /etc/hosts for the current virtual machine
        creator = VmCreator.Deployer(vmStartIP, vmUserid, vmPass)
        command = "sudo cp -f /tmp/hosts /etc/hosts"
        creator.run_command(command)

        # Shutdown the current virtual machine
        command = "sudo shutdown -r now"
        creator.run_command(command)

        # Verify virtual machine has rebooted under the changed IP
        flag = 0
        counter = 0
        while flag == 0 and counter < 12:
            try:
                VmCreator.Deployer(ipaddress, vmUserid, vmPass)
                flag = 1
            except:
                counter += 1
                time.sleep(5)
        if counter == 12:
            print "Unable to connect to virtual machine"
            exit(-1)

        print "Virtual machine %s has successfully been created" % vmName


def createHostsFile(vmsList):

    """
    This function creates the hosts file based on the content of the configuration file.
    @param vmsList: the list of all virtual machines specified in the configuration file
    """

    f = open('/tmp/hosts', 'w')
    f.write("127.0.0.1\t\tlocalhost.localdomain\tlocalhost localhost4 localhost4.localdomain4\n")
    f.write("::1\t\tlocalhost.localdomain\tlocalhost localhost6 localhost6.localdomain6\n")
    for aVM in vmsList:
        print aVM
        f.write(aVM['ip_address'] + "\t" + aVM['name']+"." + domain + "\t" + aVM['name'] + "\n")


def startAllVMs():

    """
    This function starts all virtual machines specified in the configuration file
    """

    for vms_on_a_server in vmsOnServerList:
        for a_vm in vms_on_a_server:
            creator = VmCreator.Deployer(a_vm['server'], serverUserid, serverPass)
            commandStart = "VBoxManage startvm " + a_vm['name'] + " --type headless"
            # Run command to start a vm
            creator.run_command(commandStart)


def poweroffAllVMs():

    """
    This function powers off all virtual machines specified in the configuration file
    """

    for vms_on_a_server in vmsOnServerList:
        for a_vm in vms_on_a_server:
            creator = VmCreator.Deployer(a_vm['server'], serverUserid, serverPass)
            commandPowerOff = "VBoxManage controlvm " + a_vm['name'] + " poweroff"
            # Run command to poweroff a vm
            creator.run_command(commandPowerOff)


def deleteAllVMs():

    """
    This function deletes all virtual machines specified in the configuration file
    """

    for vms_on_a_server in vmsOnServerList:
        for a_vm in vms_on_a_server:
            creator = VmCreator.Deployer(a_vm['server'], serverUserid, serverPass)
            commandDelete = "VBoxManage unregistervm " + a_vm['name'] + " --delete"
            # Run command to delete a vm
            creator.run_command(commandDelete)


if __name__ == "__main__":
    main()

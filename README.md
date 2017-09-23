# virtual_machines_creator
Create and setup virtual machines on multiple servers using VirtualBox

This project is used to create multiple virtual machines on multiple servers starting from an existing .ova generic
virtual machine.

The configuration file config.yaml contains:
- specification of the .ova generic virtual machine, under virtual_machines_defaults block
- specification of the virtual machines to be created, under virtual_machines block

The project offers the possibility to create, start, poweroff and delete the virtual machines specified in the
configuration file. To do so, select the desired function from main by uncommenting the call of the desired function:
 - setupAndStartVMs()
 - startAllVMs()
 - poweroffAllVMs()
 - deleteAllVMs()

 For connection to the server and the created virtual machines, replace with personal credentials the following
 variables, which are defined in main function: serverUserid, serverPass, vmUserid, vmPass


# mininet-topology
Custom topologies written for mininet emulator
In this repository you can find out different topologies written for mininet network emulator. Each python script refers a network topology in which some hosts or controllers manages some services, such as ospfd,bgpd etc.

## Double Host-Double Router Chain
2 hosts are connected through 2 routers...
![](https://s23.postimg.org/9d1qhn817/Double_Host-_Double_Router_Chain.png)
[Look at source code...](https://github.com/mkucukdemir/mininet-topology/blob/master/Custom%20Topologies/src/hostsMultiRoute.py)

## OSPF Exercise
Three areas, five routers and one switch...
![](https://s21.postimg.org/izh0uj65z/ospf_Exercise_Topology.jpg)

Each router runs quagga/ospfd service to advertise and share routing tables with their neighbor that makes every node reachable. Check [Wiki](https://github.com/mkucukdemir/mininet-topology/wiki)

## BGP Exercise
Two autonomous system, five routers...
![](https://s15.postimg.org/prokyynej/bgp_Exercise_Topology.jpg)
AS 5500 runs iBGP between r1 and r4 while r4-r5 pair share routes through eBGP. Check [Wiki](https://github.com/mkucukdemir/mininet-topology/wiki)

## Inter Autonomous System Routing: CoreNet
To exercise both OSPF, iBGP and eBGP in Mininet the following topology will be implemented.
Topology elements:
* 6 AS Border Routers, running BGP route
* 8 Area Border Routers, runing OSPF (in their areas)
* 8 Switches, will be connected to some hosts
![](https://s13.postimg.org/l9n3y5ion/core_Net.png)

To be able to run routing suite, do not forget to extract configuration files from tar archive: 'Custom Topologies/quaggacfgs/coreNet_confs.tar'

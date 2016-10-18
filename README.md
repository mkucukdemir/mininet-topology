# mininet-topology
Custom topologies written for mininet emulator
In this repository you can find out different topologies written for mininet network emulator. Each python script refers a network topology in which some hosts or controllers manages some services, such as ospfd,bgpd etc.

## OSPF Exercise
Three areas, five routers and one switch...
![](https://s21.postimg.org/izh0uj65z/ospf_Exercise_Topology.jpg)

Each router runs quagga/ospfd service to advertise and share routing tables with their neighbor that makes every node reachable. Check [Wiki](https://github.com/mkucukdemir/mininet-topology/wiki)

## BGP Exercise
Two autonomous system, five routers...
![](https://s15.postimg.org/prokyynej/bgp_Exercise_Topology.jpg)
AS 5500 runs iBGP between r1 and r4 while r4-r5 pair share routes through eBGP. Check [Wiki](https://github.com/mkucukdemir/mininet-topology/wiki)

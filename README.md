# mininet-topology
Custom topologies written for mininet emulator
In this repository you can find out different topologies written for mininet network emulator. Each python script refers a network topology in which some hosts or controllers manages some services, such as ospfd,bgpd etc.

## OSPF Exercise
Three areas, five routers and one switch...
![](https://s17.postimg.org/dy9q4e0kf/ospf_Exercise_Topology.jpg)

Each router runs quagga/ospfd service to advertise and share routing tables with their neighbor that makes every node reachable.

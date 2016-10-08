#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="m.kucukdemir"
__date__ ="$Oct 7, 2016 10:59:00 AM$"

from mininet.topo import Topo
from mininet.node import OVSSwitch
from mininet.node import Controller
from mininet.node import RemoteController
from mininet.node import Host
from mininet.node import OVSKernelSwitch
from mininet.link import TCLink
from mininet.node import OVSSwitch
from mininet.node import Node

c1 = RemoteController( 'c1', ip='127.0.0.1', port=6633 )
c2 = RemoteController( 'c2', ip='127.0.0.1', port=6643 )
c3 = RemoteController( 'c3', ip='127.0.0.1', port=6653 )

csmap = {
            'as1a1s1': c1,
            'as1a1s2': c1,
            'as1a1s3': c1,
            'as2a2s1': c2,
            'as2a2s2': c2,
            'as3a3s1': c3,
            'as3a3s2': c3,
            'as3a3s3': c3
        }
        
customLink = {'bw':1000}
l_eth = {
            'bw': 10,
            'delay': '1ms',
            'loss': 0
        }
l_3g = {
            'bw': 2,
            'delay': '75ms',
            'loss': 2
        }
l_wifi = {
            'bw': 2,
            'delay': '5ms',
            'loss': 3
        }
        
class SmallFeRouter( Node ):

    def config( self, **params ):
        super( SmallFeRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( SoftRouter, self ).terminate()
        
    def startBGP(self):
        self.cmd("/usr/lib/quagga/zebra -f conf/zebra-%s.conf -d -i /tmp/zebra-%s.pid > logs/%s-zebra-stdout 2>&1" % (self.name, self.name, self.name))
        self.waitOutput()
        self.cmd("/usr/lib/quagga/bgpd -f conf/bgpd-%s.conf -d -i /tmp/bgp-%s.pid > logs/%s-bgpd-stdout 2>&1" % (self.name, self.name, self.name), shell=True)
        self.waitOutput()
        
    def startOSPF(self):
        self.cmd("/usr/lib/quagga/zebra -f conf/zebra-%s.conf -d -i /tmp/zebra-%s.pid > logs/%s-zebra-stdout 2>&1" % (self.name, self.name, self.name))
        self.waitOutput()
        self.cmd("/usr/lib/quagga/ospfd -f conf/ospfd-%s.conf -d -i /tmp/ospf-%s.pid > logs/%s-ospfd-stdout 2>&1" % (self.name, self.name, self.name), shell=True)
        self.waitOutput()

class SmallFeNet( Topo ):
    def __init__(self,**kwargs):
        Topo.__init__(self,**kwargs)
        # ASBRS
        asbr1 = self.addNode( 'asbr1',cls=SmallFeRouter )
        asbr2 = self.addNode( 'asbr2',cls=SmallFeRouter )
        asbr3 = self.addNode( 'asbr3',cls=SmallFeRouter )
        
        # AS1 ABRS
        as1abr1 = self.addNode( 'as1abr1',cls=SmallFeRouter )
        as1abr2 = self.addNode( 'as1abr2',cls=SmallFeRouter )
        as1abr3 = self.addNode( 'as1abr3',cls=SmallFeRouter )
        # AS1 AREA1 ROUTERS
        as1a1r1 = self.addNode( 'as1a1r1',cls=SmallFeRouter )
        # AS1 AREA1 SWITCHES
        as1a1s1 = self.addSwitch('as1a1s1',cls=OVSSwitch)
        as1a1s2 = self.addSwitch('as1a1s2',cls=OVSSwitch)
        as1a1s3 = self.addSwitch('as1a1s3',cls=OVSSwitch)
        # AS1 AREA1 HOSTS
        as1a1h1 = self.addHost('as1a1h1',cls=Host,mac='00:00:11:11:11:11',ip='10.1.1.20/24',defaultRoute='via 10.1.1.1')
        as1a1h2 = self.addHost('as1a1h2',cls=Host,mac='00:00:11:11:22:11',ip='10.1.2.20/24',defaultRoute='via 10.1.2.1')
        as1a1h3 = self.addHost('as1a1h3',cls=Host,mac='00:00:11:11:22:22',ip='10.1.2.21/24',defaultRoute='via 10.1.2.1')
        as1a1h4 = self.addHost('as1a1h4',cls=Host,mac='00:00:11:11:33:11',ip='10.1.3.20/24',defaultRoute='via 10.1.3.1')
        as1a1h5 = self.addHost('as1a1h5',cls=Host,mac='00:00:11:11:33:22',ip='10.1.3.21/24',defaultRoute='via 10.1.3.1')
        # AS1 LINKS HOST-SWITCH
        self.addLink(as1a1h1, as1a1s1, cls=TCLink,**customLink)
        self.addLink(as1a1h2, as1a1s2, cls=TCLink,**customLink)
        self.addLink(as1a1h3, as1a1s2, cls=TCLink,**customLink)
        self.addLink(as1a1h4, as1a1s3, cls=TCLink,**customLink)
        self.addLink(as1a1h5, as1a1s3, cls=TCLink,**customLink)
        # AS1 LINKS SWITCH-ROUTER
        self.addLink(as1a1s1, as1a1r1, intfName2='as1a1r1-eth1', params2={'ip':'10.1.1.20/24'})
        self.addLink(as1a1s2, as1a1r1, intfName2='as1a1r1-eth2', params2={'ip':'10.1.1.21/24'})
        self.addLink(as1a1s3, as1a1r1, intfName2='as1a1r1-eth3', params2={'ip':'10.1.1.22/24'})
        # AS1 LINKS ROUTER-ABR
        self.addLink(as1abr1, as1a1r1, intfName1='as1abr1-eth1', params1={'ip':'10.1.1.2x/24'}, intfName2='as1a1r1-eth4', params2={'ip':'10.1.1.23/24'})
        self.addLink(as1abr2, as1a1r1, intfName1='as1abr2-eth1', params1={'ip':'10.1.1.2x/24'}, intfName2='as1a1r1-eth5', params2={'ip':'10.1.1.24/24'})
        # AS1 LINKS ABR-ABR
        self.addLink(as1abr1, as1abr3, cls=TCLink,**customLink)
        self.addLink(as1abr2, as1abr3, cls=TCLink,**customLink)
        
        # AS2 ABRS
        as2abr1 = self.addNode( 'as2abr1',cls=SmallFeRouter )
        as2abr2 = self.addNode( 'as2abr2',cls=SmallFeRouter )
        as2abr3 = self.addNode( 'as2abr3',cls=SmallFeRouter )
        # AS2 AREA2 ROUTERS
        as2a2r1 = self.addNode( 'as2a2r1',cls=SmallFeRouter )
        # AS2 AREA2 SWITCHES
        as2a2s1 = self.addSwitch('as2a2s1',cls=OVSSwitch)
        as2a2s2 = self.addSwitch('as2a2s2',cls=OVSSwitch)
        # AS2 AREA2 HOSTS
        as2a2h1 = self.addHost('as2a2h1',cls=Host,mac='00:00:22:22:11:11',ip='20.2.1.20/24',defaultRoute='via 20.2.1.1')
        as2a2h2 = self.addHost('as2a2h2',cls=Host,mac='00:00:22:22:11:22',ip='20.2.1.21/24',defaultRoute='via 20.2.1.1')
        as2a2h3 = self.addHost('as2a2h3',cls=Host,mac='00:00:22:22:22:11',ip='20.2.2.20/24',defaultRoute='via 20.2.2.1')
        # AS2 LINKS HOST-SWITCH
        self.addLink(as2a2h1, as2a2s1, cls=TCLink,**customLink)
        self.addLink(as2a2h2, as2a2s1, cls=TCLink,**customLink)
        self.addLink(as2a2h3, as2a2s2, cls=TCLink,**customLink)
        # AS2 LINKS SWITCH-ROUTER
        self.addLink(as2a2s1, as2a2r1, cls=TCLink,**customLink)
        self.addLink(as2a2s2, as2a2r1, cls=TCLink,**customLink)
        # AS2 LINKS ROUTER-ABR
        self.addLink(as2abr2, as2a2r1, cls=TCLink,**customLink)
        self.addLink(as2abr3, as2a2r1, cls=TCLink,**customLink)
        # AS2 LINKS ABR-ABR
        self.addLink(as2abr1, as2abr2, cls=TCLink,**customLink)
        self.addLink(as2abr1, as2abr3, cls=TCLink,**customLink)
        
        # AS3 ABRS
        as3abr1 = self.addNode( 'as3abr1',cls=SmallFeRouter )
        as3abr2 = self.addNode( 'as3abr2',cls=SmallFeRouter )
        as3abr3 = self.addNode( 'as3abr3',cls=SmallFeRouter )
        # AS3 AREA2 ROUTERS
        as3a3r1 = self.addNode( 'as3a3r1',cls=SmallFeRouter )
        # AS3 AREA3 SWITCHES
        as3a3s1 = self.addSwitch('as3a3s1',cls=OVSSwitch)
        as3a3s2 = self.addSwitch('as3a3s2',cls=OVSSwitch)
        as3a3s3 = self.addSwitch('as3a3s3',cls=OVSSwitch)
        # AS3 AREA3 HOSTS
        as3a3h1 = self.addHost('as3a3h1',cls=Host,mac='00:00:33:33:11:11',ip='30.3.1.20/24',defaultRoute='via 30.1.1.1')
        as3a3h2 = self.addHost('as3a3h2',cls=Host,mac='00:00:33:33:22:11',ip='30.3.2.20/24',defaultRoute='via 30.1.2.1')
        as3a3h3 = self.addHost('as3a3h3',cls=Host,mac='00:00:33:33:33:11',ip='30.3.3.20/24',defaultRoute='via 30.3.3.1')
        as3a3h4 = self.addHost('as3a3h4',cls=Host,mac='00:00:33:33:33:22',ip='30.3.3.21/24',defaultRoute='via 30.3.3.1')
        # AS3 LINKS HOST-SWITCH
        self.addLink(as3a3h1, as3a3s1, cls=TCLink,**customLink)
        self.addLink(as3a3h2, as3a3s2, cls=TCLink,**customLink)
        self.addLink(as3a3h3, as3a3s3, cls=TCLink,**customLink)
        self.addLink(as3a3h4, as3a3s3, cls=TCLink,**customLink)
        # AS3 LINKS SWITCH-ROUTER
        self.addLink(as3a3s1, as3a3r1, cls=TCLink,**customLink)
        self.addLink(as3a3s2, as3a3r1, cls=TCLink,**customLink)
        self.addLink(as3a3s3, as3a3r1, cls=TCLink,**customLink)
        # AS3 LINKS ROUTER-ABR
        self.addLink(as3abr1, as3a3r1, cls=TCLink,**customLink)
        self.addLink(as3abr3, as3a3r1, cls=TCLink,**customLink)
        # AS3 LINKS ABR-ABR
        self.addLink(as3abr1, as3abr2, cls=TCLink,**customLink)
        self.addLink(as3abr2, as3abr3, cls=TCLink,**customLink)
        
        # LINKS ABR-ASBR1
        self.addLink(as1abr1, asbr1, cls=TCLink,**customLink)
        self.addLink(as1abr3, asbr1, cls=TCLink,**customLink)
        self.addLink(as3abr1, asbr1, cls=TCLink,**customLink)
        self.addLink(as3abr2, asbr1, cls=TCLink,**customLink)
        # LINKS ABR-ASBR2
        self.addLink(as1abr2, asbr2, cls=TCLink,**customLink)
        self.addLink(as1abr3, asbr2, cls=TCLink,**customLink)
        self.addLink(as2abr1, asbr2, cls=TCLink,**customLink)
        self.addLink(as2abr2, asbr2, cls=TCLink,**customLink)
        # LINKS ABR-ASBR3
        self.addLink(as2abr1, asbr3, cls=TCLink,**customLink)
        self.addLink(as2abr3, asbr3, cls=TCLink,**customLink)
        self.addLink(as3abr2, asbr3, cls=TCLink,**customLink)
        self.addLink(as3abr3, asbr3, cls=TCLink,**customLink)

def main():

    topo = SmallFeNet(n=args.n)

    net = Mininet(topo=topo)

    net.start()
    
    asBorderRouter1 = net.getNodeByName('asbr1')
    asBorderRouter1.startBGP()
    asBorderRouter2 = net.getNodeByName('asbr2')
    asBorderRouter2.startBGP()
    asBorderRouter3 = net.getNodeByName('asbr3')
    asBorderRouter3.startBGP()
    
    as1_areaBorderRouter1 = net.getNodeByName('as1abr1')
    as1_areaBorderRouter1.startOSPF()
    as1_areaBorderRouter2 = net.getNodeByName('as1abr2')
    as1_areaBorderRouter2.startOSPF()
    as1_areaBorderRouter3 = net.getNodeByName('as1abr3')
    as1_areaBorderRouter3.startOSPF()
    
    as1_area1_router1 = net.getNodeByName('as1a1r1')
    as2_area2_router1 = net.getNodeByName('as2a2r1')
    as3_area3_router1 = net.getNodeByName('as3a3r1')
    
    CLI(net)
    net.stop()

if __name__ == "__main__":
    print "SmallFeNet Simulation"
    main()

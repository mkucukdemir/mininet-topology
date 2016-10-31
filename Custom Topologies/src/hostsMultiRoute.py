#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="m.kucukdemir"
__date__ ="$Oct 31, 2016 05:06:34 PM$"

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.node import OVSSwitch
from mininet.node import Controller
from mininet.node import RemoteController
from mininet.node import Host
from mininet.node import OVSKernelSwitch
from mininet.link import TCLink
from mininet.node import OVSSwitch
from mininet.node import Node
from mininet.log import setLogLevel, info

class CustomNode( Node ):

    def config( self, **params ):
        super( CustomNode, self).config( **params )
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( CustomNode, self ).terminate()
        
class CustomNet( Topo ):
    def build( self, **opts ):
        # Hosts
        h1 = self.addHost('h1',cls=Host,ip='192.1.1.20/24',defaultRoute=None)
        h2 = self.addHost('h2',cls=Host,ip='192.1.2.20/24',defaultRoute=None)

        #Routers
        r1 = self.addNode( 'r1', cls=CustomNode, ip="192.1.1.1/24")
        r2 = self.addNode( 'r2', cls=CustomNode, ip="192.2.1.1/24")

        # Links
        self.addLink(h1,r1,intfName1='h1-eth0',params1={'ip':'192.1.1.20/24'},intfName2='r1-eth0',params2={'ip':'192.1.1.1/24'})
        self.addLink(h2,r1,intfName1='h2-eth0',params1={'ip':'192.1.2.20/24'},intfName2='r1-eth1',params2={'ip':'192.1.2.1/24'})
        self.addLink(h1,r2,intfName1='h1-eth1',params1={'ip':'192.2.1.20/24'},intfName2='r2-eth0',params2={'ip':'192.2.1.1/24'})
        self.addLink(h2,r2,intfName1='h2-eth1',params1={'ip':'192.2.2.20/24'},intfName2='r2-eth1',params2={'ip':'192.2.2.1/24'})

def run():

    net = Mininet( topo=CustomNet(),controller=None )

    net[ 'h1' ].cmd('route add -net 192.1.2.0 netmask 255.255.255.0 gw 192.1.1.1')
    net[ 'h1' ].cmd('route add -net 192.2.2.0 netmask 255.255.255.0 gw 192.2.1.1')
    net[ 'h2' ].cmd('route add -net 192.1.1.0 netmask 255.255.255.0 gw 192.1.2.1')
    net[ 'h2' ].cmd('route add -net 192.2.1.0 netmask 255.255.255.0 gw 192.2.2.1')
    net[ 'r1' ].cmd('ip route add 192.2.1.0/24 dev r1-eth0')
    net[ 'r1' ].cmd('ip route add 192.2.2.0/24 dev r1-eth1')
    net[ 'r2' ].cmd('ip route add 192.1.1.0/24 dev r2-eth0')
    net[ 'r2' ].cmd('ip route add 192.1.2.0/24 dev r2-eth1')
    
    net.start()
    CLI(net)
    net.stop()

if __name__ == "__main__":
    setLogLevel( 'info' )
    run()

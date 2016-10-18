#!/usr/bin/python


__author__="m.kucukdemir"
__date__ ="$Oct 15, 2016 10:34:06$"

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from time import sleep


class SoftRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( SoftRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( SoftRouter, self ).terminate()

    def runOSPF( self ):
        print "*** OSPF starting ", self.name
        self.cmd("/usr/lib/quagga/zebra -f conf/zebra-%s.conf -d -i /tmp/zebra-%s.pid > logs/%s-zebra-stdout 2>&1" % (self.name, self.name, self.name))
        self.waitOutput()
        self.cmd("/usr/lib/quagga/ospfd -f conf/ospfd-%s.conf -d -i /tmp/ospfd-%s.pid > logs/%s-ospfd-stdout 2>&1" % (self.name, self.name, self.name))
        self.waitOutput()

    def runBGP( self ):
        print "*** BGP starting ", self.name
        self.cmd("/usr/lib/quagga/zebra -f conf/zebra-%s.conf -d -i /tmp/zebra-%s.pid > logs/%s-zebra-stdout 2>&1" % (self.name, self.name, self.name))
        self.waitOutput()
        self.cmd("/usr/lib/quagga/bgpd -f conf/bgpd-%s.conf -d -i /tmp/bgpd-%s.pid > logs/%s-bgpd-stdout 2>&1" % (self.name, self.name, self.name))
        self.waitOutput()

    def stopQuagga( self ):
        print "*** Zebra, OSPF & BGP services are being terminated ", self.name
        self.cmd("pkill zebra")
        self.waitOutput()
        self.cmd("pkill bgpd")
        self.waitOutput()
        self.cmd("pkill ospfd")
        self.waitOutput()


class NetworkTopo( Topo ):

    def build( self, **_opts ):

        # IP address for rx-eth1
        r1 = self.addNode( 'r1', cls=SoftRouter, ip='10.1.12.1/24' )
        r2 = self.addNode( 'r2', cls=SoftRouter, ip='10.1.12.2/24' )
        r3 = self.addNode( 'r3', cls=SoftRouter, ip='10.1.13.2/24' )
        r4 = self.addNode( 'r4', cls=SoftRouter, ip='10.1.24.2/24' )
        r5 = self.addNode( 'r5', cls=SoftRouter, ip='10.1.45.2/24' )

        self.addLink( r1, r2,
                      intfName1='r1-eth1',
                      params1={'ip':'10.1.12.1/24'},
                      intfName2='r2-eth1',
                      params2={'ip':'10.1.12.2/24'})
        self.addLink( r1, r3,
                      intfName1='r1-eth2',
                      params1={'ip':'10.1.13.1/24'},
                      intfName2='r3-eth1',
                      params2={'ip':'10.1.13.2/24'})
        self.addLink( r2, r4,
                      intfName1='r2-eth2',
                      params1={'ip':'10.1.24.1/24'},
                      intfName2='r4-eth1',
                      params2={'ip':'10.1.24.2/24'})
        self.addLink( r3, r4,
                      intfName1='r3-eth2',
                      params1={'ip':'10.1.34.1/24'},
                      intfName2='r4-eth2',
                      params2={'ip':'10.1.34.2/24'})
        self.addLink( r4, r5,
                      intfName1='r4-eth3',
                      params1={'ip':'10.1.45.1/24'},
                      intfName2='r5-eth1',
                      params2={'ip':'10.1.45.2/24'})

def run():

    topo = NetworkTopo()
    net = Mininet( topo=topo, controller=None)

    net.start()
    info( '*** Routing Table on Router 1:\n' )
    info( net[ 'r1' ].cmd( 'route' ) )

    net[ 'r1' ].stopQuagga()
    ospfRouters = ['r1','r2','r3','r4']
    for router in ospfRouters:
        net [ router ].runOSPF()
	sleep(2)
    bgpRouters = ['r1','r4','r5']
    for router in bgpRouters:
        net [ router ].runBGP()
	sleep(2)
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()

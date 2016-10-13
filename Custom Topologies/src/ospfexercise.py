#!/usr/bin/python


__author__="m.kucukdemir"
__date__ ="$Oct 13, 2016 17:34:42$"

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
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
        r1 = self.addNode( 'r1', cls=SoftRouter, ip='172.30.0.1/24' )
        r2 = self.addNode( 'r2', cls=SoftRouter, ip='172.30.0.2/24' )
        r3 = self.addNode( 'r3', cls=SoftRouter, ip='172.30.0.3/24' )
        r4 = self.addNode( 'r4', cls=SoftRouter, ip='172.30.20.4/24' )
        r5 = self.addNode( 'r5', cls=SoftRouter, ip='172.30.10.5/24' )

        s1 = self.addSwitch('s1',protocols='OpenFlow13')

        self.addLink( s1, r1, intfName2='r1-eth1',
                      params2={ 'ip' : '172.30.0.1/24' } )
        self.addLink( s1, r2, intfName2='r2-eth1',
                      params2={ 'ip' : '172.30.0.2/24' } )
        self.addLink( s1, r3, intfName2='r3-eth1',
                      params2={ 'ip' : '172.30.0.3/24' } )
        self.addLink( r2, r5,
                      intfName1='r2-eth2',
                      params1={'ip':'172.30.10.2/24'},
                      intfName2='r5-eth1',
                      params2={'ip':'172.30.10.5/24'})
        self.addLink( r3, r4,
                      intfName1='r3-eth2',
                      params1={'ip':'172.30.20.3/24'},
                      intfName2='r4-eth1',
                      params2={'ip':'172.30.20.4/24'})

def run():

    topo = NetworkTopo()
    net = Mininet( topo=topo, controller=None)  # controller is used by s1-s3
    net.addController( 'c0', controller=RemoteController, ip='192.168.56.1', port=6653 )

    net.start()
    info( '*** Routing Table on Router 1:\n' )
    info( net[ 'r1' ].cmd( 'route' ) )

    net[ 'r1' ].stopQuagga()
    routers = ['r1','r2','r3','r4','r5']
    for router in routers:
        net [ router ].runOSPF()
        # need some delay for clear configuration
	sleep(2)
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()

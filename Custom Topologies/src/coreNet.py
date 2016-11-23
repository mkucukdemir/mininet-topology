#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="m.kucukdemir"
__date__ ="$Oct 7, 2016 10:59:00 AM$"

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
from time import sleep
from os import environ

POX_DEFAULT_DIR = environ[ 'HOME' ] + '/pox'

class DefaultPOXController( Controller ):
    def __init__(
            self,
            name,
            cdir=POX_DEFAULT_DIR,
            command='python pox.py',
            cargs=( 'log.level --DEBUG openflow.of_01 --port=%s forwarding.l2_learning' ),
            **kwargs
        ):
        Controller.__init__(self,name,cdir=cdir,command=command,cargs=cargs,**kwargs)

class LxRouter( Node ):

    def config( self, **params ):
        super( LxRouter, self).config( **params )
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LxRouter, self ).terminate()

    def startBGP(self):
        print("***[%s] BGP starting " % self.name)
        self.cmd("/usr/lib/quagga/zebra -f ../quaggacfgs/zebra-%s.conf -d -i /tmp/zebra-%s.pid > ../logs/%s-zebra-stdout 2>&1" % (self.name, self.name, self.name))
        self.waitOutput()
        self.cmd("/usr/lib/quagga/bgpd -f ../quaggacfgs/bgpd-%s.conf -d -i /tmp/bgp-%s.pid > ../logs/%s-bgpd-stdout 2>&1" % (self.name, self.name, self.name), shell=True)
        self.waitOutput()
        
    def startOSPF(self):
        print("***[%s] OSPF starting " % self.name)
        self.cmd("/usr/lib/quagga/zebra -f ../quaggacfgs/zebra-%s.conf -d -i /tmp/zebra-%s.pid > ../logs/%s-zebra-stdout 2>&1" % (self.name, self.name, self.name))
        self.waitOutput()
        self.cmd("/usr/lib/quagga/ospfd -f ../quaggacfgs/ospfd-%s.conf -d -i /tmp/ospf-%s.pid > ../logs/%s-ospfd-stdout 2>&1" % (self.name, self.name, self.name), shell=True)
        self.waitOutput()

    def stopQuagga( self ):
        print("***[%s] Zebra, OSPF & BGP services are being terminated. Please wait... " % (self.name))
        self.cmd("pkill zebra")
        self.waitOutput()
        self.cmd("pkill bgpd")
        self.waitOutput()
        self.cmd("pkill ospfd")
        self.waitOutput()

class CoreNet( Topo ):
    '''
    AS1 10.0.0.0/8
        Area-0 (Backbone)   10.0.0.0/16
        Area-1              10.1.0.0/16
        Area-2              10.2.0.0/16
        Area-3              10.3.0.0/16
    AS2 20.0.0.0/8
        Area-0 (Backbone)   20.0.0.0/16
        Area-1              20.1.0.0/16
        Area-2              20.2.0.0/16
    AS3 30.0.0.0/8
        Area-0 (Backbone)   30.0.0.0/16
        Area-1              30.1.0.0/16
        Area-2              30.2.0.0/16
        Area-3              30.3.0.0/16
    '''
    def build(self, **_opts ):
        # ASBRs
        asbr11 = self.addNode( 'asbr11', cls=LxRouter, ip="200.11.21.11/24")
        asbr21 = self.addNode( 'asbr21', cls=LxRouter, ip="200.11.21.21/24")
        asbr12 = self.addNode( 'asbr12', cls=LxRouter, ip="200.12.31.12/24")
        asbr31 = self.addNode( 'asbr31', cls=LxRouter, ip="200.12.31.31/24")
        asbr22 = self.addNode( 'asbr22', cls=LxRouter, ip="200.22.32.22/24")
        asbr32 = self.addNode( 'asbr32', cls=LxRouter, ip="200.22.32.32/24")
        # AS1 Backbone ABRs
        as1abr1 = self.addNode( 'as1abr1', cls=LxRouter, ip="10.0.111.1/24")
        as1abr2 = self.addNode( 'as1abr2', cls=LxRouter, ip="10.0.121.2/24")
        as1abr3 = self.addNode( 'as1abr3', cls=LxRouter, ip="10.0.132.3/24")
        # AS2 Backbone ABRs
        as2abr1 = self.addNode( 'as2abr1', cls=LxRouter, ip="20.0.111.1/24")
        as2abr2 = self.addNode( 'as2abr2', cls=LxRouter, ip="20.0.123.2/24")
        # AS3 Backbone ABRs
        as3abr1 = self.addNode( 'as3abr1', cls=LxRouter, ip="30.0.113.1/24")
        as3abr2 = self.addNode( 'as3abr2', cls=LxRouter, ip="30.0.123.2/24")
        as3abr3 = self.addNode( 'as3abr3', cls=LxRouter, ip="30.0.133.3/24")
        # Switches
        as1a1s1 = self.addSwitch( 'as1a1s1', protocols='OpenFlow13')
        as1a1s2 = self.addSwitch( 'as1a1s2', protocols='OpenFlow13')
        as1a1s3 = self.addSwitch( 'as1a1s3', protocols='OpenFlow13')
        as2a2s1 = self.addSwitch( 'as2a2s1', protocols='OpenFlow13')
        as2a2s2 = self.addSwitch( 'as2a2s2', protocols='OpenFlow13')
        as3a2s1 = self.addSwitch( 'as3a2s1', protocols='OpenFlow13')
        as3a2s2 = self.addSwitch( 'as3a2s2', protocols='OpenFlow13')
        as3a2s3 = self.addSwitch( 'as3a2s3', protocols='OpenFlow13')

        # Links
        # ASBR - ASBR Runs eBGP
        self.addLink( asbr11, asbr21,
                                intfName1='asbr11-br1',
                                params1={'ip':'200.11.21.11/24'},
                                intfName2='asbr21-br1',
                                params2={'ip':'200.11.21.21/24'})
        self.addLink( asbr22, asbr32,
                                intfName1='asbr22-br1',
                                params1={'ip':'200.22.32.22/24'},
                                intfName2='asbr32-br1',
                                params2={'ip':'200.22.32.32/24'})
        self.addLink( asbr12, asbr31,
                                intfName1='asbr12-br1',
                                params1={'ip':'200.12.31.12/24'},
                                intfName2='asbr31-br1',
                                params2={'ip':'200.12.31.31/24'})
        # ASBR - ASBR Runs iBGP
        self.addLink( asbr11, asbr12,
                                intfName1='asbr11-br2',
                                params1={'ip':'10.0.212.11/24'},
                                intfName2='asbr12-br2',
                                params2={'ip':'10.0.212.12/24'})
        self.addLink( asbr21, asbr22,
                                intfName1='asbr21-br2',
                                params1={'ip':'20.0.212.21/24'},
                                intfName2='asbr22-br2',
                                params2={'ip':'20.0.212.22/24'})
        self.addLink( asbr31, asbr32,
                                intfName1='asbr31-br2',
                                params1={'ip':'30.0.212.31/24'},
                                intfName2='asbr32-br2',
                                params2={'ip':'30.0.212.32/24'})
        # ASBR - ABR
        self.addLink( asbr11, as1abr1,
                                intfName1='asbr11-br3',
                                params1={'ip':'10.0.111.11/24'},
                                intfName2='as1abr1-br2',
                                params2={'ip':'10.0.111.1/24'})
        self.addLink( asbr11, as1abr2,
                                intfName1='asbr11-br4',
                                params1={'ip':'10.0.121.11/24'},
                                intfName2='as1abr2-br2',
                                params2={'ip':'10.0.121.2/24'})
        self.addLink( asbr12, as1abr2,
                                intfName1='asbr12-br3',
                                params1={'ip':'10.0.122.12/24'},
                                intfName2='as1abr2-br3',
                                params2={'ip':'10.0.122.2/24'})
        self.addLink( asbr12, as1abr3,
                                intfName1='asbr12-br4',
                                params1={'ip':'10.0.132.12/24'},
                                intfName2='as1abr3-br2',
                                params2={'ip':'10.0.132.3/24'})
        self.addLink( asbr21, as2abr1,
                                intfName1='asbr21-br3',
                                params1={'ip':'20.0.111.21/24'},
                                intfName2='as2abr1-br2',
                                params2={'ip':'20.0.111.1/24'})
        self.addLink( asbr22, as2abr2,
                                intfName1='asbr22-br3',
                                params1={'ip':'20.0.123.22/24'},
                                intfName2='as2abr2-br2',
                                params2={'ip':'20.0.123.2/24'})
        self.addLink( asbr31, as3abr1,
                                intfName1='asbr31-br3',
                                params1={'ip':'30.0.113.31/24'},
                                intfName2='as3abr1-br2',
                                params2={'ip':'30.0.113.1/24'})
        self.addLink( asbr31, as3abr2,
                                intfName1='asbr31-br4',
                                params1={'ip':'30.0.123.31/24'},
                                intfName2='as3abr2-br2',
                                params2={'ip':'30.0.123.2/24'})
        self.addLink( asbr31, as3abr3,
                                intfName1='asbr31-br5',
                                params1={'ip':'30.0.133.31/24'},
                                intfName2='as3abr3-br2',
                                params2={'ip':'30.0.133.3/24'})
        self.addLink( asbr32, as3abr1,
                                intfName1='asbr32-br4',
                                params1={'ip':'30.0.112.32/24'},
                                intfName2='as3abr1-br1',
                                params2={'ip':'30.0.112.1/24'})
        self.addLink( asbr32, as3abr2,
                                intfName1='asbr32-br5',
                                params1={'ip':'30.0.122.32/24'},
                                intfName2='as3abr2-br1',
                                params2={'ip':'30.0.122.2/24'})
        self.addLink( asbr32, as3abr3,
                                intfName1='asbr32-br3',
                                params1={'ip':'30.0.132.32/24'},
                                intfName2='as3abr3-br1',
                                params2={'ip':'30.0.132.3/24'})
        # ABR - ABR
        self.addLink( as1abr1, as1abr2,
                                intfName1='as1abr1-br1',
                                params1={'ip':'10.0.12.1/24'},
                                intfName2='as1abr2-br1',
                                params2={'ip':'10.0.12.2/24'})
        self.addLink( as1abr2, as1abr3,
                                intfName1='as1abr2-br4',
                                params1={'ip':'10.0.23.2/24'},
                                intfName2='as1abr3-br1',
                                params2={'ip':'10.0.23.3/24'})
        self.addLink( as2abr1, as2abr2,
                                intfName1='as2abr1-br1',
                                params1={'ip':'20.0.12.1/24'},
                                intfName2='as2abr2-br1',
                                params2={'ip':'20.0.12.2/24'})
        # ABR - Switch
        self.addLink( as1a1s1, as1abr1, intfName2='as1abr1-eth1', params2={'ip':'10.1.1.1/24'})
        self.addLink( as1a1s2, as1abr1, intfName2='as1abr1-eth2', params2={'ip':'10.1.2.1/24'})
        self.addLink( as1a1s3, as1abr1, intfName2='as1abr1-eth3', params2={'ip':'10.1.3.1/24'})
        self.addLink( as2a2s1, as2abr2, intfName2='as2abr2-eth1', params2={'ip':'20.2.1.1/24'})
        self.addLink( as2a2s2, as2abr2, intfName2='as2abr2-eth2', params2={'ip':'20.2.2.1/24'})
        self.addLink( as3a2s1, as3abr2, intfName2='as3abr2-eth1', params2={'ip':'30.2.1.1/24'})
        self.addLink( as3a2s2, as3abr2, intfName2='as3abr2-eth2', params2={'ip':'30.2.2.1/24'})
        self.addLink( as3a2s3, as3abr2, intfName2='as3abr2-eth3', params2={'ip':'30.2.3.1/24'})

def generateLoopbackIp(router):
    return router[4:] + ' ' + router[4:] + '.' + router[4:] + '.' + router[4:] + '.' + router[4:]

def run():

    topo = CoreNet()

    net = Mininet( topo=CoreNet(), build=False, controller=None)
    c0 = net.addController( 'c0', controller=DefaultPOXController, ip='127.0.0.1', port=6633)

    net.start()
    net[ 'asbr11' ].stopQuagga()
    
    ospfRouters = [ 'as1abr1', 'as1abr2', 'as1abr3', 'as2abr1', 'as2abr2', 'as3abr1', 'as3abr2', 'as3abr3', 'asbr11', 'asbr12', 'asbr21', 'asbr22', 'asbr31', 'asbr32']
    bgpRouters = [ 'asbr11', 'asbr12', 'asbr21', 'asbr22', 'asbr31', 'asbr32']

    #Define loopback interfaces
    #for router in bgpRouters:
    #    net[ router ].cmd( 'ifconfig lo:' + generateLoopbackIp(router) + ' netmask 255.255.255.255 up' )

    for router in ospfRouters:
        net[ router ].startOSPF()
        sleep(0.5)

    for router in bgpRouters:
        net[ router ].startBGP()
        sleep(0.5)

    #DEBUGGING
    #net[ 'as1abr1' ].cmd('tcpdump -i as1abr1-br2 -l -e > /home/mininet/dump_as1abr1_br2.pcap &')
    #net[ 'asbr11' ].cmd('tcpdump -i asbr11-br3 -l -e > /home/mininet/dump_asbr11_br3.pcap &')
    #net[ 'asbr11' ].cmd('tcpdump -i asbr11-br1 -l -e > /home/mininet/dump_asbr11_br1.pcap &')
    #net[ 'asbr21' ].cmd('tcpdump -i asbr21-br1 -l -e > /home/mininet/dump_asbr21_br1.pcap &')
    #net[ 'asbr21' ].cmd('tcpdump -i asbr21-br2 -l -e > /home/mininet/dump_asbr21_br2.pcap &')
    #net[ 'asbr21' ].cmd('tcpdump -i asbr21-br3 -l -e > /home/mininet/dump_asbr21_br3.pcap &')

    CLI(net)
    print "CoreNet is terminating"
    net.stop()
    print "CoreNet has been terminated"

if __name__ == "__main__":
    print "CoreNet Simulation"
    setLogLevel( 'info' )
    run()

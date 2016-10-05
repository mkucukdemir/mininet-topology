#! /usr/bin/python

#           R
#        /  |  \
#      /    |    \
#    /      |      \
#   S       S       S
#  / \     / \      |
# H   H   H   H     H

__author__ = "m.kucukdemir"
__date__ = "$Sep 30, 2016 9:49:01 PM$"

from mininet.topo import Topo
from mininet.node import Host
from mininet.node import OVSKernelSwitch
from mininet.link import TCLink
from mininet.node import OVSSwitch
from mininet.node import Node

class SoftRouter( Node ):

    def config( self, **params ):
        super( SoftRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )
        # Enable interface eth2
	self.cmd( 'ifconfig r1-eth2 10.0.2.1' )
	self.cmd( 'ifconfig r1-eth2 netmask 255.255.255.0' )
	self.cmd( 'ifconfig r1-eth2 broadcast 10.0.2.255' )
        #Enable interface eth3
	self.cmd( 'ifconfig r1-eth3 10.0.3.1' )
	self.cmd( 'ifconfig r1-eth3 netmask 255.255.255.0' )
	self.cmd( 'ifconfig r1-eth3 broadcast 10.0.3.255' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( SoftRouter, self ).terminate()

class MyNetworkTopology( Topo ):

	def __init__(self,**kwargs):
		Topo.__init__(self,**kwargs)
                
		h1 = self.addHost('h1',cls=Host,mac='00:00:00:00:00:11',ip='10.0.1.2/24',defaultRoute='via 10.0.1.1')
		h2 = self.addHost('h2',cls=Host,mac='00:00:00:00:00:22',ip='10.0.1.3/24',defaultRoute='via 10.0.1.1')
		h3 = self.addHost('h3',cls=Host,mac='00:00:00:00:00:33',ip='10.0.2.2/24',defaultRoute='via 10.0.2.1')
		h4 = self.addHost('h4',cls=Host,mac='00:00:00:00:00:44',ip='10.0.2.3/24',defaultRoute='via 10.0.2.1')
		h5 = self.addHost('h5',cls=Host,mac='00:00:00:00:00:55',ip='10.0.3.2/24',defaultRoute='via 10.0.3.1')

		s1 = self.addSwitch('s1',cls=OVSSwitch)
		s2 = self.addSwitch('s2',cls=OVSSwitch)
		s3 = self.addSwitch('s3',cls=OVSSwitch)

		r1 = self.addNode( 'r1',cls=SoftRouter,ip='10.0.1.1/24')

		specialLink = {'bw':1000}
		
		self.addLink(h1, s1, cls=TCLink,**specialLink)
		self.addLink(h2, s1, cls=TCLink,**specialLink)
		self.addLink(h3, s2, cls=TCLink,**specialLink)
		self.addLink(h4, s2, cls=TCLink,**specialLink)
		self.addLink(h5, s3, cls=TCLink,**specialLink)
		
		self.addLink(s1,r1,intfName2='r1-eth1',params2={'ip':'10.0.1.1/24'})
		self.addLink(s2,r1,intfName2='r1-eth2',params2={'ip':'10.0.2.1/24'})
		self.addLink(s3,r1,intfName2='r1-eth3',params2={'ip':'10.0.3.1/24'})

topos = {'mytopo':( lambda **args: MyNetworkTopology(**args))}
#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "mehmet"
__date__ = "$Sep 30, 2016 9:49:01 PM$"

from mininet.topo import Topo
from mininet.node import Host
from mininet.node import OVSKernelSwitch
from mininet.link import TCLink
from mininet.node import OVSSwitch
from mininet.node import Node

class MyRouter( Node ):

    def config( self, **params ):
        super( MyRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( MyRouter, self ).terminate()

class MyNetworkTopology( Topo ):

	"My Custom Network Topology"
	def __init__(self,**kwargs):
		Topo.__init__(self,**kwargs)
		# h1 = self.addHost('h1',cls=Host,mac='00:00:00:00:00:01',ip='10.0.0.2/24',defaultRoute=None)
		h1 = self.addHost('h1',cls=Host,mac='00:00:00:00:00:01',ip='10.0.0.2/24')
		h2 = self.addHost('h2',cls=Host,mac='00:00:00:00:00:02',ip='10.0.0.3/24',defaultRoute=None)
		h3 = self.addHost('h3',cls=Host,mac='00:00:00:00:00:03',ip='10.0.1.2/24',defaultRoute=None)

		s1 = self.addSwitch('s1',cls=OVSSwitch)
		s2 = self.addSwitch('s2',cls=OVSSwitch)

		# defaultIP = '10.1.0.1/16'  # IP address for r1-eth0
		#r1 = self.addNode( 'r1', cls=MyRouter, ip=defaultIP )

		specialLink = {'bw':1000}
		
		self.addLink(h1, s1, cls=TCLink,**specialLink)
		self.addLink(h2, s1, cls=TCLink,**specialLink)
		self.addLink(h3, s2, cls=TCLink,**specialLink)
		
		self.addLink(s1, s2, cls=TCLink, **specialLink)

topos = {'mytopo':( lambda **args: MyNetworkTopology(**args))}
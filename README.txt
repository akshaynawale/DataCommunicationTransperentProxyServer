###################### AUTHOR ##############################
Name: Akshay Satyendra Navale
Occupation: ITP Student at University of Colorado, Boulder.USA.
Contact Details: akna8887@colorado.edu
Phone Number: 720-345-4053
############################################################


Welcome!!! 
This is a README file for HTTPproxy.py.
The python code is written in python version 2.7.


############### Required Arguments ############################
This program required one argument which should be in following
format. It conatains IP and the port separated by colon
<Proxy IP>:<Proxy Port>
e.g:
192.168.0.1:5000

================ Design Decisions ==========================

############### Network Configuration #######################
This program is running on a machine, which is a default 
gateway for http server and clinet. The Server side IP 
addresses are in 172.16.0.0/24 network and Clinet side IP
are in 192.168.0.0/24 network. Proxy server also have a 
interface that is connected to the internet.

############## Used OS for Nework Setup ######################
I am using CentOS on HTTP server and Proxy Server and Ubuntu OS
on client.

############### To add interface configuration on VM ##########
On CentOS:-----------------------------------------------------

Change the interface file at /etc/sysconfig/network-scripts/ 
location :
TYPE=Ethernet
BOOTPROTO=none
DEFROUTE=yes
PEERDNS=yes
PEERROUTES=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_PEERDNS=yes
IPV6_PEERROUTES=yes
IPV6_FAILURE_FATAL=no
NAME=enp0s3
UUID=755776c2-47ed-41b7-97a9-154ba74ea90d
DEVICE=enp0s3
ONBOOT=yes
IPADDR=172.16.0.2 ===> Ip address for Server
NETMASK=255.255.255.0 ===> Network mask
GATEWAY=172.16.0.1	===> Ip address of proxy as a default gateway
NM_CONTROLLED=no
DNS1=8.8.8.8  ===> DNS address 

Debugging commands used:
ping <ip address>
ip addr [<interface name>]
systemctl restart network
systemctl status network
ifup <interface name>
ifdown <interface name>

On Ubuntu OS:-------------------------------------------------------
To configure Static IP address on ubuntu OS
iface eth0 inet static
address 192.168.0.2   ==> Ip address assign to the client
netmask 255.255.255.0
gateway 192.168.0.1 ==> Ip address of Proxy server
dns-nameservers 8.8.8.8

Debugging commands used:
sudo ifup eth0
sudo ifdown eth0
ip addr

############# iptables configuration on proxy server#################
If your proxy by default blocking some connections remove the rules
from the proxy or you can remove all rules from the iptables by 
following command:
iptables -F INPUT
iptables -F OUTPUT
iptables -F FORWARD

############ To make Proxy act as Router #############################
iptables -t nat -F PREROUTING
iptables -t nat -F POSTROUTING
iptables -t nat -A POSTROUTING -o enp0s3 -j MASQUERADE

to save this config:
iptables-save > /etc/sysconfig/iptables

Also we have to change the file content at location below:
vi /etc/sysctl.conf
write following in this file
net.ipv4.ip_forward = 1

============== Code Design ===============================

############## Genral info  ###############################
HTTPproxy.py installs automatic iptables rules so that the 
traffic destine for port 80 will be DNAT (destination NAT)
to Proxy`s IP and Port Number.
Then it Parse the request and send the request to the HTTP
Server. But it also configure a SNAT (Source NAT)  rule so 
that this request`s source IP will be changed to the Client
IP and Client request port. 
Now the Server will think that the request is directly comming 
from the client.
Now when Server send reply Proxy server will again do DNAT and 
will do SNAT while sending response to the clinet and so clinet
will think that the Server has directly sended this response.
Their is no one in middle of them.

############### Multi Threading ############################
This HTTP proxy code uses thread which allow the Proxy server
to handle multiple requests at same time.

############### Functions Used #############################
Get_Arguments----------------------------------------------
Get command line argument from the User that is Proxy`s Ip and 
Port number.

Initialise--------------------------------------------------
This will install initial rules in IP tables so that all traffic
for HTTP will be DNAT to Proxy IP address.

Handle_Request-----------------------------------------------
handles requests , does multi threading.

Install_Rules------------------------------------------------
Installs rules for SNAT for a user`s IP and Port.

RemoveRule---------------------------------------------------
remove the specific rules installed for a users.

############### Tools used for Debugging #####################
TCPDUMP-------------------------------------------------------
used to sniff HTTP traffic on both client and server.

To install:
On CentOS:
yum install tcpdump
On Ubuntu:
sudo apt-get install tcpdump

usage:
tcpdump -i enp0s3 -p tcp port http -vvv

NMAP-----------------------------------------------------------
To chack which ports are open.
usage:
nmap localhost

################################################################
Thank You!!!  

 
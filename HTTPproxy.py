import socket
import thread
import struct
import subprocess
import time
import sys


def Get_Arguments():    # Get Ip and Port number from User
    if (len(sys.argv)!=2):
        print("This program require 1 argument => in (IP:Port) format")
        sys.exit()
    else:
        IP_Info=sys.argv[1]
        IP_Info=IP_Info.split(":")
        if (len(IP_Info)==2):
            return IP_Info[0], IP_Info[1]
        else:
            print("The IP and port must be separated with : sign")
            sys.exit()


def ParseReq(Req):      # Parse The User request
    lineList=Req.split('\n')
    Line1=lineList[0]
    Line1_Info=Line1.split()
    Method=Line1_Info[0]
    Path=Line1_Info[1]
    Version=Line1_Info[2]
    Line2=lineList[1]
    Line2_Info=Line2.split()
    HostAddr=Line2_Info[1]
    return Method, Path, Version, HostAddr

def Install_Rules(CLI_IP, CLI_Port, Proxy_CLI_IP,Proxy_CLI_Port, Proxy_Server_IP, Proxy_Server_Port, Dest_Server_Port, Dest_Server_IP): # install user specific rules
    Rule1="iptables -t nat -I POSTROUTING 1 -o enp0s9 -p tcp -j SNAT --to-source "+CLI_IP+":"+str(CLI_Port)
    try:
        p = subprocess.Popen(Rule1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except:
        print("unable to install rules on machine")
        return False
    '''
    p = subprocess.Popen('iptables -t nat -L POSTROUTING --line-numbers -nv', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        if line:
                print(line)
    '''
    return True, Rule1

def RemoveRule(Rule):   # Remove user specific rules after 30 sec
    time.sleep(30)
    Rule=Rule.replace("-I POSTROUTING 1", "-D POSTROUTING")
    try:
        p = subprocess.Popen(Rule, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except:
        print("unable to Remove rules on machine")
        return False
    return True

def Handle_Request(CLISoc,CLIAddr,Req, Proxy_CLI_IP,Proxy_CLI_Port):    # Handle User Request
    SO_ORIGINAL_DST = 80
    sockaddr_in = CLISoc.getsockopt(socket.SOL_IP, SO_ORIGINAL_DST, 16)
    (proto, port, a, b, c, d) = struct.unpack('!HHBBBB', sockaddr_in[:8])
    Dest_Server_IP=('%d.%d.%d.%d'%(a,b,c,d))
    Dest_Server_Port=('%d'%(port))
    CLI_IP=CLIAddr[0]
    CLI_Port=CLIAddr[1]
    SERSoc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Dest_Server_Port=int(Dest_Server_Port)
    Dest_Server_IP=str(Dest_Server_IP)
    SERSoc.connect((Dest_Server_IP,Dest_Server_Port))
    Proxy_Server_Addr_Info=SERSoc.getsockname()
    Proxy_Server_IP=Proxy_Server_Addr_Info[0]
    Proxy_Server_Port=Proxy_Server_Addr_Info[1]
    Result, Rule=Install_Rules(CLI_IP, CLI_Port, Proxy_CLI_IP,Proxy_CLI_Port, Proxy_Server_IP, Proxy_Server_Port, Dest_Server_Port, Dest_Server_IP)
    if Result:
        time.sleep(0.5)
        SERSoc.send(Req)
        TotalPages=""
        Pages=SERSoc.recv(999999)
        while Pages:
                TotalPages+=Pages
                Pages=SERSoc.recv(999999)
        CLISoc.sendall(TotalPages)
        SendData=len(TotalPages)
        ReqData=len(Req)
        print(CLI_IP.rjust(15)+(str(CLI_Port)).rjust(15)+Dest_Server_IP.rjust(15)+(str(Dest_Server_Port)).rjust(15)+(str(SendData)).rjust(15)+(str(ReqData)).rjust(15))
        SERSoc.close()
        CLISoc.close()
        Result1=RemoveRule(Rule)

def Initialise(Proxy_CLI_IP, Proxy_CLI_Port):   # Install all rules to DNAT traffic to Proxy IP
    R1="iptables -t nat -F PREROUTING"
    R2="iptables -t nat -F POSTROUTING"
    R3="iptables -t nat -A POSTROUTING -o enp0s3 -j MASQUERADE"
    R4="iptables -t nat -A PREROUTING -p tcp --dport 80 -i enp0s8 -j DNAT --to "+Proxy_CLI_IP+":"+str(Proxy_CLI_Port)
    #print(R4)
    try:
        p = subprocess.Popen(R1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p = subprocess.Popen(R2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p = subprocess.Popen(R3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p = subprocess.Popen(R4, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except:
        print("unable to install Initail Rules on machine")
        return False
    '''
    p = subprocess.Popen('iptables -t nat -L PREROUTING --line-numbers -nv', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        if line:
                print(line)
    '''
    return True

#Main Program Starts#
size=999999
Proxy_CLI_IP, Proxy_CLI_Port=Get_Arguments()
try:
    Proxy_CLI_Port=int(Proxy_CLI_Port)
except:
    print("Post must be a number")
    sys.exit()
Result=Initialise(Proxy_CLI_IP, Proxy_CLI_Port)
if Result==False:
    quit()
print("CLI IP".rjust(15)+"CLI Port".rjust(15)+"Server IP".rjust(15)+"Server Port".rjust(15)+"Send Data".rjust(15)+"Recv Data".rjust(15))
# create Main Socket
try:
    MainS=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    MainS.bind((Proxy_CLI_IP,Proxy_CLI_Port))
    MainS.listen(5)
except:
    print("Unable to creata a socket : Already a process is running on the same port and IP")
    sys.exit()
while True:
    CLISoc, CLIAddr=MainS.accept()
    Req=CLISoc.recv(size)
    if Req:
        thread.start_new_thread(Handle_Request,(CLISoc, CLIAddr, Req, Proxy_CLI_IP,Proxy_CLI_Port,))# Start Thread

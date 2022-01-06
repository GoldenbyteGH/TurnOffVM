#!/usr/bin/python3
"""
Script to turn OFF a specific VM  in ESXI

e.g.  TurnOffVm.py GNS3

"""

import sys
import paramiko
from cryptography.fernet import Fernet
import configparser

class ESXI_Srv:
    def __init__(self,IP,user,enc_psw,key):

        self.IP = IP
        self.user = user
        self.fernet_enc = Fernet(key.encode())                              #define fernet encryption based on key parameter
        self.psw = self.fernet_enc.decrypt(enc_psw.encode()).decode().replace("'","")
        self.WorldID = 0

    def get_world_id(self,Name_VM):

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.IP, username=self.user, password=self.psw)

        # Run command.
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("esxcli vm process list")
        output = ssh_stdout.readlines()
        for index, elem in enumerate(output):
            if Name_VM in elem:
                self.WorldID = output[index + 1].replace("World ID: ", "")
                self.WorldID = self.WorldID.replace(" ", "")
                break
        if self.WorldID != 0:
            return self.WorldID
        else:
            return -1           # VM not found

    def turn_off_vm(self,WorldID):

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.IP,username=self.user,password=self.psw)

        # Run command.
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("esxcli vm process kill -t=soft -w="+str(WorldID))
        #chan.send("esxcli vm process kill -t=soft -w="+str(self.WorldID))

        output = ssh_stdout.readlines()
        ssh.close()

        return output


if __name__ == '__main__':

    #get my encrypted password
    config = configparser.ConfigParser()
    config.read('config.ini')
    #default state is OFF
    try:
        arg = sys.argv[1:]              # name of VM to TURN OFF
    except:
        print("ERROR - missing  parameter")
        exit()
    gbserver = ESXI_Srv(config["Account"]["IP"],config["Account"]["user"], config["Account"]["esxi_en_psw"], config["Account"]["key"])
    GNS3_ID = gbserver.get_world_id(arg[0])
    if GNS3_ID == -1:
        raise ValueError(arg[0]+' vm not found')

    output = gbserver.turn_off_vm(GNS3_ID)
    print("VM "+arg[0]+" turned OFF\n")

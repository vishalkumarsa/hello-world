import base64
import argparse
import sys
import requests
import ssl
import subprocess
import time
import os
from subprocess import call

requests.packages.urllib3.disable_warnings()

def get_volumes():
    base64string = base64.encodestring('%s:%s' % ('admin', 'Password@123')).replace('\n', '')

    url = "https://10.195.29.232:8443/api/1.0/ontap/volumes/"
    headers = {
        "Authorization": "Basic %s" % base64string,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    r = requests.get(url, headers=headers,verify=False)
    #print r.json()
    return r.json()

def check_vol(vol_name):
    tmp = dict(get_volumes())
    vols = tmp['result']['records']
    names = [i['name'] for i in vols]
    #print "Volume Names: ", names
    return vol_name in names

def get_jpath(vol_name):
    tmp = dict(get_volumes())
    vols = tmp['result']['records']
    for i in vols:
         if i['name'] == vol_name:
            # print i
            return i['junction_path']

def make_volume(vol_name):
    base64string = base64.encodestring('%s:%s' % ('admin', 'Password@123')).replace('\n', '')
    url = "https://10.195.29.232:8443/api/1.0/ontap/volumes/"
    headers = {
    "Authorization": "Basic %s" % base64string,
    "Content-Type": "application/json",
    "Accept": "application/json"
    }
    data= {
    "aggregate_key":"086a90ce-8a14-11e5-aae4-00a09873c208:type=aggregate,uuid=ba14cc0b-9194-4558-9fa3-a78ef1e95b90",
    "size":"368709120",
    "storage_vm_key":"086a90ce-8a14-11e5-aae4-00a09873c208:type=vserver,uuid=7528f769-d07b-11e5-aae5-00a09873c208",
    "name":vol_name,
    "junction_path":'/'+vol_name,
    "security_permissions":"777"
    }
    r = requests.post(url, headers=headers,json=data, verify=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Passing variables to the program')
    parser.add_argument('-v','--vol_name', help='Volume to create or clone from',dest='vol_name',required=True)
    parser.add_argument('-scm','--branch_name', help='Branch of the SCM to clone',dest='branch_name',required=True)
    parser.add_argument('-mp','--mount_path', help='Mount path for base volume',dest='mount_path')
    parser.add_argument('-l','--link', help='SCM link',dest='link')
    globals().update(vars(parser.parse_args()))
    count = 0
    #make_volume(vol_name)
    while check_vol(vol_name) == False:
        time.sleep(1)
        count=count+1
    mnt_cmd = "sudo mount 10.195.29.79:{} /tmp/master".format(get_jpath(vol_name))
    return_code = subprocess.call(mnt_cmd,shell=True)
    
    print "Base Volume created snd mounted successfully in {} seconds".format(count)
    mnt_cmd = "git clone https://github.com/vishalkumarsa/hello-world /tmp/master "
    return_code = subprocess.call(mnt_cmd,shell=True)
    print "Code pull from SCM complete"

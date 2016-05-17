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

def get_jpath(vol_name):
    tmp = dict(get_volumes())
    vols = tmp['result']['records']
    for i in vols:
         if i['name'] == vol_name:
            # print i
            return i['junction_path']

def get_key(vol_name):
    tmp = dict(get_volumes())
    vols = tmp['result']['records']
    for i in vols:
        if i['name'] == vol_name:
            # print i
            return i['key']

def get_sskey(vol_name,snap_name):
    tmp = dict(get_snaps(vol_name))
    snaps = tmp['result']['records']
    for i in snaps:
        if i['name'] == snap_name:
            # print i
            return i['key']

def get_snaps(vol_name):
    key=get_key(vol_name)
    base64string = base64.encodestring('%s:%s' % ('admin', 'Password@123')).replace('\n', '')
    #print key
    url4= "https://10.195.29.232:8443/api/1.0/ontap/snapshots?volume_key={}".format(key)
    headers = {
        "Authorization": "Basic %s" % base64string,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    #print url4
    r = requests.get(url4,headers=headers,verify=False)
    #print r.json()
    return r.json()

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
    #print "get_volumes works"
    return r.json()

def make_clone(vol_name,snapshot_name,clone_name):
    #print snapshot_name
    base64string = base64.encodestring('%s:%s' % ('admin', 'Password@123')).replace('\n', '')
    key=get_key(vol_name)
    #print key
    url2= "https://10.195.29.232:8443/api/1.0/ontap/volumes/{}/jobs/clone".format(key)
    #print url2
    headers = {
        "Authorization": "Basic %s" % base64string,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    ss_key= get_sskey(vol_name,snapshot_name)
    #print ss_key
    data= {

        "volume_clone_name":"{}".format(clone_name),
        "snapshot_key":get_sskey(vol_name,snapshot_name)
        }
    #print data
    r = requests.post(url2, headers=headers,json=data,verify=False)
    #clone_name= "Master5_clone4"
    #make_clonejpath(clone_name)
    #print "Clone Created"

def make_clonejpath(clone_name):
    base64string = base64.encodestring('%s:%s' % ('admin', 'Password@123')).replace('\n', '')
    clone = check_vol(clone_name)
    #print clone
    url6= "https://10.195.29.232:8443/api/1.0/ontap/volumes/{}/jobs/mount".format(get_key(clone_name))
    #print url6
    headers = {
        "Authorization": "Basic %s" % base64string,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data= {
            "junction_path":'/'+clone_name
          }
    #print data
    r = requests.post(url6, headers=headers,json=data,verify=False)
    return clone

def check_vol(vol_name):
    tmp = dict(get_volumes())
    vols = tmp['result']['records']
    names = [i['name'] for i in vols]
    #print "Volume Names: ", names
    return vol_name in names

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Passing variables to the program')
    parser.add_argument('-v','--vol_name', help='Volume to create or clone from',dest='vol_name',required=True)
    parser.add_argument('-mp','--mount_path', help='Local mount path',dest='mount_path',required=True)
    parser.add_argument('-s','--snapshot_name', help='Snapshot to create or clone from',dest='snapshot_name')
    parser.add_argument('-c','--clone_name', help='Name of the clone to create',dest='clone_name')
    globals().update(vars(parser.parse_args()))
    clone = False
    count = 0 
    make_clone(vol_name,snapshot_name,clone_name)
    while (clone == False):
        clone = make_clonejpath(clone_name)
        time.sleep(1)
        count=count+1
    
    mnt_cmd = "sudo mount 10.195.29.79:{} /tmp/clone".format(get_jpath(clone_name))
    #print mnt_cmd
    return_code = subprocess.call(mnt_cmd,shell=True)
    print "Clone created and mounted successfully in {} seconds.".format(count)


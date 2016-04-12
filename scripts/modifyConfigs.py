import json
import os
import sys
import requests
from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
import time



def modifyCoreSiteConfig(hostName,auth,tag,currentProperties):
    print "MODIFY CORE-SITE"
    url = "http://" + hostName +"/api/v1/clusters/Sandbox"
    headers = {"X-Requested-By": "HDB Installer"}
    properties = currentProperties
    desConfig={}
    cluster={}
    config={}
    properties["ipc.client.connection.maxidletime"] = 3600000
    properties["ipc.client.connect.timeout	"] = 300000
    properties["ipc.server.listen.queue.size"] = 3300
    desConfig["properties"]=properties
    desConfig["type"]="core-site"
    desConfig["tag"]="hdb-updates"
    cluster["desired_config"]=desConfig
    config["Clusters"]=cluster
    configChange = requests.put(url,auth=auth,headers=headers,data=json.dumps(config))

def modifyHdfsSiteConfig(hostName, auth, tag, currentProperties):
    print "MODIFY HDFS-SITE"
    url = "http://" + hostName + "/api/v1/clusters/Sandbox"
    headers = {"X-Requested-By": "HDB Installer"}
    properties = currentProperties
    desConfig = {}
    cluster = {}
    config = {}
    properties["dfs.allow.truncate"] = "true"
    properties["dfs.support.append"] = "true"
    properties["dfs.block.access.token.enable"] = "false"
    properties["dfs.client.read.shortcircuit"] = "true"
    properties["dfs.block.local-path-access.user"] = "gpadmin"
    properties["dfs.datanode.data.dir.perm"] = 750
    properties["dfs.datanode.max.transfer.threads"] = 40960
    properties["dfs.datanode.handler.count"] = 60
    properties["dfs.namenode.accesstime.precision"] = 0
    desConfig["properties"] = properties
    desConfig["type"] = "hdfs-site"
    desConfig["tag"] = "hdb-updates"
    cluster["desired_config"] = desConfig
    config["Clusters"] = cluster
    configChange = requests.put(url, auth=auth, headers=headers, data=json.dumps(config))


def getProperties(hostName,auth,fileName,tag):
    print "GET PROPERTIES"
    url = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations?type="+fileName+"&tag="+tag
    fileInfo = requests.get(url, auth=auth)
    fileJSON = json.loads(fileInfo.text)

    return fileJSON["items"][0]["properties"]



def getConfigTag(hostName,auth,fileName):
    print "GET CONFIG TAG"
    url = "http://" + hostName +"/api/v1/clusters/Sandbox?fields=Clusters/desired_configs/" + fileName
    fileInfo = requests.get(url, auth=auth)
    fileJSON = json.loads(fileInfo.text)
    return fileJSON["Clusters"]["desired_configs"][fileName]["tag"]

def activateConfig(hostName,auth):
    print "ACTIVATE CONFIG"
    url = "http://" + hostName + "/api/v1/clusters/Sandbox/services/HDFS"
    headers = {"X-Requested-By": "HDB Installer"}
    stopPayload = '{"RequestInfo": {"context": "Stop HDFS"}, "Body": {"ServiceInfo": {"state": "INSTALLED","maintenance_state": "OFF"}}}'
    stopHDFS = requests.put(url, auth=auth, headers=headers, data=stopPayload)
    # NEED TO POLL FOR STOPPED SERVICE
    # Polling doesn't seem to work, so trying just a timer

    time.sleep(45)

    startPayload = '{"RequestInfo": {"context": "Start HDFS"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}'
    startHDFS = requests.put(url, auth=auth, headers=headers, data=startPayload)
    maintenancePayload = '{"RequestInfo": {"context": "Put HDFS in Maintenance Mode"}, "Body": {"ServiceInfo": {"state": "STARTED","maintenance_state": "ON"}}}'
    maintenanceMode = requests.put(url, auth=auth, headers=headers, data=maintenancePayload)


if __name__ == '__main__':
    hostName = "localhost:8080"
    auth = HTTPBasicAuth('admin', 'admin')
    os.system("ambari-server restart")
    time.sleep(120)

    hdfsSiteTag = getConfigTag(hostName,auth,"hdfs-site")
    coreSiteTag = getConfigTag(hostName,auth,"core-site")

    hdfsSiteProperties = getProperties(hostName,auth,"hdfs-site",hdfsSiteTag)
    coreSiteProperties = getProperties(hostName,auth,"core-site",coreSiteTag)

    modifyHdfsSiteConfig(hostName,auth,hdfsSiteTag,hdfsSiteProperties)
    modifyCoreSiteConfig(hostName,auth,coreSiteTag,coreSiteProperties)
    activateConfig(hostName,auth)

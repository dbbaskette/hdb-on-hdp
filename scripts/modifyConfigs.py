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


def modifyYarnSiteConfig(hostName,auth,tag,currentProperties):
    print "MODIFY YARN-SITE"
    url = "http://" + hostName + "/api/v1/clusters/Sandbox"
    headers = {"X-Requested-By": "HDB Installer"}
    properties = currentProperties
    desConfig = {}
    cluster = {}
    config = {}
    properties["yarn.scheduler.maximum-allocation-mb"] = 3076
    properties["yarn.scheduler.minimum-allocation-mb"] = 256
    properties["yarn.nodemanager.resource.memory-mb"] = 3076
    desConfig["properties"] = properties
    desConfig["type"] = "yarn-site"
    desConfig["tag"] = "hdb-updates"
    cluster["desired_config"] = desConfig
    config["Clusters"] = cluster
    configChange = requests.put(url, auth=auth, headers=headers, data=json.dumps(config))


def getProperties(hostName,auth,fileName,tag):
    url = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations?type="+fileName+"&tag="+tag
    fileInfo = requests.get(url, auth=auth)
    fileJSON = json.loads(fileInfo.text)
    return fileJSON["items"][0]["properties"]


def getConfigTag(hostName,auth,fileName):
    url = "http://" + hostName +"/api/v1/clusters/Sandbox?fields=Clusters/desired_configs/" + fileName
    fileInfo = requests.get(url, auth=auth)
    fileJSON = json.loads(fileInfo.text)
    return fileJSON["Clusters"]["desired_configs"][fileName]["tag"]

def activateConfig(hostName,auth):
    # STOP HDFS
    print "STOPPING HDFS"
    hdfsURL = "http://" + hostName + "/api/v1/clusters/Sandbox/services/HDFS"
    headers = {"X-Requested-By": "HDB Installer"}
    stoppedHDFS = False
    stopPayload = '{"RequestInfo": {"context": "Stop HDFS"}, "Body": {"ServiceInfo": {"state": "INSTALLED","maintenance_state": "OFF"}}}'
    stopHDFS = requests.put(hdfsURL, auth=auth, headers=headers, data=stopPayload)
    while not stoppedHDFS:
        time.sleep(5)
        response = requests.get(hdfsURL+"?fields=ServiceInfo/state",auth=auth)
        status = json.loads(response.text)["ServiceInfo"]["state"]
        if status in "INSTALLED":
            stoppedHDFS = True
    print "HDFS STOPPED"

    # STOP YARN
    print "STOPPING YARN"
    stoppedYARN = False
    yarnURL = "http://" + hostName + "/api/v1/clusters/Sandbox/services/YARN"
    headers = {"X-Requested-By": "HDB Installer"}
    stopPayload = '{"RequestInfo": {"context": "Stop YARN"}, "Body": {"ServiceInfo": {"state": "INSTALLED","maintenance_state": "OFF"}}}'
    stopYARN = requests.put(yarnURL, auth=auth, headers=headers, data=stopPayload)
    while not stoppedYARN:
        time.sleep(5)
        response = requests.get(yarnURL + "?fields=ServiceInfo/state", auth=auth)
        status = json.loads(response.text)["ServiceInfo"]["state"]
        if status in "INSTALLED":
            stoppedYARN = True
    print "YARN STOPPED"

    # START HDFS - WAIT UNTIL FINISHED STARTING
    print "STARTING HDFS"
    startedHDFS = False
    startPayload = '{"RequestInfo": {"context": "Start HDFS"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}'
    startHDFS = requests.put(hdfsURL, auth=auth, headers=headers, data=startPayload)
    startRequest = json.loads(startHDFS.text)
    startRequestURL = startRequest["href"]
    while not startedHDFS:
        time.sleep(5)
        response = requests.get(startRequestURL, auth=auth)
        status = json.loads(response.text)["Requests"]["request_status"]
        if status in "COMPLETED":
            startedHDFS = True

    maintenancePayload = '{"RequestInfo": {"context": "Put HDFS in Maintenance Mode"}, "Body": {"ServiceInfo": {"state": "STARTED","maintenance_state": "ON"}}}'
    maintenanceMode = requests.put(hdfsURL, auth=auth, headers=headers, data=maintenancePayload)
    print "HDFS STARTED"

    #START YARN - WAIT UNTIL FINISHED STARTING
    print "STARTING YARN"
    startPayload = '{"RequestInfo": {"context": "Start YARN"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}'
    startYARN = requests.put(yarnURL, auth=auth, headers=headers, data=startPayload)

    startedYARN = False
    while not startedYARN:
        time.sleep(5)
        response = requests.get(yarnURL + "?fields=ServiceInfo/state", auth=auth)
        status = json.loads(response.text)["ServiceInfo"]["state"]
        if status in "STARTED":
            startedYARN = True

    print "YARN STARTED"




if __name__ == '__main__':
    hostName = "localhost:8080"
    auth = HTTPBasicAuth('admin', 'admin')
    os.system("ambari-server restart")
    time.sleep(60)

    hdfsSiteTag = getConfigTag(hostName,auth,"hdfs-site")
    coreSiteTag = getConfigTag(hostName,auth,"core-site")
    yarnSiteTag = getConfigTag(hostName,auth,"yarn-site")


    hdfsSiteProperties = getProperties(hostName,auth,"hdfs-site",hdfsSiteTag)
    coreSiteProperties = getProperties(hostName,auth,"core-site",coreSiteTag)
    yarnSiteProperties = getProperties(hostName,auth,"yarn-site",yarnSiteTag)


    modifyHdfsSiteConfig(hostName,auth,hdfsSiteTag,hdfsSiteProperties)
    modifyCoreSiteConfig(hostName,auth,coreSiteTag,coreSiteProperties)
    modifyYarnSiteConfig(hostName,auth,yarnSiteTag,yarnSiteProperties)


    activateConfig(hostName,auth)

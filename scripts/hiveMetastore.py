import json
import sys
import requests
from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
import time






def stopHive(hostName,auth):


    print "STOPPING HIVE"
    stoppedHIVE = False
    hiveURL = "http://" + hostName + "/api/v1/clusters/Sandbox/services/HIVE"
    headers = {"X-Requested-By": "HDB Installer"}
    stopPayload = '{"RequestInfo": {"context": "Stop HIVE"}, "Body": {"ServiceInfo": {"state": "INSTALLED","maintenance_state": "OFF"}}}'
    stopHIVE = requests.put(hiveURL, auth=auth, headers=headers, data=stopPayload)
    while not stoppedHIVE:
        time.sleep(5)
        response = requests.get(hiveURL + "?fields=ServiceInfo/state", auth=auth)
        status = json.loads(response.text)["ServiceInfo"]["state"]
        if status in "INSTALLED":
            stoppedHIVE = True
    print "HIVE STOPPED"

def startHive(hostName,auth):

    print "STARTING HIVE"
    hiveURL = "http://" + hostName + "/api/v1/clusters/Sandbox/services/HIVE"
    headers = {"X-Requested-By": "HDB Installer"}
    startPayload = '{"RequestInfo": {"context": "Start HIVE"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}'
    startHIVE = requests.put(hiveURL, auth=auth, headers=headers, data=startPayload)

    startedHIVE = False
    while not startedHIVE:
        time.sleep(5)
        response = requests.get(hiveURL + "?fields=ServiceInfo/state", auth=auth)
        status = json.loads(response.text)["ServiceInfo"]["state"]
        if status in "STARTED":
            startedHIVE = True

    print "HIVE STARTED"

def getConfigTag(hostName,auth,fileName):
    url = "http://" + hostName +"/api/v1/clusters/Sandbox?fields=Clusters/desired_configs/" + fileName
    fileInfo = requests.get(url, auth=auth)
    print fileInfo.text
    fileJSON = json.loads(fileInfo.text)
    return fileJSON["Clusters"]["desired_configs"][fileName]["tag"]

def getProperties(hostName,auth,fileName,tag):
    url = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations?type="+fileName+"&tag="+tag
    fileInfo = requests.get(url, auth=auth)
    print fileInfo.text
    fileJSON = json.loads(fileInfo.text)
    return fileJSON["items"][0]["properties"]

def modifyHiveSiteConfig(hostName,auth,tag,currentProperties):

    print "MODIFY HIVE-SITE"
    url = "http://" + hostName + "/api/v1/clusters/Sandbox"
    headers = {"X-Requested-By": "HDB Installer"}
    properties = currentProperties
    desConfig = {}
    cluster = {}
    config = {}
    properties["hive_metastore_user_passwd"] = "hive"
    properties["javax.jdo.option.ConnectionDriverName"] = "org.postgresql.Driver"
    properties["javax.jdo.option.ConnectionURL"] = "jdbc:postgresql://sandbox.hortonworks.com:5432/hive"
    properties["javax.jdo.option.ConnectionUserName"] = "hive"

    desConfig["properties"] = properties
    desConfig["type"] = "hive-site"
    desConfig["tag"] = "hdb-updates"
    cluster["desired_config"] = desConfig
    config["Clusters"] = cluster
    configChange = requests.put(url, auth=auth, headers=headers, data=json.dumps(config))

def modifyHiveEnvConfig(hostName,auth,tag,currentProperties):

    print "MODIFY HIVE-ENV"
    url = "http://" + hostName + "/api/v1/clusters/Sandbox"
    headers = {"X-Requested-By": "HDB Installer"}
    properties = currentProperties
    desConfig = {}
    cluster = {}
    config = {}
    properties["hive_database_type"] = "postgres"
    properties["hive_ambari_database"] = "postgres"
    desConfig["properties"] = properties
    desConfig["type"] = "hive-env"
    desConfig["tag"] = "hdb-updates"
    cluster["desired_config"] = desConfig
    config["Clusters"] = cluster
    configChange = requests.put(url, auth=auth, headers=headers, data=json.dumps(config))


if __name__ == '__main__':
    hostName = "sandbox.hortonworks.com:8080"
    auth = HTTPBasicAuth('admin', 'admin')
    hiveSiteTag = getConfigTag(hostName,auth,"hive-site")
    hiveSiteProperties = getProperties(hostName, auth, "hive-site", hiveSiteTag)
    modifyHiveSiteConfig(hostName,auth,hiveSiteTag,hiveSiteProperties)
    hiveEnvTag = getConfigTag(hostName, auth, "hive-env")
    hiveEnvProperties = getProperties(hostName, auth, "hive-env", hiveEnvTag)
    modifyHiveEnvConfig(hostName, auth, hiveEnvTag, hiveEnvProperties)
    stopHive(hostName,auth)
    startHive(hostName,auth)
    print "HIVE METASTORE MOVE TO POSTGRESQL COMPLETE"
import json
import sys
import requests
from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
import time





def installHAWQ(hostName,auth):

#PUT -d '{"RequestInfo": {"context" :"Installing HAWQ via API"}, "Body": {"ServiceInfo": {"state" : "INSTALLED"}}}'  "http://localhost:8080/api/v1/clusters/Sandbox/services/HAWQ"
#PUT -d '{"RequestInfo": {"context" :"Installing PXF via API"}, "Body": {"ServiceInfo": {"state" : "INSTALLED"}}}'  "http://localhost:8080/api/v1/clusters/Sandbox/services/PXF"

    url = "http://" + hostName + "/api/v1/clusters/Sandbox/services"
    headers = {"X-Requested-By": "HDB Installer"}

    hawqPayload = '{"RequestInfo": {"context" :"Installing HAWQ via API"}, "Body": {"ServiceInfo": {"state" : "INSTALLED"}}}'
    pxfPayload = '{"RequestInfo": {"context" :"Installing PXF via API"}, "Body": {"ServiceInfo": {"state" : "INSTALLED"}}}'

    hawqInstall = requests.put(url+"/HAWQ",auth=auth,headers=headers,data = hawqPayload )
    print hawqInstall.text
    pxfInstall = requests.put(url+"/PXF",auth=auth,headers=headers,data = pxfPayload )
    print pxfInstall.text
    print "Pause for Install to Complete"
# REPLACE THESE PAUSES WITH ACTUAL POLLING
    time.sleep(360)




def startHAWQ(hostName,auth):
    print  "Start HAWQ to complete Install"
    #PUT - d '{"RequestInfo": {"context" :"Starting HAWQ via API"}, "Body": {"ServiceInfo": {"state" : "STARTED"}}}'  "http://localhost:8080/api/v1/clusters/Sandbox/services/HAWQ"
    #PUT -d '{"RequestInfo": {"context" :"Starting PXF via API"}, "Body": {"ServiceInfo": {"state" : "STARTED"}}}'  "http://localhost:8080/api/v1/clusters/Sandbox/services/PXF"
    headers = {"X-Requested-By": "HDB Installer"}

    hawqPayload = '{"RequestInfo": {"context" :"Starting HAWQ via API"}, "Body": {"ServiceInfo": {"state" : "STARTED"}}}'
    pxfPayload = '{"RequestInfo": {"context" :"Starting PXF via API"}, "Body": {"ServiceInfo": {"state" : "STARTED"}}}'

    url =  "http://localhost:8080/api/v1/clusters/Sandbox/services/"
    hawqStart =  requests.put(url+"/HAWQ",auth=auth,headers=headers,data = hawqPayload )
    pxfStart = requests.put(url + "/PXF", auth=auth, headers=headers, data=pxfPayload)
    print hawqStart.text
    print pxfStart.text
    print "Pause for Start to Complete"
    # REPLACE THESE PAUSES WITH ACTUAL POLLING

    time.sleep(360)



def addServices(hostName,auth):
#POST -d '{"ServiceInfo":{"service_name":"HAWQ"}}' "http://localhost:8080/api/v1/clusters/Sandbox/services"
#POST -d '{"ServiceInfo":{"service_name":"PXF"}}' "http://localhost:8080/api/v1/clusters/Sandbox/services"
    url = "http://" + hostName + "/api/v1/clusters/Sandbox/services"
    headers = {"X-Requested-By": "HDB Installer"}

    hawqPayload = '{"ServiceInfo":{"service_name":"HAWQ"}}'
    pxfPayload = '{"ServiceInfo":{"service_name":"PXF"}}'


    hawqService = requests.post(url, auth=auth, headers=headers, data=hawqPayload)
    pxfService = requests.post(url, auth=auth, headers=headers, data=pxfPayload)


def addComponentsToService(hostName,auth):

    # POST -d '{"host_components" : [{"HostRoles":{"component_name":"HAWQMASTER"}}] }' "http://localhost:8080/api/v1/clusters/Sandbox/hosts?Hosts/host_name=sandbox.hortonworks.com"
    # POST -d '{"host_components" : [{"HostRoles":{"component_name":"HAWQSEGMENT"}}] }' "http://localhost:8080/api/v1/clusters/Sandbox/hosts?Hosts/host_name=sandbox.hortonworks.com"
    # POST -d '{"host_components" : [{"HostRoles":{"component_name":"PXF"}}] }' "http://localhost:8080/api/v1/clusters/Sandbox/hosts?Hosts/host_name=sandbox.hortonworks.com"

    url = "http://" + hostName + "/api/v1/clusters/Sandbox/services"
    headers = {"X-Requested-By": "HDB Installer"}

    masterComponent = requests.post(url+"/HAWQ/components/HAWQMASTER", auth=auth, headers=headers)
    segmentComponent = requests.post(url + "/HAWQ/components/HAWQSEGMENT", auth=auth, headers=headers)
    pxfComponent = requests.post(url + "/PXF/components/PXF", auth=auth, headers=headers)

def modifyConfig(hostName,auth):

#PUT -d '{ "Clusters" : {"desired_config": {"type": "hawq-site", "tag" : "0" }}}'  "http://localhost:8080/api/v1/clusters/Sandbox"
#POST -d '{"type": "hawq-site", "tag": "1", "properties" : { "hawq.master.port" : 15432,"hawq.segments.per.node" : 1,"hawq.temp.directory" : "/data/hawq/temp"}}' "http://localhost:8080/api/v1/clusters/Sandbox/configurations"
#PUT -d '{ "Clusters" : {"desired_config": {"type": "hawq-site", "tag" : "1" }}}'  "http://localhost:8080/api/v1/clusters/Sandbox"
#http://192.168.9.131:8080/api/v1/stacks/HDP/versions/2.3/services/HAWQ/configurations?fields=*


    headers = {"X-Requested-By": "HDB Installer"}

    # Put New Empty Config

    hawqURL = "http://" + hostName + "/api/v1/clusters/Sandbox"
    payload = '{ "Clusters" : {"desired_config": {"type": "hawq-site", "tag" : "0" }}}'
    emptyConfig = requests.put(hawqURL,auth=auth,headers=headers,data = payload )
    payload = '{ "Clusters" : {"desired_config": {"type": "hawq-sysctl-env", "tag" : "0" }}}'
    emptyConfig = requests.put(hawqURL, auth=auth, headers=headers, data=payload)
    payload = '{ "Clusters" : {"desired_config": {"type": "hawq-limits-env", "tag" : "0" }}}'
    emptyConfig = requests.put(hawqURL, auth=auth, headers=headers, data=payload)
    payload = '{ "Clusters" : {"desired_config": {"type": "hawq-env", "tag" : "0" }}}'
    emptyConfig = requests.put(hawqURL, auth=auth, headers=headers, data=payload)

    #PUT PXF EMPTY CONFIGS

    payload = '{ "Clusters" : {"desired_config": {"type": "pxf-profiles", "tag" : "0" }}}'
    emptyConfig = requests.put(hawqURL, auth=auth, headers=headers, data=payload)
    payload = '{ "Clusters" : {"desired_config": {"type": "pxf-public-classpath", "tag" : "0" }}}'
    emptyConfig = requests.put(hawqURL, auth=auth, headers=headers, data=payload)
    payload = '{ "Clusters" : {"desired_config": {"type": "pxf-site", "tag" : "0" }}}'
    emptyConfig = requests.put(hawqURL, auth=auth, headers=headers, data=payload)



    # Process Defaults into new Configs - This results in multiple sets that need to be processed.

    hawqURL = "http://" + hostName + "/api/v1/stacks/HDP/versions/2.4/services/HAWQ/configurations?fields=*"
    pxfURL = "http://" + hostName + "/api/v1/stacks/HDP/versions/2.4/services/PXG/configurations?fields=*"

    hawqDefaults = requests.get(hawqURL,auth=auth, headers=headers)
    pxfDefaults = requests.get(pxfURL,auth=auth, headers=headers)



    hawqJSON = json.loads(hawqDefaults.text)
    hawqSite = {}
    hawqSysCtl = {}
    hawqLimits = {}
    hawqEnv = {}
    hdfsClient = {}
    yarnClient = {}
    gpCheck = {}

    for item in hawqJSON["items"]:
        if item["StackConfigurations"]["type"] in "hawq-site.xml":
            hawqSite[item["StackConfigurations"]["property_name"]] = item["StackConfigurations"]["property_value"]
            hawqSite["hawq_master_address_host"] =  "sandbox.hortonworks.com"
            #hawqSite["hawq_standby_address_host"] =  "sandbox.hortonworks.com"
            hawqSite["hawq_dfs_url"] = "sandbox.hortonworks.com:8020/hawq_default"
            hawqSite["hawq_master_address_port"] = 10432
            hawqSite["hawq_global_rm_type"] = "yarn"
            hawqSite["hawq_rm_yarn_address"] = "sandbox.hortonworks.com:8050"
            hawqSite["hawq_rm_yarn_scheduler_address"] = "sandbox.hortonworks.com:8030"
            hawqSite["hawq_password"] = "gpadmin"
        if item["StackConfigurations"]["type"] in "hawq-sysctl-env.xml":
            hawqSysCtl[item["StackConfigurations"]["property_name"]] = item["StackConfigurations"]["property_value"]
        if item["StackConfigurations"]["type"] in "hawq-limits-env.xml":
            hawqLimits[item["StackConfigurations"]["property_name"]] = item["StackConfigurations"]["property_value"]
        if item["StackConfigurations"]["type"] in "hawq-env.xml":
            hawqEnv[item["StackConfigurations"]["property_name"]] = item["StackConfigurations"]["property_value"]
            hawqEnv["hawq_password"]="gpadmin"
        if item["StackConfigurations"]["type"] in "hdfs-client.xml":
            hdfsClient[item["StackConfigurations"]["property_name"]] = item["StackConfigurations"]["property_value"]
        if item["StackConfigurations"]["type"] in "yarn-client.xml":
            yarnClient[item["StackConfigurations"]["property_name"]] = item["StackConfigurations"]["property_value"]
        if item["StackConfigurations"]["type"] in "gpcheck-env.xml":
            gpCheck[item["StackConfigurations"]["property_name"]] = item["StackConfigurations"]["property_value"]


    pxfJSON = json.loads(pxfDefaults.text)
    pxfProfiles = {}
    pxfClasspath = {}
    pxfSite = {}

    for item in pxfJSON["items"]:
        if item["StackConfigurations"]["type"] in "pxf-profiles.xml":
            pxfProfiles[item["StackConfigurations"]["property_name"]] = item["StackConfigurations"]["property_value"]
        if item["StackConfigurations"]["type"] in "pxf-public-classpath.xml":
            pxfClasspath[item["StackConfigurations"]["property_name"]] = item["StackConfigurations"]["property_value"]
        if item["StackConfigurations"]["type"] in "pxf-site.xml":
            pxfSite[item["StackConfigurations"]["property_name"]] = item["StackConfigurations"]["property_value"]

    desired = {}
    config = {}
    cluster = {}
    activateURL = "http://" + hostName + "/api/v1/clusters/Sandbox"
    desConfig={}


    config["properties"] = hawqSite
    config["type"] = "hawq-site"
    config["tag"] = "hawq-updates"
    desired["desired_config"] = config
    configURL = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations"
    configBuild = requests.post(configURL,auth=auth,headers=headers,data=json.dumps(config))
    #desConfig = '{ "Clusters" : {"desired_config": {"type": "hawq-site", "tag" : "hawq-updates" }}}'
    desConfig["Clusters"] = desired
    del config["properties"]
    configActivate = requests.put(activateURL,auth=auth,headers=headers,data=json.dumps(desConfig))

    config["properties"] = hawqSysCtl
    config["type"] = "hawq-sysctl-env"
    config["tag"] = "hawq-updates"
    desired["desired_config"] = config
    configURL = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations"
    configBuild = requests.post(configURL, auth=auth, headers=headers, data=json.dumps(config))
    # desConfig = '{ "Clusters" : {"desired_config": {"type": "hawq-site", "tag" : "hawq-updates" }}}'
    desConfig["Clusters"] = desired
    del config["properties"]
    configActivate = requests.put(activateURL, auth=auth, headers=headers, data=json.dumps(desConfig))


    config["properties"] = hawqLimits
    config["type"] = "hawq-limits-env"
    config["tag"] = "hawq-updates"
    desired["desired_config"] = config
    configURL = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations"
    configBuild = requests.post(configURL, auth=auth, headers=headers, data=json.dumps(config))
    # desConfig = '{ "Clusters" : {"desired_config": {"type": "hawq-site", "tag" : "hawq-updates" }}}'
    desConfig["Clusters"] = desired
    del config["properties"]
    configActivate = requests.put(activateURL, auth=auth, headers=headers, data=json.dumps(desConfig))


    config["properties"] = hawqEnv
    config["type"] = "hawq-env"
    config["tag"] = "hawq-updates"
    desired["desired_config"] = config
    configURL = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations"
    configBuild = requests.post(configURL, auth=auth, headers=headers, data=json.dumps(config))
    desConfig["Clusters"] = desired
    del config["properties"]
    configActivate = requests.put(activateURL, auth=auth, headers=headers, data=json.dumps(desConfig))

    config["properties"] = hdfsClient
    config["type"] = "hdfs-client"
    config["tag"] = "hawq-updates"
    desired["desired_config"] = config
    configURL = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations"
    configBuild = requests.post(configURL, auth=auth, headers=headers, data=json.dumps(config))
    desConfig["Clusters"] = desired
    del config["properties"]
    configActivate = requests.put(activateURL, auth=auth, headers=headers, data=json.dumps(desConfig))

    config["properties"] = yarnClient
    config["type"] = "yarn-client"
    config["tag"] = "hawq-updates"
    desired["desired_config"] = config
    configURL = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations"
    configBuild = requests.post(configURL, auth=auth, headers=headers, data=json.dumps(config))
    desConfig["Clusters"] = desired
    del config["properties"]
    configActivate = requests.put(activateURL, auth=auth, headers=headers, data=json.dumps(desConfig))

    config["properties"] = gpCheck
    config["type"] = "gpcheck-env"
    config["tag"] = "hawq-updates"
    desired["desired_config"] = config
    configURL = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations"
    configBuild = requests.post(configURL, auth=auth, headers=headers, data=json.dumps(config))
    desConfig["Clusters"] = desired
    del config["properties"]
    configActivate = requests.put(activateURL, auth=auth, headers=headers, data=json.dumps(desConfig))

    config["properties"] = pxfProfiles
    config["type"] = "pxf-profiles"
    config["tag"] = "pxf-updates"
    desired["desired_config"] = config
    configURL = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations"
    configBuild = requests.post(configURL, auth=auth, headers=headers, data=json.dumps(config))
    desConfig["Clusters"] = desired
    del config["properties"]
    configActivate = requests.put(activateURL, auth=auth, headers=headers, data=json.dumps(desConfig))


    config["properties"] = pxfClasspath
    config["type"] = "pxf-public-classpath"
    config["tag"] = "pxf-updates"
    desired["desired_config"] = config
    configURL = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations"
    configBuild = requests.post(configURL, auth=auth, headers=headers, data=json.dumps(config))
    desConfig["Clusters"] = desired
    del config["properties"]
    configActivate = requests.put(activateURL, auth=auth, headers=headers, data=json.dumps(desConfig))

    config["properties"] = pxfSite
    config["type"] = "pxf-site"
    config["tag"] = "pxf-updates"
    desired["desired_config"] = config
    configURL = "http://" + hostName + "/api/v1/clusters/Sandbox/configurations"
    configBuild = requests.post(configURL, auth=auth, headers=headers, data=json.dumps(config))
    desConfig["Clusters"] = desired
    del config["properties"]
    configActivate = requests.put(activateURL, auth=auth, headers=headers, data=json.dumps(desConfig))



def createHostComponents(hostName,auth):
    masterMap = '{"host_components" : [{"HostRoles":{"component_name":"HAWQMASTER"}}] }'
    segmentMap = '{"host_components" : [{"HostRoles":{"component_name":"HAWQSEGMENT"}}] }'
    pxfMap = '{"host_components" : [{"HostRoles":{"component_name":"PXF"}}] }'

    url = "http://localhost:8080/api/v1/clusters/Sandbox/hosts?Hosts/host_name=sandbox.hortonworks.com"
    headers = {"X-Requested-By": "HDB Installer"}

    masterMapComponent = requests.post(url, auth=auth, headers=headers, data=masterMap)
    segementMapComponent = requests.post(url, auth=auth, headers=headers, data=segmentMap)
    pxfMapComponent = requests.post(url, auth=auth, headers=headers, data=pxfMap)


if __name__ == '__main__':
    hostName = "sandbox.hortonworks.com:8080"
    auth = HTTPBasicAuth('admin', 'admin')
    addServices(hostName,auth)
    addComponentsToService(hostName, auth)
    #getProperties(hostName,auth,"hawq-site")
    modifyConfig(hostName,auth)
    createHostComponents(hostName, auth)
    installHAWQ(hostName,auth)
    startHAWQ(hostName,auth)

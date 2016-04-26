import json
import sys
import requests
from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
import time






def removeOOZIE(hostName,auth):

#PUT -d '{"RequestInfo": {"context" :"Installing HAWQ via API"}, "Body": {"ServiceInfo": {"state" : "INSTALLED"}}}'  "http://localhost:8080/api/v1/clusters/Sandbox/services/HAWQ"
#PUT -d '{"RequestInfo": {"context" :"Installing PXF via API"}, "Body": {"ServiceInfo": {"state" : "INSTALLED"}}}'  "http://localhost:8080/api/v1/clusters/Sandbox/services/PXF"

#curl -u admin:admin -H "X-Requested-By: ambari" -X PUT -d '{"RequestInfo":{"context":"Stop Service"},"Body":{"ServiceInfo":{"state":"INSTALLED"}}}' "http://localhost:8080/api/v1/clusters/Sandbox/services/OOZIE"


    print "STOPPING OOZIE"
    stoppedOOZIE = False
    oozieURL = "http://" + hostName + "/api/v1/clusters/Sandbox/services/OOZIE"
    headers = {"X-Requested-By": "HDB Installer"}
    stopPayload = '{"RequestInfo": {"context": "Stop OOZIE"}, "Body": {"ServiceInfo": {"state": "INSTALLED","maintenance_state": "OFF"}}}'
    stopOOZIE = requests.put(oozieURL, auth=auth, headers=headers, data=stopPayload)
    while not stoppedOOZIE:
        time.sleep(5)
        response = requests.get(oozieURL + "?fields=ServiceInfo/state", auth=auth)
        status = json.loads(response.text)["ServiceInfo"]["state"]
        if status in "INSTALLED":
            stoppedOOZIE = True
    print "OOZE STOPPED"

#-H "X-Requested-By: ambari" -X DELETE "http://localhost:8080/api/v1/clusters/Sandbox/services/OOZIE"
    print "REMOVING OOZIE"
    url = "http://" + hostName + "/api/v1/clusters/Sandbox/services/OOZIE"
    headers = {"X-Requested-By": "HDB Installer"}
    oozieDelete = requests.delete(url, auth=auth, headers=headers)
    print "OOZIE DELETED"








if __name__ == '__main__':
    hostName = "sandbox.hortonworks.com:8080"
    auth = HTTPBasicAuth('admin', 'admin')
    removeOOZIE(hostName,auth)

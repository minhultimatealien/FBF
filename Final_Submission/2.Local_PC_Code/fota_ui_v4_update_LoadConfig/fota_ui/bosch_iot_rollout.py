import requests
import json
from requests_kerberos import HTTPKerberosAuth
from urllib3.util import parse_url
import hashlib
import os

class HTTPAdapterWithProxyKerberosAuth(requests.adapters.HTTPAdapter):
    def proxy_headers(self, proxy):
        headers = {}
        auth = HTTPKerberosAuth()
        negotiate_details = auth.generate_request_header(None, parse_url(proxy).host, is_preemptive=True)
        headers['Proxy-Authorization'] = negotiate_details
        return headers

class Server:
    def __init__(self):
        self.proxy_port = '8080'
        self.proxy_ip = 'rb-proxy-de.bosch.com'
        self.session_start()

        self.tenant_id = "70658C59-820F-49A3-9F41-6043C628F788"
        self.username = "bb538793-7a94-436b-b19c-d35212cc154a"
        self.password = "38367083-22fe-40bb-bd42-08b68cdbc7e6"
        self.hostname = "api.eu1.bosch-iot-rollouts.com"
        self.auth_br = "70658C59-820F-49A3-9F41-6043C628F788\\bb538793-7a94-436b-b19c-d35212cc154a"
        self.controller_id = "device_rasp_nmu3hc_fbf"

        self.sm_id=""
        self.ds_id=""
        self.action_ID = ""
        self.lastFeedBack = ""

    def session_start(self):
        self.session = requests.Session()
        self.session.proxies = {"http":f'{self.proxy_ip}:{self.proxy_port}', "https":f'{self.proxy_ip}:{self.proxy_port}'}
        self.session.mount('http://', HTTPAdapterWithProxyKerberosAuth())
        self.session.mount('https://', HTTPAdapterWithProxyKerberosAuth())
    
    def create_software_module(self, vendor:str, name:str, description:str, type:str, version:str)->str:
        """
        Function to request Bosch IoT Rollout

        :vendor     : Name of software vendor.         Ex: xx69420 Ltd.
        :name       : Name of software.                Ex: SAIC_ZP22_CB_BSS01
        :description: Software description.            Ex: Hello World!!
        :type       : Bosch IoT rollout software type. Ex: application
        :version    : Software version.                Ex: 1.0.69.420
        :return     : Return a sentence describing request result
        """ 
        auth = (self.auth_br, self.password)
        url = "https://"+ self.hostname+ "/rest/v1/softwaremodules"
        header = {"Content-Type": "application/json", "charset":"UTF-8"}
        data = [
            {
                'vendor': vendor,
                'name': name,
                'description': description,
                'type': type,
                'version': version,
            },
        ]

        response = self.session.post(url, auth=auth, headers=header, json=data)
        
        if response.status_code == 201:
            self.sm_id = str(json.loads(response.text)[0]["id"])
            return "Software module {} created with ID {}".format(name,self.sm_id)
        else:
            return "Can't create new software module due to error {}: {}".format(response.status_code,response.text)
    def create_swmd_metadata(self, diagReqId:str,diagResID:str,timeout:int,pendingTimeout:int,flash:str,block:str)->str:
        """
        Function to request Bosch IoT Rollout

        :diagReqId       : Diag frame request ID.           Ex: 0x7DF
        :diagResID       : Diag frame response ID.          Ex: 0x7E8
        :timeout         : Timeout of diagframe.            Ex: 1000 (ms)
        :pendingTimeout  : Timeout of Diag response.        Ex: 1000 (ms)
        :flash           : Opt                              Ex: Opt
        :block           : block for flashing               Ex: CB
        :return     : Return a sentence describing request result
        """
        auth = (self.auth_br, self.password)
        url = "https://" + self.hostname+ "/rest/v1/softwaremodules/" + self.sm_id + "/metadata"
        header = {"Content-Type": "application/hal+json"}
        data = [
            {
                "targetVisible" : True,
                "value" : diagReqId,
                "key" : "diagReqId"
            },
            {
                "targetVisible" : True,
                "value" : diagResID,
                "key" : "diagResID"
            },
            {
                "targetVisible" : True,
                "value" : timeout,
                "key" : "timeout"
            },
            {
                "targetVisible" : True,
                "value" : pendingTimeout,
                "key" : "pendingTimeout"
            },
            {
                "targetVisible" : True,
                "value" : flash,
                "key" : "flash"
            },
            {
                "targetVisible" : True,
                "value" : block,
                "key" : "block"
            },
        ]

        response = self.session.post(url, auth=auth, headers=header, json=data)
        
        if response.status_code == 201:
            return "Software module metadata updated:\n"
        else:
            return "Can't create new software module due to error {}: {}".format(response.status_code,response.text)
    def create_upload_artifact(self, file_path:str)->str:
        """
        Function to request Bosch IoT Rollout

        :file_path  : Name of software.                Ex: SAIC_ZP22_CB_BSS01
        :return     : Return a sentence describing request result
        """ 
        auth = (self.auth_br, self.password)
        url = "https://" + self.hostname+ "/rest/v1/softwaremodules/" + self.sm_id + "/artifacts"
        header = {}
        # print(file_path)
        try:
            md5Hash = hashlib.md5()
            sha1Hash = hashlib.sha1()
            with open(file_path, 'rb') as f: 
                fb = f.read(65536) 
                while len(fb) > 0: 
                    md5Hash.update(fb)
                    sha1Hash.update(fb)
                    fb = f.read(65536) # Read the next block from the file
            files = {
                'file': open(file_path, 'rb'),
            }
            md5Hashed = md5Hash.hexdigest()
            sha1Hashed = sha1Hash.hexdigest()
        except IOError:
            # print(file_path)
            return ("Could not read software hex file")

        response = self.session.post(url, auth=auth, headers=header, files=files)

        if response.status_code == 201:
            res_md5 = json.loads(response.text)["hashes"]["md5"]
            res_sha = json.loads(response.text)["hashes"]["sha1"]
            name = json.loads(response.text)["providedFilename"]
            if (res_md5 == md5Hashed and res_sha == sha1Hashed):
                return "Software uploaded.".format(name)
            else:
                return "Software upload failed. Hash ID mismatched"
        else:
            return "Can't upload software to cloud due to error {}: {}".format(response.status_code,response.text)
    def create_distribution_set(self, name:str, description:str, type:str, version:str, requiredMigrationStep:bool=False)->str:
        """
        Function to request Bosch IoT Rollout

        :requiredMigrationStep     : True if this DS is prequisite for another DS Default to False.         Ex: xx69420 Ltd.
        :name                      : Name of DS.                      Ex: SAIC_ZP22_CB_BSS01
        :description               : DS description.                  Ex: Hello World!!
        :type                      : Bosch IoT rollout DS type.       Ex: application
        :version                   : DS version.                      Ex: 1.0.69.420
        :return                    : Return a sentence describing request result
        """ 
        auth = (self.auth_br, self.password)
        url = "https://"+ self.hostname+ "/rest/v1/distributionsets"
        header = {"Content-Type": "application/json", "charset":"UTF-8"}
        data = [
            {
                'requiredMigrationStep': requiredMigrationStep,
                'name': name,
                'description': description,
                'type': type,
                'version': version,
                "modules": [
                    {
                    "id": self.sm_id
                    }
                ]
            }
        ]

        response = self.session.post(url, auth=auth, headers=header, json=data)
        
        if response.status_code == 201:
            self.ds_id = str(json.loads(response.text)[0]["id"])
            return "DS {} created with ID {}".format(name,self.ds_id)
        else:
            return "Can't create new DS due to error {}: {}".format(response.status_code,response.text)

    def create_rollout_request(self)->str:
        """
        Function to request Bosch IoT Rollout

        :id                        : device controller ID                           Ex: device_rasp_nmu3hc_fbf
        :type                      : Is it a forced rollout? default to "forced"    Ex: forced
        :return                    : Return a sentence describing request result
        """ 
        auth = (self.auth_br, self.password)
        url = "https://"+ self.hostname+ "/rest/v1/distributionsets/"+self.ds_id+"/assignedTargets/"
        header = {"Content-Type": "application/json", "charset":"UTF-8"}
        data = [
            {
                'id': self.controller_id,
                'type': 'forced',
            }
        ]

        response = self.session.post(url, auth=auth, headers=header, json=data)
        
        if response.status_code == 200:
            self.action_ID = str(json.loads(response.text)["assignedActions"][0]["id"])
            return "Created rollout request, waiing for flashing done on {}".format(self.controller_id)
        else:
            return "Can't create rollout request {}: {}".format(response.status_code,response.text)
    def get_current_status(self)->str:
        """
        Function to request Bosch IoT Rollout

        :return                    : Return a sentence describing request result
        """ 
        auth = (self.auth_br, self.password)
        url = "https://"+ self.hostname+ "/rest/v1/actions/"+self.action_ID

        response = self.session.get(url, auth=auth)
        
        if response.status_code == 200:
            try:
                status_code = json.loads(response.text)["lastStatusCode"]
                # print(json.loads(response.text)["lastStatusCode"])
                feedback = ""
                if (status_code in range(0,101)):
                    feedback = "Flashing on device progress {} %".format(status_code)
                elif (status_code == 200):
                    feedback = "Triggering Raspberry for update"
                elif (status_code == 201):
                    feedback = "Flashing Done"
                elif (status_code == 202):
                    feedback = "Software received on local Raspberry"
                elif (status_code == 203):
                    feedback = "Canceled previous install software"
                elif (status_code == 204 or status_code == 205):
                    feedback = "Error downloading software on Raspberry"
                # elif (status_code in [])
                if not feedback == self.lastFeedBack:
                    # print(feedback)
                    self.lastFeedBack = feedback
                    return feedback
                else: 
                    return ""
            except KeyError:
                return ""
        else:
            return ""


        

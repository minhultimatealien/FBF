import requests
import json
import hashlib
import os
import time
    
class Target:
    def __init__(self):
        self.tenant_id = "70658C59-820F-49A3-9F41-6043C628F788"
        self.hostname = "device.eu1.bosch-iot-rollouts.com"
        self.controller_id = "device_rasp_nmu3hc_fbf"
        self.token = "a42d9fa0a89dbbed2a95dfad4ad09d4f"
        self.update_link = ""
        self.download_link = ""
        self.metadata ={}
        self.filename = ""
        self.filepath = ""
        self.dep_id = ""
    def create_polling_request(self)->str:
        """
        Function to request Bosch IoT Rollout

        :return     : Return a sentence describing request result
        """ 
    
        url = "https://"+ self.hostname + "/" + self.tenant_id + "/controller/v1/"+self.controller_id
        header = {
            'Accept': 'application/hal+json',
            'Authorization': 'TargetToken ' + self.token,
        }

        response = requests.get(url, headers=header)
        
        if response.status_code == 200:
            # print(json.loads(response.text))
            json_data = json.loads(response.text)["_links"]
            if "deploymentBase" in json_data:
                self.update_link = json_data["deploymentBase"]["href"]
                return "Update action received"
            elif "cancelAction" in json_data:
                self.update_link = json_data["cancelAction"]["href"]
                return "Update cancelled"
            return "No new update"
        else:
            return "Can't request polling"
        
    def get_software_update(self)->str:
        """
        Function to request Bosch IoT Rollout

        :return     : Return a sentence describing request result
        """ 
    
        url = self.update_link
        header = {
            'Accept': 'application/hal+json',
            'Authorization': 'TargetToken ' + self.token,
        }

        response = requests.get(url, headers=header)
        
        if response.status_code == 200:
            json_data = json.loads(response.text)
            # print(json_data)
            self.hashes = json_data["deployment"]["chunks"][0]["artifacts"][0]["hashes"]
            self.download_link = json_data["deployment"]["chunks"][0]["artifacts"][0]["_links"]["download"]["href"]
            self.filename = json_data["deployment"]["chunks"][0]["artifacts"][0]["filename"]
            self.dep_id = json_data["id"]
            metadata = json_data["deployment"]["chunks"][0]["metadata"]
            for kv_pair in metadata:
                self.metadata[kv_pair["key"]] = kv_pair["value"]
            return "Software information gotten."
        else:
            return "Can't request polling"
    def download_software_update(self)->str:
        """
        Function to request Bosch IoT Rollout

        :return     : Return a sentence describing request result
        """ 
    
        url = self.download_link
        header = {
            'Accept': 'application/hal+json',
            'Authorization': 'TargetToken ' + self.token,
        }

        response = requests.get(url, headers=header)
        
        md5Hash = hashlib.md5()
        sha1Hash = hashlib.sha1()
        sha256Hash = hashlib.sha256()
        for byte in response:
            md5Hash.update(byte)
            sha1Hash.update(byte)
            sha256Hash.update(byte)
        md5Hashed = md5Hash.hexdigest()
        sha1Hashed = sha1Hash.hexdigest()
        sha256Hashed = sha256Hash.hexdigest()

        if (md5Hashed == self.hashes["md5"] and sha1Hashed == self.hashes["sha1"] and sha256Hashed == self.hashes["sha256"]):
            filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)),self.filename)
            open(filepath, "wb").write(response.content)
            self.filepath = filepath
            return "Downloaded successfully software {}".format(self.filename)
        else:
            return "File was not downloaded properly"
    def create_feedback(self, execution:str, result:str, status:int)->str:
        """
        Function to request Bosch IoT Rollout

        :excution   : Current action (closed / proceeding / download / downloaded / cancel / scheduled / rejected / resume)
        :result     : Result of action (success / failure / none)
        :return     : Return a sentence describing request result
        """ 
    
        url = "https://"+ self.hostname + "/" + self.tenant_id + "/controller/v1/"+self.controller_id + "/deploymentBase/" + self.dep_id + "/feedback"
        header = {
            'Accept': 'application/hal+json',
            'Authorization': 'TargetToken ' + self.token,
        }

        data = {
            'time': time.strftime("%d/%m/%y at %I:%M%p"),
            'status': {
                'execution': execution,
                'result': {
                    'finished': result,
                },
                'code': str(status),
                'details': [
                    'Successfully download software',
                ],
            },
        }
        response = requests.post(url, headers=header, json=data)
        
        if response.status_code == 200:
            pass
        else:
            return "Can't create feedback {}:".format(response.status_code) 


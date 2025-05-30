from bosch_iot_rollout import *
import time

cloud = Server()

def request_update_software(ui,filepath:str,diagReqId="0x7DF",diagResID="0x7E8",timeout=1000,pendingTimeout=1000,flash="All",block="CB"):  
    random_time = str(int(time.time()))
    ui.DebugtextBrowser.append(cloud.create_software_module("5ting inc","Software_"+random_time,"Update software","application","1.0"))
    ui.DebugtextBrowser.append(cloud.create_upload_artifact(filepath))
    ui.DebugtextBrowser.append(cloud.create_distribution_set("DS_"+random_time,"New Distribution set","app","1.0",False))
    ui.DebugtextBrowser.append(cloud.create_swmd_metadata(diagReqId,diagResID,timeout,pendingTimeout,flash,block))
    ui.DebugtextBrowser.append(cloud.create_rollout_request())
    
def get_client_feedback(ui):
    while True:
        # ui.DebugtextBrowser.append(cloud.get_current_status())
        # print(cloud.get_current_status())
        response = cloud.get_current_status()
        if not response == "":
            ui.DebugtextBrowser.append(response)
        if ("Error" in response or response == "Flashing Done"):
            break
        time.sleep(0.5)

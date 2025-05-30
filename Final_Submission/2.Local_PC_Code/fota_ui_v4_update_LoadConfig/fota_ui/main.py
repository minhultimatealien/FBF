import sys
import typing
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog
from PyQt5.uic import loadUi
from request_update import *
from threading import *

import configparser
import os.path


my_path = os.path.abspath(os.path.dirname(__file__))
configPath = os.path.join(my_path, 'gui\configWindow_widget_v3.ui')
startPath = os.path.join(my_path, 'gui\StartWindow_widget_v4.ui')

# initialize default value of Input data 
# data can accessed here

timeout = "1000"
diagReqID = "0x7E0"
diagResID  = "0x7E8"
flash =""
opt =""
block =""

all_mem_Stat = True       # TRUE if all hex file to be flashed 
option_mem_stat = False   
CB_stat = False           # TRUE if CB to be flashed
ASW2_stat = False         # TRUE if ASW2 to be flashed
DS0_stat = False          # TRUE if DS0 to be flashed
VDS_stat = False          # TRUE if VDS to be flashed
ASW0_stat = False         # TRUE if ASW0 to be flashed
ASW1_stat = False         # TRUE if ASW1 to be flashed

hexfilePath=""            # direction to hex file

class configWindow(QWidget):
    def __init__(self):
        super(configWindow, self).__init__()
        self.w = None  # No external window yet.
        loadUi(configPath, self)
        # set input default 
        self.in_timeout.setText(timeout)
        self.In_DiagReq.setText(diagReqID)
        self.In_DiagRes.setText(diagResID)
        
        self.NextBtn.clicked.connect(self.changetoStartWindow)
        self.LoadConfigBtn.clicked.connect(self.loadInifile)
        self.saveBtn.clicked.connect(self.save)
        
        self.flashAllBtn.setChecked(all_mem_Stat)
        self.flashOprionBtn.setChecked(option_mem_stat)
        
        self.CBcheckBox.setChecked(CB_stat)
        self.ASWEcheckBox.setChecked(ASW2_stat)
        self.DS0checkBox.setChecked(DS0_stat)
        self.vdscheckBox.setChecked(VDS_stat)
        self.ASW0checkBox.setChecked(ASW0_stat)
        self.ASW1checkBox.setChecked(ASW1_stat)
        
        if  all_mem_Stat:
            self.CBcheckBox.setCheckable(False)
            self.ASWEcheckBox.setCheckable(False)
            self.DS0checkBox.setCheckable(False)
            self.vdscheckBox.setCheckable(False)
            self.ASW0checkBox.setCheckable(False)
            self.ASW1checkBox.setCheckable(False)
        
        self.flashAllBtn.clicked.connect(self.FlashAll)
        self.flashOprionBtn.clicked.connect(self.FlashOpt)
    def changetoStartWindow(self):
        # saving configuration
        # covert from string can create err if string is empty 

        global timeout,diagReqID, diagResID, startAdd, endAdd
        global all_mem_Stat, CB_stat, ASW2_stat, DS0_stat, VDS_stat, ASW0_stat, ASW1_stat
    
        timeout = self.in_timeout.text()
        diagReqID = self.In_DiagReq.text()
        diagResID  = self.In_DiagRes.text()
        print("information: timeout {timeout}, diagReq {diagReq}".format(timeout=timeout, diagReq = diagReqID) )
        
        all_mem_Stat = self.flashAllBtn.isChecked()
        CB_stat = self.CBcheckBox.isChecked()
        ASW2_stat = self.ASWEcheckBox.isChecked()
        DS0_stat = self.DS0checkBox.isChecked()
        VDS_stat = self.vdscheckBox.isChecked()
        ASW0_stat = self.ASW0checkBox.isChecked()
        ASW1_stat = self.ASW1checkBox.isChecked()
        
        if self.w is None:
            self.w=StartWindow()
            self.w.show()
            self.hide()
        else:
            self.w.close()  # Close window.
            self.w = None  # Discard referenc
            
    def FlashAll(self):
        global all_mem_Stat, option_mem_stat, CB_stat, ASW2_stat, DS0_stat, VDS_stat, ASW0_stat, ASW1_stat
        
        if self.flashAllBtn.isChecked():
            all_mem_Stat = True
            option_mem_stat = False
            
            CB_stat = False
            ASW2_stat = False
            DS0_stat = False
            VDS_stat = False
            ASW0_stat = False
            ASW1_stat = False
            
            self.CBcheckBox.setChecked(CB_stat)
            self.ASWEcheckBox.setChecked(ASW2_stat)
            self.DS0checkBox.setChecked(DS0_stat)
            self.vdscheckBox.setChecked(VDS_stat)
            self.ASW0checkBox.setChecked(ASW0_stat)
            self.ASW1checkBox.setChecked(ASW1_stat)
            
            self.CBcheckBox.setCheckable(False)
            self.ASWEcheckBox.setCheckable(False)
            self.DS0checkBox.setCheckable(False)
            self.vdscheckBox.setCheckable(False)
            self.ASW0checkBox.setCheckable(False)
            self.ASW1checkBox.setCheckable(False)
            
        else:
            all_mem_Stat = False
            option_mem_stat = True
            self.CBcheckBox.setCheckable(True)
            self.ASWEcheckBox.setCheckable(True)
            self.DS0checkBox.setCheckable(True)
            self.vdscheckBox.setCheckable(True)
            self.ASW0checkBox.setCheckable(True)
            self.ASW1checkBox.setCheckable(True)
            
    def FlashOpt(self):
        global all_mem_Stat, option_mem_stat
        
        if self.flashOprionBtn.isChecked():
            all_mem_Stat = False
            option_mem_stat = True

            self.CBcheckBox.setCheckable(True)
            self.CBcheckBox.setCheckable(True)
            self.ASWEcheckBox.setCheckable(True)
            self.DS0checkBox.setCheckable(True)
            self.vdscheckBox.setCheckable(True)
            self.ASW0checkBox.setCheckable(True)
            self.ASW1checkBox.setCheckable(True)
            
    
    def save(self):
        
        ###################
        # DONE
        ###################
        
        # saving configuration
        global timeout, diagReqID, diagResID

        timeout = self.in_timeout.text()
        diagReqID = self.In_DiagReq.text()
        diagResID  = self.In_DiagRes.text()
        
        config = configparser.ConfigParser()
        
        config['ID'] = {}
        config['ID']['diagReqID'] = diagReqID
        config['ID']['diagResID'] = diagResID
        
        config['TIMEOUT']={}
        config['TIMEOUT']['timeout'] = timeout
        
        try:
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
                print("config saved")
        except Exception as bug:
            print(bug)
        
    def loadInifile(self):
        
        ###################
        # DONE
        ###################
        try: 
            global timeout, diagReqID, diagResID
            
            fname=QFileDialog.getOpenFileName(self, 'open file', my_path)
            configfilePath = fname[0]
            config = configparser.ConfigParser()

            config.read(configfilePath)       
            config.sections()
            
            timeout = config['TIMEOUT']['timeout']
            diagReqID = config['ID']['diagReqID']
            diagResID  = config['ID']['diagResID']

            self.in_timeout.setText(timeout)
            self.In_DiagReq.setText(diagReqID)
            self.In_DiagRes.setText(diagResID)
            
        except Exception as bug:
            print(bug)
        
        
class StartWindow(QWidget):
    def __init__(self):
        super(StartWindow, self).__init__()
        self.w = None  # No external window yet.
        loadUi(startPath, self)
        
        self.BackBtn.clicked.connect(self.changetoConfigtWindow)
        self.BrowserBtn.clicked.connect(self.openfile)
        self.StartBtn.clicked.connect(self.StartReqFlashing)
        
        self.in_uploadfileDir.setText(hexfilePath)
        self.thread()

    def thread(self): 
        t1=Thread(target=self.Operation) 
        t1.start() 
  
    def Operation(self): 
        try: 
            get_client_feedback(self)
        except:
            # print(Exception)
            pass

    def changetoConfigtWindow(self):
        #saving config
        global hexfilePath
        
        hexfilePath = self.in_uploadfileDir.text()
        
        if self.w is None:
            self.w=configWindow()
            print("stored latest data when window is changes : timeout {timeout}, diagReq {diagReq}, diagRes:{diagResID}".format(timeout=timeout, diagReq = diagReqID, diagResID=diagResID) )
            self.w.show()
            self.hide()
        else:
            self.w.close()  # Close window.
            self.w = None  # Discard referenc
            
    def StartReqFlashing(self):
        
        ###################
        # START FLASHING BUTTON UPDATE HERE
        ###################
        global flash, block
        try:
            sendFlashCmd = "diagReqId:{},diagResID:{},timeout:{}".format(diagReqID,diagResID,timeout)
            block = ""
            if all_mem_Stat == True:
                sendFlashCmd = sendFlashCmd + ',flash:All'
                flash = "All"
            elif option_mem_stat == True:
                flash = "Opt"
                sendFlashCmd = sendFlashCmd + ',flash:Opt'
                if CB_stat == True:
                    sendFlashCmd = sendFlashCmd + ',block:CB'
                    block = block + "CB_"
                if ASW2_stat == True:
                    sendFlashCmd = sendFlashCmd + ',block:ASW2'
                    block = block + "ASW2_"
                if DS0_stat == True:
                    sendFlashCmd = sendFlashCmd + ',block:DS0'
                    block = block + "DS0_"
                if VDS_stat == True:
                    sendFlashCmd = sendFlashCmd + ',block:VDS'
                    block = block + "VDS_"
                if ASW0_stat == True:
                    sendFlashCmd = sendFlashCmd + ',block:ASW0'
                    block = block + "ASW0_"
                if ASW1_stat == True:
                    sendFlashCmd = sendFlashCmd + ',block:ASW1'
                    block = block + "ASW1_"
            print(sendFlashCmd)
            print(block)
            print(hexfilePath)
            request_update_software(self,hexfilePath, diagReqID, diagResID, timeout, flash, block)
        except Exception as bug:
            print(bug)
    
    def openfile(self):
        global hexfilePath
        fname=QFileDialog.getOpenFileName(self, 'open file', my_path)
        hexfilePath = fname[0]
        self.in_uploadfileDir.setText(hexfilePath)
        print(hexfilePath)
        
    
app=QApplication(sys.argv)
widget = QtWidgets.QWidget()
w = configWindow()
w.show()
sys.exit(app.exec())




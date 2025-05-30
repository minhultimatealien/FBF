import time
import can
from threading import Thread
from threading import Event
from abc import ABC, abstractmethod
#import canopen
from datetime import datetime
from threading import Thread
import os
import sys

#sys.stdout = open("var.txt","w")
REQ_ID = 0x7E0
RSP_ID = 0x7E8
SECURITY_ACCESS_MASK = 0x77982990
req_session_state_dafault   = [0x10,0x01]
req_session_state_prog      = [0x10,0x02]
req_session_state_extended  = [0x10,0x03]
req_diag_mask               = [0x85,0x02]
req_com_stop                = [0x28,0x03,0x01]
req_request_seed            = [0x27,0x01]
req_send_key                = [0x27,0x02]
req_WDBI                    = [0X2E, 0xF1, 0x98]
req_erase_mem               = [0x31, 0x01, 0xFF, 0x00]
req_download                = [0x34, 0x00, 0x44]
req_transfer                = [0x36]
req_exit_transfer           = [0x37]
req_erase_mem_CB            = [0x31, 0x01, 0xFF, 0x00, 0x00]
req_erase_mem_ASW           = [0x31, 0x01, 0xFF, 0x00, 0x01]
req_erase_mem_DS            = [0x31, 0x01, 0xFF, 0x00, 0x02]

log_file = open("/home/nmu3hc/Downloads/var.txt","w")

posRes_flag                 = 0                                 #0 = waiting positive response, 1 = enable to send next request
req_data                    = [0x00]                            #request data
key                         = [0x00,0x00,0x00,0x00]             #key to unlock ECU

CB_startAddr                = 0x8001C000
CB_memSize                  = 0x00019800
ASW2_startAddr              = 0x80038000
ASW2_memsize                = 0x0000F700
DS0_startAddr               = 0x80080000
DS0_memsize                 = 0x002C0000
VDS_startAddr               = 0x80340000
VDS_memsize                 = 0x000E8000
ASW0_startAddr              = 0x80428000
ASW0_memsize                = 0x0015F140
ASW1_startAddr              = 0x80600000
ASW1_memsize                = 0x0011CF00
#memory mapping


store_state_machine		= 0			#0 : default
									#1 : CB
									#2 : ASW2
									#3 : DS0
									#4 : VDS
									#5 : ASW0
									#6 : ASW1
									#7 : End of hex file
data_CB					= ''
data_ASW2				= ''
data_DS0				= ''
data_VDS				= ''
data_ASW0				= ''
data_ASW1				= ''
#store_ability			= 0			#0 : initial store ability
									#	 
									#1 : CB
									#2 : ASW2
									#3 : DS0
									#4 : VDS
									#5 : AWS0
									#6 : AWS1
									#7 : End of hex file
				
allowable_memory = 0
current_data_of_state_machine = 0
data = ""
data_seq_CB = 0
data_seq_ASW0 = 0
data_seq_ASW1 = 0
data_seq_ASW2 = 0
data_seq_DS0 = 0
data_seq_VDS = 0
#
#	parse_hex_line extracts information out of
#	individual HEX records passed as the arg line
#

def parse_hex_line(line):
	if len( current_line) == 0 : return
	bytecount 	= int( line[0:2],16 )
	address 	= int( line[2:6],16 )
	rec_type 	= int( line[6:8],16 )
	global data
	data = line[8:(8+2*(bytecount))]


		
	global store_state_machine
	global data_CB
	global data_ASW2
	global data_DS0
	global data_VDS
	global data_ASW0
	global data_ASW1
	global allowable_memory
	global current_data_of_state_machine
	global CB_memSize
	global ASW2_memsize
	global DS0_memsize
	global VDS_memsize
	global ASW0_memsize
	global ASW1_memsize
	#print(unused_addr)
	if rec_type == 0 :
		#CB
		if address == int(0xC000) and current_data_of_state_machine == str(8001):
			allowable_memory = int(CB_memSize)
			store_state_machine = 1
			
		#ASW2
		if address == int(0x8000) and current_data_of_state_machine == str(8003):
			allowable_memory = int(ASW2_memsize)
			store_state_machine = 2
		#DS0
		if address == int(0x0000) and current_data_of_state_machine == str(8008):
			allowable_memory = int(DS0_memsize)
			store_state_machine = 3

		#VDS
		if address == int(0x0000) and current_data_of_state_machine == str(8034):
			allowable_memory = int(VDS_memsize)
			store_state_machine = 4	
			
		#ASW0
		if address == int(0x8000) and current_data_of_state_machine == str(8042):
			allowable_memory = int(ASW0_memsize)
			store_state_machine = 5
		#ASW1
		if address == int(0x0000) and current_data_of_state_machine == str(8060):
			allowable_memory = int(ASW1_memsize)
			store_state_machine = 6
			
		print(store_state_machine)
		print(current_data_of_state_machine)
		match store_state_machine :
			case 1:
#				data_CB = store_data_machine(1,bytecount,data)
				if allowable_memory <= bytecount:
					data = line[8:(8+2*(allowable_memory))]
					data_CB += data
					allowable_memory = 0
					store_state_machine = 0
				else:
					data_CB += data
					allowable_memory -= bytecount
				return
			case 2:
#				data_ASW2 = store_data_machine(2,bytecount,data)
				
				if allowable_memory <= bytecount:
					data = line[8:(8+2*(allowable_memory))]
					data_ASW2 += data
					allowable_memory = 0
					store_state_machine = 0
				else:
					data_ASW2 += data
					allowable_memory -= bytecount
				return
			case 3:
#				data_DS0 = store_data_machine(3,bytecount,data)
				if allowable_memory <= bytecount:
					data = line[8:(8+2*(allowable_memory))]
					data_DS0 += data
					allowable_memory = 0
					store_state_machine = 0
				else:
					data_DS0 += data
					allowable_memory -= bytecount
				return
			case 4:
#				data_VDS = store_data_machine(4,bytecount,data)
				if allowable_memory <= bytecount:
					data = line[8:(8+2*(allowable_memory))]
					data_VDS += data
					allowable_memory = 0
					store_state_machine = 0
				else:
					data_VDS += data
					allowable_memory -= bytecount
				return

			case 5:
#				data_ASW0 = store_data_machine(5,bytecount,data)
				if allowable_memory <= bytecount:
					data = line[8:(8+2*(allowable_memory))]
					data_ASW0 += data
					allowable_memory = 0
					store_state_machine = 0
				else:
					data_ASW0 += data
					allowable_memory -= bytecount
				return
			case 6:
#				data_ASW1 = store_data_machine(6,bytecount,data)
				if allowable_memory <= bytecount:
					data = line[8:(8+2*(allowable_memory))]
					data_ASW1 += data
					allowable_memory = 0
					store_state_machine = 0
				else:
					data_ASW1 += data
					allowable_memory -= bytecount
				return
	
	elif rec_type == 1:
		store_state_machine = 7
		print('Hex data is stored completely')
	elif rec_type == 4:
		current_data_of_state_machine = data
		
#open hex file
hex_file_path = os.path.abspath("/home/nmu3hc/Downloads/P1655CS12C4_VK0A.hex")
print("Parsing" + hex_file_path)
hex_file = open(hex_file_path,"r")

#Analyze the hex file line by line
current_line = ""
try:
	byte = "1" #initial placeholder
	while byte != "":
		byte = hex_file.read(1)
		if byte == ":":
			
			#parse the current line
			parse_hex_line(current_line)
			#reset the current line to build the next one
			current_line = ""
			#print(byte)
		else:
			current_line += str(byte)
	parse_hex_line(current_line)
	#print(data_CB)
finally:
	hex_file.close()
#log_file.write(str(data_ASW1))
#cantp

def set_up_Data(start_address,mem_size,data_section):
	#set up data
    block_size_max = int(0xFFF) - 2
    total_block_seq_count = int(int(mem_size)/block_size_max)
    last_block_seq_data  = int(mem_size)-block_size_max*total_block_seq_count
    arr = []
    if last_block_seq_data == 0:
        total_block_seq_count += 0
    else:
        total_block_seq_count +=1
    data_hex = [hex(int(data_section[:2],16))]
    for i in range (int(mem_size)-1):
        d = '0x'
        d += data_section[(2*i+2):(2*i+4)]
        x = int(d,16)
        data_hex += [hex(x)]
    data_hex = [int(val,16) for val in data_hex]
    if start_address == 0x8001C000:
        global data_seq_CB
        data_seq_CB = [[0 for x in range (block_size_max)] for y in range(total_block_seq_count)]
        for i in range (total_block_seq_count):
            if i == (total_block_seq_count-1):
                arr = data_hex[(i*block_size_max):((i*block_size_max)+last_block_seq_data)]
                data_seq_CB[i] = arr
            else:
                arr = data_hex[(i*block_size_max):((i+1)*block_size_max)]
                data_seq_CB[i] = arr
        return
    if start_address == 0x80428000:
        global data_seq_ASW0
        data_seq_ASW0 = [[0 for x in range (block_size_max)] for y in range(total_block_seq_count)]
        for i in range (total_block_seq_count):
            if i == (total_block_seq_count-1):
                arr = data_hex[(i*block_size_max):((i*block_size_max)+last_block_seq_data)]
                data_seq_ASW0[i] = arr
            else:
                arr = data_hex[(i*block_size_max):((i+1)*block_size_max)]
                data_seq_ASW0[i] = arr
        return
    if start_address == 0x80600000:
        global data_seq_ASW1
        data_seq_ASW1 = [[0 for x in range (block_size_max)] for y in range(total_block_seq_count)]
        for i in range (total_block_seq_count):
            if i == (total_block_seq_count-1):
                arr = data_hex[(i*block_size_max):((i*block_size_max)+last_block_seq_data)]
                data_seq_ASW1[i] = arr
            else:
                arr = data_hex[(i*block_size_max):((i+1)*block_size_max)]
                data_seq_ASW1[i] = arr
        return
    if start_address == 0x80038000:	
        global data_seq_ASW2
        data_seq_ASW2 = [[0 for x in range (block_size_max)] for y in range(total_block_seq_count)]
        for i in range (total_block_seq_count):
            if i == (total_block_seq_count-1):
                arr = data_hex[(i*block_size_max):((i*block_size_max)+last_block_seq_data)]
                data_seq_ASW2[i] = arr
            else:
                arr = data_hex[(i*block_size_max):((i+1)*block_size_max)]
                data_seq_ASW2[i] = arr
        return
    if start_address == 0x80080000:
        global data_seq_DS0
        data_seq_DS0 = [[0 for x in range (block_size_max)] for y in range(total_block_seq_count)]
        for i in range (total_block_seq_count):
            if i == (total_block_seq_count-1):
                arr = data_hex[(i*block_size_max):((i*block_size_max)+last_block_seq_data)]
                data_seq_DS0[i] = arr
            else:
                arr = data_hex[(i*block_size_max):((i+1)*block_size_max)]
                data_seq_DS0[i] = arr
        return
    if start_address == 0x80340000:
        global data_seq_VDS
        data_seq_VDS = [[0 for x in range (block_size_max)] for y in range(total_block_seq_count)]
        for i in range (total_block_seq_count):
            if i == (total_block_seq_count-1):
                arr = data_hex[(i*block_size_max):((i*block_size_max)+last_block_seq_data)]
                data_seq_VDS[i] = arr
            else:
                arr = data_hex[(i*block_size_max):((i+1)*block_size_max)]
                data_seq_VDS[i] = arr
        return
set_up_Data(CB_startAddr,CB_memSize,data_CB)
set_up_Data(ASW0_startAddr, ASW0_memsize, data_ASW0)
set_up_Data(ASW1_startAddr, ASW1_memsize, data_ASW1)
set_up_Data(ASW2_startAddr,ASW2_memsize,data_ASW2)
set_up_Data(DS0_startAddr, DS0_memsize,data_DS0)
set_up_Data(VDS_startAddr, VDS_memsize, data_VDS)

class CANTP(can.Listener):
    class Observer(ABC):
        @abstractmethod
        def on_cantp_msg_received(self,data):
            pass
    def addObserver(self,observer:Observer):
        self.observers.append(observer)
    
    def notify(self):
        payload = self.rx_data[:self.rx_data_size]
        payload_str = "".join(["{:02X}".format(byte) for byte in payload])
        print(f"CANTP:notify - {payload_str}")
        for observer in self.observers:
            observer.on_cantp_msg_received(payload)
            
    def on_error(self,exc: Exception) -> None:
        print(f"CANTP:error : {exc}")
        return super().on_error(exc)
    
    def on_message_received(self,msg) -> None:
        can_id = msg.arbitration_id
        #print(can_id)
        data = msg.data
        #print(msg.data)
        
        if can_id == self.rxid:
            log_msg = "RX     -     ID: {:04X}     DL: {:02X}    DATA: {}".format(can_id, msg.dlc, "".join(["{:02X}".format(byte) for byte in msg.data]))
            print(log_msg)
            global log_file
            log_file.write(log_msg)
            log_file.write("\n")
            #return msg.data
            if (data[0] & 0x7F) == 0x7F:
                if data[2] & 0x78 == 0x78:
                    #time.sleep(1)
                    return
            if (data[0] & 0xF0) == 0x00:
                self.readSingleFrame(data)
                return
            
            if data[0] & 0xFD == 0x10:
                self.received_blocks = 0
                self.readFirstFrame(data)
                time.sleep(self.st_min_for_rx/10e3)
                self.writeFlowControlFrame()
                return
            
            if data[0] & 0xFD == 0x20:
                self.received_blocks += 1
                self.readConsecutiveFrame(data)
                time.sleep(self.st_min_for_rx/10e3)
                if not (self.received_blocks % self.blk_size_for_rx):
                    self.writeFlowControlFrame()
                return
            
            if data[0] & 0xFD == 0x30:
                self.readFlowControlFrame(data)
                log_file.write("1\n")
                return
        
    def __init__(self, bus, txid, rxid):
        self.flow_ctrl_ok = Event()
        self.st_min_for_tx = 0x14 #20ms
        self.st_min_for_rx = 0x14 #20ms
        self.blk_size_for_tx = 4
        self.blk_size_for_rx = 4
        self.rx_data = []
        self.rx_data_size = 0
        self.max_blk_size = 4096
        self.received_blocks = 0
        self.txid, self.rxid = txid, rxid
        self.observers = []
        self.bus = bus

    def readSingleFrame(self,data):
        self.rx_data_size = data[0]
        self.rx_data = [byte for byte in bytes(data[1:])]
        self.notify()
        global req_data
        global key
        global posRes_flag 
        pos_sid = req_data[0] + 0x40
        if data[1] & pos_sid == pos_sid:
            if data[1] == 0x67 and data[2] == 0x01:
                #global posRes_flag 
                posRes_flag = 1
                print('security seed')
                for i in range (4):
                    key[i] = data[i+3]
                #return data
            #global posRes_flag 
            posRes_flag = 1
            print(self.rx_data)
        
    def readFirstFrame(self,data):
        self.rx_data_size = ((data[0] & 0x0F) << 8) | data[1]
        self.rx_data = [byte for byte in bytes(data[2:])]
        
    def readConsecutiveFrame(self,data):
        self.rx_data +=[byte for byte in bytes(data[1:])]
        if len(self.rx_data) >= self.rx_data_size:
            self.notify()
            
    def readFlowControlFrame(self,data):
        self.st_min_for_tx = (data[2] / 10e3) if (data[2] <= 0x7F) else (self.st_min_for_tx + (data[2] / 10e6))
        self.blk_size_for_tx = data[1] if data[1] else self.max_blk_size
        self.flow_ctrl_ok.set()
        print(data)
        
    def sendMessage(self,msg):
        msg = can.Message(arbitration_id = self.txid, data = msg, is_extended_id = False)
        self.bus.send(msg)
        global log_file
        log_file.write(str(msg))
        log_file.write("\n")
        time.sleep(0.001)
        #print(msg)
        
    def writeSingleFrame(self,data):
        data_len = len(data)
        msg = [data_len] + data
        msg +=[0x00 for i in range(8 - len(msg))]
        self.sendMessage(msg)
        print(msg)
        
    def writeFirstFrame(self,data):
        self.seq = 0
        data_len = len(data)
        last_idx = 6
        msg = [0x10  | ((data_len & 0xF00) >> 8)] +[(data_len & 0xFF)] +data [:last_idx]
        self.sendMessage(msg)
        return data[last_idx:]
    
    def writeConsecutiveFrame(self,data):
        data_len = len(data)
        last_idx = (data_len %8) if (data_len < 7) else 7
        self.seq = (self.seq + 1) % 16
        msg = [0x20 | self.seq] + data[:last_idx]
        msg += [0x00 for  i in range(8-len(msg))]
        self.sendMessage(msg)
        return data[last_idx:]
    
    def writeFlowControlFrame(self):
        msg = [0x30,self.blk_size_for_rx, self.st_min_for_rx, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.sendMessage(msg)
        
    def writeMultiFrame(self,data):
        block_count = 0
        self.flow_ctrl_ok.clear()
        data = self.writeFirstFrame(data)
        data_len = len(data)
        timeout = 0
        while data_len:
            timeout = 0 if self.flow_ctrl_ok.wait(0.01) else (timeout+1)
            if timeout == 0:
                data = self.writeConsecutiveFrame(data)
                data_len = len(data)
                time.sleep(self.st_min_for_tx)
                block_count += 1
                if block_count % self.blk_size_for_tx == 0:
                    self.flow_ctrl_ok.clear()
                    block_count = 0
            elif timeout > 10:
                print("CANTP::writeMultiFrame : flow ctrl timeout")
                break
            
    def sendData(self,data):
        if(len(data) < 8):
           self.writeSingleFrame(data)
           print("sending data")
        else:
           self.writeMultiFrame(data)
           

#calculate seed
def calculateKey(SEED):
    Key = SEED
    Seed_temp = ((SEED[0] << 24) | (SEED[1] << 16) | (SEED[2] << 8) | (SEED[3])) & 0xFFFFFFFF
    for index in range(0,35):
        if Seed_temp >= 0x80000000:
            Seed_temp = ((Seed_temp << 1) ^ SECURITY_ACCESS_MASK) & 0xFFFFFFFF
        else:
            Seed_temp = (Seed_temp << 1) & 0xFFFFFFFF
    Key[0] = (Seed_temp >> 24) & 0xFF
    Key[1] = (Seed_temp >> 16) & 0xFF
    Key[2] = (Seed_temp >> 8) & 0xFF
    Key[3] = Seed_temp & 0xFF
    return Key

filters = [{"can_id":0x7E8,"can_mask":0x7FF,"extended":False}]
#set up interface
bus1 = can.Bus(bustype='socketcan',channel = 'can0',bitrate = 500000,cam_filters = filters)
tp1 = CANTP(bus1, REQ_ID, RSP_ID)

#Cyclic task to check response from ECU
def background_task(interval_sec):
    while True:
        can_rsp = bus1.recv()
        tp1.on_message_received(can_rsp)
        #print(can_rsp)
        
daemon = Thread(target=background_task,args=(0.00001,),daemon = True,name = 'Background')
daemon.start()

#request to extended session ( 10 03 )
while posRes_flag == 0:
    req_data = req_session_state_extended
    tp1.sendData(req_data)
    time.sleep(1)
posRes_flag = 0
time.sleep(0.1)

#request to diagnosis mask processing ( 85 02 )
while posRes_flag == 0:
    req_data = req_diag_mask
    tp1.sendData(req_data)
    time.sleep(1)
posRes_flag = 0
time.sleep(0.1)

#request to communication stop (28 03 01)
while posRes_flag == 0:
    req_data = req_com_stop
    tp1.sendData(req_data)
    time.sleep(1)
posRes_flag = 0
time.sleep(0.1)

#request to reprogramming session ( 10 02 )
while posRes_flag == 0:
    req_data = req_session_state_prog
    tp1.sendData(req_data)
    time.sleep(1)
posRes_flag = 0
time.sleep(0.1)

#request seed (27 01)
while posRes_flag == 0:
    req_data = req_request_seed
    tp1.sendData(req_data)
#    key = tp1.sendData(req_data)
    time.sleep(1)
print(key)
posRes_flag = 0
time.sleep(0.1)

key = calculateKey(key)

#send key (27 02)
while posRes_flag == 0:
    req_data = [req_send_key[0],req_send_key[1], key[0] , key[1] , key[2] , key[3] ]
    tp1.sendData(req_data)
    time.sleep(2)
posRes_flag = 0
time.sleep(0.1)

#erase memory (31 01 FF 00)
while posRes_flag == 0:
    req_data = req_erase_mem_CB
    tp1.sendData(req_data)
    time.sleep(2)
print("31 done")
posRes_flag = 0
time.sleep(2)



#request Flash data for CB(34 xx xx xx xx xx xx xx)

#print(data_CB_seq)
def flash_sequence(start_address,mem_size,data_seq):
	#set up data
    block_size_max = int(0xFFF) - 2
    total_block_seq_count = int(int(mem_size)/block_size_max)
    last_block_seq_data  = int(mem_size)-block_size_max*total_block_seq_count
    if last_block_seq_data == 0:
        total_block_seq_count += 0
    else:
        total_block_seq_count +=1
    global req_download
    global req_transfer
    global req_exit_transfer
    global req_data
    global posRes_flag
    global data_ASW0
    
    #Download request (34 00 44 80 01 00 00 00 01 98 00)
    posRes_flag = 0
    while posRes_flag == 0:
        download_req = [(start_address >> 24),(start_address >> 16 & 0xFF),(start_address >> 8 & 0xFF),(start_address & 0xFF),(mem_size >> 24),(mem_size >> 16 & 0xFF),(mem_size >> 8 & 0xFF),(mem_size & 0xFF)]
        print("download_req")
        print(download_req)
        req_data = req_download + download_req
        print(req_data)
        tp1.sendData(req_data)
        time.sleep(2)
    posRes_flag = 0
    time.sleep(0.1)
    u = 0
    #Transfer request (36 xx xx xx)
    while posRes_flag == 0:
        for i in range (total_block_seq_count):
            if i > 2*int(0xFF):
                u = i - (2*int(0xFF))
                u = u -1
                req_block_seq_count = [hex(u)]
                req_block_seq_count = [int(val,16) for val in req_block_seq_count]
                req_data = req_transfer + req_block_seq_count + data_seq[i]
                tp1.sendData(req_data)
                time.sleep(0.4)
            elif i > (2*int(0xFF)-1):
                u = i - int(0xFF)
                req_block_seq_count = [hex(u)]
                req_block_seq_count = [int(val,16) for val in req_block_seq_count]
                req_data = req_transfer + req_block_seq_count + data_seq[i]
                tp1.sendData(req_data)
                time.sleep(0.4)
              
            elif i > (int(0xFF)-1):
                u = i - int(0xFF)
                req_block_seq_count = [hex(u)]
                req_block_seq_count = [int(val,16) for val in req_block_seq_count]
                req_data = req_transfer + req_block_seq_count + data_seq[i]
                tp1.sendData(req_data)
                time.sleep(0.4)
                
            else:
        #for i in range (total_block_seq_count):
                req_block_seq_count = [hex(i+1)]
                req_block_seq_count = [int(val,16) for val in req_block_seq_count]
                req_data = req_transfer + req_block_seq_count + data_seq[i]
            #log_file.write(str(len(req_data)))
                tp1.sendData(req_data)
                time.sleep(0.5)
                
        #time.sleep(10)
    posRes_flag = 0
    time.sleep(0.1)
    #Exit transfer request
    while posRes_flag == 0:
        req_data = req_exit_transfer
        tp1.sendData(req_data)
        time.sleep(2)
    posRes_flag = 0
    time.sleep(0.1)
    return

print("*********CB**********")
log_file.write("********* CB **********")
log_file.write("\n")
flash_sequence(CB_startAddr,CB_memSize,data_seq_CB)
print("*********ASW0*********")
log_file.write("********* ASW0 **********")
log_file.write("\n")
flash_sequence(ASW0_startAddr, ASW0_memsize,data_seq_ASW0)
print("*********ASW1*********")
log_file.write("********* ASW1 **********")
log_file.write("\n")
flash_sequence(ASW1_startAddr, ASW1_memsize,data_seq_ASW1)
print("*********ASW2*********")
log_file.write("********* ASW2 **********")
log_file.write("\n")
flash_sequence(ASW2_startAddr,ASW2_memsize,data_seq_ASW2)
print("*********DS0*********")
log_file.write("********* DS0 *********")
log_file.write("\n")
flash_sequence(DS0_startAddr, DS0_memsize,data_seq_DS0)
print("*********VDS*********")
log_file.write("********* VDS *********")
log_file.write("\n")
flash_sequence(VDS_startAddr, VDS_memsize,data_seq_VDS)



#sys.stdout.close()
        
log_file.close() 
    

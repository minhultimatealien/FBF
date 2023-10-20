import sys
import os

#
#   parse_hex_line extracts information out of
#   individual HEX records passed as the arg line.
#
def parse_hex_line( line ):
    #print (line)
    if len( current_line ) == 0: return
    bytecount = int( line[0:2], 16 )
    address = int( line[2:6], 16 )
    rec_type = int( line[6:8], 16 )

    #rec_output = str(hex(address)) + '\t' + str(bytecount) + '\t'
    rec_output = str(bytecount)
    if rec_type == 0:
        #rec_output += 'data'
        rec_output += '\t\t' + line[8:(8+2*(bytecount))]
    elif rec_type == 1:
        rec_output += 'end of file'
    elif rec_type == 2:
        rec_output += 'ext segment addr'
    elif rec_type == 3:
        rec_output += 'start segment address'
    elif rec_type == 4:
        rec_output += 'ext linear addr'
    elif rec_type == 5:
        rec_output += 'start linear address'
    print (rec_output)

#   (1) Open the Hex File
hex_file_path = os.path.abspath("C:\PMI5HC\sharcc_ws\JOEM\Suzuki\XE619\ABS_103_MBML\Gen\XE619x103MLextxD3EDxCSWXCP\Build_20230911_153113\PRJ_Hexfile_BB86884_01_01_20230911_153113_XE619x103MLextxD3EDxCSWXCP.hex")
print ("Parsing " + hex_file_path)
hex_file = open(hex_file_path, "rb")

#   (2) Analyze the hex file line by line
current_line = ""
try:
    byte = "1" # initial placeholder
    print ("Address\tLength\tType\t\tData")
    while byte != "":
        byte = hex_file.read(1)
        if byte == ":":
            #   (1) Parse the current line!
            parse_hex_line( current_line )
            #   (2) Reset the current line to build the next one!
            current_line = ""
        else:
            current_line += byte
    parse_hex_line( current_line )
finally:
    hex_file.close()
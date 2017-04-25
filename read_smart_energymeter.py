#!/bin/python2.7

##########
# CONFIG #
##########

serialport = '/dev/ttyUSB0'
baudrate = 9600
databits = 7
parity = 'E'
stopbits = 1
zabbix_server = 'zabbix.domain.tld'
zabbix_hostname = 'myhome'

#################
# ACTUAL SCRIPT #
#################
import serial
import sys
import subprocess
from time import sleep

serport = serial.Serial()
serport.port = serialport
serport.baudrate = baudrate
serport.bytesize = databits
serport.parity = parity
serport.stopbits = stopbits

try:
    serport.open()
except:
    sys.exit("Failed to open serial port %s.", serialport)

sleep(3)

linesfound = {}
while True:
    line = serport.readline()

    # Total power used in low price periods
    if line.startswith('1-0:1.8.1'):
        rawvalue = line.split('(')[1].split('*')[0]
        linesfound['power_low_total'] = rawvalue
    # Total power used in high price periods
    elif line.startswith('1-0:1.8.2'):
        rawvalue = line.split('(')[1].split('*')[0]
        linesfound['power_high_total'] = rawvalue
    # Current price period
    elif line.startswith('0-0:96.14.0'):
        rawvalue = line.split('(')[1].split(')')[0]
        linesfound['power_current_period'] = rawvalue
    # Current power usage
    elif line.startswith('1-0:1.7.0'):
        rawvalue = line.split('(')[1].split('*')[0]
        linesfound['power_current_usage'] = rawvalue
    # End of the current information block
    elif line.startswith('!'):
        zabbix_sender_input = []
        for keys,values in linesfound.items():
            zabbix_sender_input.append(' '.join((zabbix_hostname, keys, values)))
        subprocess.call('echo -e "' + "\n".join(zabbix_sender_input) + '" | /bin/zabbix_sender -z ' + zabbix_server + " -i -" , shell=True)
        linesfound = {}

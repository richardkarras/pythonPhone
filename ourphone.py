#!/usr/bin/env python2
import time
import os
import subprocess
import Adafruit_BBIO.GPIO as GPIO

#cpn = 5 #for "hook" connector
GPIO.setup("P9_17",GPIO.IN)
cpn = GPIO.output("P9_17")
#dpn = 49 #for rotary/Traverse or test pin for dialing
GPIO.setup("P9_19",GPIO.IN)
dpn = GPIO.output("P9_19")
#npn = 3 #for number in
GPIO.setup("P9_21",GPIO.IN)
npn = GPIO.output("P9_21")

#load the config file
config = {}
def load_config():
	global config
	this_file =  os.path.abspath(__file__)
	dir = os.path.dirname(this_file)
	cfile = os.path.join(dir ,"phone.conf" )
	file_lines = open(cfile)
	for line in file_lines:
		#trim the white spaces
		line = line.strip()
		#if the line has length and the first char isn't a hash
		if len(line) and line[0]!="#":
			#this is a parsible line
			(key,value) = line.split(":",1)
			config[key.strip()] = value.strip()

#load the config
load_config()

cradle_lifted = False
dialing = False
number_count = 0
error_number = -999

regular_time = 0.2
dialing_time = 0.01
sleep_time = regular_time

print "dialer: %s" % (get_val(dpn))
print "number: %s" % ( get_val(npn))

old_nval = 0
number_string = ""
GPIO.add_event_detect("P9_21",GPIO.RISING)


while (1):
    time.sleep(sleep_time)
	#check the cradle switch
    GPIO.wait_for_edge("P9_17", GPIO.RISING)
    print "cradle lift"
    while GPIO.input("P9_17"):
        GPIO.wait_for_edge("P9_19", GPIO.RISING)
        print "traverse on"
            while (GPIO.input("P9_19")):
                if GPIO.event_detected("P9_21"):
                    print "pulse counted"
                    number_count += 1
                    print number_count
                else:
                    sleep_time = dialing_time
                if number_count == 10:
                    number_string += "0"
                else:
                    number_string += str(number_count)
                number_count = 0
        print "traverse off"
        sleep_time = regular_time
        print number_string
        if number_string not in config:
            load_config()
        try:
            cmd = config[ number_string ]
            if cmd:
                ret = subprocess.call( [cmd, "2> /dev/null" ], shell=True)

        except Exception, e:
            cmd = config[ error_number ]
            print e.message
		#reset the number string
        number_string = ""
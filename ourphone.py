#!/usr/bin/env python2
import time
import os
import subprocess

cpn = 5 #for "hook" connector
dpn = 49 #for rotary/Traverse or test pin for dialing
npn = 3 #for number in

#mux pin 8-15
try:
	f = open("/sys/kernel/debug/omap_mux/gpmc_a0","wb")
	f.write("0x37")
	f.close()
	print "muxed gpmc_a0"
except Exception, e:
	print e.message, 'failed to mux gpmc_a0'

input_pins = [cpn, dpn, npn]

for pin in input_pins:
	print pin
	try:
		f = open("/sys/class/gpio/export","w")
		f.write("%d" % (pin) )
		f.close()
		print "exported %d" % (pin)
	except Exception, e:
		print e.message, pin
	try:
		f = open("/sys/class/gpio/gpio"+str(pin)+"/direction","w")
		f.write("in")
		f.close()
	except Exception, e:
		print e.message


#load the config file ########### WHAT CONFIG FILE? #############
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

#def led( num, val="0" ):
#	path = "/sys/devices/platform/leds-gpio/leds/beaglebone::usr%d/brightness" % ( num )
#	f = open(path, 'w')
#	f.write(val)

#disable all of the leds
#def all_leds( val="0"):
#	for i in range(4):
#		led(i, val)

#def get_led_val( num ):
#	path = "/sys/devices/platform/leds-gpio/leds/beaglebone::usr%d/brightness" % ( num )
#	f = open(path, "r")
#       val = f.read().strip()
#	f.close()
#	return val

#toggle an led on or off
#def toggle_led( i ):
#	if get_led_val(i)=="1":
#		val = "0"
#	else:
#		val = "1"
#	led(i,val)

def get_val(pin):
	pval = open("/sys/class/gpio/gpio"+str(pin)+"/value", "r")
	#check the switch
	val = pval.read().strip()
	pval.close()
	return val


#load the config
load_config()

cradle_lifted = False
dialing = False
number_count = 0

regular_time = 0.2
dialing_time = 0.01
sleep_time = regular_time

print "dialer: %s" % (get_val(dpn))
print "number: %s" % ( get_val(npn))

old_nval = 0
number_string = ""

#disable all of the little leds
#for i in range(4):
#	led(i,"0")

while (1):
    time.sleep(sleep_time)
	#check the cradle switch
    val = get_val(cpn)
    if val == "0":
        if cradle_lifted:
            dval = get_val(dpn)
            if dval != "1":
                if not dialing:
                    print "dialing"
                    #led(1,"1")
                    #led(2,"0")

                dialing = True
                nval =  get_val(npn)
                #print nval
                if nval != old_nval:
                    old_nval = nval
                    number_count +=1
                    #toggle an led	
                    #toggle_led(2)

            else:
                if dialing:
                    dialing = False
                    #led(1,"0")
                    #led(2,"0")

                    dialed_number = number_count/2
                    if dialed_number == 10:
                        number_string += "0"
                    else:
                        number_string += str(dialed_number)
                    number_count = 0

        else:
            sleep_time = dialing_time
            print "cradle lift"
            cradle_lifted = True
            #led(0,"1")

    elif val == "1" and cradle_lifted:
        print "cradle down"
        print number_string
        sleep_time = regular_time
        #all_leds()
        cradle_lifted = False 
        if number_string not in config:
            load_config()
        try:
            cmd = config[ number_string ]
            if cmd:
                ret = subprocess.call( [cmd, "2> /dev/null" ], shell=True)

        except Exception, e:
            os.system('#error file')
            #print e.message
		#reset the number string
        number_string = ""    

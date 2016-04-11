#!/usr/bin/python

import setproctitle as spt
import Button

# the gpio pin we are looking at in relation to the BMC
hw_pin = 26
# the absolute path to the config file 
config_file = "/opt/button-interface/config.txt"
#set the process title
spt.setproctitle('hwbuttond')
#create the button listener
multi_purpose_button = Button.Button(hw_pin, config_file)
multi_purpose_button.buttonListener()
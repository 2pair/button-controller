#!/usr/bin/python

import RPi.GPIO as GPIO
import atexit, time, sys, re, os.path, subprocess, shlex, math

# A button listener that does different actions based on whats in its config file
class Button:
    # dictionary of actions.
    # key = button hold time, value = script to run
    actions = {}
    # the maximum time we need to listen to the button
    max_hold = None
    # the minimum time we will respond to
    min_hold = None
    # To initialize the Button, define what BMC pin it operates on and point to the config file
    #config file format: 
    # each line has a length of time to hold the button in integer seconds, followed by a colon and then a script to execute
    # example:          2: python /usr/bin/myscript -OpTioNs "arg1" "arg2"
    # if there is no 0 value a short press will do nothing.
    # the script will round down to the nearest action.
    def __init__(self, pin, config_file):
        self.pin = pin
        
        #set up this button's actions
        self.config(config_file)   
        # setup the gpio pin
        self.setupGpio(self.pin)
        # register the cleanup function
        atexit.register(self.cleanup)
    
    # configure this button by reading in a config file
    # then set our min and max hold times
    def config(self, config_file):
        # clear out the actions dictionary before populating it
        self.actions.clear()
        # read in and parse our config file
        line_number = 0
        with open(config_file) as c:
            for line in iter(c.readline, ''):
                line_number += 1
                self.processLine(line, line_number)
        c.close()
        
        # figure out what the maximum time we can hold is
        self.max_hold = 0
        for i in list(self.actions.keys()):
            if i > self.max_hold:
                self.max_hold = i
        # figure out what the minimum time we care about is
        self.min_hold = self.max_hold
        for i in list(self.actions.keys()):
            if i < self.min_hold:
                self.min_hold = i;
    
    # sets up the GPIO pins
    # accepts a pin
    def setupGpio(self, pin):
        GPIO.setmode(GPIO.BCM)
        # suppress the 'already in use' warning that isn't helpful
        GPIO.setwarnings(False)
        self.setupPin(pin, force=True)
        return 0
    
    # setup a specific pin
    # checks that it is available before assignment
    def setupPin(self, pin, force=False):
        func = GPIO.gpio_function(pin)
        
        if func != 0 and force != True:
            raise PinInUseError(pin, func)
        else:
            GPIO.setup(pin, GPIO.IN)
        return 0
        
    # read in a line from our config file
    # add its data to our dictionary
    def processLine(self, line, line_number):
        m = re.match(r"^([0-9]+)[ \t]*:[ \t]*(.+)", line)
        if m:
            time_length = m.group(1)
            command = m.group(2)
        # regex didn't match
        else:
            raise ConfigReadError(line_number)
        
        # make sure we dont have this key already
        if time_length not in self.actions:
            pass
        else:
            raise KeyExists(time_length, line_number)
        # make sure the script actually exists
        #if os.path.isfile(command):
        #    pass
        #else:
        #    raise FileNotFound(command, line_number)
        # add to the dictionary
        self.actions[int(time_length)] = command
        return 0
    
    # hangs out and waits for the button to be pressed
    # figures out how long the button was pressed for,
    # then runs the script associated with that length of time
    # assumes pin is active high (high when pressed)
    def buttonListener(self):
        count = 0
        sleep_time = 0.050 #seconds
        
        while True:
            # button pressed
            if GPIO.input(self.pin):
                # add number of milliseconds
                count += sleep_time
                #see if we really need to keep monitoring
                if count > self.max_hold:
                    self.doAction(self.max_hold)
            # button released
            else:    
                # button has been pressed
                if count > 0:
                    action = self.findAction(math.floor(count))
                    if action in self.actions:
                        self.doAction()
                count = 0
            time.sleep(sleep_time)
    
    # search for the nearest lower-valued action
    def findAction(self, time_length):
        # assume a bad value
        candidate = -1
        for i in list(self.actions.keys()):
            if i <= time_length and i > candidate:
                candidate = i
        return candidate
    
    # do the action from the action dictionary
    def doAction(self, key):
        args = shlex.split(self.actions[key])
        subprocess.Popen(args)
    
    # clean up function to run when done
    def cleanup(self):
        GPIO.cleanup()
        return 0
        
# error class for when we try to use an LED on an already in use pin
class PinInUseError(Exception):
    def __init__(self, pin, function):
        self.pin = pin
        self.function = function
        self.function_dict = { 0 : 'GPIO.OUTPUT',
                               1 : 'GPIO.IN',
                               40 : 'GPIO.SERIAL',
                               41 : 'GPIO.SPI',
                               42 : 'GPIO.I2C',
                               43 : 'GPIO.HARD_PWM',
                               -1 : 'GPIO.UNKNOWN'}
        self.return_string = "pin " + str(pin) + " already in use. Currently set to mode " + self.function_dict[self.function]
    def __str__(self):
        return repr(self.return_string)           
        
# error class for a poorly formatted config file
class ConfigReadError(Exception):
    def __init__(self, line_number):
        self.return_string = "Error on line " + str(line_number) + " of config file. Please ensure each line has a time and script pair seperated by a colon (:)."
    def __str__(self):
        return repr(self.return_string)           

# error class for a duplicate entry in the config file
class KeyExists(Exception):
    def __init__(self, key, line_number):
        self.return_string = "Error on line " + str(line_number) + " of config file. An entry for " + str(key) + " seconds already exists."
    def __str__(self):
        return repr(self.return_string)
        
# error class for a non existant script specified in the config file
class FileNotFound(Exception):
    def __init__(self, file, line_number):
        self.return_string = "Error on line " + str(line_number) + " of config file. The file " + file + " was not found."
    def __str__(self):
        return repr(self.return_string)

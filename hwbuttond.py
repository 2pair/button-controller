#!/usr/bin/python

import setproctitle as spt
import Button, argparse, sys, os, subprocess

#argument parsing
parser = argparse.ArgumentParser(description='Start a service to monitor a push button.')
# the gpio pin we are looking at in relation to the BMC
parser.add_argument('-p','--pin', 
                    dest='hw_pin', 
                    type=int, 
                    required=True,
                    help='The gpio pin attached to the button (BMC relative).',
                    choices=[2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]
                    )
# the absolute path to the config file 
parser.add_argument('-f','--file', 
                    dest='config_file',  
                    required=False,
                    help='The location of the file describing the button\'s actions.'
                    )
# start or stop monitoring
parser.add_argument('-a','--action',
                    dest='action',
                    required=False,
                    help='Start or stop monitoring this button. The default action is to start.'
                    )
args = parser.parse_args()

#normalize the action argument
if args.action.lower()=='start' or args.action==None:
    args.action = 'start'
elif args.action.lower()=='stop':
    args.action = 'stop'
else:
    print("Invalid value to argument \'-a/--action\'. Valid values are start/stop")
    parser.print_usage()
    sys.exit(0)    

#make sure we have a valid config file when starting the service
if args.action=='start' or args.action==None:
    if args.config_file==None:
        print("When starting the service a config file must be specified.")
        parser.print_usage()
        sys.exit(0)
    elif os.path.isfile(args.config_file):
        pass
    else:
        print("Specified config file was not found.")
        parser.print_usage()
        sys.exit(0)

# make a new button listener
if args.action=='start' or args.action==None:
    #set the process title
    title = 'hwbutton' + str(args.hw_pin) + 'd'
    spt.setproctitle(title)
    #create the button listener
    multi_purpose_button = Button.Button(args.hw_pin, args.config_file)
    multi_purpose_button.buttonListener()
# kill an existing button listener
elif args.action=='stop':
    process = 'hwbutton' + str(args.hw_pin) + 'd'
    subprocess.call(["pkill", process])
    
sys.exit(0)

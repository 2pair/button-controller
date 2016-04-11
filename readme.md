# button-interface

This is a small project to control a button on the raspberry pi.

## Installation

I'm assuming this is being used on a linux system.
Place the following files in a directory of your choice:
Button.py
hwbuttond.py
config.txt
hwbuttond-start.sh
hwbuttond-stop.sh

edit hwbuttond.py and hwbutton.service to point to your directory as necessary.
put hwbutton.service in /usr/lib/systemd/system (assuming you're running systemd).
run "systemctl enable hwbuttond.service" then check that its working by running "systemctl status hwbuttond.service".

## Usage

Edit the config file to do whatever actions you want. the format of the file is as follows:
- one action per line.
- time in seconds for the button to be held followed by a colon(:) followed by the action.
- white space is allowed.
- an action is defined as anything you can do on the command line.
- do not leave any blank lines.
- do not repeat a time.

## License

GPL v3 http://www.gnu.org/licenses/gpl-3.0.en.html
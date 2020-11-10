## Remote keypresses

This script allows you to launch programs using a TV remote and operate with OS. This is useful when you have Kodi installed and you don't want to use a keyboard.

## Installation

On Debian-based distros run

`sudo apt install cec-utils xdotool`

Please edit this script to configure keystrokes and change the default script path/environment variables in the .service file.

Copy the .service file to `/etc/systemd/system` folder

Run `sudo systemctl enable cec-keypresses` if you wish to add this script to autostart

Please run `sudo systemctl start cec-keypresses` to run this script

#!/usr/bin/env bash
#
# react to cec keypresses in the jankiest way possible
#
# Author: Dave Eddy <dave@daveeddy.com>
# Date: 10/15/2013
# Licens: MIT
# Tested on: Raspberry pi with libcec compiled from soure
# Source code: https://gist.github.com/bahamas10/6996290
# Edited by enaix

onright() {
 	echo 'right button pressed'
	xdotool key --delay 100 Right
}
onleft() {
	echo 'left button pressed'
	xdotool key --delay 100 Left
}
ondown() {
	echo 'down button pressed'
	xdotool key --delay 100 Down
}
onup() {
	echo 'up button pressed'
	xdotool key --delay 100 Up
}
onselect() {
	echo 'select button pressed'
	xdotool key --delay 100 Return
}
onplay() {
	echo 'play button pressed'
	xdotool key --delay 100 Ctrl+space # You may specify any keystroke here or run nero directly
}
onpause() {
	echo 'pause button pressed'
}
onforward() {
	echo 'forward button pressed'
}
onbackward() {
	echo 'back button pressed'
}

filter() {
	perl -nle 'BEGIN{$|=1} /key pressed: (.*) \(.*\,.*\)/ && print $1'
}

echo as | cec-client | filter | \
while read cmd; do
	if pgrep -x "kodi" > /dev/null; then
		continue
	fi
	case "$cmd" in
		right) onright;;
		left) onleft;;
		down) ondown;;
		up) onup;;
		select) onselect;;
		play) onplay;;
		pause) onpause;;
		forward) onforward;;
		backward) onbackward;;
		*) echo "unrecognized button ($cmd)";;
	esac
done

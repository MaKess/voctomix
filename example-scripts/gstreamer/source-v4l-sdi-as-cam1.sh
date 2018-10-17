#!/bin/sh
confdir="`dirname "$0"`/../"
. $confdir/default-config.sh
if [ -f $confdir/config.sh ]; then
	. $confdir/config.sh
fi

VDEV=$(v4l2-ctl --list-devices | grep -A 1 SDI | tail -n 1 | sed 's/^[ \t]*//')
#VDEV=/dev/video1
ADEV=hw:CARD=SDI,DEV=0

gst-launch-1.0 -vv \
	v4l2src device=$VDEV ! \
		timeoverlay shaded-background=1 ! \
		videoconvert ! \
		video/x-raw,format=I420,width=$WIDTH,height=$HEIGHT,framerate=$FRAMERATE/1,pixel-aspect-ratio=1/1 ! \
		queue ! \
		mux. \
	alsasrc device=$ADEV ! \
		audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=$AUDIORATE !\
		queue ! \
		mux. \
	matroskamux name=mux ! \
		tcpclientsink host=localhost port=10000

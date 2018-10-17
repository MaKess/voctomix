ffmpeg \
	-i tcp://localhost:15000 \
	-vaapi_device /dev/dri/renderD128 \
	-vf 'format=nv12,hwupload' \
	-c:v h264_vaapi \
	-c:a aac -b:a 96k -ar 44100 \
	-f flv rtmp://stream.antibes.moegger.de/dash/high

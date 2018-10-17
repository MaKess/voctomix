import logging
import os

from gi.repository import Gst

from lib.config import Config
from lib.sources.avsource import AVSource

class V4L2Source(AVSource):
    def __init__(self, name, outputs=None, has_audio=True, has_video=True):
        self.log = logging.getLogger('V4L2Source[{}]'.format(name))
        super().__init__(name, outputs, has_audio, has_video)

        section = 'source.{}'.format(name)
        self.sourcetype = Config.get(section, 'sourcetype')

        self.launch_pipeline()

    def __str__(self):
        return 'V4L2Source[{name}] displaying {uri}'.format(
            name=self.name,
            uri=self.imguri
        )

    def launch_pipeline(self):
        sysdir = "/sys/class/video4linux"
        for f in os.listdir(sysdir):
            with open(os.path.join(sysdir, f, "name")) as fd:
                fullname = fd.read().rstrip()
                if self.sourcetype in fullname:
                    logging.info("for source [{}] use V4L2 device [{}]".format(self.name, fullname))
                    vdev = os.path.join("/dev", f)
                    break
        else:
            raise RuntimeError("could not find source with sourcetype [{}]".format(self.sourcetype))

        #ADEV=hw:CARD=SDI,DEV=0
        #VDEV=$(v4l2-ctl --list-devices | grep -A 1 SDI | tail -n 1 | sed 's/^[ \t]*//')

        #arecord --list-pcms
        #arecord --list-devices
        #v4l2-ctl --list-devices

        adev = "hw:CARD={},DEV=0".format(self.sourcetype)

        pipeline = """
            alsasrc device={adev} name=aout

            v4l2src device={vdev} ! videoconvert name=vout
        """.format(adev=adev,
                   vdev=vdev)

        self.build_pipeline(pipeline)
        self.pipeline.set_state(Gst.State.PLAYING)

    def build_audioport(self, audiostream):
        return 'aout.'

    def build_videoport(self):
        return 'vout.'

    def restart(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.launch_pipeline()

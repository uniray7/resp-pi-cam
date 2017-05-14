import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import cv2
import numpy

img_arr =None

def new_sample(appsink):
  global img_arr
  sample = appsink.emit('pull-sample')
  buf = sample.get_buffer()
  caps = sample.get_caps()
  
  print caps.get_structure(0).get_value('format')
  print caps.get_structure(0).get_value('height')
  print caps.get_structure(0).get_value('width')

  print buf.get_size()

  arr = numpy.ndarray(
      (caps.get_structure(0).get_value('height'),
       caps.get_structure(0).get_value('width'),
       3),
      buffer=buf.extract_dup(0, buf.get_size()),
      dtype=numpy.uint8)
  img_arr = arr
  return Gst.FlowReturn.OK

def start_consume():
  Gst.init(None)
  
  pipeline = Gst.Pipeline()
  
  tcpsrc = Gst.ElementFactory.make('tcpclientsrc','source')
  tcpsrc.set_property("host", "172.20.10.12")
  tcpsrc.set_property("port", 5000)
  
  gdepay = Gst.ElementFactory.make('gdpdepay', 'gdepay')
  rdepay = Gst.ElementFactory.make('rtph264depay')
  avdec = Gst.ElementFactory.make('avdec_h264')
  vidconvert = Gst.ElementFactory.make('videoconvert')

  asink = Gst.ElementFactory.make('appsink', 'sink')
  asink.set_property('sync', False)
  asink.set_property('emit-signals', True)
  asink.set_property('drop', True)
  caps = Gst.caps_from_string("video/x-raw, format=(string){BGR, GRAY8}; video/x-bayer,format=(string){rggb,bggr,grbg,gbrg}")
  asink.set_property("caps", caps)
  asink.connect('new-sample', new_sample)
  
  pipeline.add(tcpsrc)
  pipeline.add(gdepay)
  pipeline.add(rdepay)
  pipeline.add(avdec)
  pipeline.add(vidconvert)
  pipeline.add(asink)
 
  tcpsrc.link(gdepay)
  gdepay.link(rdepay)
  rdepay.link(avdec)
  avdec.link(vidconvert)
  vidconvert.link(asink)

  pipeline.set_state(Gst.State.PLAYING)
  return pipeline

if __name__ == "__main__":
  try:
    pipeline = start_consume()
    bus = pipeline.get_bus()
    while True:
      message = bus.timed_pop_filtered(10000, Gst.MessageType.ANY)
      if img_arr is not None:   
        cv2.imshow("appsink image arr", img_arr)
        cv2.waitKey(1)
  except KeyboardInterrupt:
    print "Closing pipeline"
    pipeline.set_state(Gst.State.NULL)
    loop.quit() 

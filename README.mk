# resp-pi-cam
It is for extracting frames(ndarray) from remote(tcp source) respberry PI cam.
I adopt Gstreamer to implement. Gstreamer is a framewok under GNOME for supporting multimedia streamming.

### Respberry PI
```bash
$ raspivid -t 0 -w 300 -h 300 -fps 20 -hf -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=172.20.10.12 port=5000
```
Then the respberry PI will transfer H.264 binary through gstreamer

### PC
```bash
$ gst-launch-1.0 -v tcpclientsrc host=172.20.10.12 port=5000 ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink sync=false
```

Above is bash command for receiving stream and showing.
The python code here will do the same thing, and moreover transform to ndarray, which can be manipulated by CV and ML in python

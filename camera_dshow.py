from pygrabber.dshow_graph import FilterGraph
import threading
import numpy as np

def list_cameras():
    """Return a list of available cameras"""
    
    graph = FilterGraph()
    cameras = graph.get_input_devices()
    
    return cameras

def list_formats(camera_idx):
    """Return a list of available formats for a camera index"""
    
    graph = FilterGraph()
    graph.add_video_input_device(camera_idx)
    
    formats = graph.get_input_device().get_formats()
    
    return formats

def create_filter_graph(camera, fmt_idx):
    """Return a FilterGraph instance with camera and fmt_idx"""
    
    graph = FilterGraph()
    graph.add_video_input_device(camera)
    
    formats = graph.get_input_device().get_formats()
    
    graph.get_input_device().set_format(formats[fmt_idx]['index'])
    return graph

def print_list_cameras():
    cameras = list_cameras()
    print("Available cameras")
    for i, k in enumerate(cameras):
        print(f"{i} - {k}")

def print_list_camera_cap(idx):
    formats = list_formats(idx)
    print("Available camera modes")
    for i, k in enumerate(formats):
        print(f"{i} - {k['width']}x{k['height']}@{int(k['max_framerate'])} {k['media_type_str']}")

class CameraBackend:
    """Camera backend class"""
    def __init__(self, camera, cap):
        self.graph = create_filter_graph(camera, cap)
        self.graph.add_sample_grabber(self.img_cb)
        self.graph.add_null_render()
        self.graph.prepare_preview_graph()
        self.graph.run()
        self.image_done = threading.Event()
        self.image_grabbed = None
    def img_cb(self, image):
        self.image_grabbed = image
        self.image_done.set()
    def read(self):
        self.image_done.clear()
        self.graph.grab_frame()
        ret = self.image_done.wait(1000)
        return ret, np.array(self.image_grabbed)
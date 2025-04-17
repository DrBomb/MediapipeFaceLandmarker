import cv2

def list_cameras():
    result = []
    MAX_CAMERAS = 10
    for c in range(MAX_CAMERAS):
        camera = cv2.VideoCapture(c)
        if camera.isOpened():
            result.append(c)
    return result

def print_list_cameras():
    cameras = list_cameras()
    for i, c in enumerate(cameras):
        print(f"{i} - Camera {c}")

def create_camera(camera, w=None, h=None, fps=None):
    cap = cv2.VideoCapture(camera)
    if w is not None and h is not None and fps is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        cap.set(cv2.CAP_PROP_FPS, fps)
    return cap
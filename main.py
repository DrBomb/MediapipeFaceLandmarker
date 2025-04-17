import argparse, sys, socket, time, json
from sys import platform

import mediapipe as mp

# CLI argument parser
parser = argparse.ArgumentParser(
    prog="mediapipefacelandmarker",
    description="Quick and easy mediapipe face landmark tracker program. Sends raw data to UDP port in JSON format"
)
parser.add_argument("--host", type=str, action="store", default="127.0.0.1", help="IP address to send data, defaults to 127.0.0.1")
parser.add_argument("--port", type=int, action="store", default=9500, metavar="UDP", help="UDP port to send data to.")
parser.add_argument("--camera", type=int, action="store", default=0, metavar="X", help="Camera to use.")
parser.add_argument("--model-file", type=str, action="store", default="face_landmarker.task", help="Model file downloaded from mediapipe's website.", metavar="face_landmarker.task")
parser.add_argument("--list-cameras", action="store_true", help="List cameras and exit. Linux platform can only list by index.")

subparsers = parser.add_subparsers(dest="backend", help="Backend to use", required=True)

opencv_parser = subparsers.add_parser('opencv')
opencv_parser.add_argument('--format', nargs=3, type=int, help="Override default CV2 video format. Requires 3 arguments. Width, Height and FPS", metavar="X", default=[None, None, None])

# Add 'dshow' as backend for win32 platforms
if platform == "win32":
    dshow_parser = subparsers.add_parser('dshow')
    dshow_parser.add_argument("--cap", type=int, metavar="X", default=0, help="Override default cap selection")
    dshow_parser.add_argument("--list-caps", action="store_true", help="List all capabilities for the selected camera, then exit")

if __name__ == "__main__":
    args = parser.parse_args()
    
    camera = None
    
    # Handle dshow backend
    if args.backend == "dshow":
        import camera_dshow as dshow
        
        if args.list_cameras:
            dshow.print_list_cameras()
            sys.exit(0)
        if args.list_caps:
            dshow.print_list_camera_cap(args.camera)
            sys.exit(0)
        
        print("DirectShow backend")
        camera = dshow.CameraBackend(args.camera, args.cap)
    # Handle opencv backend
    elif args.backend == "opencv":
        import camera_opencv as opencv
        
        if args.list_cameras:
            opencv.print_list_cameras()
            sys.exit(0)
        
        print("OpenCV backend")
        camera = opencv.create_camera(args.camera, *args.format)
    
    # Import mediapipe
    import mediapipe as mp
    
    # Running Constants
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode
    
    # UDP sender socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Frame timer
    frame_start = time.perf_counter()
    
    # FaceLandmarker callback function
    def onDetect(DetectionResult, Image, Cnf):
        frame_delta = time.perf_counter() - frame_start
        # print(DetectionResult)
        face_points = DetectionResult.face_landmarks
        face_blendshapes = DetectionResult.face_blendshapes
        face_transforms = DetectionResult.facial_transformation_matrixes
        if len(face_points) == 0 or len(face_blendshapes) == 0 or len(face_transforms) == 0:
            print("No tracking      ", end='\r')
            return
        
        # Create payload
        payload = {
            "face_points": [[i.x, i.y, i.z] for i in face_points[0]],
            "face_blendshapes": [{"name": c.category_name, "score": c.score} for c in face_blendshapes[0]],
            "face_transforms": [
                [face_transforms[0][0][0], face_transforms[0][0][1], face_transforms[0][0][2], face_transforms[0][0][3]],
                [face_transforms[0][1][0], face_transforms[0][1][1], face_transforms[0][1][2], face_transforms[0][1][3]],
                [face_transforms[0][2][0], face_transforms[0][2][1], face_transforms[0][2][2], face_transforms[0][2][3]],
                [face_transforms[0][3][0], face_transforms[0][3][1], face_transforms[0][3][2], face_transforms[0][3][3]]
            ]
        }
        #Send UPD packet
        sock.sendto(json.dumps(payload).encode('utf-8'), (args.host, args.port))
        print(f"Tracking... {int(1/frame_delta)}FPS", end='\r')
    # Set landmarker options
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=args.model_file),
        running_mode=VisionRunningMode.LIVE_STREAM,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        result_callback=onDetect)
    
    print(f"Starting MediapipeFaceLandmarker on {args.host}:{args.port}")
    with FaceLandmarker.create_from_options(options) as landmarker:
        # Store frame start times
        frame_start = None
        while True:
            # Frame start time
            frame_start = time.perf_counter()
            # Capture frame
            ret, frame = camera.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # Convert to mediapipe format
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            # Send to landmarker, timestamp in ms
            landmarker.detect_async(mp_image, int(time.perf_counter()*1000))
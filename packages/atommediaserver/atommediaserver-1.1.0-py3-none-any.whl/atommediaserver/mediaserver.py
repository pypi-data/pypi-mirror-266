from ffmpeg import FFmpeg, Progress
import ctypes
import threading
import time
import os

def run_server():
    current_path = os.path.dirname(os.path.abspath(__file__))

    dll_path = os.path.join(current_path, 'atommedia.dll')
    dll = ctypes.CDLL(dll_path)

    result = dll.RunMediaServer("".encode('utf-8'))

def run_rtsp(input_cam, output_postfix):
    current_path = os.path.dirname(os.path.abspath(__file__))
    path_to_decoder = os.path.join(current_path, 'decoder.exe')
    ffmpeg = (
        FFmpeg(executable=path_to_decoder)
        .option("y")
        .input("video=" + input_cam, f="dshow")
        .output(
            "rtsp://localhost:8554/" + output_postfix,
            {"codec:v": "libx264"},
            preset="ultrafast",
            tune="zerolatency",
            bufsize="500k",
            f="rtsp",
        )
    )
    
    ffmpeg.execute()

def run(input_cam1, output_postfix1, input_cam2, output_postfix2):  
    thread = threading.Thread(target=run_server)
    thread.start()

    time.sleep(5)

    thread = threading.Thread(target=run_rtsp, args=(input_cam1, output_postfix1))
    thread.start()

    time.sleep(1)

    thread = threading.Thread(target=run_rtsp, args=(input_cam2, output_postfix2))
    thread.start()
    
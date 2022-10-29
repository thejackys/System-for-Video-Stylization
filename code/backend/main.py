import subprocess
import re
from flask import Flask, jsonify, request, Response, send_file
from model import cast_model, fst_model
from flask_cors import CORS
import os
import cv2
import numpy as np
from module.stylizer_caller import del_files, style_transfer
import time
# ---------------------------------------------------------------------------- #
#                             Environment Variables                            #
# ---------------------------------------------------------------------------- #

VIDEO_FILE = 'static/videos/video.mp4'
VIDEO_OUTPUT = 'static/videos/video_styled.mp4'
FRAME_DIR = 'static/frames/'
LOG_FILE = 'static/log.txt'

# ---------------------------------------------------------------------------- #
#                                  Flask Setup                                 #
# ---------------------------------------------------------------------------- #

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------- #
#                                  Model Setup                                 #
# ---------------------------------------------------------------------------- #

model_cast = cast_model.CAST()
model_fst = fst_model.FST()


# ---------------------------------------------------------------------------- #
#                                    Routes                                    #
# ---------------------------------------------------------------------------- #

@app.route('/')
def index():
    return send_file('index.html')


# ---------------------------------------------------------------------------- #
#                                     APIs                                     #
# ---------------------------------------------------------------------------- #

@app.route('/api/style/image', methods=['POST'])
def api_style_image():

    # Extract Keyframes
    video_path = os.path.abspath(VIDEO_FILE)
    print(video_path)
    if os.path.exists(video_path) is False:
        return Response('Video not found', status=404)
    keyframes = request.values.get('keyframes', '').split(',')
    print(keyframes)
    if len(keyframes) == 0:
        return Response('No keyframes provided', status=400)
    try:
        cap = cv2.VideoCapture(video_path)
        image_keyframes = []
        keyframes = [int(k) for k in keyframes]
        for keyframe in keyframes:
            cap.set(cv2.CAP_PROP_POS_FRAMES, keyframe)
            ret, frame = cap.read()
            if ret:
                image_keyframes.append(frame)
    except:
        return Response('Video file or Keyframe error', status=400)
    
    # Choose model and apply
    if request.values.get('model') == 'FST':
        style = request.values.get('style')
        if style is None or style not in model_fst.styles:
            return Response('No style provided', status=400)
        results = model_fst.transform(image_keyframes, style, same_shape=False)
    elif request.values.get('model') == 'CAST':
        style = request.files.get('style')
        if style is None:
            return Response('No style provided', status=400)
        image_style = cv2.imdecode(np.frombuffer(style.read(), np.uint8), cv2.IMREAD_COLOR)
        image_style = cv2.cvtColor(image_style, cv2.COLOR_BGR2RGB)
        results = model_cast.transform(image_keyframes, [image_style], same_shape=False, 
                                        preserve_content=request.values.get('preserve_content', 'false', type=lambda x: x.lower() == 'true'),
                                        preserve_style=request.values.get('preserve_style', 'false', type=lambda x: x.lower() == 'true'))
    else:
        return Response('No model provided', status=400)
    
    # Save results
    del_files(FRAME_DIR)
    path_results = [os.path.join(FRAME_DIR, f'{keyframe:04d}.jpg') for keyframe in keyframes]
    for index, result in enumerate(results):
        cv2.imwrite(path_results[index], cv2.cvtColor(result, cv2.COLOR_RGB2BGR))

    # Cache Busting
    random_str = str(time.time())
    path_results = [path_result+'?'+random_str for path_result in path_results]

    # Return path to results
    return jsonify({'path': path_results})

@app.route('/api/style/video')
def api_style_video():
    try:
        os.remove(LOG_FILE)
    except:
        pass
    style_transfer(os.path.abspath(VIDEO_FILE), 
                   os.path.abspath(FRAME_DIR), 
                   os.path.abspath(VIDEO_OUTPUT), 
                   os.path.abspath('module/Stylization'),
                   os.path.abspath('module/ebsynth'),
                   os.path.abspath('static/tmp/frames'),
                   os.path.abspath('static/tmp/tmp'),
                   os.path.abspath(LOG_FILE),
                   )
    return jsonify({'status': 'success'})

@app.route('/api/style/status')
def api_style_status():
    status = ''
    # try:
    frames = int(subprocess.check_output('grep "inputFrames" ' + os.path.abspath(LOG_FILE), shell=True).decode('UTF-8').split(':')[1].strip())
    last_keyframe = int(subprocess.check_output('grep "lastKey" ' + os.path.abspath(LOG_FILE), shell=True).decode('UTF-8').split(':')[1].strip())
    total_frames = last_keyframe*2 + frames-last_keyframe
    processed_frames = int(subprocess.check_output('grep "image result was written to" ' + os.path.abspath(LOG_FILE) + ' | wc -l', shell=True).decode('UTF-8').strip())
    status = subprocess.check_output('grep "status" ' + os.path.abspath(LOG_FILE) + ' | tail -n 1', shell=True).decode('UTF-8').split(':')[1].strip()
    if status == 'finished':
        return jsonify({'percentage': processed_frames*100/total_frames, 'status': status, 'path': VIDEO_OUTPUT+'?'+str(time.time())})
    else:
        return jsonify({'percentage': processed_frames*100/total_frames, 'status': status})
    # except:
    #     return jsonify({'percentage': time.time()% 100, 'status': 'error'})


# ---------------------------------------------------------------------------- #
#                                     Main                                     #
# ---------------------------------------------------------------------------- #

if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)
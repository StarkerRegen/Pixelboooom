from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

import torch
import numpy as np
import base64
import PIL.ImageOps
from io import BytesIO
from PIL import Image
from forward import forwardModel, cat

app = Flask(__name__)

bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

model = forwardModel()

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('base.html')

@app.route('/explore', methods=['GET', 'POST'])
def explore():
    return render_template('explore.html')

@app.route('/playground', methods=['GET', 'POST'])
def playground():
    return render_template('playground.html')

@socketio.on('cav', namespace='/playground')
def playground_message(message):
    img = base64_to_image(message['data'][22:])
    model.set_edge(np.asarray(img))
    if(message['refresh']):
        model.resample(message['id'])
    result_fake, result_real, _, _, _ = model.forward()
    msg = {
        "id": message['id'],
        "data_0": image_to_base64(result_fake[0]),
        "data_1": image_to_base64(result_fake[1]),
        "data_2": image_to_base64(result_fake[2]),
        "data_3": image_to_base64(result_fake[3]),
        "data_4": image_to_base64(result_fake[4]),
        "data_5": image_to_base64(result_fake[5]),
        "data_6": image_to_base64(result_fake[6]),
        "data_7": image_to_base64(result_fake[7]),
        "data_8": image_to_base64(result_fake[8]),
        "data_9": image_to_base64(result_fake[9])
    }
    emit('my response', msg, namespace='/playground')
    # emit('my response', {'data':image_to_base64(img)}, namespace='/playground')

@socketio.on('connect', namespace='/playground')
def playground_connect():
    print('connect')

@socketio.on('disconnect', namespace='/playground')
def playground_disconnect():
    print('Client disconnected')

def base64_to_image(base64_data, image_path=None):
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    try:
        img_f = Image.open(image_data).convert('RGB')
        img = PIL.ImageOps.invert(img_f)
        if image_path:
            img.save(image_path)
        return img.resize((512,512))
    except(OSError, NameError):
        print('OSError')

def image_to_base64(img):
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str


if __name__ == '__main__':
    # app.run(debug=True, use_reloader=True)
    socketio.run(app, debug=True, use_reloader=True)
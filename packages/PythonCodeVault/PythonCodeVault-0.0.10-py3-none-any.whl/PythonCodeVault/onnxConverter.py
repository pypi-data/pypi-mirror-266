import tf2onnx, onnx
import os
from keras.models import load_model
import subprocess
from pathlib import Path


def keras2onnx(model_src_dir, dest_dir = 'c:\\Users\\fischekevinr\\Desktop\\models\\', opset = 17):
    dest_dir = os.path.abspath(dest_dir)
    if not Path(dest_dir).is_dir():
        raise Exception('Destination Path is not a Directory')

    name = os.path.split(model_src_dir)[1]
    print('Keras Model Name: ' + str(name))

    model = load_model(model_src_dir)
    onnx_model, _ = tf2onnx.convert.from_keras(model, opset=opset) # opset = 9

    onnx_model_name = name[:-3] + '.onnx'
    dest_path = os.path.join(dest_dir,  onnx_model_name)

    onnx.save(onnx_model, dest_path)

    subprocess.Popen(r'explorer /select,' + os.path.abspath(dest_path))
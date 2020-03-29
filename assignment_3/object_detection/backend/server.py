import base64
import os

from detection import YOLOv3DetectionModel
from flask import Flask, request, jsonify, after_this_request, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '../uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)


def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        resp = jsonify({'message': 'No file in the request'})
        resp.status_code = 400
        return resp
    file = request.files.getlist('files')[0]
    filename = secure_filename(file.filename)
    if '.' in filename and get_extension(file.filename) in ALLOWED_EXTENSIONS:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        try:
            model = YOLOv3DetectionModel()
            model.run_detection(file_path, file_path)
        finally:
            file_handle = open(file_path, 'rb')
            data = file_handle.read()
            base64_encoded_data = base64.b64encode(data)
            base64_message = base64_encoded_data.decode('utf-8')
            extension = get_extension(filename)

            try:
                os.remove(file_path)
                file_handle.close()
            except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)

            response = make_response(base64_message)
            response.mimetype = f'image/{extension}'
            response.headers['Content-Transfer-Encoding'] = 'base64'
            return response
    else:
        response = make_response('File type is not allowed')
        response.status_code = 400
        return response


if __name__ == "__main__":
    app.run()

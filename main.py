import argparse
import os

from flask import Flask
from flask import abort
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from werkzeug.utils import secure_filename

# from google.cloud import storage

import os
import uuid

app = Flask(__name__)
data_dir = ''

# Configure this environment variable via app.yaml
# CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']
# [end config]

@app.route("/")
def welcome():
    session_id = request.cookies.get('session_id')
    if session_id:
        all_done = request.cookies.get('all_done')
        if all_done:
            return render_template("thanks.html")
        else:
            return render_template("record.html")
    else:
        return render_template("welcome.html")

@app.route("/legal")
def legal():
    return render_template("legal.html")

@app.route("/start")
def start():
    response = make_response(redirect('/'))
    session_id = uuid.uuid4().hex
    response.set_cookie('session_id', session_id)
    return response

@app.route('/upload', methods=['POST'])
def upload():
    session_id = request.cookies.get('session_id')
    if not session_id:
        make_response('No session', 400)
    word = request.args.get('word')
    audio_data = request.data
    filename = word + '_' + session_id + '_' + uuid.uuid4().hex + '.ogg'
    secure_name = secure_filename(filename)
    # Left in for debugging purposes. If you comment this back in, the data
    # will be saved to the local file system.
    #with open(secure_name, 'wb') as f:
    #    f.write(audio_data)

    with open(f'{data_dir}{secure_name}', 'wb') as f:
        f.write(audio_data)
    # Create a Cloud Storage client.
    # gcs = storage.Client()
    # bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    # blob = bucket.blob(secure_name)
    # blob.upload_from_string(audio_data, content_type='audio/ogg')
    return make_response('All good')

# CSRF protection, see http://flask.pocoo.org/snippets/3/.
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session['_csrf_token']
        if not token or token != request.args.get('_csrf_token'):
            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = uuid.uuid4().hex
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token
# Change this to your own number before you deploy.
# app.secret_key = os.environ['SESSION_SECRET_KEY']
app.secret_key = 'a427d62b1f748b7af2a965c88a99005'


if __name__ == "__main__":
    # app.run(debug=True)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        type=str,
        # pylint: disable=line-too-long
        default='127.0.0.1',
        # pylint: enable=line-too-long
        help='服务器地址，0.0.0.0为外网访问')
    parser.add_argument(
        '--port',
        type=int,
        # pylint: disable=line-too-long
        default=5000,
        # pylint: enable=line-too-long
        help='端口地址')
    parser.add_argument(
        '--save_dir',
        type=str,
        # pylint: disable=line-too-long
        default='.',
        # pylint: enable=line-too-long
        help='文件存放地址')
    args = parser.parse_args()
    data_dir = args.save_dir
    if data_dir[-1] != '/':
        data_dir += '/'
    app.run(host=args.host, port=args.port, debug=True)

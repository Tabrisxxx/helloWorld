import os
from flask import Flask, render_template, request, redirect, url_for, abort, send_file
import flask
from werkzeug.utils import secure_filename
import os.path as op
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
# Place to save the folder and log file on flask
UPLOAD_FOLDER = './tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def hello_world():
    return redirect(url_for('upload_file'))


# welcome when successfully uploaded
@app.route('/welcome')
@app.route('/welcome/<name>')
def welcome(name=None):
    return render_template('welcome.html', name=name)


# Store Path
abs_dir_path = r'C:\Users\Admin\PycharmProjects\helloWorld\tmp'


# read and render file from user uploaded file or folder
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file[]')
        for file in files:
            upload_dirname = op.dirname(file.filename)
            local_dirname = op.join(app.config['UPLOAD_FOLDER'], upload_dirname)

            # check if the folder already exist
            # this feature could be change when we have multiple user
            # APPEND if dict exist
            if not op.exists(local_dirname):
                os.mkdir(local_dirname)

            #global abs_dir_path
            #abs_dir_path = local_dirname

            filename = op.join(upload_dirname, secure_filename(op.basename(file.filename)))
            file.save(op.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('list_files'))
    return render_template('index.html')


# ---------------- Reading file related ------------

# function use to get icon for uploaded files
def get_icons_for_file(filename):
    file_ext = Path(filename).suffix
    file_ext = file_ext[1:] if file_ext.startswith(".") else file_ext
    file_types = ["csv", "doc", "docx", "exe", "html", "jpg", "json", "jsx", "md", "mdx", "log",
                  "pdf", "png", "pptx", "raw", "rb", "sh", "svg", "tsx", "ttf", "txt", "xlsx", "xml", "yml"]
    file_icon_class = f"bi bi-filetype-{file_ext}" if file_ext in file_types else "bi bi-file-earmark"
    return file_icon_class


# get modified time
def get_time_file(time_sec: float) -> str:
    time_obj = datetime.fromtimestamp(time_sec)
    time_str = datetime.strftime(time_obj, '%Y-%m-%d %H:%M:%S')
    return time_str


# list of directory
@app.route('/list/', defaults={'req_path': ''})
@app.route('/list/<path:req_path>')
def list_files(req_path):
    # return render_template('welcome.html')
    abs_path = op.join(abs_dir_path, req_path)

    # return 404 if not exists such folder
    if not op.exists(abs_path):
        return abort(404)

    # check serve
    if op.isfile(abs_path):
        return send_file(abs_path)

    # Show content
    def list_folder_content(x):
        file_stat = x.stat()
        return{
            'name': x.name,
            'fIcon': "bi bi-folder-fill" if op.isdir(x.path) else get_icons_for_file(x.name),
            'relPath': os.path.relpath(x.path, abs_dir_path).replace("\\", "/"),
            'mTime': get_time_file(file_stat.st_mtime)
        }

    file_objs = [list_folder_content(x) for x in os.scandir(abs_path)]
    parent_folder = op.relpath(Path(abs_path).parents[0], abs_dir_path).replace("\\", "/")
    return render_template('files_list.html.j2', data={'files': file_objs, 'parentFolder': parent_folder})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4363, debug=True)

# coding=utf-8
from flask import Flask, request, send_from_directory, url_for, redirect
from flask import render_template
import os, chardet
import codecs

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'files')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def list_dir(path, result=[], name=None):
    files = os.listdir(path)
    for i in files:
        c, name_get = os.path.split(i)
        if os.path.isdir(os.path.join(path, i)):
            list_dir(os.path.join(path, i), result, name_get)
        else:

            if not name:
                m = chardet.detect(name_get)
                print m
                result.append(name_get.decode(m.get('encoding')))
            else:
                m = chardet.detect(name_get)
                print m
                result.append(os.path.join(str(name.decode(m.get('encoding'))), i))
    return result


@app.route('/')
def index():
    result = list_dir(UPLOAD_FOLDER, result=[])
    return render_template('index.html', res=result)


@app.route('/download/<path:name>')
def get_file(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], name)


@app.route('/<path:name>')
def get_content(name):
    path = os.path.join(UPLOAD_FOLDER, name)
    if IsEr().is_binary_file(path):
        cc = '二进制文件，请直接下载'
    else:
        with open(path, 'rb') as f:
            cc = ''
            res = f.readline()
            for x in range(100):
                if not res:
                    break
                cc += res
                res = f.readline()
    return cc


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files['file']
        filename = files.filename
        if filename.split('.')[-1] in ['txt', '']:
            utf = files.read().decode('gbk').encode('utf-8')
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                f.write(utf)
        else:
            files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('upload_file', filename=filename))

    return '''
        <!doctype html>
        <title>Upload  File</title>
        <h1>上传文件</h1>
        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=提交>
        </form>
        <br>
        <a href="/">返回主页</a>
        '''


class IsEr:
    _TEXT_BOMS = (
        codecs.BOM_UTF16_BE,
        codecs.BOM_UTF16_LE,
        codecs.BOM_UTF32_BE,
        codecs.BOM_UTF32_LE,
        codecs.BOM_UTF8,
    )

    def is_binary_file(self, file_path=None, file_obj=None):
        if file_path:
            with open(file_path, 'rb') as f:
                initial_bytes = f.read(8192)
                f.close()
        else:
            initial_bytes = file_obj.read(8192)
        return not any(initial_bytes.startswith(bom) for bom in self._TEXT_BOMS) and b'\0' in initial_bytes


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)

import os
import sys
from flask import Flask, request
import subprocess
from werkzeug.utils import secure_filename
app = Flask(__name__)
is_win = sys.platform == 'win32'

if is_win:
    UPLOAD_FOLDER = '.\crop_photo'
else:
    UPLOAD_FOLDER = './crop_photo/'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

AUDIO_GROUP = {
        'red': "红色识别成功",
        'blue': "蓝色识别成功",
        'green': "绿色识别成功",
        'black': "黑色识别成功",
        'purple': "紫色识别成功",
        'orange': "橙色识别成功",
        'gray': "灰色识别成功",
        'charge_begin': "开始充电",
        'charge_end': "充电完成",
        'test': '语音广播系统启动',
        'charge_find_begin': '电量不足，寻找充电点',
        'charge_find_end': '寻找充电点成功',
        'droping_begin': '开始投放',
        'droping_end': '投放完成',
        'task_begin': '无人机开始作业, 请注意远离作业区域',
        'takeoff_begin': '无人机开始起飞',
        'takeoff_end': '无人机起飞完成',
        'land_begin': '无人机开始降落',
        'land_end': '无人机降落完成',
        'prohibited_crop': '识别违禁作物,上传作物信息',
        'abnormal_crop': '识别异常作物,上传作物信息',
        'rover_move': '无人车启动',
        }

@app.route('/test')
def test():
    return 'OK'

@app.route('/audio_broadcast/<student_id>/<name>')
def audio_broadcast(student_id, name):
    text = AUDIO_GROUP.get(name)
    if text:
        if is_win:
            sound_path = os.path.join(os.getcwd(), "sounds", f"{name}.wav")
            subprocess.call(['powershell', '-c', f'(New-Object Media.SoundPlayer {sound_path}).PlaySync()'])
        else:
            os.system(f"say {text}")
        return 'OK'
    else:
        return '不支持此语音!'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/crop_photo/<student_id>', methods=['POST'])
def crop_photo(student_id):
    if request.method == 'POST':
        # check if the post request has the file part
        print(request.files)
        if 'file' not in request.files:
            return "无文件"
        file = request.files['file']
        print(file.filename)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return "无文件"
        if file and allowed_file(file.filename):
            #  filename = secure_filename(file.filename)
            filename = file.filename
            os.system(f"mkdir {os.path.join(app.config['UPLOAD_FOLDER'], str(student_id))}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(student_id), filename))
            return "上传成功"

if __name__ == '__main__':
    if is_win:
        os.system(".\play_test.bat")
    else:
        os.system("say 语音广播系统启动!")

    app.run(host='0.0.0.0', port='5000', debug=True)

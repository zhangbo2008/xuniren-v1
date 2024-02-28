# pip install click --upgrade
import librosa
from flask import Flask, request, jsonify, session
import os
import alitts
from pydub import AudioSegment
import requests
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'
wav_name = "test.wav"
usd_file_name = "DefaultOfficialInstance.usd"
usd_absolute_path = os.path.abspath(usd_file_name)
a2fserverurl='http://127.0.0.1:10246'

#计时器
record_time=0

# 获取wav时长
def get_duration(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None) # sr=None 保持原始采样率
        duration = librosa.get_duration(y=y, sr=sr)
        return duration
    except Exception as e:
        print(f"Error with librosa: {e}")
        return None

@app.route('/daduan', methods=['POST'])
def daduan():
    data = request.json
    global record_time
    # 接收 JSON 数据
    data_message = data["message"]
    # 判断是否在说话
    start_time = session.get('start_time')
    if start_time is None:
        response = {'message': 'not start'}
        return jsonify(response)  # 返回JSON响应
    
    elapsed_time = time.time() - start_time  # 计算经过的时间
    if elapsed_time < record_time:
        print("执行打断")
        # api执行暂停说话
        url = a2fserverurl+'/A2F/Player/Pause'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            'a2f_player': '/World/audio2face/Player'
        }
        response = requests.post(url, headers=headers, json=data)
        # 回答，在的，你说
        output = "在的，你说"
        wav_file = wav_name
        alitts.speakword(wav_file,output)
        print(2) 
        # 计算音频总长度，秒
        total_length = get_duration(wav_file)
        audio = AudioSegment.from_file(wav_file)
        length = len(audio) / 1000 # 获取的长度单位是毫秒，转换为秒钟
        
        url = a2fserverurl+'/A2F/Player/SetTrack'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            'a2f_player': '/World/audio2face/Player',
            'file_name': wav_name,
            'time_range': [0, -1]
        }
        response = requests.post(url, headers=headers, json=data)
        url = a2fserverurl+'/A2F/Player/Play'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            'a2f_player': '/World/audio2face/Player'
        }
        response = requests.post(url, headers=headers, json=data)
        # 返回收到的数据，这只是为了演示
        response = {'message': 'ok'}
    else:
        print("没有在说话，不执行打断")
        # 返回收到的数据，这只是为了演示
        response = {'message': 'failed'}
    return jsonify(response)  # 返回JSON响应

@app.route('/apppost', methods=['POST'])
def post_example():
    global record_time
    session['start_time'] = time.time()  # 记录开始时间
    data = request.json
    # 接收 JSON 数据
    # F:/audio2face-2023.1.1/exts/omni.audio2face.player_deps/deps/audio2face-data/tracks/
    # {"message":"你好吗"}
    data_message = data["message"]
    print(data_message)
    print(1) 
    # 根据中文TTS生成wav文件
    output = data_message
    wav_file = wav_name
    alitts.speakword(wav_file,output)
    print(2) 
    # 计算音频总长度，秒
    total_length = get_duration(wav_file)
    audio = AudioSegment.from_file(wav_file)
    length = len(audio) / 1000 # 获取的长度单位是毫秒，转换为秒钟
    
    url = a2fserverurl+'/A2F/Player/SetTrack'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    dat2a = {
        'a2f_player': '/World/audio2face/Player',
        'file_name': wav_name,
        'time_range': [0, -1]
    }
    response = requests.post(url, headers=headers, json=dat2a)
    url = a2fserverurl+'/A2F/Player/Play'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    dat2a = {
        'a2f_player': '/World/audio2face/Player'
    }
    response = requests.post(url, headers=headers, json=dat2a)
    record_time=total_length
    # 返回收到的数据，这只是为了演示
    data["message"]=total_length
    print(jsonify(data))
    return jsonify(data)

if __name__ == '__main__':
    print(usd_absolute_path)
    url = a2fserverurl+'/A2F/USD/Load'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'file_name': usd_absolute_path
    }
    response = requests.post(url, headers=headers, json=data)
    wav_absolute_pathdir = os.path.abspath(wav_name).replace("\\"+wav_name,"")
    print(wav_absolute_pathdir)
    url = a2fserverurl+'/A2F/Player/SetRootPath'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'a2f_player': '/World/audio2face/Player',
        'dir_path': wav_absolute_pathdir
    }
    response = requests.post(url, headers=headers, json=data)
    print("初始化完成")
    app.run(port=5000, debug=True)
 

# pip install click --upgrade
import librosa
from flask import Flask, request, jsonify
import os
import alitts
from pydub import AudioSegment
import requests

app = Flask(__name__)

wav_name = "test.wav"
usd_file_name = "DefaultOfficialInstance.usd"
usd_absolute_path = os.path.abspath(usd_file_name)
a2fserverurl='http://127.0.0.1:10246'

# 获取wav时长
def get_duration(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None) # sr=None 保持原始采样率
        duration = librosa.get_duration(y=y, sr=sr)
        return duration
    except Exception as e:
        print(f"Error with librosa: {e}")
        return None
    

@app.route('/apppost', methods=['POST'])
def post_example():
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
 

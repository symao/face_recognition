face_recognition是一个功能强大,使用简单的python人脸识别库, 提供人脸检测, 人脸特征点定位, 人脸识别功能. 具体功能见[github主页](https://github.com/ageitgey/face_recognition). 

## Ubuntu16.04下安装
---
1. 先安装dlib
```
git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build
cd build
cmake .. -DDLIB_USE_CUDA=0 -DUSE_AVX_INSTRUCTIONS=1
cmake --build
cd ..
python3 setup.py install --yes USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA
```
2. 安装face_recognition
```
pip3 install face_recognition
```

> python2安装应该类似, 把3替换成2就行. 安装完成后, 进入python, import face_recognition, 没有报错应该就安装成功了.

## windows下安装
```
pip install cmake

git clone https://github.com/davisking/dlib
cd dlib
python setup.py install --no DLIB_GIF_SUPPORT

pip install face_recognition
```

使用
---
1. API调用样例
见代码face_demo.py, so easy.
Python API见https://face-recognition.readthedocs.io/en/latest/readme.html
2. 人脸考勤机demo
见face_attendance.py, 基于pyqt5做的UI.

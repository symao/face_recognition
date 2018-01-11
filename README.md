介绍
---
face_recognition是一个功能强大,使用简单的python人脸识别库, 提供人脸检测, 人脸特征点定位, 人脸识别功能. 具体功能见[github主页](https://github.com/ageitgey/face_recognition). 

安装(Ubuntu16.04)
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

使用
---
见代码face_demo.py, so easy.
Python API见https://face-recognition.readthedocs.io/en/latest/readme.html
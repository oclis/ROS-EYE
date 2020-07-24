# ROS_EYE

ROS기반 영상인식기술을 이용한 물류적재로봇 제어 SW

산업현장 로봇을 쉽게 사용할 수 있도록 시뮬레이션과 연동되는 통합화면 으로 구성되는 영상처리모듈(OpenCV)과 로봇제어 모듈(ROS)이 통합된 로봇지능제어 패키지

# =============================================================== 
##설치
## blender Setting
blender version 2.80이상 버전 필요.
필수 모듈 설치
blender/2.83/python/bin$ ./python3.7m -m ensurepip 실행
blender/2.83/python/bin$ ./python3.7m -m pip install opencv-python 
blender/2.83/python/bin$ ./python3.7m -m pip install pyrealsense2 
blender/2.83/python/bin$ ./python3.7m -m pip install multipledispatch

## 마우스
1. 왼쪽마우스
→ 드래그 : 로봇팔 이동

2. 오른쪽마우스
→ 클릭 : 좌표 설정

## 키보드
"C" : View전환
"LCTRL" : View전환 특수키

## 메뉴판
Run : GUI에 표시된 좌표로 로봇 이동(동작)
Motion Delete : GUI에 표시된 좌표 삭제(GUI에서만 삭제됨)
Save : GUI에 표시된 좌표를 ~/Data 폴더에 *.txt로 저장
Load : ~/Data에서 좌표 불러오기
Program Shutdown : blender종료

# 로봇 동작
1. 오른쪽마우스로 좌표를 1개 이상 설정하고 Run버튼으로 로봇 동작
2. ~/Data에 저장된 좌표를 "Load"버튼으로 불러 와 Run버튼으로 로봇 동작

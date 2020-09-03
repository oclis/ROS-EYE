

# ROS_EYE

ROS기반 영상인식기술을 이용한 물류적재로봇 제어 SW

산업현장 로봇을 쉽게 사용할 수 있도록 시뮬레이션과 연동되는 통합화면 으로 구성되는 영상처리모듈(OpenCV)과 로봇제어 모듈(ROS)이 통합된 로봇지능제어 패키지

## 설치

git clone https://github.com/oclis/ROS-EYE.git

## Blender Setting

blender version 2.80이상 설치 [https://www.blender.org/](https://www.blender.org/) 참조
blender 설치 위치는 home 경로 위치에 설치

필수 모듈 설치
local에 설치된 python과 blender의 python은 개별관리 된다.
blender Python용 모듈을 별로도 다시 pip를 이용하여 설치 해야한다.
설치된 blender의 python 경로 "blender/2.83/python/bin" 폴더에서 pip를 이용해 blender python 모듈을 설치 가능하다.

#### 예시 이미지

<img src="/doc/guide5.png" width="800px" height="500px" title="px(픽셀) 크기 설정" alt="ROS_EYE"></img><br/>

#### Blender Python 추가 모듈 목록
	blender/2.83/python/bin$ ./python3.7m -m ensurepip 실행
	blender/2.83/python/bin$ ./python3.7m -m pip install opencv-python
	blender/2.83/python/bin$ ./python3.7m -m pip install pyrealsense2
	blender/2.83/python/bin$ ./python3.7m -m pip install multipledispatch

>아래의 오류가 발생한 경우
###
<pre>
<code>
###
WARNING: You are using pip version 19.0.3; however, version 20.2.2 is available.  
you should consider upgrading via the  
'/home/"user_name"/blender/2.83/python/bin/python3.7m -m pip install --upgrade pip' command
</pre>
</code>
###  
./python3.7m -m pip install --upgrade pip

### 실행

#### ROS_EYE가 설치 된 경로에서 blender를 실행
<img src="/doc/guide1.png" width="800px" height="500px" title="px(픽셀) 크기 설정" alt="ROS_EYE"></img><br/>

#### blender가 실행되면 ROS_EYE/blender에 있는 UR5_Handler.blend 파일을 연다.
<img src="/doc/guide2.png" width="800px" height="500px" title="px(픽셀) 크기 설정" alt="ROS_EYE"></img><br/>

#### blender 메뉴 라인의 Scripting 탭 선택
<img src="/doc/guide3.png" width="800px" height="500px" title="px(픽셀) 크기 설정" alt="ROS_EYE"></img><br/>


#### Scripting 탭에서 Run script 버튼 실행
<img src="/doc/guide4.png" width="800px" height="500px" title="px(픽셀) 크기 설정" alt="ROS_EYE"></img><br/>

<img src="/doc/guide6.jpg" width="800px" height="500px" title="px(픽셀) 크기 설정" alt="ROS_EYE"></img><br/>

### 마우스

1. 왼쪽마우스
   → 드래그 : 로봇팔 이동
2. 오른쪽마우스
   → 클릭 : 좌표 설정

### 키보드

로컬 축 기준 카메라 시점 변환  
 y 　z  
↑↗  
▣ → x  

H : 기본 위치로 이동  
W : +z방향 이동  
S : -z방향 이동  
D : +x방향 이동  
A : -x방향 이동  
Q : y축 기준 +방향 회전  
E : y축 기준 -방향 회전  
R : x축 기준 +방향 회전  
F : x축 기준 -방향 회전  

### 메뉴판

Run : GUI에 표시된 좌표로 로봇 이동(동작)
Motion Delete : GUI에 표시된 좌표 삭제(GUI에서만 삭제됨)
Save : GUI에 표시된 좌표를 ~/Data 폴더에 *.txt로 저장
Load : ~/Data에서 좌표 불러오기
Program Shutdown : blender종료

### 로봇 동작

1. 오른쪽마우스로 좌표를 1개 이상 설정하고 Run버튼으로 로봇 동작
2. ~/Data에 저장된 좌표를 "Load"버튼으로 불러 와 Run버튼으로 로봇 동작

# PI-SIGHT SW - GPS Racer

'GPS Racer'는 [PI-SIGHT](https://github.com/younsj97/PI-SIGHT_Helmet_HUD)를 랩타이머 또는 스마트폰 연동 블루투스 GPS 수신기로 사용할 수 있도록 하며, 랩타임 기록과 출력에 관련된 부분은 [Exit_Speed]([https://github.com/opencardev/crankshaft](https://github.com/djhedges/exit_speed)) 소프트웨어를 커스터마이징하여 만들어졌습니다.


## 기능

 - PI-SIGHT의 외장 GPS 모듈을 통해 10Hz GPS 데이터를 수신합니다.
 - 리시버 모드를 사용하면 PI-SIGHT는 스마트폰과 블루투스로 연결해 10Hz GPS 데이터를 전송하는 외장 GPS 모듈이 되며, RaceChrono 앱에서 외장 GPS 장치로 등록해 사용할 수 있습니다.
 - 랩타이머 모드를 사용하면 PI-SIGHT는 GPS 데이터를 자체적으로 사용해 가장 가까운 트랙을 자동으로 찾고, 랩타임 기록을 저장하며, 베스트 랩타임과 비교한 현재 시간 차이를 실시간으로 출력합니다.
 - 자세한 내용은 [VUDEV 홈페이지](https://sites.google.com/vudev.net/vudevnet/gpsracer-info) 또는 [설명서를 다운로드](https://github.com/younsj97/PI-SIGHT_SW_GPSRacer/blob/main/PI-SIGHT%20%EC%82%AC%EC%9A%A9%EC%84%A4%EB%AA%85%EC%84%9C-4%20(GPS%EB%A0%88%EC%9D%B4%EC%84%9C).pdf)하여 확인하세요


## 설치

 1. [라즈베리파이 imager 다운로드](https://www.raspberrypi.com/software/)하고 설치하세요
 2. [파일을 다운로드](http://naver.me/G1w16QKO)한 뒤, 압축을 해제하여 GPSRacer-16GB-yymmdd.img 파일을 만드세요.
 3. 라즈베리파이 imager를 실행하고, MicroSD를 PC에 연결한 뒤, Erase를 선택하여 메모리를 포맷하세요.
 4. 포맷이 완료되면, Use Custom을 선택하여 GPSRacer-16GB-yymmdd.img 파일을 선택하세요. (SSH를 비롯한 커스텀 세팅은 사용하지 마세요.)


## 주의사항

 - _GPS 신호 간섭으로 인해 후방카메라는 작동하지 않습니다._
 - _GPSRacer-16GB-yymmdd.img 펌웨어는 16GB microSD 메모리에 설치할 수 있습니다._
 - _32GB 이상의 메모리 카드를 사용해 boot 파티션의 용량 늘리고 싶은 경우, 우선 16GB 펌웨어를 설치한 뒤, [GParted를 통해 boot 파티션 크기를 늘리세요.](https://learn.adafruit.com/resizing-raspberry-pi-boot-partition/edit-partitions)_


## 커스터마이징

 - 기본 Raspberry pi OS로부터 PI-SIGHT GPS Racer 시스템을 적용하고 싶은 경우, [설정 방법](https://vudev.notion.site/GPS-Racer-7e79e486b4ea4caca37722aa5a25803d?pvs=4)을 참고하세요.

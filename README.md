# Motion/Rodent detector

Are you struggling with rodents, you do not know where they come from? This repo is for you.

## Description
This project is an OpenCV based mouse/rodent motion detector which also records the motion and saves it to the drive.
The recorded video includes frames stored in memory, hence, the saved video also shows few seconds prior the motion detected.
It helps to see what happens before the movement and where the rodent is arriving. In case a movement detected, you are going to get
an email notification with a picture showing the first frame of the real movement. Frequency of the email sent to you can be controlled
like an email in every 30 minutes.
You can follow the detector live on a small flask application.

I hope that project can help you to identify the root where rodents are entering into your property and seal the holes.
With the live surveillance you can always be sure that no mouse it running in the room where you like to enter. 

The project is based on material of Adrian at [pyimagesearch](https://www.pyimagesearch.com/) and applied for a specific use case. 
Thanks Adrian for the brilliant guide. The original tutorials can be in the "built on" section.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine. See deployment for notes on how to deploy the project on a live system.

### Installing

First clone the repository to your local machine or download it manually from git.

The requirements.txt contains all the neccessary packages, please make sure you install them. In order to do this, use your existing virtual env or create a new one, navigate to the root folder of the project and execute:

```
pip install -r requirements.txt
```

You can start the applaiction by executing the following command:

```
python main.py --ip:[your ip address] -- port [port number from (1024 to 65535)] 
```

Further parameters to define in command line:
* --ip: IP address of the device used for flask server (ipconfig in command line)
* --port: port number
* --frame-count: number of frames of the background
* --records: output directory where the recorded videos are saved
* --fps: FPS of video
* --codec: codec of recorded video
* --buffer-size: buffer size of video writer
* --area-threshold: area in pixels of small contours to be filtered out
* --email: frequency of emails (in minutes) to be sent in case of detection. Before turning it on, please set up the config file with email data.

You can use them like:
```
python main.py --ip: 192.168.178.6 -- port 6000 --records C:/Users/Videos --fps 20 --are-threshold 500 --email 30
```

### Features:
* Flask live video stream
* Motion detection with customizable frame number of background model and fps. For less/more sensitive motion detection adjust the threshold value in the detect function or set area threshold to 
filter out small contours as identified motion (most likely mirroring or light change).
* Motion recording as video saved to disk. You can change the buffer size that set the maximum number of frames cached in memory. The format of the video file is .avi.
* Sending email in case of motion detected. Please fill in the config file with your details. The provided config file has been set up for gmail smtp. To be able to send email through gmail, 
you can change either [your security settings](https://myaccount.google.com/lesssecureapps) (new developer account is recommended) or you can create a [google cloud platform project.](https://developers.google.com/gmail/api/quickstart/python).
You can turn on the email sending functionality by setting the --email.
  
 ### Sample gif made from a recorded video:
 ![sample-gif](https://github.com/sand-ki/roedent-motion-detector/blob/main/assets/mouse.gif)
 
 ## Built on:
* [Motion detection](https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/) at pyimagesearch
* [Event recorder](https://www.pyimagesearch.com/2016/02/29/saving-key-event-video-clips-with-opencv/) at pyimagesearch

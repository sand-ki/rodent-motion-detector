# USAGE
# python main.py --ip 192.168.178.216 --port 5000 --records /records --fps 20


from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2
from imutils.video import VideoStream
from sendemail import send_email
from motiondetector import MotionDetector
from eventrecorder import EventRecorder


outputFrame = None
lock = threading.Lock()
app = Flask(__name__)

#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=1).start()
time.sleep(2.0)

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

def detect_motion(frameCount):
	# grab global references to the video stream, records frame, and
	# lock variables
	global vs, outputFrame, lock
	detector = MotionDetector(weight=0.1)
	total = 0

	# initialize key clip writer and the consecutive number of
	# frames that have *not* contained any action
	er = EventRecorder(buff_size=args["buffer_size"])
	consecFrames = 0

	# loop over frames from the video stream
	time_now = datetime.datetime.now()
	while True:
		# resize, convert to grey scale and blur to "remove details"
		frame = vs.read()
		frame = imutils.resize(frame, width=640, height = 480)
		frame_mod = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		frame_mod = cv2.GaussianBlur(frame_mod, (15, 15), 0)
		updateConsecFrames = True

		# display date and time on the stream
		timestamp = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
		font = cv2.FONT_HERSHEY_SIMPLEX
		text_place = (8, frame.shape[0] - 8)
		font_scale = 0.4
		bgr = (0, 0, 255)
		thickness = 1
		cv2.putText(frame, timestamp, text_place, font, font_scale, bgr, thickness)

		# if the total number of frames has reached a sufficient
		# number to construct a reasonable background model, then
		# continue to process the frame
		if total > frameCount:
			motion = detector.detect(image=frame_mod, area_threshold=args["area_threshold"])
			if motion is not None:
				# unpack the tuple and draw the box surrounding the
				# "motion area" on the records frame
				(thresh, (minX, minY, maxX, maxY)) = motion
				cv2.rectangle(frame, (minX, minY), (maxX, maxY),
					(0, 0, 255), 2)
				consecFrames = 0

				# Send maximum one email in every X minutes
				if args["email"] is not None:
					if (datetime.datetime.now() - time_now).total_seconds() > 60 * args["email"]:
						_, saved_image = vs.read()
						time_now = datetime.datetime.now()
						image_path = f"{args['records']}/cap_img_{time_now.strftime('%Y%m%d-%H%M%S')}.png"
						cv2.imwrite(image_path, saved_image)
						send_email(image_path)

				# if we are not already recording, start recording
				if not er.recording:
					path = f"{args['records']}/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.avi"
					er.start(path, cv2.VideoWriter_fourcc(*args["codec"]),
							 args["fps"])

		# otherwise, no action has taken place in this frame, so
		# increment the number of consecutive frames that contain
		# no action
		if updateConsecFrames:
			consecFrames += 1

		# update the key frame clip buffer
		er.update(frame)

		# if we are recording and reached a threshold on consecutive
		# number of frames with no action, stop recording the clip
		if er.recording and consecFrames == args["buffer_size"]:
			er.finish()

		# update the background model and increment the total number
		# of frames read thus far
		detector.update(frame_mod)
		total += 1

		# acquire the lock, set the records frame, and release the
		# lock
		with lock:
			outputFrame = frame.copy()

	# if we are in the middle of recording a clip, wrap it up
	# if er.recording:
	# 	er.finish()

def generate():
	# grab global references to the records frame and lock variables
	global outputFrame, lock

	# loop over frames from the records stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the records frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the records frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	ap.add_argument("-rec", "--records", default="records",
					help="path to records directory")
	ap.add_argument("-fps", "--fps", type=int, default=32,
					help="FPS of records video")
	ap.add_argument("-c", "--codec", type=str, default="MJPG",
					help="codec of records video")
	ap.add_argument("-b", "--buffer-size", type=int, default=32,
					help="buffer size of video clip writer")
	ap.add_argument("-at", "--area-threshold", type=int, default=1,
					help="area in pixels of small contours to be filtered out")
	ap.add_argument("-em", "--email", type=int, default=None,
					help="frequency of emails (in minutes) to be sent in case of detection")
	args = vars(ap.parse_args())

	# start a thread that will perform motion detection
	t = threading.Thread(target=detect_motion, args=(
		args["frame_count"],))
	t.daemon = True
	t.start()

	# start the flask app
	app.run(host=args["ip"], port=args["port"],
			debug=True,
			threaded=True, use_reloader=False)

# release the video stream pointer
vs.stop()
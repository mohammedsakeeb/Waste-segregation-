import cv2
import RPi.GPIO as GPIO
from time import sleep
import os
import socket
from PIL import Image

def server_connectivity(image_address):
    s = socket.socket()
    HOST = '127.0.0.1'
    port = 8080
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect((HOST, port))

    cap = cv2.VideoCapture(0)  

    ret, frame = cap.read()
    if not ret:
        print("Error: Couldn't capture a frame from the webcam.")
        cap.release()
        return None

    # Save the captured image
    image_address = "captured_image.jpg"
    cv2.imwrite(image_address, frame)
    cap.release()

    # Resize the image using PIL
    i = Image.open(image_address)
    i = i.resize((128, 128))
    i.save("resized_image.jpg")

    file1 = open("resized_image.jpg", 'rb')

    fsize = os.stat("resized_image.jpg").st_size
    print(fsize)
    client_socket.send(str(fsize).encode())
    l = file1.read(fsize)
    client_socket.sendall(l)
    print("Sent")
    prediction = client_socket.recv(1024).decode()
    print(prediction)
    client_socket.close()
    return prediction


def motor_controller(GPIO, classifier, angle=90, servoPIN=22,angle2=90,servoPIN2 = 23):
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(servoPIN, GPIO.OUT)
	GPIO.setup(servoPIN2, GPIO.OUT)
	
	# elbow motor
	p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
	q = GPIO.PWM(servoPIN2, 50) # GPIO 17 for PWM with 50Hz
	p.start(0)
	q.start(0)
	duty = angle / 18
	duty += 2.5
	duty2 = angle2 / 18
	duty2 += 2.5
	if classifier == 1:
		while duty >= 5.0:
			duty -= 0.1
			p.ChangeDutyCycle(duty)
			sleep(0.05)
		sleep(0.5)
		
		while duty2 >= 2.5:
			duty2 -= 0.1
			q.ChangeDutyCycle(duty2)
			sleep(0.001)
		sleep(0.5)
		
		while duty2 <= 7.2:
			duty2 += 0.1
			q.ChangeDutyCycle(duty2)
			sleep(0.001)
		sleep(0.5)
		
		while duty <= 7.0:
			duty += 0.1
			p.ChangeDutyCycle(duty)
			sleep(0.05)
		
	elif classifier == 2:
		while duty <= 7.0:
			duty += 0.1
			p.ChangeDutyCycle(duty)
			sleep(0.05)
		sleep(0.5)
		
		while duty2 >= 2.5:
			duty2 -= 0.1
			q.ChangeDutyCycle(duty2)
			sleep(0.001)
		sleep(0.5)
		
		while duty2 <= 7.2:
			duty2 += 0.1
			q.ChangeDutyCycle(duty2)
			sleep(0.001)
		sleep(0.5)
	
	else:	
		while duty <= 9.0:
			duty += 0.1
			p.ChangeDutyCycle(duty)
			sleep(0.05)
		sleep(0.5)
		
		while duty2 >= 2.5:
			duty2 -= 0.1
			q.ChangeDutyCycle(duty2)
			sleep(0.001)
		sleep(0.5)
		
		while duty2 <= 7.2:
			duty2 += 0.1
			q.ChangeDutyCycle(duty2)
			sleep(0.0051)
		sleep(0.5)
		
		while duty >= 7.0:
			duty -= 0.1
			p.ChangeDutyCycle(duty)
			sleep(0.05)
	
	
	p.stop()
	q.stop()

def camera_controller(camera=None, name=None):
    if camera is None:
        camera = cv2.VideoCapture(0)  # 0 is usually the default index for the first webcam
    if name is None:
        name = 'x.jpg'
    else:
        name = str(name) + '.jpg'
    print("camera")

    # Capture an image from the webcam
    ret, frame = camera.read()
    if ret:
        cv2.imwrite(name, frame)
    else:
        print("Error capturing an image from the webcam")

    print("re")
    return name




def sensor_controller(GPIO):
	sensor = x
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(sensor,GPIO.IN)
	if GPIO.input(sensor):
		return True
	return False

def main():
    GPIO.setmode(GPIO.BOARD)

    name = 0

    try:
        while True:
            name = name + 1
            response = server_connectivity(f"{name}.jpg")
            if response is not None:
                motor_controller(GPIO, classifier=int(response))
                sleep(5)

    except KeyboardInterrupt:
        GPIO.cleanup()
        print(f"Serviced {name} images")

if __name__ == '__main__':
    main()

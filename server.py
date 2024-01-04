import socket
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import numpy as np
import cv2
from scipy.stats import kurtosis
import operator
import time
import os


s = socket.socket()

def is_recyclable(image):
	image3 = image.copy()
	image2 = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
	lower = np.array([155,25,0])
	upper = np.array([179,255,255])
	mask = cv2.inRange(image2,lower, upper)
	image3 = cv2.bitwise_and(image3, image3, mask=mask)
	histr = cv2.calcHist([image3],[2],None,[256],[0,256])
	cv2.imwrite('x-red.jpg', image3)
	k = kurtosis(histr)
	print(k)
	if k >= 242 and k<=251:
		return True
	return False




def get_prediction(image_file, model=None):
	image = cv2.imread(image_file)
	recyclable = is_recyclable(image)
	image = image.astype('float')/255.0
	x = img_to_array(image)
	x = np.expand_dims(x, axis = 0)
	c = model.predict(x)[0]

	output_list = ['Cardboard', 'Glass', 'Metal', 'Paper', 'Plastic', 'Trash']

	index, value = max(enumerate(c), key=operator.itemgetter(1))

	bio = ['Paper', 'Cardboard']
	rec = ['Glass', 'Metal']
	non_rec = ['Plastic', 'Trash']

	m = output_list[index]
	if recyclable:
		m = 'Metal'
		# if c[1] + c[2] > 0.15:
		# 	m = 'Metal'
	# print(m)
	print(c)
	if m in bio:
		print("Biodegradable")
		# send_android_notification("Biodegradable")
		return 3
	elif m in rec:
		print("Recyclable")
		# send_android_notification("Recyclable")
		return 1
	else:
		print("Non-recyclable")
		# send_android_notification("Non-recyclable")
		return 2


model = load_model('tf_model.h5')
file_name = 'X.jpg'
# file_path = 'D://College//Capstone//'
HOST = '127.0.0.1'
PORT = 8080
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(10)
print("Listening")
while True:
	s, addr = server_socket.accept()
	print('Connected with client with address: ', addr)
	fsize = int(s.recv(1024).decode())
	print(fsize)
	file = open(file_name, 'wb')
	print('Receiving image...')
	l = s.recv(1)
	t = 0
	while (l):
		# if os.path.exists('X.jpg'):
		# 	with open(file_name, 'wb') as file:
		# 		file.write(l)
		# else:
		# with open(file_name, 'ab') as file:
		# 	file.write(l)
		file.write(l)
		file.close()
		size = os.stat(file_name).st_size
		if size == fsize:
			t = 1
			break
		file = open(file_name, 'ab')
		l = s.recv(1)
		# fsize -= 1
	print('T')
	# l = s.recv(fsize)
	# file.write(l)
	print('Done')
	if t == 0:
		file.close()
	prediction = get_prediction(file_name, model)
	s.sendall(str(prediction).encode())
	os.remove(file_name)

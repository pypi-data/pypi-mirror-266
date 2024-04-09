import matplotlib.pyplot as plt
import numpy as np
import os
import time

def keep_or_not(yes_no):
		if yes_no == "y" or yes_no == "":
			pass
		elif yes_no == "n":
			return True
			#move to other path?
		else:
			yes_no = input("Keep this image? y/n:\n>>>")
			keep_or_not(yes_no)


n = 10
m = 50
list_of_image_paths = [i for i in os.listdir() if i[:4]=="img_"]
pth = ""
if "deleted" not in os.listdir("."):
	pth="deleted"
	os.mkdir(pth)
else:
	pth= "deleted_{}".format(time.time())
	os.mkdir(pth)

if pth=="":
	exit()

for i,img in enumerate(list_of_image_paths):
	array = np.load(img)
	plt.imshow(array)
	plt.title(img)
	plt.show(block=False)
	yes_no = input("Keep this image? y/n:\n>>>")
	print("yes or no: ",yes_no)
	delete=keep_or_not(yes_no)
	if delete:
		os.rename(img, pth+"/"+img)
	
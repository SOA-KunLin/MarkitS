import os
import cv2
import csv
import datetime
import sys
from pathlib import Path

def replace_circle(img_path, label_path, image_name, output_dir2):
    img = cv2.imread(img_path)

    height_, width_= img.shape[:2]

    with open(label_path ,'r', encoding='utf-8') as f: #read label file
        lines = f.readlines()

    for j in lines:
        parts = j.strip().split(" ")

        _, x, y, w, h = map(float, parts)

        xmax = int((x*width_) + (w * width_)/2.0)
        xmin = int((x*width_) - (w * width_)/2.0)
        ymax = int((y*height_) + (h * height_)/2.0)
        ymin = int((y*height_) - (h * height_)/2.0)

        #replace circle
        x = [xmin, ymin, xmax, ymax]
        color = (255, 255, 255)#red 0, 0, 255
        c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
        cv2.rectangle(img, c1, c2, color, thickness=-1)
        

    cv2.imwrite(output_dir2 + image_name + "_circle.png", img)

start_time = datetime.datetime.now()

#img_dir = "./" + sys.argv[1] + "/"
img_dir = str(Path(sys.argv[1]).resolve()) + "/"
label_dir = './exp_circle/labels/'
output_dir2 = './output_replace_circle_blank/'
os.makedirs(output_dir2, exist_ok=True)
label_file = os.listdir(label_dir)


for i in range(len(label_file)):
    image_name = label_file[i].split(".")[0]
    img_path = img_dir + image_name + '.png'
    label_path = label_dir + image_name + '.txt'
    if os.path.isfile(label_path):
        replace_circle(img_path, label_path, image_name, output_dir2)

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

import os
import cv2
import csv
import datetime
import sys
from pathlib import Path

def cut_img(img_path, label_path, image_name, output_dir2):
    img = cv2.imread(img_path)
    img2 = cv2.imread(str(Path(__file__).resolve().parent / "V.png")) #the images to replace R

    height_, width_= img.shape[:2]

    with open(label_path ,'r', encoding='utf-8') as f: #read label file
        lines = f.readlines()
    
    count = 1
    for j in lines:
        img = cv2.imread(img_path)
        parts = j.strip().split(" ")

        _, x, y, w, h = map(float, parts)

        xmax = int((x*width_) + (w * width_)/2.0)
        xmin = int((x*width_) - (w * width_)/2.0)
        ymax = int((y*height_) + (h * height_)/2.0)
        ymin = int((y*height_) - (h * height_)/2.0)

        #replace R

        re_img2= cv2.resize(img2,(xmax-xmin, ymax-ymin)) #resize image2
        img[ymin:ymax, xmin:xmax] = re_img2 #replace images2 to R

        cv2.imwrite(output_dir2 + image_name + "_replace_" + str(count) + ".png", img)

        count += 1

start_time = datetime.datetime.now()

#img_dir = "./"+ sys.argv[1] + "/"
img_dir = str(Path(sys.argv[1]).resolve()) + "/"
label_dir = './exp_200/labels/'
output_dir2 = './output_replaceR/' #replace R
os.makedirs(output_dir2, exist_ok=True)
img_file = os.listdir(img_dir)


with open('./replace_data.csv', "r", encoding='utf-8') as file:
    data1 = list(csv.reader(file, delimiter="," ))

for i in range(len(data1)):
    image_name = data1[i][0].split(".")[0]
    img_path = img_dir + image_name + '.png'
    label_path = label_dir + image_name + '.txt'
    if os.path.isfile(label_path):
        cut_img(img_path, label_path, image_name, output_dir2)

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

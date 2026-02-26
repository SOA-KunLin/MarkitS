import os
import os.path
import cv2
import datetime
import sys
from pathlib import Path

def cut_img(img_path, label_path, image_name, output_dir, f2):
    img = cv2.imread(img_path)

    height_, width_ = img.shape[:2]

    with open(label_path ,'r', encoding='utf-8') as f: #read label file
        lines = f.readlines()
    
    count = 1
    for line in lines:
            
        parts = line.strip().split(" ")
        _, x, y, w, h = map(float, parts)

        xmax = int((x*width_) + (w * width_)/2.0)
        xmin = int((x*width_) - (w * width_)/2.0)
        ymax = int((y*height_) + (h * height_)/2.0)
        ymin = int((y*height_) - (h * height_)/2.0)

        if ymax > (height_ - 8):
            ymax = height_
        
        #R image
        out = img[ymin:ymax, xmin:xmax]
        output_filename = f"{image_name}_{count}.png"
        cv2.imwrite(os.path.join(output_dir, output_filename), out)
            
        #R image coordinates
        coord = f"{xmin} {xmax} {ymin} {ymax}"
        f2.write(f"{output_filename} {coord}\n") #store in R_label.txt

        count += 1

start_time = datetime.datetime.now()

#img_dir = "./" + sys.argv[1] + "/"
img_dir = str(Path(sys.argv[1]).resolve()) + "/"
label_dir = './exp_200/labels/'
output_dir = './output_R/' #store R image
os.makedirs(output_dir, exist_ok=True)

with open('./R_label.txt', 'w', encoding="utf-8") as f2:
    for img_file in os.listdir(img_dir):
        image_name, ext = os.path.splitext(img_file) #filename + .png
        img_path = os.path.join(img_dir, img_file)
        label_path = os.path.join(label_dir, image_name + '.txt')

        if os.path.isfile(label_path):
            cut_img(img_path, label_path, image_name, output_dir, f2)

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

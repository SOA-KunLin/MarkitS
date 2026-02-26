import os
import os.path
import cv2
import datetime

def cut_img(img_path, label_path, image_name, output_dir, f2):
    img = cv2.imread(img_path)

    height_, width_= img.shape[:2]

    with open(label_path ,'r', encoding='utf-8') as f: #read label file
        lines = f.readlines()
    
    count = 1
    for line in lines:
        img = cv2.imread(img_path)
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
        cv2.imwrite(output_dir + image_name + "_" + str(count) + ".png", out)

        coord = f"{xmin} {xmax} {ymin} {ymax}"
        f2.write(image_name + "_" + str(count) + ".png" + " " + coord + '\n')

        count += 1

start_time = datetime.datetime.now()

img_dir = './generate_smiles/'
label_dir = './exp_gen/labels/'
output_dir = './output_gen/' #gen R image
os.makedirs(output_dir, exist_ok=True)

img_file = os.listdir(img_dir)

f2 = open('./R_label_gen.txt', 'w', encoding="utf-8")
for i in img_file:
    image_name = i.split(".")[0]
    img_path = img_dir + image_name + '.png'
    label_path = label_dir + image_name + '.txt'
    if os.path.isfile(label_path):
        cut_img(img_path, label_path, image_name, output_dir, f2)


f2.close()

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

import os
import cv2
import csv
import ast
import torch
from molscribe import MolScribe
from huggingface_hub import hf_hub_download
import pandas as pd
import re
import sys
import datetime
from pathlib import Path

#os.environ["CUDA_VISIBLE_DEVICES"] = "0"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#generate replace img
def replace_img(img_path, label_path, image_name, output_dir2):
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


def predict_smiles(dir_path):
    ckpt_path = hf_hub_download('yujieq/MolScribe', 'swin_base_char_aux_1m.pth')
    model = MolScribe(ckpt_path, device=device)

    allFileList = os.listdir(dir_path)

    list_latex_del = []
    for filename in allFileList:
        image_path = os.path.join(dir_path, filename)
        output = model.predict_image_file(image_path, return_atoms_bonds=True, return_confidence=True)

        smiles_parts = output['smiles'].split('.')
        res_smiles = max(smiles_parts, key=len) if len(smiles_parts) > 1 else output['smiles']
        res_smiles = re.sub('\[R\w\]', '*', res_smiles)
        res_smiles = res_smiles.replace('[3H]', '[T]')
        #res_smiles = re.sub('\[Zn\]', '*', res_smiles)

        if "[V]" not in res_smiles:
            list_latex_del.append(filename.replace('replace_',''))


    return list_latex_del


start_time = datetime.datetime.now()

#img_dir = "./" + sys.argv[1]+ "/"
img_dir = str(Path(sys.argv[1]).resolve()) + "/"
label_dir = './exp_200/labels/'
output_dir_ion = './output_ion/' #replace R
os.makedirs(output_dir_ion, exist_ok=True)


with open('./SMILES_ion.txt', "r", encoding='utf-8') as file:
    lines = file.readlines()

list_ion = ast.literal_eval(lines[0].strip())
for i in range(len(list_ion)):
    filename = list_ion[i][0]
    smiles = list_ion[i][1]
    img_path = img_dir + filename + '.png'
    label_path = label_dir + filename + '.txt'
    if os.path.isfile(label_path):
        replace_img(img_path, label_path, filename, output_dir_ion)

with open('./R_label_latex_ver1.txt' ,'r', encoding='utf-8') as f: #read label file
        lines = f.readlines()

list_yolo_del = predict_smiles(output_dir_ion)
print(list_yolo_del)

with open('./R_label_latex_ver2.txt', 'w', encoding="utf-8") as f2:
    for j in lines:
        if j.split(' ')[0] in list_yolo_del:
                print(j.strip())
        else:
            f2.write(j)

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

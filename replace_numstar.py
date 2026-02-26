import difflib
import csv
import re
import pandas as pd
from collections import Counter
import datetime

start_time = datetime.datetime.now()
#with open('./SMILES_ver1.csv', "r", encoding='utf-8') as file:
#    data1 = list(csv.reader(file, delimiter="," ))

with open('./replace_data.csv', "r", encoding='utf-8') as file:
    data1 = list(csv.reader(file, delimiter="," ))


with open('R_label_latex_ver2.txt' ,'r', encoding='utf-8') as f: #yolo R
    lines = f.readlines()



list_result = []

for filename, smiles in data1:
    filename = filename.replace('.png','')
    print(filename)
    print(smiles)
    res = re.findall(r'\[\d+\*\]', smiles) #replace [num*] by Rnum
    yolo_list = [k.split(' ')[5].strip() for k in lines if re.sub(r'_\d+\.png$', '', k.split(' ')[0]) == filename]
    if res:
        for i in range(len(res)):
            #print(res[i])
            #digit = re.search('\d+', res[i]).group()
            smiles_R = res[i].replace('*]','').replace('[','R')
            if smiles_R in yolo_list:
                smiles = smiles.replace(res[i], '[' + smiles_R + ']', 1)
                yolo_list.remove(smiles_R)
            elif smiles_R not in yolo_list and sum(1 for j in res if j  == res[i]) > 1:
                smiles = smiles.replace('[' + smiles_R + ']', res[i], 1)

    print(smiles)


    if len(re.findall(r'\*',smiles)) == 1: #only one * in SMILES

        smiles_R = re.findall('\[[AEGLMQORXYZa-z0-9]+[a-zA-Z]*\]', smiles)
        for k in range(len(smiles_R)):
            smiles_R[k] = re.sub(r'\[[ON]R(\d+)\]|\[CO2R(\d+)\]|\[NR(\d+)\]', lambda m: f'[R{m.group(1) or m.group(2)}]', smiles_R[k])
            smiles_R[k] = re.sub(r'\[([xyz])\]',lambda m: f'[{m.group(1).upper()}]', smiles_R[k])
        print(smiles_R)

        yolo_R = []
        for j in lines:
            if re.sub(r'_\d+\.png$', '', j.split(' ')[0]) == filename:
                R = '[' + j.split(' ')[5].strip() + ']'
                R = re.sub(r'\[([xyz])\]',lambda m: f'[{m.group(1).upper()}]', R)
                yolo_R.append(R)
        print(yolo_R)

        counter1 = Counter(smiles_R)
        counter2 = Counter(yolo_R)

        diff = counter2 - counter1
        if len(diff) == 1:
            replace_r = list(diff.keys())[0]
            smiles = re.sub(r'\[\d+\*\]|\*', replace_r, smiles)
            #smiles = smiles.replace('*', replace_r)

    print(smiles)

    list_result.append([filename + '.png', smiles])
    print("----------------------")


df = pd.DataFrame(list_result)
df.to_csv('SMILES_ver1.csv', encoding='utf-8', index=False, header=False)

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

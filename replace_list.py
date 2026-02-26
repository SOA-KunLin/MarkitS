import difflib
import csv
import re
import pandas as pd
import datetime

with open('./SMILES_orig.csv', "r", encoding='utf-8') as file:
    data1 = list(csv.reader(file, delimiter="," ))  #orig images SMILES

with open('./R_label_latex_ver2.txt' ,'r', encoding='utf-8') as f: #yolo R
    lines = f.readlines()

def count_mol_R(file_name, smiles): #Check if the number of '*' in SMILES and the number of yolo R are the same.
    count_mol_R = smiles.count('*') + len(re.findall(r'\[[AEGLMQRXYZa-z0-9\(\)]+[a-zA-Z]*\]|\[OR\d+\]|\[NR\d+\]|\[CO2R\d+\]|\[NHR\d+\]|\[R[A-Za-z0-9]*O\]', smiles)) - len(re.findall(r'\[[w]\]', smiles))

    count_yolo_R = 0 # number of yolo R
    for k in lines:
        if re.sub(r'_\d+\.png$', '', k.split(' ')[0]) == file_name:
            count_yolo_R += 1
    print(count_mol_R)
    print(count_yolo_R)
    return count_mol_R == count_yolo_R

def mol_num(file_name, smiles):
    
    res_star = re.findall(r'\[\d+\*\]', smiles) #list of the [digit]* and [XYZ...] in the SMILES    
    res_xyz = re.findall(r'\[[AEGLMQRXYZa-z0-9\(\)]+[a-zA-Z]*\]|\[OR\d+\]|\[NR\d+\]|\[NHR\d+\]|\[CO2R\d+\]', smiles) 
    res_w = re.findall(r'\[[w]\]', smiles)

    #count_yolo = sum(1 for k in lines if k.split()[0].split('_')[0] == file_name)# the number of yolo
    res_star_replace = [j.replace('*]','').replace('[','R') for j in res_star]
    yolo_list = [k.split(' ')[5].strip() for k in lines if re.sub(r'_\d+\.png$', '', k.split(' ')[0]) == file_name]
    count_yolo = len(yolo_list)

    for ele in res_star_replace:
        if ele in yolo_list:
            yolo_list.remove(ele)
        else:
            return False

    print(f"res_star {res_star}, res_xyz {res_xyz}, count_yolo {count_yolo}")
    return len(res_star) + len(res_xyz) - len(res_w) == count_yolo

def replace_R(file_name, smiles):
    res = re.findall(r'\[\d+\*\]', smiles)
    if res:
        for i in range(len(res)):
            digit = re.search('\d+', res[i]).group()
            for k in lines:
                if re.sub(r'_\d+\.png$', '', k.split(' ')[0]) == file_name:
                    yolo_R_text = k.split(' ')[5].strip()
                    if 'R' in yolo_R_text:
                        yolo_R_num = re.sub(r'R(\d+)[A-Za-z]*', r'\1', yolo_R_text)
                        if digit == yolo_R_num:
                            smiles = smiles.replace(res[i], '[' + yolo_R_text + ']', 1)
                            break
    return smiles

list_replace = []
list_result = []
error_list = []
ion_list = []

start_time = datetime.datetime.now()

for filename, smiles in data1:
    filename = filename.replace('.png','')#data1[i][0].replace('.png','')#filename.replace('.png','')
    smiles = smiles.replace(',', '')#data1[i][1].replace(',', '')#smiles.replace(',', '')
    print(filename)
    print(smiles)
    if count_mol_R(filename, smiles): #
        if mol_num(filename, smiles):
            smiles = replace_R(filename, smiles)
            list_result.append([filename + '.png', smiles])
        else:
            list_replace.append([filename + '.png', smiles])
    else:
        if smiles.count('*') == 0:
            list_result.append([filename + '.png', smiles])
        elif re.findall(r'[A-Za-z]+[\+\-]', smiles):
            ion_list.append([filename, smiles])
        else:
            error_list.append([filename, smiles])


with open('SMILES_error.txt', 'w', encoding="utf-8") as f2:
    for err in error_list:
        f2.write(str(err) + '\n')


df = pd.DataFrame(list_replace)
df.to_csv('replace_data.csv', encoding='utf-8', index=False, header=False)

df2 = pd.DataFrame(list_result)
df2.to_csv('SMILES_first.csv', encoding='utf-8', index=False, header=False)

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

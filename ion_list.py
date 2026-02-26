import difflib
import csv
import re
import pandas as pd

with open('./SMILES_orig.csv', "r", encoding='utf-8') as file:
    data1 = list(csv.reader(file, delimiter="," ))  #orig images SMILES

with open('R_label_latex.txt' ,'r', encoding='utf-8') as f: #yolo R
    lines = f.readlines()

#def count_mol_R(file_name, smiles): #Check if the number of '*' in SMILES and the number of yolo R are the same.
#    count_mol = smiles.count('*') #number of '*' in SMILES

#    count_R = 0 # number of yolo R
#    for k in lines:
#        if k.split(' ')[0].split('_')[0] == file_name:
#            count_R += 1

#    return count_mol == count_R

ion_list = []
zn_list = []
error_list = []

for filename, smiles in data1:
    filename = filename.replace('.png','')

    count_mol_R = smiles.count('*') + len(re.findall(r'\[[AEGLMQRXYZa-z0-9\(\)]+[a-zA-Z]*\]|\[OR\d+\]|\[NR\d+\]|\[CO2R\d+\]|\[NHR\d+\]|\[R[A-Za-z0-9]*O\]', smiles)) - len(re.findall(r'\[[w]\]', smiles))
    
    count_yolo_R = 0 # number of yolo R
    for k in lines:
        if re.sub(r'_\d+\.png$', '', k.split(' ')[0]) == filename:
            count_yolo_R += 1

    if count_mol_R != count_yolo_R:
        #print(filename)
        #print(smiles)
        #print(f"count_mol_R {count_mol_R}")
        #print(f"count_yolo_R {count_yolo_R}")
        if re.findall(r'[A-Za-z]+[\+\-]', smiles):
            ion_list.append([filename, smiles])
        elif re.findall(r'\[Zn\]',smiles):
            zn_list.append(filename)
            #print(filename)
        else:
            error_list.append([filename, smiles])

print(ion_list)
with open('SMILES_ion.txt', 'w', encoding="utf-8") as f:
    f.write(str(ion_list) + '\n')



with open('./R_label_latex_ver1.txt', 'w', encoding="utf-8") as f2:
    for j in lines:
        if re.sub(r'_\d+\.png$', '', j.split(' ')[0]) in zn_list and j.split(' ')[5].strip() == 'Zn':
                print(j.strip())
        else:
            f2.write(j)


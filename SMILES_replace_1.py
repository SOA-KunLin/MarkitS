import csv
import re
import pandas as pd
import datetime
from collections import Counter
from pathlib import Path
import jpype
import jpype.imports
from jpype.types import *

jpype.startJVM(classpath=[str(Path(__file__).resolve().parent / "cdk-2.11.jar")])

from org.openscience.cdk.smiles import SmilesParser, SmilesGenerator
from org.openscience.cdk.layout import StructureDiagramGenerator
from org.openscience.cdk.depict import DepictionGenerator
from org.openscience.cdk import DefaultChemObjectBuilder
from org.openscience.cdk.exception import InvalidSmilesException
from org.openscience.cdk.interfaces import IAtomContainer

sp = SmilesParser(DefaultChemObjectBuilder.getInstance())
sg = SmilesGenerator.unique()

start_time = datetime.datetime.now()

with open('./SMILES_orig.csv', "r", encoding='utf-8') as file:
   data_orig = list(csv.reader(file, delimiter="," ))

points_data_orig = {item[0]: item[1] for item in data_orig} #filename:smiles

with open('SMILES_ver2.csv', "r", encoding='utf-8') as file:
    data = list(csv.reader(file, delimiter="," ))

with open('R_label_latex_ver2.txt' ,'r', encoding='utf-8') as f: #read label file
    lines = f.readlines()

with open('./SMILES_R.csv', "r", encoding='utf-8') as file:
    data2 = list(csv.reader(file, delimiter="," ))


list_output = []
for i in range(len(data)):
    file_name = data[i][0].split('.')[0]
    smiles = data[i][1]
    print(file_name)
    print(smiles)
    smiles_R = re.findall('\[[AEGLMQRXYZa-z0-9]+[a-zA-GI-Z]*\]|\[NHR\d+\]', smiles)
    if '[w]' in smiles_R:
        smiles_R.remove('[w]')

    for k in range(len(smiles_R)):
        smiles_R[k] = re.sub(r'\[[ON]R(\d+)\]|\[CO2R(\d+)\]|\[NR(\d+)\]|\[NHR(\d+)\]', lambda m: f'[R{m.group(1) or m.group(2) or m.group(3) or m.group(4)}]', smiles_R[k])
        smiles_R[k] = re.sub(r'\[([xyz])\]',lambda m: f'[{m.group(1).upper()}]', smiles_R[k])
        smiles_R[k] = smiles_R[k].replace('O','')

    print(smiles_R)
    
    yolo_R = []
    for j in lines:
        if re.sub(r'_\d+\.png$', '', j.split(' ')[0]) == file_name:
            R = '[' + j.split(' ')[5].strip() + ']'
            R = re.sub(r'\[([xyz])\]',lambda m: f'[{m.group(1).upper()}]', R)
            yolo_R.append(R)
    print(yolo_R)
    
    smiles_cleaned = re.sub(r'\[[A-Za-z]+\d*\*\]', '', smiles)
    if len(re.findall(r'\*',smiles_cleaned)) == 1:
        #print(smiles_R)
        #print(yolo_R)
        counter1 = Counter(smiles_R)
        counter2 = Counter(yolo_R)

        diff = counter2 - counter1
        if len(diff) == 1:
            replace_r = list(diff.keys())[0]
            smiles = re.sub(r'\[\d*\*\]|\*', replace_r, smiles)
            #smiles = smiles.replace('*', replace_r)
        print(smiles)

    elif len(re.findall(r'\*',smiles_cleaned)) == 2:
        counter1 = Counter(smiles_R)
        counter2 = Counter(yolo_R)
        diff = counter2 - counter1
        if len(diff) == 1 and list(diff.values())[0] == 2:
            replace_r = list(diff.keys())[0]
            smiles = re.sub(r'\[\d*\*\]|\*', replace_r, smiles)
        
        
        else:
            points_replace = {}
            flag = 0
            str1 = points_data_orig[file_name + '.png'] # orig smiles
            replaceV_list = [[m.start(), m.end()] for m in re.finditer(r'\[\d*\*\]|\*', smiles)] # index of * or [6*] or [*]
            for k in range(len(replaceV_list)):
                idx_start, idx_end = replaceV_list[k]
                str_replace = smiles[:idx_start] + '[V]' + smiles[idx_end:]
            
                for d2 in range(len(data2)):
                    if data2[d2][0].split('_')[0] == file_name:
                        str2 = data2[d2][1]
                        R = '[' + data2[d2][2] + ']'
                        if R not in smiles:
                    
                            try:
                                mol1 = sp.parseSmiles(str_replace)
                                mol2 = sp.parseSmiles(str2)

                                canonical1 = sg.create(mol1)
                                canonical2 = sg.create(mol2)


                                if canonical1 == canonical2:
                                    if not any(data2[d2][0] in value for value in points_replace.values()):
                                        points_replace[(idx_start, idx_end)] = [R, data2[d2][0]]
                                    else:
                                        points_replace = {}
                                        flag = 1
                                        break

                            except InvalidSmilesException as e:
                                print("error1", e)
                            except Exception as e:
                                print("error2", e)
                if flag == 1:
                    break
        
            counter1 = Counter(smiles_R)
            counter2 = Counter(yolo_R)

            diff = counter2 - counter1
            list_diff = list(diff.keys())
        
            points_replace_sorted = dict(sorted(points_replace.items(), key=lambda x:x[0], reverse=True)) #index由大到小排序
            print(points_replace_sorted)
            for key, value in points_replace_sorted.items():
                start_, end_ = key
                if len(re.findall(r'\[\d+\*\]|\*', smiles[start_:end_])) != 0:
                    smiles = smiles[:start_] + value[0] + smiles[end_:]

            if len(points_replace_sorted) == 1:
                replace_R = list(points_replace_sorted.values())[0][0]
                if replace_R in list_diff:
                    if diff[replace_R] == 1:
                        list_diff.remove(replace_R)
                        smiles = re.sub(r'\[\d*\*\]|\*', list_diff[0], smiles)
        print(smiles)


    elif len(re.findall(r'\*',smiles_cleaned)) > 2:
        for m in range(len(smiles_R)):
            if smiles_R[m] in yolo_R:
                yolo_R.remove(smiles_R[m])
        if len(set(yolo_R)) == 1:
            smiles = re.sub(r'\[\d*\*\]|\*', list(set(yolo_R))[0], smiles)
        print(smiles)
    list_output.append([data[i][0], smiles])
           

df = pd.DataFrame(list_output)
df.to_csv('SMILES_ver3.csv', encoding='utf-8', index=False, header=False)

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

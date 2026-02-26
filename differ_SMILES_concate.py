import difflib
import csv
import re
import pandas as pd
import datetime
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

with open('./SMILES_ver1.csv', "r", encoding='utf-8') as file:
    data1 = list(csv.reader(file, delimiter="," ))

with open('./SMILES_R.csv', "r", encoding='utf-8') as file:
    data2 = list(csv.reader(file, delimiter="," ))

def count_replace(str1, str2): #count the number of delete/insert
    count = 0
    count_replace = 0
    matcher = difflib.SequenceMatcher(None, str1, str2)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'delete' or tag == 'insert':
            count += 1
        elif tag == 'replace':
            count_replace += 1

    return count, count_replace


list_output = [] #smiles
#list_remain = []

for i in range(len(data1)):#len(data1)
    filename = data1[i][0].replace('.png','')
    smiles = data1[i][1]
    # print(filename)
    # print(smiles)

    if len(re.findall(r'\*',smiles)) == 0:
        list_output.append([data1[i][0], smiles])
    else:
        print(filename)
        # print(smiles)
        #list_remain1 = []#First
        #list_remain2 = [] #Second
        points_replace = {} # {idx : R}
        points_repeat = {}
        points_first_repeat  = {}
        first_flag = 0
        second_flag = 0

        list_replace = []
    
        #replace image SMILES compare with orig SMILES, and replace the * with R in the orig SMILES
        for j in range(len(data2)): # SMILES_R.csv
            if re.sub(r'_replace_\d+\.png$', '', data2[j][0]) == filename:

                str1 = points_data_orig[filename + '.png'] # orig smiles
                replaceV_list = [[m.start(), m.end()] for m in re.finditer(r'\[\d*\*\]|\*', smiles)] # index of * or [6*] or [*]
                str2 = data2[j][1] # 替換smiles
                R = data2[j][2]
                # print(str1)
                # print(str2)

                ##計算要替換*的index及對應的R
                #First method
                count_d, count_r = count_replace(str1, str2)
                matcher = difflib.SequenceMatcher(None, str1, str2)
                if matcher.ratio() >= 0.80 and count_d == 0 and count_r == 1:
                    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                        if tag == 'replace' and 'V' in str2[j1:j2] and j2-j1 < 4:
                            list_replace.append([i1, i2, R, data2[j][0]])
                            
                #else:
                #    list_remain1.append([R, data2[j][0]])

                #Second method
                for k in range(len(replaceV_list)):
                    idx_start, idx_end = replaceV_list[k]
                    str_replace = str1[:idx_start] + '[V]' + str1[idx_end:] #orig smiles replace by [V]
                    # print(str_replace)
                    # print(str2)
                    try:
                        mol1 = sp.parseSmiles(str_replace)
                        mol2 = sp.parseSmiles(str2)

                        canonical1 = sg.create(mol1)
                        canonical2 = sg.create(mol2)

                        #print(canonical1 == canonical2)
                        if canonical1 == canonical2:
                            print(idx_start, idx_end, R)
                            print(f"points_replace {points_replace}")
                            if (idx_start, idx_end) not in points_replace and (idx_start, idx_end) not in points_repeat and (idx_start, idx_end) not in points_first_repeat:
                                #print(f"{idx_start}-{idx_end} >> {R}")
                                points_replace[(idx_start, idx_end)] = [R, data2[j][0]]
                                if first_flag == 1:
                                    points_first_repeat[(idx_start, idx_end)] = [R, data2[j][0]]
                                    print(f"first_repeat {points_first_repeat}")
                                    first_flag = 0
                                break
                            else:
                                print("repeat")
                                print(f"first_repeat {points_first_repeat}")
                                if len(points_first_repeat) == 0: #first repeat
                                    print("step1")
                                    points_first_repeat[(idx_start, idx_end)] = points_replace[(idx_start, idx_end)]
                                    first_flag = 1
                                elif (idx_start, idx_end) in points_repeat:
                                    break
                                elif (idx_start, idx_end) not in points_first_repeat and R != points_replace[(idx_start, idx_end)][0]:
                                    print("step2")
                                    del points_replace[(idx_start, idx_end)]
                                    points_repeat[(idx_start, idx_end)] = [R, data2[j][0]]
                                    break
                                elif (idx_start, idx_end) in points_replace  and R == points_replace[(idx_start, idx_end)][0]:
                                    print("step3")
                                    first_flag = 1
                                elif (idx_start, idx_end) in points_first_repeat and len(points_first_repeat) < 2:
                                    print("step4")
                                    first_flag = 1
                                elif (idx_start, idx_end) in points_first_repeat and len(points_first_repeat) == 2 and second_flag == 0:
                                    print("step5")
                                    second_flag = 1
                                    for key in points_first_repeat:
                                        del points_replace[key]
                                    break
                                elif (idx_start, idx_end) in points_first_repeat and len(points_first_repeat) == 2 and second_flag == 1:
                                    print("step6")
                                    break


                    except InvalidSmilesException as e:
                        print("error1", e)
                    except Exception as e:
                        print("error2", e)

                #if not any(data2[j][0] in value for value in points_replace.values()): #data2[j][0]不在points_replace中
                    #print(data2[j][0])
                 #   list_remain2.append([R, data2[j][0]])

        if second_flag == 1:
            print("second_flag")
            for key, value in points_first_repeat.items():
                points_replace[key] = value
                break

        if len(points_replace) == 0 and len(points_first_repeat) != 0:
            for key, value in points_first_repeat.items():
                points_replace[key] = value
                break
        

        #First method

        seen = set()
        unique_list = []
        for item in list_replace: #[i1, i2, R, data2[j][0]]
            key = (item[0], item[1])
            if key not in seen:
                seen.add(key)
                unique_list.append(item)
            #else:
             #   list_remain1.append([item[2],item[3]])

        sorted_list = sorted(unique_list, key=lambda x: x[0], reverse=True)
        print(sorted_list)
        #print(len(sorted_list))

        #Second method
        points_replace_sorted = dict(sorted(points_replace.items(), key=lambda x:x[0], reverse=True)) #index由大到小排序
        print(points_replace_sorted)
        #print(len(points_replace_sorted))


        #First
        if len(sorted_list) > len(points_replace_sorted):
            smiles_orig = smiles
            for k in sorted_list: #replace R
                print(k)
                start_idx, end_idx, replacement, file_ = k
                replacement = re.escape(replacement)
                match = re.search(replacement, smiles_orig, re.IGNORECASE)
                if match == None:
                    if start_idx == 0 or end_idx == len(smiles) or (smiles[start_idx-1] != '[' and smiles[end_idx] != ']') :
                        #print(f"{replacement}, {start_idx} - {end_idx}")
                        #print(smiles[start_idx:end_idx])
                        if len(re.findall(r'\[\d+\*\]|\*', smiles[start_idx:end_idx])) != 0:
                            smiles = smiles[:start_idx] + '['  + replacement + ']' + smiles[end_idx:]
                    else:
                        #print(f"{replacement}, {start_idx-1} - {end_idx+1}")
                        #print(smiles[start_idx-1:end_idx+1])
                        if len(re.findall(r'\[\d+\*\]|\*', smiles[start_idx-1:end_idx+1])) != 0:
                            smiles = smiles[:start_idx] + replacement + smiles[end_idx:]
            #list_remain = list_remain + list_remain1
        #Second
        elif len(sorted_list) <= len(points_replace_sorted):
            smiles_orig = smiles
            for key, value in points_replace_sorted.items():
                start_, end_ = key
                #print(smiles[start_:end_])
                value[0] = re.escape(value[0])
                match = re.search(value[0], smiles_orig, re.IGNORECASE)
                if match == None:
                    if len(re.findall(r'\[\d+\*\]|\*', smiles[start_:end_])) != 0:
                        smiles = smiles[:start_] + '[' + value[0] + ']' + smiles[end_:]
            #list_remain = list_remain + list_remain2

        print(smiles)
        print("-------------------------------")
        list_output.append([data1[i][0], smiles])


df = pd.DataFrame(list_output)
df.to_csv('SMILES_ver2.csv', encoding='utf-8', index=False, header=False)

with open('R_label_latex_ver2.txt' ,'r', encoding='utf-8') as f: #read label file
    lines = f.readlines()

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")
'''
with open('R_label_latex_remain.txt', 'w', encoding="utf-8") as f:
    for n in range(len(list_remain)):
        for m in lines:
            if list_remain[n][1].replace('_replace','') == m.split(' ')[0]:
                f.write(m)

'''

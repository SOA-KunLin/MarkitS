import csv
import pandas as pd
from collections import Counter
import numpy as np
import re
import datetime

def normalize_r_label_gen(r):
    r = re.sub(r'(R)([B-Z])', lambda m: m.group(1) + m.group(2).lower(), r.strip())  # RX → Rx (小寫)
    r = re.sub(r'(^[^R]?[a-z])', lambda m: m.group(1).upper(), r)                    # z → Z
    # r = re.sub(r'[ON]R(\d+)|CO2R(\d+)', lambda m: f'R{m.group(1) or m.group(2)}', r)
    r = r.replace('Ri', 'R1').replace('RI', 'R1').replace('AI', 'A1')
    
    return r

def normalize_r_label_orig(r):
    r = re.sub(r'(^[^R]?[a-z])', lambda m: m.group(1).upper(), r.strip())                    # z → Z
    return r

def extract_coordinates(lines, s_name, s_list, normalize=True):
    list_coord = []
    list_coord2 = []

    for m in lines:
        file_name, xmin, xmax, ymin, ymax, R = m.split(" ")[:6]
        if normalize: #gen
            R = normalize_r_label_gen(R)
        else:
            R = normalize_r_label_orig(R)

        if 'gen' in file_name:
            file_name = re.sub(r'_gen_\d+\.png$', '', file_name)
        else:
            file_name = re.sub(r'_\d+\.png$', '', file_name)

        if file_name == s_name and R == s_list[0]: #the first same R insert in list_coord[0]
            list_coord.insert(0, [file_name, R, [(int(xmax) + int(xmin)) / 2, (int(ymax) + int(ymin)) / 2]])
        elif R not in s_list and file_name.split("_")[0] == s_name: #another R (not in the list same)
            list_coord.append([file_name, R, [(int(xmax) + int(xmin)) / 2, (int(ymax) + int(ymin)) / 2]])

        if file_name == s_name:
            list_coord2.append([file_name, R, [(int(xmax) + int(xmin)) / 2, (int(ymax) + int(ymin)) / 2]])

    return list_coord, list_coord2


start_time = datetime.datetime.now()

with open('R_label_latex_gen.txt' ,'r', encoding='utf-8') as f: #read label file
    lines_1 = f.readlines()

with open('R_label_latex_ver2.txt' ,'r', encoding='utf-8') as f2: #read label file
    lines_2 = f2.readlines()

with open('SMILES_generate.csv', "r", encoding='utf-8') as file:
    data = list(csv.reader(file, delimiter="," ))

points_data = {item[0]: item[1] for item in data} #filename:smiles

list_file_gen = []

for i in lines_1:
    file_name = re.sub(r'_gen_\d+\.png$', '', i.split(' ')[0])
    if file_name not in list_file_gen:
        #print(file_name)
        list_file_gen.append(file_name)

list_R_gen = [] #[filename, gen_R_list, orig_R_list]
for file_name in list_file_gen:
    list_R = [normalize_r_label_gen(k.split(" ")[5])
            for k in lines_1 if re.sub(r'_gen_\d+\.png$', '', k.split(' ')[0]) == file_name]
    list_R_gen.append([file_name, list_R])

for j in range(len(list_file_gen)):
    list_R = [normalize_r_label_orig(k.split(" ")[5])
            for k in lines_2 if re.sub(r'_\d+\.png$', '', k.split(' ')[0]) == list_file_gen[j]]
    list_R_gen[j].append(list_R)
    #print(list_R_gen[j])

#yolo R 跟 generate smiles R 比對 > 更正 (修正texteller錯誤的R)
for entry in list_R_gen: #list_R_gen = [filename, gen_R_list, orig_R_list]
    filename, gen_R_list = entry[0], entry[1]
    # print(filename)
    # print(gen_R_list)

    smiles = points_data[filename + '.png']
    correct_R = re.findall('\[[AEGLMQRXYZa-z0-9]+[a-zA-Z]*\]', smiles)
    print(correct_R)
    for i in range(len(correct_R)):
        correct_R[i] = re.sub(r'\[[ON]R(\d+)\]|\[CO2R(\d+)\]', lambda m: f'[R{m.group(1) or m.group(2)}]', correct_R[i])
        correct_R[i] = re.sub(r'(^[^R]?[a-z])', lambda m: m.group(1).upper(), correct_R[i])

    latex_R_dist = {}
    latex_R_list = []
    for j in range(len(gen_R_list)):
        latex_R_dist[j] = f'[{gen_R_list[j]}]' #{ j : gen_R_list[j] }
        latex_R_list.append(f'[{gen_R_list[j]}]')

    set1 = set(correct_R)
    set2 = set(latex_R_list)
    print(filename)
    print(smiles)
    set1_differ = list(set1 -set2)
    set2_differ = list(set2 -set1)

    if len(set1_differ) == 1 and len(set2_differ) == 1: #避免set1_differ多一個[Co]情況
        keys = [key for key, val in latex_R_dist.items() if val == set2_differ[0]] #找出不同R的index
        gen_R_list[keys[0]] = set1_differ[0].replace('[','').replace(']','') #替換正確的R
    elif len(set1_differ) == 2 and len(set2_differ) == 2 and "[z]" in set1_differ and "[Z]" in set2_differ: #不同的為兩個(其中一個為[Z])
        set1_differ.remove("[z]")
        set2_differ.remove("[Z]")
        keys = [key for key, val in latex_R_dist.items() if val == set2_differ[0]]
        gen_R_list[keys[0]] = set1_differ[0].replace('[','').replace(']','')

#print(list_R_gen)

# find the same R between list_R_gen[1], list_R_gen[2]
list_same = []
repeat_same = []
for i in range(len(list_R_gen)):

    list1 = list_R_gen[i][1]
    list2 = list_R_gen[i][2]
    print(list1)
    print(list2)
    counter1 = Counter(list1)
    counter1_1 = [key for key, count in counter1.items() if count == 1]
    points_counter1 = {}
    for key, count in counter1.items():
        if count > 1:
            points_counter1[key] = count

    counter2 = Counter(list2)
    counter2_1 = [key for key, count in counter2.items() if count == 1]
    points_counter2 = {}
    for key, count in counter2.items():
        if count > 1:
            points_counter2[key] = count

    common_elements = list(set(counter1_1) & set(counter2_1))

    repeat_elements = []
    for key, value in points_counter1.items():
        if key in points_counter2 and points_counter2[key] == value:
            repeat_elements.append(key)
    repeat_same.append([list_R_gen[i][0], repeat_elements])


    list_same.append([list_R_gen[i][0], common_elements])

    print([list_R_gen[i][0], common_elements])




list_coord_orig = [] #[filename, R, [x, y]]
list_coord_gen = []
list_coord_orig_all = [] #no delete list same
list_coord_gen_all = []

for j in range(len(list_same)):
    s_name = list_same[j][0]
    s_list = list_same[j][1]
    if s_list:
        list_coord, list_coord2 = extract_coordinates(lines_2, s_name, s_list, normalize=False)
        list_coord_orig.append(list_coord)
        list_coord_orig_all.append(list_coord2)


        list_coord , list_coord2 = extract_coordinates(lines_1, s_name, s_list, normalize=True)
        list_coord_gen.append(list_coord)
        list_coord_gen_all.append(list_coord2)

    else:
        list_coord2 = []

        for m in lines_2:
            file_name, xmin, xmax, ymin, ymax, R = m.split(" ")[:6]
            R = normalize_r_label_orig(R)

            if re.sub(r'_\d+\.png$', '', file_name) == s_name:
                list_coord2.append([file_name, R, [(int(xmax) + int(xmin)) / 2, (int(ymax) + int(ymin)) / 2]])
        list_coord_orig_all.append(list_coord2)

        list_coord2 = []
        for n in lines_1:
            file_name, xmin, xmax, ymin, ymax, R_gen = n.split(" ")[:6]
            R_gen = normalize_r_label_gen(R_gen)

            if re.sub(r'_gen_\d+\.png$', '', file_name) == s_name:
                list_coord2.append([file_name, R_gen, [(int(xmax) + int(xmin)) / 2, (int(ymax) + int(ymin)) / 2]])

        list_coord_gen_all.append(list_coord2)


with open('list_same_coord.txt', 'w', encoding='utf-8') as file:
    file.write(str(list_same) + '\n')
    file.write(str(repeat_same) + '\n')
    file.write(str(list_coord_orig) + '\n')
    file.write(str(list_coord_gen) + '\n')
    file.write(str(list_coord_orig_all) + '\n')
    file.write(str(list_coord_gen_all) + '\n')

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

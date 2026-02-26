import csv
import pandas as pd
import ast
import numpy as np
import re
import math
import datetime
import sys

start_time = datetime.datetime.now()

with open('SMILES_orig.csv', 'r', encoding='utf-8') as file:
    data1 = list(csv.reader(file, delimiter="," ))

points_data1 = {item[0]: item[1] for item in data1} #filename:smiles

with open('SMILES_ver3.csv', 'r', encoding='utf-8') as file:
    data2 = list(csv.reader(file, delimiter="," ))

points_data2 = {item[0]: item[1] for item in data2} #filename:smiles

with open('SMILES_generate.csv', 'r', encoding='utf-8') as file:
    data3 = list(csv.reader(file, delimiter="," )) 

points_data3 = {item[0]: item[1] for item in data3} #filename:smiles

with open('SMILES_R.csv', 'r', encoding='utf-8') as file:
    data4 = list(csv.reader(file, delimiter="," )) 

points_data4 = {item[0]: (item[1], item[2]) for item in data4} #filename:smiles

 
with open("list_same_coord.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()

list_same = ast.literal_eval(lines[0].strip())
points_same = {item[0]: item[1] for item in list_same}

list_repeat_same = ast.literal_eval(lines[1].strip())
points_repeat_same = {item[0]: item[1] for item in list_repeat_same}

list_coord_orig = ast.literal_eval(lines[2].strip())
list_coord_gen = ast.literal_eval(lines[3].strip())

list_coord_orig_all = ast.literal_eval(lines[4].strip())
list_coord_gen_all = ast.literal_eval(lines[5].strip())


for i in range(len(list_coord_gen_all)):#修正list_coord_gen_all裡texteller錯誤的R
    #print(list_coord_gen_all[i])
    filename = re.sub(r'_gen_\d+\.png$', '', list_coord_gen_all[i][0][0])
    smiles = points_data3[filename + '.png']
    print(filename)
    #correct_R = re.findall('\[[A-GIJL-SVX-Za-z0-9]+\]', smiles)
    correct_R = re.findall('\[[AEGLMQORXYZa-z0-9]+[a-zA-Z]*\]|\[[ON]R\d+\]|\[CO2R\d+\]|NR\d+\]|\[NHR\d+\]', smiles)
    for k in range(len(correct_R)):
        correct_R[k] = re.sub(r'\[[ON]R(\d+)\]|\[CO2R(\d+)\]|\[NR(\d+)\]|\[NHR(\d+)\]', lambda m: f'[R{m.group(1) or m.group(2) or m.group(3) or m.group(4)}]', correct_R[k])
        correct_R[k] = re.sub(r'\[([xyz])\]',lambda m: f'[{m.group(1).upper()}]', correct_R[k])
    
    latex_R = {}
    latex_R_list = []
    for j in range(len(list_coord_gen_all[i])):
        latex_R[j] = f'[{list_coord_gen_all[i][j][1]}]'
        latex_R_list.append(f'[{list_coord_gen_all[i][j][1]}]')
    # print(latex_R_list)
    # print(latex_R)
    set1 = set(correct_R)
    set2 = set(latex_R_list)
    # diff_elements = set(correct_R).symmetric_difference(set(latex_R_list))
    set1_differ = list(set1 -set2)
    set2_differ = list(set2 -set1)

    if len(set1_differ) == 1 and len(set2_differ) == 1:
        keys = [key for key, val in latex_R.items() if val == set2_differ[0]]
        list_coord_gen_all[i][keys[0]][1] = set1_differ[0].replace('[','').replace(']','')
    elif len(set1_differ) == 2 and len(set2_differ) == 2 and "[z]" in set1_differ and "[Z]" in set2_differ:
        set1_differ.remove("[z]")
        set2_differ.remove("[Z]")
        keys = [key for key, val in latex_R.items() if val == set2_differ[0]]
        list_coord_gen_all[i][keys[0]][1] = set1_differ[0].replace('[','').replace(']','')
# print(list_coord_gen_all)


def compute_distance(coord_list, x1, y1):
    list_dist = []
    for j in range(len(coord_list)):
        x2, y2 = coord_list[j][2]
        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        list_dist.append([coord_list[j][0], coord_list[j][1], distance])#[filename, R ,distance]
    all_dist = sorted(list_dist, key=lambda x: x[2]) #sort according to the distance
    return all_dist

all_dist_orig = []
all_dist_gen = []

for ele in range(len(list_same)):#len(list_same)
    print(list_same[ele])
    print(points_repeat_same[list_same[ele][0]])
    for i in range(len(list_same[ele][1])):
        list_coord_orig_no_same = []
        list_coord_gen_no_same = []
        for j in range(len(list_coord_orig_all[ele])):
            if list_coord_orig_all[ele][j][1] == list_same[ele][1][i]:
                x1, y1 = list_coord_orig_all[ele][j][2]
            if list_coord_orig_all[ele][j][1] not in list_same[ele][1] and list_coord_orig_all[ele][j][1] not in points_repeat_same[list_same[ele][0]]:
                # print(list_coord_orig_all[ele][j])
                list_coord_orig_no_same.append(list_coord_orig_all[ele][j])
        dist_orig = compute_distance(list_coord_orig_no_same, x1, y1)
        
        for k in range(len(list_coord_gen_all[ele])):
            if list_coord_gen_all[ele][k][1] == list_same[ele][1][i]:
                x1_g , y1_g = list_coord_gen_all[ele][k][2]
            if list_coord_gen_all[ele][k][1] not in list_same[ele][1] and list_coord_gen_all[ele][k][1] not in points_repeat_same[list_same[ele][0]]:
                # print(list_coord_gen_all[ele][k])
                list_coord_gen_no_same.append(list_coord_gen_all[ele][k])
        dist_gen = compute_distance(list_coord_gen_no_same, x1_g, y1_g)
        
        all_dist_orig.append(dist_orig)
        all_dist_gen.append(dist_gen)

print(all_dist_orig)

   
dict_list = []
for i in range(len(all_dist_orig)):#len(all_dist_orig)
    filename = re.sub(r'_\d+\.png$', '', all_dist_orig[i][0][0])
    print(filename)
    d = {'file': filename}


    if len(all_dist_orig[i]) == len(all_dist_gen[i]):
        print(all_dist_orig[i])
        print(all_dist_gen[i])
        count = 2
        for j in range(len(all_dist_orig[i])):
            # d[all_dist_gen[i][j][1]] = all_dist_orig[i][j][1]
            if d.get(all_dist_orig[i][j][1]) == None:
                d[all_dist_orig[i][j][1]] = all_dist_gen[i][j][1]
            else:
                d[all_dist_orig[i][j][1] + '_' + str(count)] = all_dist_gen[i][j][1]
                count += 1    
            # print(f'{all_dist_orig[i][j][1]} >> {all_dist_gen[i][j][1]}', end=' / ')
    # else:
    #     print('yolo error')
    # print()
    d2 = {}
    d2['file'] = d['file']
    for key, value in d.items():
        if key != 'file':
            d2[value] = key
    # print(d2)
    dict_list.append(d2)
# print(dict_list)


no_match = []
one_same = []

for i in range(len(list_same)):#len(list_same)
    print(list_same[i])
    filename = list_same[i][0]
    smiles = points_data3[list_same[i][0]+'.png']
    print(smiles)


    if len(list_same[i][1]) > 1:
        
        list_d = [d for d in dict_list if d.get('file') == filename]
        # print(list_d)
        exit_outer_loop = False
        for m in range(len(list_d)):
            # print(any(k == v for k, v in list_d[m].items()))
            for n in range(m+1, len(list_d)):
                # print(f"{m} >> {n}")
                print(list_d[m])
                print(list_d[n])
                diff = list_d[m].keys() & list_d[n]
                diff_vals = [(k, list_d[m][k], list_d[n][k]) for k in diff if list_d[m][k] != list_d[n][k]]
                common = list_d[m].items() & list_d[n].items()
                if not diff_vals:
                    for r in iter(common):
                        smiles = smiles.replace(r[0], r[1], 1)
                    print(f'after : {smiles}')
                    points_data2[list_same[i][0]+'.png'] = smiles
                    exit_outer_loop = True
                    break
            if exit_outer_loop:
                break
        if not exit_outer_loop:
            no_match.append(filename)
    elif len(list_same[i][1]) == 1:
        print("one") 
        one_same.append(filename)
    elif len(list_same[i][1]) == 0:
        print(list_same[i][0])
        smiles_star = points_data2[list_same[i][0]+'.png']
        print(smiles_star)
        res = re.findall('\*', smiles_star)
        # print(res)
        if len(res) == 2:
            smiles_r1 = points_data4[list_same[i][0] + '_replace_1.png'][0]
            smiles_r2 = points_data4[list_same[i][0] + '_replace_2.png'][0]
            print(smiles_r1)
            print(smiles_r2)
            if '[V]' in smiles_r1:
                smiles_r1 = smiles_r1.replace('[V]', '[' + points_data4[list_same[i][0] + '_replace_1.png'][1] + ']')
                smiles_r1 = smiles_r1.replace('*', '[' + points_data4[list_same[i][0] + '_replace_2.png'][1] + ']')
                points_data2[list_same[i][0]+'.png'] = smiles_r1
                print(smiles_r1)
            elif '[V]' in smiles_r2:
                smiles_r2 = smiles_r2.replace('[V]', '[' + points_data4[list_same[i][0] + '_replace_2.png'][1] + ']')
                smiles_r2 = smiles_r2.replace('*', '[' + points_data4[list_same[i][0] + '_replace_1.png'][1] + ']')
                points_data2[list_same[i][0]+'.png'] = smiles_r2
                print(smiles_r2)
            



print("--------------------------------------------------------")
# print(one_same)
remain = no_match + one_same
# print(remain)
def euclidean_distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def count_total_distance(x1, y1, point):
    total = 0
    for key in point:
        x2, y2 = point[key][1]
        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        total += distance
    return total

for num in range(len(remain)):#len(remain)
    filename = remain[num]
    print(filename)
    # print(points_repeat_same[filename])
    sssame = [filename, points_same[filename]]
    print(sssame)
    smiles = points_data3[filename + '.png']
    print(smiles)
    # print(list_coord_orig_all[num])
    # print(list_coord_gen_all[num])

    # 建立一個字典以便快速查找
    all_visited1 = []
    all_visited2 = []

    for j in range(len(list_coord_orig_all)):
        if re.sub(r'_\d+\.png$', '', list_coord_orig_all[j][0][0]) == filename:
            num2 = j
    for i in range(len(sssame[1])):#len(sssame[1])
        # points1 = {item[1]: (item[0], item[2]) for item in list_coord_orig_all[num2] if item[1] not in points_repeat_same[filename]}
        # print(list_coord_gen_all[num2])
        points2 = {re.sub(r'[ON]R(\d+)|CO2R(\d+)|NR(\d+)|NHR(\d+)', lambda m: f'R{m.group(1) or m.group(2) or m.group(3) or m.group(4)}', item[1]): (item[0], item[2]) for item in list_coord_gen_all[num2] if re.sub(r'[ON]R(\d+)|CO2R(\d+)|NR(\d+)|NHR(\d+)', lambda m: f'R{m.group(1) or m.group(2) or m.group(3) or m.group(4)}', item[1]) not in points_repeat_same[filename]}
        points1 = {}
        for item in list_coord_orig_all[num2]: 
            if item[1] not in points_repeat_same[filename]:
                if points1.get(item[1]) == None:
                    points1[item[1]] = (item[0], item[2])
                else:
                    points1[item[1] + '_2'] = (item[0], item[2])
        print(points1)
        print(points2)
    # # 初始化
        visited1 = []
        current_label = sssame[1][i]
        visited1.append((current_label, points1[current_label][0], points1[current_label][1]))
        for j in range(len(sssame[1])):
            del points1[sssame[1][j]]
        
        visited2 = []
        if current_label not in points2:
            print(f"{current_label} not in generated labels")
            continue
        visited2.append((current_label, points2[current_label][0], points2[current_label][1]))
        for j in range(len(sssame[1])):
            if sssame[1][j] in points2:
                del points2[sssame[1][j]]


        # 主迴圈
        while points1:
            current_coord = visited1[-1][2]
            # 找出距離當前點最近的點
            next_label, (next_file, next_coord) = min(
                points1.items(),
                key=lambda item: euclidean_distance(current_coord, item[1][1]) #current_coord對所有points裡的計算距離，找出最近的
            )
            visited1.append((next_label, next_file, next_coord))
            del points1[next_label]
        all_visited1.append(visited1)

        while points2:
            current_coord = visited2[-1][2]
            # 找出距離當前點最近的點
            next_label, (next_file, next_coord) = min(
                points2.items(),
                key=lambda item: euclidean_distance(current_coord, item[1][1]) #current_coord對所有points裡的計算距離，找出最近的
            )
            visited2.append((next_label, next_file, next_coord))
            del points2[next_label]
        all_visited2.append(visited2)
    

    # 輸出結果
    dist_list = []
    if len(all_visited1[0]) == len(all_visited2[0]):
        for j in range(len(all_visited1)):
            d = {}
            # print(all_visited1[0])
            # print(all_visited2[0])
            for i in range(1, len(all_visited1[j])):
                d[all_visited1[j][i][0]] = all_visited2[j][i][0]
            dist_list.append(d)

    print(len(dist_list))
    if len(dist_list) > 1:
        flag = 0
        for m in range(len(dist_list)):
            for n in range(m+1, len(dist_list)):
                print(dist_list[m])
                print(dist_list[n])

                diff = dist_list[m].keys() & dist_list[n]
                diff_vals = [(k, dist_list[m][k], dist_list[n][k]) for k in diff if dist_list[m][k] != dist_list[n][k]]
                common = dist_list[m].items() & dist_list[n].items()
                print(f"diff_vals: {diff_vals}")
                print(f"common : {common}")
                if not diff_vals: # diff_vals = []
                    for r in iter(common):
                        smiles = smiles.replace(r[1], r[0], 1)
                    flag = 1
                    break
            if flag == 1:
                break
        if flag == 0:
            print("no match")
            print(dist_list[0])
            for r in iter(dist_list[0]):
                smiles = smiles.replace(dist_list[0][r], r, 1)

    elif len(dist_list) == 1:
        print(dist_list[0])
        for r in iter(dist_list[0]):
            smiles = smiles.replace(dist_list[0][r], r, 1)
    print(smiles)
    points_data2[filename +'.png'] = smiles

data_new = []
for key, value in points_data2.items():
    data_new.append([key, value])

for d1 in data1:
    for d2 in data_new:
        if d2[0] == d1[0]:
            d1.append(d2[1])
            break


with open('SMILES_first.csv', 'r', encoding='utf-8') as file:
    data_first = list(csv.reader(file, delimiter="," ))

for d1 in data1:
    for d_f in data_first:
        if d1[0] == d_f[0]:
            d1.append(d_f[1])
            break
    if len(d1)!= 3:
        d1.append(' ')

mon = sys.argv[1]
df = pd.DataFrame(data1)
df.to_csv("SMILES_dist_near" + mon + ".csv", encoding='utf-8', index=False, header=False)

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

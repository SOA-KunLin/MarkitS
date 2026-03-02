import csv
import re
import pandas as pd
import sys

output_intermediate = sys.argv[3]
project_path = sys.argv[4]

with open('SMILES_dist_near' + sys.argv[1] + '.csv', 'r', encoding='utf-8') as file:
    data = list(csv.reader(file, delimiter="," ))

list_output = []
for i in range(len(data)):
    data[i][2] = data[i][2].replace('_2','')
    list_output.append([data[i][0], data[i][2]])

def load_to_dict(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # 建立字典 {ID: Value}
        return {row[0]: row[1] for row in reader if row}

if output_intermediate:
    dict_first = load_to_dict(project_path + '/SMILES_first.csv')
    dict_ver1  = load_to_dict(project_path + '/SMILES_ver1.csv')
    dict_ver3  = load_to_dict(project_path + '/SMILES_ver3.csv')
    dict_final = {d[0]: d[1] for d in list_output if d}

    # 2. 讀取原始資料並直接合併
    with open(project_path + '/SMILES_orig.csv', 'r', encoding='utf-8') as f:
        data_orig = list(csv.reader(f))

    for row in data_orig:
        row_id = row[0]
        if dict_first.get(row_id):
            row.append(dict_first.get(row_id))
        if dict_ver1.get(row_id):
            row.append(dict_ver1.get(row_id))

        if len(row) < 3:
            row.append("")
        if dict_ver3.get(row_id):
            row.append(dict_ver3.get(row_id))
        if len(row) < 4:
            row.append("")
        if dict_final.get(row_id):
            row.append(dict_final.get(row_id))

    df = pd.DataFrame(data_orig)
    df.to_csv(sys.argv[2], encoding='utf-8', index=False, header=['filename', 'orig_smiles', 'yolo', 'V', 'final'])

else:

    df = pd.DataFrame(list_output)
    df.to_csv(sys.argv[2], encoding='utf-8', index=False, header=['filename', 'SMILES'])




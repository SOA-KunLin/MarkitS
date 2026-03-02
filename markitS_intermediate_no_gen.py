import csv
import re
import pandas as pd
import sys

output_intermediate = sys.argv[2]

def load_to_dict(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # 建立字典 {ID: Value}
        return {row[0]: row[1] for row in reader if row}

dict_first = load_to_dict('SMILES_first.csv')
dict_ver3  = load_to_dict('SMILES_ver3.csv')

with open('SMILES_orig.csv', 'r', encoding='utf-8') as f:
    data_orig = list(csv.reader(f))

if output_intermediate:
    dict_ver1  = load_to_dict('SMILES_ver1.csv')

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

    df = pd.DataFrame(data_orig)
    df.to_csv(sys.argv[1], encoding='utf-8', index=False, header=['filename', 'orig_smiles', 'yolo', 'V/final'])

else:
    output = []
    for row in data_orig:
        row_id = row[0]
        output.append(row_id)
        if dict_first.get(row_id):
            output.append(dict_first.get(row_id))
        if dict_ver3.get(row_id):
            output.append(dict_ver3.get(row_id))

    df = pd.DataFrame(output)
    df.to_csv(sys.argv[1], encoding='utf-8', index=False, header=False)




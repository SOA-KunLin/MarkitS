import csv
import re
import pandas as pd
import sys

with open('SMILES_dist_near' + sys.argv[1] + '.csv', 'r', encoding='utf-8') as file:
    data = list(csv.reader(file, delimiter="," ))

list_output = []
for i in range(len(data)):
    data[i][2] = data[i][2].replace('_2','')
    list_output.append(data[i])

df = pd.DataFrame(list_output)
df.to_csv(sys.argv[2], encoding='utf-8', index=False, header=False)

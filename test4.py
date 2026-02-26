import csv
import re
import pandas as pd
import sys

with open('SMILES_dist_near' + sys.argv[1] + '.csv', 'r', encoding='utf-8') as file:
    data = list(csv.reader(file, delimiter="," ))

list_output = []
for i in range(len(data)):
    common_smiles = data[i][2]
    if len(re.findall(r'\[[AEGLMQRXYZa-z0-9\(\)]+[a-gi-zA-GI-Z]*\]|\[OR\d+\]|\[NR\d+\]|\[NHR\d+\]|\[CO2R\d+\]|\[RV\d+\]', common_smiles)) != 0:
        #print(data[i][0], data[i][2])
        data[i][2] = data[i][2].replace('_2','')
        list_output.append(data[i])

df = pd.DataFrame(list_output)
df.to_csv(sys.argv[2], encoding='utf-8', index=False, header=False)

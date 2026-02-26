import csv
import re
import pandas as pd
import datetime
import requests
import sys
from cairosvg import svg2png
import os
import urllib.parse
import time
from pathlib import Path

import jpype
import jpype.imports
from jpype.types import *

jpype.startJVM(classpath=[str(Path(__file__).resolve().parent / "cdk-2.11.jar")])

from org.openscience.cdk.smiles import SmilesParser
from org.openscience.cdk.layout import StructureDiagramGenerator
from org.openscience.cdk.depict import DepictionGenerator
from org.openscience.cdk import DefaultChemObjectBuilder


def generate_img(smiles, png_filename):
    base_url = "https://www.simolecule.com/cdkdepict/depict/bow/svg?smi="

    width = 40
    height = 40
    encoded_smiles = urllib.parse.quote(smiles)
    url = f"{base_url}{encoded_smiles}&w={width}&h={height}"
    
    max_retries=40
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = requests.get(url, verify=False, timeout=15)

            if response.status_code == 200:
                svg_content = response.content

                with open(png_filename, "wb") as file:
                    svg2png(bytestring=svg_content, dpi=600, write_to=file)
                return

            else:
                print(url)
                print("failed", response.status_code)
        
        except requests.exceptions.ProxyError:
            print("ProxyError.")
        except Exception as e:
            print(e)
            print("Retry...")
        

        retry_count += 1
        time.sleep(1)

    
    print("Failed")

start_time = datetime.datetime.now()

with open('SMILES_ver3.csv', "r", encoding='utf-8') as file:
    data = list(csv.reader(file, delimiter="," ))


replace = ["w", "v", "t", "m", "k", "p", "q", "s", "d", "y", "x", "c", "r", "z", "o"]

list_output = []
gen_dir = "./generate_smiles/"
os.makedirs(gen_dir, exist_ok=True)

for i in range(len(data)):
    file_name = data[i][0].split('.')[0]
    smiles = data[i][1]
    
    smiles_cleaned = re.sub(r'\[[A-Za-z]+\d*\*\]', '', smiles)
    res = re.findall(r'\*',smiles_cleaned)
    if res:
        for j in range(len(res)):
            if j < len(replace):
                replace_char = replace[j]
            elif j >= len(replace) and j < 2*len(replace):
                replace_char = f"1{replace[j-15]}"
            else:
                replace_char = f"2{replace[j-30]}"
            
            #print(f"Processing: {file_name}, replacing `*` with `[R{replace_char}]`")
            smiles = re.sub(r'\[\d*\*\]|\*', "[R" + replace_char + "]", smiles, count=1)

        #print(smiles)
        list_output.append([data[i][0], smiles])
        generate_img(smiles, gen_dir + file_name + "_gen.png")
        print(file_name)

df = pd.DataFrame(list_output)
df.to_csv('SMILES_generate.csv', encoding='utf-8', index=False, header=False)

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

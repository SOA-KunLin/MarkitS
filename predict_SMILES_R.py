import torch
from molscribe import MolScribe
from huggingface_hub import hf_hub_download
import os
import pandas as pd
import re
import sys
import datetime

#os.environ["CUDA_VISIBLE_DEVICES"] = "0"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main(dir_path):
    ckpt_path = hf_hub_download('yujieq/MolScribe', 'swin_base_char_aux_1m680k.pth')
    model = MolScribe(ckpt_path, device=device)

    with open('./R_label_latex_ver2.txt' ,'r', encoding='utf-8') as f: #read label file
        lines = f.readlines()


    allFileList = os.listdir(dir_path)
    
    list_all = []

    for filename in allFileList:
        list_output = []
        image_path = os.path.join(dir_path, filename)
        output = model.predict_image_file(image_path, return_atoms_bonds=True, return_confidence=True)
        
        #smiles_parts = output['smiles'].split('.')
        smiles_parts = output['smiles_orig'].split('.')
        res_smiles = max(smiles_parts, key=len) if len(smiles_parts) > 1 else output['smiles_orig']
        #res_smiles = re.sub('\[R\w\]', '*', res_smiles)
        res_smiles = re.sub('\:0', '', res_smiles)
        res_smiles = re.sub('\[RaH\]', '*', res_smiles)
        res_smiles = res_smiles.replace('[3H]', '[T]')
        res_smiles = res_smiles.replace(',', '')
        res_smiles = res_smiles.replace(';', '')
        res_smiles = res_smiles.replace('[0]', '*')

        list_output.append(filename)
        list_output.append(res_smiles)
        for j in lines:
            if j.split(' ')[0] == filename.replace('replace_',''):
                list_output.append(j.split(' ')[5].strip())
        print(filename)
        print(res_smiles)
        print(output['smiles'])
        if len(list_output)== 3:
            #print(list_output)
            list_all.append(list_output)

    df = pd.DataFrame(list_all)
    df.to_csv('SMILES_R.csv', encoding='utf-8', index=False, header=False)



if __name__ == '__main__':
    start_time = datetime.datetime.now()

    main(sys.argv[1])
    
    end_time = datetime.datetime.now()
    time_diff = end_time - start_time
    print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

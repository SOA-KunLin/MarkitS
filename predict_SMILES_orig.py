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

def main(dir_path, output_name):
    ckpt_path = hf_hub_download('yujieq/MolScribe', 'swin_base_char_aux_1m680k.pth')
    print(ckpt_path)
    model = MolScribe(ckpt_path, device=device)

    allFileList = os.listdir(dir_path)
    
    list_all1 = [] #store [filename, SMILES]
    for filename in allFileList:
        print(filename)
        image = os.path.join(dir_path, filename)
        output = model.predict_image_file(image, return_atoms_bonds=True, return_confidence=True)
        
        smiles_parts = output['smiles_orig'].split('.')
        res_smiles = max(smiles_parts, key=len) if len(smiles_parts) > 1 else output['smiles_orig']
        #res_smiles = re.sub('\[R\w\]', '*', res_smiles)
        res_smiles = re.sub('\[RaH\]', '*', res_smiles)
        res_smiles = re.sub('\:0', '', res_smiles)
        res_smiles = res_smiles.replace('[3H]', '[T]')
        res_smiles = res_smiles.replace(',', '')
        res_smiles = res_smiles.replace(';', '')
        res_smiles = res_smiles.replace('[0]', '*')
        
        print(filename)
        print(res_smiles)
        
        
        list_all1.append([filename, res_smiles])

    df = pd.DataFrame(list_all1)
    df.to_csv(output_name, encoding='utf-8', index=False, header=False)
    


if __name__ == '__main__':
    
    start_time = datetime.datetime.now()

    main(sys.argv[1], sys.argv[2])
    
    end_time = datetime.datetime.now()
    time_diff = end_time - start_time
    print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

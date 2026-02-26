import os
import sys
import argparse
import cv2 as cv
import pandas as pd
import datetime

from pathlib import Path
#from onnxruntime import InferenceSession
from models.thrid_party.paddleocr.infer import predict_det, predict_rec
from models.thrid_party.paddleocr.infer import utility

from models.utils import mix_inference
from models.ocr_model.utils.to_katex import to_katex
from models.ocr_model.utils.inference import inference as latex_inference

from models.ocr_model.model.TexTeller import TexTeller
from models.det_model.inference import PredictConfig

import re

def latex_filter(text):
    text = re.sub(r'\\frac\{\d\}|\{\\mathbb\{b\}\,\\mathbb\{b\}\}', '', text)
    text = re.sub(r'\\begin\{array\}\{[rlc]+\}|\\end\{array\}','', text)
    text = re.sub(r'\^\{\\mathbb\{s\}\}', '', text)
    text = re.sub(r'\{', '', text)
    text = re.sub(r'\}', '', text)
    text = re.sub(r'\\operatorname|\\bullet|\\circ|\\ast|\\smallsetminus|\\setminus|\\backslash|\\Lambda|\\left|\\right|\\acute|\\grave|\\tilde|\\hat|\\bar|\\widetilde|\\backsim|\\swarrow|\\bigrfloorn|\\angle|\\diagup', '', text)
    text = re.sub(r'\\tiny|\\scriptsize|\\footnotesize|\\small|\\normalsize|\\large|\\Large|\\LARGE|\\huge|\\Huge|\\sqrt|\\overline','', text)
    text = re.sub(r'\\textbf|\\textit|\\texttt|\\textsc|\\text|\\underline|\\cdot|\\dot|\\sim|\\prime|\\bm|\\frac|\\boldsymbol|\\nu|\\rm|\\bf|\\xi', '', text)
    text = re.sub(r'(\\mathrm|\\mathbf|\\mathit|\\mathsf|\\mathtt|\\mathbb|\\mathcal)','',text)
    text = re.sub(r'\`|\\|\s|\'|\.|\,|\;', '', text)
    text = re.sub(r'\_t|\_r|\_s|\_S|\_i', '', text)
    text = re.sub(r'\-$', '', text)
    text = re.sub(r'\^$|\_$', '', text)
    text = re.sub(r'Delta', 'A', text)
    text = re.sub(r'Upsilon', 'Y', text)
    text = re.sub(r'Rtimes', 'Rx', text)
    text = re.sub(r'Rg', 'R9', text)
    return text




if __name__ == '__main__':
    start_time = datetime.datetime.now()

    #dir_path = str(Path(__file__).resolve().parent)
    dir_path = sys.argv[1]

    # You can use your own checkpoint and tokenizer path.
    print('Loading model and tokenizer...')
    latex_rec_model = TexTeller.from_pretrained('default')
    tokenizer = TexTeller.get_tokenizer()
    print('Model and tokenizer loaded.')

    # img_path = args.img
    output = []
    img_dir = dir_path + '/output_gen/'
    
    '''
    img_name = 'US11498928-20221115-C00506_gen_7.png'
    img_path = img_dir + img_name
    img = cv.imread(img_path)
    res = latex_inference(latex_rec_model, tokenizer, [img], 'cuda', 1)
    res = to_katex(res[0])
    print(res)
    res_filter = latex_filter(res)
    print(res_filter)

    
    '''
    imgfile = os.listdir(img_dir)
    for i in imgfile:
        img_path = img_dir + i
        img = cv.imread(img_path)
        print(i)
        #print('Inference...')
        res = latex_inference(latex_rec_model, tokenizer, [img], 'cuda', 1)
        res = to_katex(res[0])
        print(res)
        res_filter = latex_filter(res)
        print(res_filter)
        output.append([i, res_filter])




    f2 = open(dir_path + '/R_label_latex_gen.txt', 'w', encoding="utf-8")

    with open(dir_path + '/R_label_gen.txt' ,'r', encoding='utf-8') as f: #read label file
        lines = f.readlines()

    for j in lines:
        #print(j.split(" ")[0])
        for m in range(len(output)):
            if output[m][0] == j.split(" ")[0]:
                output[m][1] = output[m][1].replace('^', '').replace('_','')
                #print(j.replace('\n',' ') + output[m][1])
                f2.write(j.replace('\n',' ') + output[m][1] + '\n')

    f2.close()
    
    end_time = datetime.datetime.now()
    time_diff = end_time - start_time
    print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

import os
import re
import shutil
import ast
import sys
from pathlib import Path

source_dir = "./circle_draw/"
#target_dir = "./" + sys.argv[1] + "/"
target_dir = str(Path(sys.argv[1]).resolve()) + "/"

#os.makedirs(target_dir, exist_ok=True)

imgfile = os.listdir(source_dir)


for filename in imgfile:
    src_path = os.path.join(source_dir, filename)
    dst_path = os.path.join(target_dir, filename)
    shutil.copy2(src_path, dst_path)




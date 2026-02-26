import sys
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import datetime
from pathlib import Path

def line_similar(line1, line2, angle_threshold=5, position_threshold=50):
    # 取出向量
    vec1 = np.array([line1[2] - line1[0], line1[3] - line1[1]]) # (Δx, Δy)
    vec2 = np.array([line2[2] - line2[0], line2[3] - line2[1]])

    # 計算方向角
    cos_theta = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) #cos(θ) = (A·B) / (||A|| × ||B||)
    angle_diff = np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0))) 
    

    # 端點距離平均
    start_dist = np.linalg.norm(np.array(line1[:2]) - np.array(line2[:2]))
    end_dist = np.linalg.norm(np.array(line1[2:]) - np.array(line2[2:]))
    avg_dist = (start_dist + end_dist) / 2

    similar = (
        angle_diff < angle_threshold and
        avg_dist < position_threshold
    )

    #print(f"angle: {angle_diff:.2f} ")
    #print(f"avg_dist: {avg_dist:.2f} ")
    return similar

def advanced_line_detection(image_path, label_path, image_name , output_dir):
    
    image = cv2.imread(image_path)
    image2 = cv2.imread(str(Path(__file__).resolve().parent / "B.png"))
    if image is None:
        print(f"無法讀取圖片: {image_path}")
        return None
    
    height_, width_= image.shape[:2]


    with open(label_path ,'r', encoding='utf-8') as f: #read label file
        label_r = f.readlines()


    # image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #彩色影像轉換為灰階影像

    #自適應閾值
    adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2) 
    
    #邊緣偵測
    edges2 = cv2.Canny(adaptive_thresh, 50, 150, 3) #50, 150


    # lines: A vector that will store the parameters (xstart,ystart,xend,yend) of the detected lines
    # threshold: The minimum number of intersections to "*detect*" a line
    # minLineLength: The minimum number of points that can form a line. Lines with less than this number of points are disregarded.
    # maxLineGap: The maximum gap between two points to be considered in the same line.
    
    lines = cv2.HoughLinesP(edges2, rho=1, theta=np.pi/180, threshold = 20, minLineLength = 8, maxLineGap = 10) #25, 15, 3
    # print(len(lines))
    
    result_image = image.copy()

    for j in label_r:
        parts = j.strip().split(" ")

        _, x, y, w, h = map(float, parts)

        #yolo 圓形的座標
        xmax = int((x*width_) + (w * width_)/2.0)
        xmin = int((x*width_) - (w * width_)/2.0)
        ymax = int((y*height_) + (h * height_)/2.0)
        ymin = int((y*height_) - (h * height_)/2.0)

        coords = [xmin - 15, ymin - 15, xmax + 15, ymax + 15]
        list_line = []
        dict_line = {}
        count = 0
        if lines is not None:
            for line in lines: #偵測到的全部線
                x1, y1, x2, y2 = line[0] #line的座標
                # cv2.line(result_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

                if (x1 >= coords[0] and x1 <= coords[2] and y1 >= coords[1] and y1 <= coords[3]) or (x2 >= coords[0] and x2 <= coords[2] and y2 >= coords[1] and y2 <= coords[3]):
                    # cv2.line(result_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    # print(line[0])
                    # print((y2-y1)/(x2-x1)) #斜率
                    list_line.append(line[0])
                    dict_line[count] = line[0]
                    count += 1


        #yolo圓形的框
        color = (14, 122, 104)#red 0, 0, 255
        c1, c2 = (int(coords[0]), int(coords[1])), (int(coords[2]), int(coords[3]))
        # cv2.rectangle(result_image, c1, c2, color, 1, cv2.LINE_AA)

        # E要放的位置
        target_width = xmax - xmin
        target_height = ymax - ymin

        # re_img2 = cv2.resize(image2, (target_width // 3, target_height // 3))

        paste_x = xmin + (target_width - image2.shape[1]) // 2
        paste_y = ymin + (target_height - image2.shape[0]) // 2

        paste_x2 = paste_x + image2.shape[1]
        paste_y2 = paste_y + image2.shape[0]

        # result_image[paste_y:paste_y2, paste_x:paste_x2] = image2 #[top:bottom, left:right]
        # cv2.rectangle(result_image, (paste_x,paste_y), (paste_x2,paste_y2), (0, 0, 102), 1, cv2.LINE_AA) #image2的外框
        print(paste_x, paste_y, paste_x2, paste_y2)

        num = 0
        paste_x = paste_x - num
        paste_y = paste_y - num
        paste_x2 = paste_x2 + num
        paste_y2 = paste_y2 + num
        
        # print(list_line)
        # print(dict_line)
        
        for m in range(len(list_line) - 1):
            for n in range(m+1, len(list_line)):
                # print(m, n)
                # print(line_similar(list_line[m], list_line[n]))
                similar = line_similar(list_line[m], list_line[n])
                if similar:
                    dict_line.pop(n, None)

        # print(dict_line)  
        # print(list_line[0])
        line_width = 2
        for value in dict_line.values():
            x1,y1,x2,y2 = value
            print(value)
            if (x2-x1) == 0:
                if y1 > paste_y2 and y2 > paste_y2:
                    cv2.line(result_image, (x2, y2), (x2, paste_y2), (0, 0, 0), line_width, cv2.LINE_AA) #pink color (255, 0, 255)
                elif y1 < paste_y and y2 < paste_y:
                    cv2.line(result_image, (x1, y1), (x2, paste_y), (0, 0, 0), line_width, cv2.LINE_AA) #pink color (255, 0, 255)


            else:
                m = (y2-y1)/(x2-x1) #斜率
                print(m)

                if m == 0:
                    if x1 < paste_x and x2 < paste_x: #▒~\▒E左▒~B~J
                        cv2.line(result_image, (x2, y2), (paste_x, y2), (0, 0, 0), line_width, cv2.LINE_AA)
                    elif x1 > paste_x2 and x2 > paste_x2: #▒~\▒E▒~O▒▒~B~J
                        cv2.line(result_image, (paste_x2, y1), (x1, y1), (0, 0, 0), line_width, cv2.LINE_AA)

                elif m > 0:
                    if x1 < paste_x and x2 < paste_x: #在E左邊 
                        adjust_y2 = int(m * (paste_x - x2) + y2)
                        print(x2, y2, paste_x, adjust_y2)
                        cv2.line(result_image, (x2, y2), (paste_x, adjust_y2), (0, 0, 0), line_width, cv2.LINE_AA) #pink color (255, 0, 255)
                    elif x1 > paste_x2 and x2 > paste_x2: #在E右邊
                        adjust_y1 = int(y1 - m * (x1 - paste_x2))
                        if paste_y2 < adjust_y1 and (adjust_y1 - paste_y2) > 5:
                            adjust_x1 = -(int(( y1 - paste_y2) / m - x1))
                            print(adjust_x1, paste_y2, x1, y1)
                            cv2.line(result_image, (adjust_x1, paste_y2), (x1, y1), (0, 0, 0), line_width, cv2.LINE_AA)
                        else:
                            print(paste_x2, adjust_y1, x1, y1)
                            cv2.line(result_image, (paste_x2, adjust_y1), (x1, y1), (0, 0, 0), line_width, cv2.LINE_AA)
                    else:
                        if y1 < paste_y and y2 < paste_y: #在上面
                            adjust_x1 = (int(( paste_y - y2) / m + x2))
                            cv2.line(result_image, (x2, y2), (adjust_x1, paste_y), (0, 0, 0), line_width, cv2.LINE_AA)
                        elif y1 > paste_y and y2 > paste_y: #在下面
                            adjust_x2 = -(int(( y1 - paste_y2) / m - x1))
                            cv2.line(result_image, (adjust_x2, paste_y2), (x1, y1), (0, 0, 0), line_width, cv2.LINE_AA)



                else: # m < 0
                    if x1 < paste_x and x2 < paste_x: #在E左邊
                        adjust_y2 = (int(m * (paste_x - x2) + y2))
                        if paste_y2 < adjust_y2 and (adjust_y2 - paste_y2) > 5:
                            adjust_x2 = (int(( paste_y2 - y2) / m + x2))
                            print(x2, y2, adjust_x2, paste_y2)
                            cv2.line(result_image, (x2, y2), (adjust_x2, paste_y2), (0, 0, 0), line_width, cv2.LINE_AA)
                        else:
                            print(x2, y2, paste_x, adjust_y2)
                            cv2.line(result_image, (x2, y2), (paste_x, adjust_y2), (0, 0, 0), line_width, cv2.LINE_AA)
                    elif x1 > paste_x2 and x2 > paste_x2: #在E右邊
                        adjust_y1 = -(int(m * (x1 - paste_x2)) - y1)
                        print(paste_x2, adjust_y1, x1, y1)
                        cv2.line(result_image, (paste_x2, adjust_y1), (x1, y1), (0, 0, 0), line_width, cv2.LINE_AA)
                    else:
                        if y1 < paste_y and y2 < paste_y: #在上面
                            adjust_x2 = -(int(( y1 - paste_y) / m - x1))
                            cv2.line(result_image, (adjust_x2, paste_y), (x1, y1), (0, 0, 0), line_width, cv2.LINE_AA)
                        elif y1 > paste_y and y2 > paste_y: #在下面
                            adjust_x1 = (int(( paste_y2 - y2) / m + x2))
                            cv2.line(result_image, (x2, y2), (adjust_x1, paste_y2), (0, 0, 0), line_width, cv2.LINE_AA)


        paste_x = paste_x + num
        paste_y = paste_y + num
        paste_x2 = paste_x2 - num
        paste_y2 = paste_y2 - num

        result_image[paste_y:paste_y2, paste_x:paste_x2] = image2 #[top:bottom, left:right]
                   

        print("---------------------------------------")
            

    # cv2.imshow('image1', image)
    # cv2.imshow('image2', edges2)


    # cv2.imshow('image3', result_image)
    result_image = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)

    cv2.imwrite(output_dir + image_name + ".png", result_image)
    # cv2.waitKey(0)
        

if __name__ == "__main__":
    
    start_time = datetime.datetime.now()

    image_dir = r'./output_replace_circle_blank/'
    label_dir = r'./exp_circle/labels/'
    output_dir = r'./circle_draw/'
    os.makedirs(output_dir, exist_ok=True)
    label_file = os.listdir(label_dir)

    for i in range(len(label_file)):#len(label_file)
        image_name = label_file[i].split(".")[0]
        image_path = image_dir + image_name + '_circle.png'
        label_path = label_dir + image_name + '.txt'
        if os.path.isfile(label_path):
            #print(image_name)
            advanced_lines = advanced_line_detection(image_path, label_path, image_name, output_dir)
    
    end_time = datetime.datetime.now()
    time_diff = end_time - start_time
    print(f"run time : {time_diff} (total seconds : {time_diff.total_seconds():.4f} seconds)")

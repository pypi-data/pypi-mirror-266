'''
摄像头设置相关的函数
'''

import cv2
import numpy as np
import math
from .robot_config import Device_Config

target_object = {
    'target_shape': 0,
    'target_color': 0,
    'color': 0,
    'shape': 0,
    'x': 0,
    'y': 0,
    'flag': 0
}


class DetectResult:
    color = None
    shape = None


screen_result_pic = {
    'red_cube': '颜色图形.001.png',
    'red_cylinder': '颜色图形.002.png',
    'red_conical': '颜色图形.003.png',
    'green_cube': '颜色图形.004.png',
    'green_cylinder': '颜色图形.005.png',
    'green_conical': '颜色图形.006.png',
    'yellow_cube': '颜色图形.007.png',
    'yellow_cylinder': '颜色图形.008.png',
    'yellow_conical': '颜色图形.009.png'
}
colors_value = {
    'red': [0, 0, 0, 0, 0, 0],
    'green': [0, 0, 0, 0, 0, 0],
    'yellow': [0, 0, 0, 0, 0, 0]
}

p_colors_value = {
    'red': [0, 0, 0, 0, 0, 0],
    'green': [0, 0, 0, 0, 0, 0],
    'yellow': [0, 0, 0, 0, 0, 0]
}
detect_color = ('red', 'green', 'yellow')
detect_shape = ('cylinder', 'cube', 'conical')


class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 设置OpenCV内部的图像缓存，可以极大提高图像的实时性。
        self.params = Device_Config('/root/unibot/robot_param_init.txt')
        self.load_color_value()
        self.load_p_color_value()

        cv2.namedWindow('camera', cv2.WND_PROP_FULLSCREEN)  # 窗口全屏
        cv2.setWindowProperty('camera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)  # 窗口全屏

    # 返回一帧图像
    def get_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # 将图片尺寸修改为320*240
                frame = cv2.resize(frame, (320, 240))
                frame = cv2.rotate(frame, cv2.ROTATE_180)
                return frame

    # 显示摄像头图像
    def show_frame(self, img):
        cv2.imshow('camera', img)
        cv2.waitKey(1)

    def update_frame(self, times):
        for i in range(times):
            self.get_frame()

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()

    # 图片的初步处理，灰度化，二值化
    def image_pre_processing(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        # 轮廓腐蚀
        eroded_img = cv2.erode(gray_img, element, iterations=1)

        # 图像二值化处理
        ret, binary = cv2.threshold(eroded_img, 0, 255, cv2.THRESH_OTSU)

        # 轮廓膨胀
        dilated_img = cv2.dilate(binary, element, iterations=1)
        return dilated_img

    # 识别水平的线条用于对齐矫正机器人
    def detect_horizontal_line(self, img):
        lineColorSet = 0
        frame = self.image_pre_processing(img)
        # 点的数量，判断横着的黑线

        # 处理图片变成点
        linePos_1 = 5

        # 画面宽度参数
        linePos_2 = 320 - 5
        colorPos_1 = frame[:, linePos_1]
        colorPos_2 = frame[:, linePos_2]

        try:
            lineColorCount_Pos1 = np.sum(colorPos_1 == lineColorSet)
            lineColorCount_Pos2 = np.sum(colorPos_2 == lineColorSet)

            lineIndex_Pos1 = np.where(colorPos_1 == lineColorSet)
            lineIndex_Pos2 = np.where(colorPos_2 == lineColorSet)
            if lineColorCount_Pos1 == 0:
                lineColorCount_Pos1 = 1
            if lineColorCount_Pos2 == 0:
                lineColorCount_Pos2 = 1
            down_Pos1 = lineIndex_Pos1[0][lineColorCount_Pos1 - 1]
            up_Pos1 = lineIndex_Pos1[0][0]
            center_Pos1 = int((down_Pos1 + up_Pos1) / 2)

            down_Pos2 = lineIndex_Pos2[0][lineColorCount_Pos2 - 1]
            up_Pos2 = lineIndex_Pos2[0][0]
            center_Pos2 = int((down_Pos2 + up_Pos2) / 2)

            cv2.line(img, (linePos_1, up_Pos1), (linePos_2, up_Pos2), (255, 128, 64), 2)
            cv2.line(img, (linePos_1, down_Pos1), (linePos_2, down_Pos2), (255, 128, 64), 2)

            cv2.line(img, (linePos_1, up_Pos1), (linePos_1, down_Pos1), (255, 128, 64), 2)
            cv2.line(img, (linePos_2, up_Pos2), (linePos_2, down_Pos2), (255, 128, 64), 2)

            cv2.line(img, (linePos_1, center_Pos1), (linePos_2, center_Pos2), (255, 128, 64), 2)
            if abs(center_Pos1 - center_Pos2) < 3:
                isEnd = True
            else:
                isEnd = False

            return isEnd, (center_Pos1, center_Pos2), img

        except:
            print("水平对线出现错误！")
            pass

    # 识别垂直的黑色线条用于巡行前进
    def detect_vertical_black_line(self, img):
        lineColorSet = 0
        frame = self.image_pre_processing(img)
        startLine = 30
        setp = 40
        num = 5
        # 点的数量，判断横着的黑线

        left_Pos2 = 0
        right_Pos2 = 0
        ls = []
        lsc = []

        for i in range(0, num):
            # 上线1
            linePos_1 = startLine + i * setp
            # 下线2
            linePos_2 = startLine + (i + 1) * setp
            # 在线1上面的所有点
            colorPos_1 = frame[linePos_1]
            # 在线2上面的所有点
            colorPos_2 = frame[linePos_2]
            left_Pos1 = 0
            right_Pos1 = 320
            left_Pos2 = 0
            right_Pos2 = 320

            try:
                # 匹配符合设置的区域的线
                # 找到线1上面的所有点的数量
                lineColorCount_Pos1 = np.sum(colorPos_1 == lineColorSet)
                # 找到线2上面的所有点的数量
                lineColorCount_Pos2 = np.sum(colorPos_2 == lineColorSet)
                # 找到线1上面的所有点的坐标，只有x坐标
                lineIndex_Pos1 = np.where(colorPos_1 == lineColorSet)
                # 找到线2上面的所有点的坐标，只有x坐标
                lineIndex_Pos2 = np.where(colorPos_2 == lineColorSet)
                # 没有找到点那么点的数量为1
                if lineColorCount_Pos1 == 0:
                    lineColorCount_Pos1 = 1
                if lineColorCount_Pos2 == 0:
                    lineColorCount_Pos2 = 1

                # 线1最左边的点的x坐标
                left_Pos1 = lineIndex_Pos1[0][lineColorCount_Pos1 - 1]
                # 线1最右边的点的x坐标
                right_Pos1 = lineIndex_Pos1[0][0]
                # 线1的中间点
                center_Pos1 = int((left_Pos1 + right_Pos1) / 2)

                # 线2最左边的点的x坐标
                left_Pos2 = lineIndex_Pos2[0][lineColorCount_Pos2 - 1]
                # 线2最右边的点的x坐标
                right_Pos2 = lineIndex_Pos2[0][0]
                # 线2的中间点
                center_Pos2 = int((left_Pos2 + right_Pos2) / 2)
                # 线1和线2中间的x坐标
                center = int((center_Pos1 + center_Pos2) / 2)
                # print(center)
            except:
                center = None
                pass
            # print(center)
            # 找点
            # contours, hierarchy = cv2.findContours(imggray,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
            # print(len(contours))
            lsc.append(lineColorCount_Pos1)
            try:
                if (center != None):
                    cv2.line(img, (left_Pos1, linePos_1), (left_Pos2, linePos_2), (255, 128, 64), 2)
                    cv2.line(img, (right_Pos1, linePos_1), (right_Pos2, linePos_2), (255, 128, 64), 2)
                    cv2.circle(img, (center, int((linePos_1 + linePos_2) / 2)), 5, (0, 255, 0),
                               -1)  # Draw middle circle RED
                    cv2.circle(img, (160, int((linePos_1 + linePos_2) / 2)), 5, (255, 255, 255), -1)
                    cv2.line(img, (160, int((linePos_1 + linePos_2) / 2)), (center, int((linePos_1 + linePos_2) / 2)),
                             (0, 0, 200), 2)
                    cv2.line(img, (left_Pos1, linePos_1), (right_Pos1, linePos_1), (255, 128, 64), 2)
                    cv2.line(img, (left_Pos2, linePos_2), (right_Pos2, linePos_2), (255, 128, 64),
                             2)  # cv2.line(img,(center-20,int((linePos_1+linePos_2)/2)),(center+20,int((linePos_1+linePos_2)/2)),(0,255,0),2)
            except:
                pass
            ls.append([center, int((linePos_1 + linePos_2) / 2)])

        return ls, lsc, img

    def display_text(self, img, str):
        cv2.putText(img, str, (160, 240), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)

    def load_color_value(self):

        colors_value['red'] = self.params.readconfsectionvalue('RED')
        colors_value['green'] = self.params.readconfsectionvalue('GREEN')
        colors_value['yellow'] = self.params.readconfsectionvalue('YELLOW')

    def load_p_color_value(self):
        p_colors_value['red'] = self.params.readconfsectionvalue('P_RED')
        p_colors_value['green'] = self.params.readconfsectionvalue('P_GREEN')
        p_colors_value['yellow'] = self.params.readconfsectionvalue('P_YELLOW')

    # 识别物体颜色形状
    def detect_object(self, myt, color_area, round_square_threshold, big_small_round_threshold, times=10):
        for l in range(0, myt):
            frame = self.get_frame()
        color_flag = 3
        str = ""

        color_flag = self.detect_object_color(times, color_area)
        if (color_flag == 0):
            str += "红色"
            target_object['color'] = 0
        elif (color_flag == 1):
            str += "绿色"
            target_object['color'] = 1
        else:
            str += "黄色"
            target_object['color'] = 2
        shape_flag = 3
        print("颜色识别结束，颜色为:", str)

        shape_flag = self.detect_object_shape(color_flag, round_square_threshold, big_small_round_threshold, times=10)
        if (shape_flag == 0):
            str += "圆柱"
            target_object['shape'] = 0
        elif (shape_flag == 1):
            str += "锥体"
            target_object['shape'] = 1
        else:
            str += "方块"
            target_object['shape'] = 2
        print("本次识别结果为：", str)
        if (target_object['shape'] == target_object['target_shape'] and target_object["target_color"] == target_object[
            "shape"]):
            target_object["flag"] = 1
        else:
            target_object["flag"] = 0
        print("形状识别结束,真假为:", target_object["flag"])

    # 识别物体颜色
    def detect_object_color(self, times: int, target: int):
        rs = []
        for l in range(0, times):
            frame = self.get_frame()
            img = frame.copy()
            timg = cv2.medianBlur(img, 5)
            lab = cv2.cvtColor(timg, cv2.COLOR_BGR2LAB)
            color_value = []
            color_value.append(colors_value['red'])
            color_value.append(colors_value['green'])
            color_value.append(colors_value['yellow'])
            # print(color_value)
            for i in range(3):
                lower = np.array([color_value[i][0], color_value[i][1], color_value[i][2]])
                upper = np.array([color_value[i][3], color_value[i][4], color_value[i][5]])
                mask = cv2.inRange(lab, lower, upper)
                cnts, hei = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                for c in cnts:
                    area = cv2.contourArea(c)

                    if area > target:
                        rect = cv2.minAreaRect(c)
                        box = cv2.boxPoints(rect)
                        box = np.int0(box)
                        # print(box)
                        center_x = 0
                        center_y = 0
                        for ti in box:
                            center_x += ti[0]
                            center_y += ti[1]
                        center_x = int(center_x / 4)
                        center_y = int(center_y / 4)
                        if 40 < center_x < 280 and 30 < center_y < 260:
                            print("颜色面积:", area)
                            # print("色块中心点:",center_x,center_y)
                            rs.append(i)
                    # cv2.imshow('camera', mask)
                    # cv2.waitKey(1)
        print(rs)
        check = [0, 0, 0]
        for i in rs:
            check[i] += 1
        # 0红色
        if check[0] > check[1] and check[0] > check[2]:
            return 0
        # 1绿色
        elif check[1] > check[0] and check[1] > check[2]:
            return 1
        # 2黄色
        elif check[2] > check[0] and check[2] > check[1]:
            return 2
        # 3重新识别
        else:
            return 3

    # 识别物体形状
    def detect_object_shape(self, color_flag, round_square_threshold, big_small_round_threshold, times=10,
                            target_area=5000):
        rs = []
        for i in range(0, times):
            frame = self.get_frame()
            img = frame.copy()
            timg = cv2.medianBlur(img, 5)
            lab = cv2.cvtColor(timg, cv2.COLOR_BGR2LAB)
            color_value = []
            if color_flag == 0:
                color_value = colors_value['red']
            if color_flag == 1:
                color_value = colors_value['green']
            if color_flag == 2:
                color_value = colors_value['yellow']
            if color_flag == 3:
                continue
            lower = np.array([color_value[0], color_value[1], color_value[2]])
            upper = np.array([color_value[3], color_value[4], color_value[5]])
            mask = cv2.inRange(lab, lower, upper)

            cnts, hei = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            mx = 0
            my = 0
            height, width = img.shape[:2]
            cy = height / 2
            cx = width / 2
            lex = 0
            ley = 0
            for c in cnts:
                area = cv2.contourArea(c)
                if area > target_area:
                    # print(c)
                    minx = c[0][0][0]
                    miny = c[0][0][1]
                    maxx = c[0][0][0]
                    maxy = c[0][0][1]
                    mix = 99999
                    maax = 0
                    for p in c:
                        minx = min(minx, p[0][0])
                        miny = min(miny, p[0][1])
                        maxx = max(maxx, p[0][0])
                        maxy = max(maxy, p[0][1])
                    for p in c:
                        if miny + 5 >= p[0][1]:
                            mix = min(mix, p[0][0])
                            maax = max(maax, p[0][0])
                    mx = int((minx + maxx) / 2)
                    my = int((miny + maxy) / 2)
                    cv2.circle(img, (int((minx + maxx) / 2), int((miny + maxy) / 2)), 3, (255, 0, 0), 3)
                    cv2.circle(img, (int(cx), int(cy)), 3, (255, 255, 255), 3)
                    peri = cv2.arcLength(c, True)
                    approx = cv2.approxPolyDP(c, 0.001 * peri, False)
                    x, y, w, h = cv2.boundingRect(c)
                    rect = cv2.minAreaRect(c)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    # print(box)
                    box_area = cv2.contourArea(box)
                    # print(area)
                    # print(float(area/area2))
                    # cv2.drawContours(img, [box], 0, (0, 255, 0), 2)
                    # print(rect)
                    # for p in approx:
                    # print(p)
                    # cv2.circle(img,(p[0][0],p[0][1]),2,(255,0,0),3)
                    # print(area)
                    per = (area / box_area) * 100
                    # cv2.drawContours(img,[c],0,(0),2)
                    # cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv2.putText(img, "Point:" + str(len(approx)), (x + w + 10, y + h + 10), cv2.FONT_HERSHEY_COMPLEX,
                                0.7, (0, 255, 0), 2)
                    print("面积", area)
                    print("百分比:", per)
                    # print("点数",len(approx))
                    if area <= big_small_round_threshold:
                        cv2.circle(img, (int((minx + maxx) / 2), int((miny + maxy) / 2)), int((maxy - miny) / 2),
                                   (255, 0, 0), 3)
                        cv2.putText(img, "conical", (x + w, y + h), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
                        rs.append(1)

                    else:
                        if per < round_square_threshold:
                            cv2.circle(img, (int((minx + maxx) / 2), int((miny + maxy) / 2)), int((maxy - miny) / 2),
                                       (255, 0, 0), 3)
                            cv2.putText(img, "cylinder", (x + w, y + h), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
                            rs.append(0)
                        else:
                            cv2.line(img, (minx, miny), (maxx, miny), color=(255, 0, 0), thickness=2)
                            cv2.line(img, (minx, miny), (minx, maxy), color=(255, 0, 0), thickness=2)
                            cv2.line(img, (maxx, maxy), (maxx, miny), color=(255, 0, 0), thickness=2)
                            cv2.line(img, (maxx, maxy), (minx, maxy), color=(255, 0, 0), thickness=2)
                            cv2.putText(img, "cube", (x + w, y + h), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
                            rs.append(2)

                    now_center_x = int((minx + maxx) / 2)
                    now_center_y = int((miny + maxy) / 2)
                    target_object['x'] = now_center_x
                    target_object['y'] = now_center_y
                    # 设置范围
                    cv2.imshow('camera', img)
                    cv2.waitKey(1)
                    # print(all_center_x,all_center_y)
        check = [0, 0, 0]
        for i in rs:
            check[i] += 1
        # 0圆柱
        if check[0] > check[1] and check[0] > check[2]:
            return 0
        # 1圆锥
        elif check[1] > check[0] and check[1] > check[2]:
            return 1
        # 2方块
        elif check[2] > check[0] and check[2] > check[1]:
            return 2
        else:
            return 3

        # 识别屏幕物体颜色的

    def get_detect_result(self, ask):
        return target_object[ask]

    def detect_screen_object(self, color_area, conical_offset, cylinder_offset):
        color_flag = 3
        str = ""

        color_flag = self.detect_screen_object_color(10, color_area)
        if color_flag == 0:
            str += "红色"
            target_object['target_color'] = 0

            print("红色")
        elif color_flag == 1:
            str += "绿色"
            target_object['target_color'] = 1
            print("绿色")
        else:
            str += "黄色"
            target_object['target_color'] = 2

            print("黄色")
        shape_flag = 3
        print("颜色识别结束")
        shape_flag = self.detect_screen_object_shape(10, color_flag, conical_offset, cylinder_offset, color_area)
        if shape_flag == 0:
            str += "圆柱"
            target_object['target_shape'] = 0
            print("圆柱")
        elif shape_flag == 1:
            str += "锥体"
            target_object['target_shape'] = 1

            print("锥体")
        else:
            str += "方块"
            target_object['target_shape'] = 2
            print("方块")
        print("形状识别结束")

        # 识别屏幕物体颜色的

    def detect_screen_object_color(self, times, target: int):
        rs = []
        for i in range(0, times):
            frame = self.get_frame()
            img = frame.copy()
            timg = cv2.medianBlur(img, 5)
            lab = cv2.cvtColor(timg, cv2.COLOR_BGR2LAB)
            color_value = []
            color_value.append(p_colors_value['red'])
            color_value.append(p_colors_value['green'])
            color_value.append(p_colors_value['yellow'])
            # print(color_value)
            for i in range(3):
                lower = np.array([color_value[i][0], color_value[i][1], color_value[i][2]])
                upper = np.array([color_value[i][3], color_value[i][4], color_value[i][5]])
                mask = cv2.inRange(lab, lower, upper)
                cnts, hei = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                for c in cnts:
                    area = cv2.contourArea(c)
                    if area > target:
                        rs.append(i)
        check = [0, 0, 0]
        for i in rs:
            check[i] += 1
        # 0红色
        if check[0] > check[1] and check[0] > check[2]:

            return 0
        # 1绿色
        elif check[1] > check[0] and check[1] > check[2]:

            return 1
        # 2黄色
        elif check[2] > check[0] and check[2] > check[1]:

            return 2
        # 3重新识别
        else:
            return 3

        # 识别屏幕物体的形状

    def detect_screen_object_shape(self, times, color_flag, conical_offset, cylinder_offset, target):
        rs = []

        color_value = []
        if color_flag == 0:
            color_value = p_colors_value['red']
        if color_flag == 1:
            color_value = p_colors_value['green']
        if color_flag == 2:
            color_value = p_colors_value['yellow']
        # 错误情况
        if color_flag == 3:
            color_value = p_colors_value['red']
        # print("阈值",color_value)
        for i in range(0, times):

            frame = self.get_frame()
            img = frame.copy()
            timg = cv2.medianBlur(img, 5)
            lab = cv2.cvtColor(timg, cv2.COLOR_BGR2LAB)
            lower = np.array([color_value[0], color_value[1], color_value[2]])
            upper = np.array([color_value[3], color_value[4], color_value[5]])
            mask = cv2.inRange(lab, lower, upper)
            cnts, hei = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            for c in cnts:
                area = cv2.contourArea(c)
                if area > target:

                    rect = cv2.minAreaRect(c)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    box_area = cv2.contourArea(box)

                    cv2.imshow('camera', mask)
                    cv2.waitKey(1)
                    per = (area / box_area) * 100
                    print(per)
                    if per > cylinder_offset:
                        # 圆柱
                        rs.append(0)
                    elif per < conical_offset:
                        # 锥形
                        rs.append(1)
                    else:
                        # 方块
                        rs.append(2)
        # except:
        # print("屏幕识别错误")
        # pass

        # print(rs)
        check = [0, 0, 0]
        for i in rs:
            check[i] += 1
        # 0圆柱
        if check[0] > check[1] and check[0] > check[2]:
            return 0
        # 1锥形
        elif check[1] > check[0] and check[1] > check[2]:
            return 1
        # 2方形
        elif check[2] > check[0] and check[2] > check[1]:
            return 2
        # 3重新识别
        else:
            return 3

            # 识别物体中心，用来矫正

    def detect_object_center(self, color_flag: int, target_area: int = 5000):
        color_value = []
        if color_flag == 0:
            color_value = colors_value['red']
        if color_flag == 1:
            color_value = colors_value['green']
        if color_flag == 2:
            color_value = colors_value['yellow']
        frame = self.get_frame()
        img = frame.copy()
        timg = cv2.medianBlur(img, 5)
        lab = cv2.cvtColor(timg, cv2.COLOR_BGR2LAB)
        lower = np.array([color_value[0], color_value[1], color_value[2]])
        upper = np.array([color_value[3], color_value[4], color_value[5]])
        mask = cv2.inRange(lab, lower, upper)
        cnts, hei = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        center_x = 0
        center_y = 0
        try:
            for c in cnts:
                area = cv2.contourArea(c)
                if area > target_area:
                    # print("面积为",area)
                    # print("点的信息为",c)
                    # cv2.drawContours(img, c, -1, (0, 0, 255), thickness=4)
                    # peri=cv2.arcLength(c,True)
                    # approx=cv2.approxPolyDP(c,0.005 * peri,True)
                    # print("点的数量",len(approx))
                    # cv2.imshow('camera', mask)
                    # cv2.waitKey(1)
                    # time.sleep(5)

                    rect = cv2.minAreaRect(c)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    center_x = 0
                    center_y = 0
                    # print(box)
                    for i in box:
                        center_x += i[0]
                        center_y += i[1]
                    center_x = int(center_x / 4)
                    center_y = int(center_y / 4)
                    # print(area)
                    # print(float(area/area2))
                    # cv2.drawContours(img, [box], 0, (0, 255, 0), 2)
                    # print(rect)
                    # for p in approx:
                    # print(p)
                    # cv2.circle(img,(p[0][0],p[0][1]),2,(255,0,0),3)
                    cv2.circle(img, (center_x, center_y), 2, (255, 0, 0), 3)
                    cv2.imshow('camera', img)
                    cv2.waitKey(1)

            if 60 < center_x < 260 and 40 < center_y <= 200:
                return center_x, center_y
            else:
                return -1, -1
        except:
            return -1, -1

    def getAreaMaxContour(self, contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  # 历遍所有轮廓
            contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 100:  # 只有在面积大于设定时，最大面积的轮廓才是有效的，以过滤干扰
                    area_max_contour = c

        return area_max_contour, contour_area_max  # 返回最大的轮廓

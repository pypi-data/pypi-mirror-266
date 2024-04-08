import cv2
import numpy as np
import math


#创建一个图像处理类
class CAMERA:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)     #设置OpenCV内部的图像缓存，可以极大提高图像的实时性。

        cv2.namedWindow('camera',cv2.WND_PROP_FULLSCREEN)    #窗口全屏
        cv2.setWindowProperty('camera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)   #窗口全屏

    #返回一帧图像
    def get_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                #将图片尺寸修改为320*240
                frame = cv2.resize(frame, (320, 240))
                return frame
    
    #显示摄像头图像
    def show_frame(self,img):
        cv2.imshow('camera', img)
        cv2.waitKey(1) 
                    


    #关闭摄像头并销毁窗口
    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()

    #图片的初步处理，灰度化，二值化
    def image_pre_processing(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        #轮廓腐蚀
        eroded_img = cv2.erode(gray_img, element, iterations=1)

        #图像二值化处理
        ret, binary = cv2.threshold(eroded_img,0,255,cv2.THRESH_OTSU)
        
        #轮廓膨胀
        dilated_img = cv2.dilate(binary, element, iterations=1)
        return dilated_img
    

    #识别水平的线条用于对齐矫正机器人
    def detect_horizontal_line(self, img):
        lineColorSet=0
        frame = self.image_pre_processing(img)
        #点的数量，判断横着的黑线

        #处理图片变成点
        linePos_1=5

        #画面宽度参数
        linePos_2=320-5
        colorPos_1=frame[:, linePos_1]
        colorPos_2=frame[:, linePos_2]

        try:
            lineColorCount_Pos1=np.sum(colorPos_1==lineColorSet)
            lineColorCount_Pos2=np.sum(colorPos_2==lineColorSet)
            
            lineIndex_Pos1 = np.where(colorPos_1==lineColorSet)
            lineIndex_Pos2 = np.where(colorPos_2==lineColorSet)
            if lineColorCount_Pos1 == 0:
                lineColorCount_Pos1 = 1
            if lineColorCount_Pos2 == 0:
                lineColorCount_Pos2 = 1
            down_Pos1=lineIndex_Pos1[0][lineColorCount_Pos1-1]
            up_Pos1=lineIndex_Pos1[0][0]
            center_Pos1=int((down_Pos1+up_Pos1)/2)

            down_Pos2=lineIndex_Pos2[0][lineColorCount_Pos2-1]
            up_Pos2=lineIndex_Pos2[0][0]
            center_Pos2=int((down_Pos2+up_Pos2)/2)

            cv2.line(img,(linePos_1,up_Pos1),(linePos_2,up_Pos2),(255,128,64),2)
            cv2.line(img,(linePos_1,down_Pos1),(linePos_2,down_Pos2),(255,128,64),2)

            cv2.line(img,(linePos_1,up_Pos1),(linePos_1,down_Pos1),(255,128,64),2)
            cv2.line(img,(linePos_2,up_Pos2),(linePos_2,down_Pos2),(255,128,64),2)

            cv2.line(img,(linePos_1,center_Pos1),(linePos_2,center_Pos2),(255,128,64),2)
            if abs(center_Pos1 - center_Pos2) <3:
                isEnd = True
            else:
                isEnd = False

            return isEnd,(center_Pos1, center_Pos2),img

        except:
            print("水平对线出现错误！")
            pass


    #识别垂直的黑色线条用于巡行前进
    def detect_vertical_black_line(self, img,lineColorSet):
        frame = self.image_pre_processing(img)
        startLine=30
        setp=40
        num=5
        #点的数量，判断横着的黑线
        endpointnum=200
        left_Pos2=0
        right_Pos2=0
        ls=[]
        lsc=[]

        for i in  range(0,num):
            #上线1
            linePos_1=startLine+i*setp
            #下线2
            linePos_2=startLine+(i+1)*setp
            #在线1上面的所有点
            colorPos_1=frame[linePos_1]
            #在线2上面的所有点
            colorPos_2=frame[linePos_2]
            left_Pos1=0
            right_Pos1=320
            left_Pos2=0
            right_Pos2=320

            try:
                #匹配符合设置的区域的线
                #找到线1上面的所有点的数量
                lineColorCount_Pos1=np.sum(colorPos_1==lineColorSet)
                #找到线2上面的所有点的数量
                lineColorCount_Pos2=np.sum(colorPos_2==lineColorSet)
                #找到线1上面的所有点的坐标，只有x坐标
                lineIndex_Pos1 = np.where(colorPos_1==lineColorSet)
                #找到线2上面的所有点的坐标，只有x坐标
                lineIndex_Pos2 = np.where(colorPos_2==lineColorSet) 
                #没有找到点那么点的数量为1
                if lineColorCount_Pos1 == 0:
                    lineColorCount_Pos1 = 1
                if lineColorCount_Pos2 == 0:
                    lineColorCount_Pos2 = 1
                
                #线1最左边的点的x坐标
                left_Pos1=lineIndex_Pos1[0][lineColorCount_Pos1-1]
                #线1最右边的点的x坐标
                right_Pos1=lineIndex_Pos1[0][0]
                #线1的中间点
                center_Pos1=int((left_Pos1+right_Pos1)/2)

                #线2最左边的点的x坐标
                left_Pos2=lineIndex_Pos2[0][lineColorCount_Pos2-1]
                #线2最右边的点的x坐标
                right_Pos2=lineIndex_Pos2[0][0]
                #线2的中间点
                center_Pos2=int((left_Pos2+right_Pos2)/2)
                #线1和线2中间的x坐标
                center=int((center_Pos1+center_Pos2)/2)
                #print(center)
            except:
                center=None
                pass
        #print(center)
        #找点
        #contours, hierarchy = cv2.findContours(imggray,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        #print(len(contours))
            lsc.append(lineColorCount_Pos1)
            try:
                if(center!=None):
                    cv2.line(img,(left_Pos1,linePos_1),(left_Pos2,linePos_2),(255,128,64),2)
                    cv2.line(img,(right_Pos1,linePos_1),(right_Pos2,linePos_2),(255,128,64),2)
                    cv2.circle(img, (center, int((linePos_1+linePos_2)/2)), 5, (0,255,0), -1) #Draw middle circle RED
                    cv2.circle(img, (160, int((linePos_1+linePos_2)/2)), 5, (255,255,255), -1)
                    cv2.line(img,(160,int((linePos_1+linePos_2)/2)),(center,int((linePos_1+linePos_2)/2)),(0,0,200),2)
                    cv2.line(img,(left_Pos1,linePos_1),(right_Pos1,linePos_1),(255,128,64),2)   
                    cv2.line(img,(left_Pos2,linePos_2),(right_Pos2,linePos_2),(255,128,64),2) #cv2.line(img,(center-20,int((linePos_1+linePos_2)/2)),(center+20,int((linePos_1+linePos_2)/2)),(0,255,0),2)
            except:
                pass        
            ls.append([center,int((linePos_1+linePos_2)/2)])

        if(lsc[1]>endpointnum):
            isEnd = True
        else:
            isEnd = False

        return isEnd,ls,img
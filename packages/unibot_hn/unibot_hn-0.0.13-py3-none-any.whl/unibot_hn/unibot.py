from .board import Board
from .camera import Camera
from .robot_config import Device_Config
import math
import unibot_hn.Misc as Misc
import time
from threading import Thread

th = None
slow_en = True

last_velocity = 0
last_angular = 0
last_direction = 90

servo_init_error_default = {'e1': 0, 'e2': 0, 'e3': 0, 'e4': 0}
servo_init_direction_default = {'e1d': 0, 'e2d': 0, 'e3d': 0, 'e4d': 0}


# 定义一个底盘
class MecanumChassis:
    def __init__(self, board, a=110, b=70, wheel_diameter=80.5, pulse_per_cycle=44 * 178):
        self.board = board
        self.a = a
        self.b = b
        self.wheel_diameter = wheel_diameter
        self.pulse_per_cycle = pulse_per_cycle
        self.velocity = 0
        self.direction = 0
        self.angular_rate = 0

    def speed_covert(self, speed):
        """
        covert speed mm/s to pulse/10ms
        :param speed:
        :return:
        """
        return speed / (math.pi * self.wheel_diameter)  # pulse/10ms

    def drive_wheels(self, LF, RF, LB, RB):
        lf_pulse = self.speed_covert(LF)
        rf_pulse = self.speed_covert(RF)
        lb_pulse = self.speed_covert(LB)
        rb_pulse = self.speed_covert(RB)
        self.board.set_motor_speed([[1, lf_pulse], [2, -rf_pulse], [3, lb_pulse], [4, -rb_pulse]])

    def reset_motors(self):
        self.board.set_motor_speed([[1, 0], [2, 0], [3, 0], [4, 0]])

        self.velocity = 0
        self.direction = 0
        self.angular_rate = 0

    def set_velocity(self, velocity, direction, angular_rate, fake=False):
        """
        底盘电机连接方式
        motor1 v2|  ↑  |v1 motor2
                 |     |
        motor3 v3|     |v4 motor4

        :param velocity: mm/s
        :param direction: Moving direction 0~360deg, 180deg<--- ↑ ---> 0deg
        :param angular_rate:  The speed at which the chassis rotates
        :param fake:
        :return:
        """
        velocity = -velocity
        # angular_rate = -angular_rate

        rad_per_deg = math.pi / 180
        vx = velocity * math.cos(direction * rad_per_deg)
        vy = velocity * math.sin(direction * rad_per_deg)
        vp = angular_rate * rad_per_deg * (self.a + self.b)
        v1 = vy - vx + vp
        v2 = vy + vx - vp
        v3 = vy - vx - vp
        v4 = vy + vx + vp
        v_s = [(self.speed_covert(v)) for v in [-v2, v1, -v3, v4]]

        if fake:
            return v_s

        self.board.set_motor_speed([[1, v_s[0]], [2, v_s[1]], [3, v_s[2]], [4, v_s[3]]])
        self.velocity = velocity
        self.direction = direction
        self.angular_rate = angular_rate

    # 控制XY方向平移函数
    def translation(self, velocity_x, velocity_y, fake=False):
        global slow_en

        velocity = math.sqrt(velocity_x ** 2 + velocity_y ** 2)
        if velocity_x == 0:
            direction = 90 if velocity_y >= 0 else 270  # pi/2 90deg, (pi * 3) / 2  270deg
        else:
            if velocity_y == 0:
                direction = 0 if velocity_x > 0 else 180
            else:
                direction = math.atan(velocity_y / velocity_x)  # θ=arctan(y/x) (x!=0)
                direction = direction * 180 / math.pi
                if velocity_x < 0:
                    direction += 180
                else:
                    if velocity_y < 0:
                        direction += 360
        if fake:
            return velocity, direction

        else:
            th = Thread(target=self.slow_velocity, args=(velocity, direction, 0))
            th.setDaemon(True)
            th.start()

    # 缓变速处理函数
    def slow_velocity(self, velocity, direction, angular):
        global th
        global last_velocity
        global last_angular
        global last_direction

        added_v = 30
        added_a = 0.2
        diff_velocity = velocity - last_velocity
        diff_angular = angular - last_angular

        if abs(diff_velocity) >= added_v or abs(diff_angular) >= added_a:
            if diff_velocity > added_v:
                dv = added_v
            elif diff_velocity < -added_v:
                dv = -added_v
            else:
                dv = 0

            if diff_angular > added_a:
                da = added_a
            elif diff_angular < -added_a:
                da = -added_a
            else:
                da = 0

            direction_ = direction
            if velocity == 0 and direction <= 0 and angular == 0:
                direction = last_direction
            last_direction = direction_

            while abs(diff_velocity) > added_v or abs(diff_angular) > added_a:
                if abs(diff_velocity) >= added_v:
                    last_velocity += dv
                if abs(diff_angular) >= added_a:
                    last_angular += da

                diff_velocity = velocity - last_velocity
                diff_angular = angular - last_angular
                last_velocity = round(last_velocity, 2)
                last_angular = round(last_angular, 2)
                self.set_velocity(last_velocity, direction, last_angular)
                time.sleep(0.05)

            last_velocity = velocity
            last_angular = angular
            self.set_velocity(last_velocity, direction, last_angular)

        else:
            last_angular = angular
            last_velocity = velocity
            last_direction = direction
            self.set_velocity(velocity, direction, angular)

        th = None

    def translational_move(self, velocity_x, velocity_y):

        self.translation(velocity_x, velocity_y)

    def move(self, velocity, direction, angular):
        global th

        angular = round(angular, 2)

        if th is None:  # 通过子线程去控制缓变速
            th = Thread(target=self.slow_velocity, args=(velocity, direction, angular))
            th.setDaemon(True)
            th.start()

    def stop(self):
        self.set_velocity(0, 0, 0)

    def move_time(self, velocity, direction, angular, duration):
        self.move(velocity, direction, angular)
        time.sleep(duration)
        self.stop()
        time.sleep(0.2)


# 定义一个机械臂的类
class RoboticArm:
    def __init__(self, board, servo_init_error, servo_init_direction) -> None:
        self.board = board
        # 每台机器修正值不同需要在设置修改
        # 舵机1修正值
        self.e1 = servo_init_error['e1']
        # 舵机2修正值
        self.e2 = servo_init_error['e2']
        # 舵机3修正值
        self.e3 = servo_init_error['e3']
        # 舵机4修正值
        self.e4 = servo_init_error['e4']
        # 舵机1正反
        self.e1d = servo_init_direction['e1d']
        # 舵机2正反
        self.e2d = servo_init_direction['e2d']
        # 舵机3正反
        self.e3d = servo_init_direction['e3d']
        # 舵机4正反
        self.e4d = servo_init_direction['e4d']
        self.servoAngle = [0 for i in range(16)]
        # 根据机器的固定参数
        # 机器前后偏差
        self.P = 4.2
        # 机器上下偏差
        self.A1 = 14.8
        # 机械臂1长度
        self.A2 = 10.5
        # 机械臂2长度
        self.A3 = 8.5
        # 机械臂末端长度
        self.A4 = 8.9
        self.MAX_LEN = self.A1 + self.A2
        self.MAX_HIGH = self.A1 + self.A2 + self.A3 - self.A4

        # 舵机编码值和角度的转换参数
        self.e = 125.0 / 30.0
        # 舵机转化角度的偏差值
        self.ep = 125

    def cos(self, degree):
        return math.cos(math.radians(degree))

    def sin(self, degree):
        return math.sin(math.radians(degree))

    def atan2(self, v1, v2):
        rad = math.atan2(v1, v2)
        return math.degrees(rad)

    def _j_degree_convert(self, joint, j_or_deg):
        # 将j1-j4和机械臂的角度表达互换
        if joint == 1:
            res = j_or_deg
        elif joint == 2 or joint == 3 or joint == 4:
            res = 90 - j_or_deg
        else:
            # 只适用于1-4关节
            raise ValueError
        return res

    def _valid_degree(self, joint, degree):
        if -100 <= degree <= 240:
            return True

        else:
            print('joint {} is invalid degree {}'.format(joint, degree))
            return False

    def _valid_j(self, joint, j):
        if j is None:
            return False
        degree = self._j_degree_convert(joint, j)
        if -100 <= degree <= 240:
            return True
        else:
            print('joint {} is invalid j:{} degree {}'.format(joint, j, degree))
            return False

    def _out_of_range(self, lengh, height):
        MAX_HIGH = self.MAX_HIGH
        MAX_LEN = self.MAX_LEN
        if height > MAX_HIGH:
            print('高度 {} 超过界限 {}'.format(height, MAX_HIGH))
            return True
        if lengh > MAX_LEN:
            print('投影长度 {} 超过界限 {}'.format(lengh, MAX_LEN))
            return True
        return False

    def _calculate_j1(self, x, y, z):
        P = self.P
        length = round(math.sqrt(pow((y + P), 2) + pow(x, 2)), 10)
        #     print('length:{}'.format(length))
        #     print('y:{}'.format(y))
        length = -length
        if length == 0:
            j1 = 0  # 可以是任意数
        else:
            j1 = self.atan2((y + P), x)
        if (j1 < 0): j1 = j1 + 180
        hight = z
        #     print('j1:{}'.format(j1))
        return j1, length, hight

    def _calculate_j3(self, L, H, y):
        A2 = self.A2
        A3 = self.A3

        cos3 = (L ** 2 + H ** 2 - A2 ** 2 - A3 ** 2) / (2 * A2 * A3)
        #     print('cos3:{}'.format(cos3))
        # cos3=(pow(L,2)+pow(H,2))-(pow(A2,2)+pow(A3,2)/2*A2*A3)
        if (cos3 ** 2 > 1):
            return None
        sin3 = math.sqrt(1 - cos3 ** 2)
        if (y < 0):
            sin3 = sin3 * -1
        j3 = self.atan2(sin3, cos3)

        #     print('j3:{}'.format(j3))
        return j3

    def _calculate_j2(self, L, H, j3):
        A2 = self.A2
        A3 = self.A3
        #     print('j3:{}'.format(j3))
        K1 = A2 + A3 * self.cos(j3)
        K2 = A3 * self.sin(j3)
        #     print('sin(j3):{}'.format(sin(j3)))
        #     print('K2:{}'.format(K2))
        w = self.atan2(K2, K1)
        #     print('w:{}'.format(w))
        #     print('atan2(L,H):{}'.format(atan2(L,H)))
        if (w > 0 and self.atan2(L, H) < 0):
            j2 = -(w + self.atan2(L, H))
        if (w < 0 and self.atan2(L, H) < 0):
            j2 = self.atan2(L, H) - w
        #     print('j2:{}'.format(j2))
        return j2

    def _calculate_j4(self, j2, j3, alpha):
        j4 = alpha - j2 - j3
        return j4

    def _xyz_alpha_to_j123(self, x, y, z):
        A1 = self.A1
        A2 = self.A2
        A3 = self.A3
        A4 = self.A4  # xiugai
        valid = False
        j1, j2, j3, j4 = None, None, None, None
        j1, length, height = self._calculate_j1(x, y, z)
        if self._valid_j(1, j1) and not self._out_of_range(length, height):
            L = length
            H = height - A1 + A4  # xiugai
            j3 = self._calculate_j3(L, H, y)
            if self._valid_j(3, j3):
                j2 = self._calculate_j2(L, H, j3)
                if self._valid_j(2, j2):
                    valid = True
        # print('j2:{} j3:{} j2+j3:{}'.format(j2,j3,j2+j3))
        if ((j2 + j3) < 180):
            j4 = 180 - (j3 + j2)
        elif (j2 + j3) > 180:
            j4 = j2 + j3 - 90
        else:
            j4 = 90 - (180 - (j2 + j3))
        # print('j41:{}'.format(j4))
        return valid, j1, j2, j3, j4

    def _xyz_to_j123(self, x, y, z):

        MIN_ALPHA = 0  # j2+j3+j4 min value, 最后一个joint不向后仰
        valid = False
        j1, j2, j3 = None, None, None
        valid, j1, j2, j3, j4 = self._xyz_alpha_to_j123(x, y, z)
        if not valid:
            alpha -= 1
        return valid, j1, j2, j3, j4

    def backward_kinematics(self, x, y, z):
        x = float(x)
        y = float(y)
        z = float(z)
        # print('x:{} y:{} z:{} '.format(x,y,z))
        valid, j1, j2, j3, j4 = self._xyz_to_j123(x, y, z)
        deg1, deg2, deg3, deg4 = None, None, None, None
        if valid:
            deg1 = round(self._j_degree_convert(1, j1), 2)
            deg2 = round(self._j_degree_convert(2, j2), 2)
            deg3 = round(self._j_degree_convert(3, j3), 2)
            deg4 = round(self._j_degree_convert(4, j4), 2)
            # print('valid:{},deg1:{},deg2:{},deg3:{},deg4:{}'.format(valid,deg1,deg2,deg3,deg4))

        return valid, deg1, deg2, deg3, deg4

    def forward_kinematics(self, deg1, deg2, deg3, deg4):
        valid = False
        A2 = self.A2
        A3 = self.A3
        A1 = self.A1
        A4 = self.A4
        P = self.P
        if not self._valid_degree(1, deg1) or not self._valid_degree(2, deg2) or not self._valid_degree(3, deg3):
            return valid, None, None, None
        j1 = self._j_degree_convert(1, deg1)
        j2 = self._j_degree_convert(2, deg2)
        j3 = self._j_degree_convert(3, deg3)
        j4 = self._j_degree_convert(4, deg4)
        length = A2 * self.sin(j2) + A3 * self.sin(j2 + j3)
        # print("test",j2,j3,j2+j3,j4)
        height = A1 + A2 * self.cos(j2) + A3 * self.cos(j2 + j3) - A4
        alpha = j2 + j3
        # print('length:{}'.format(length))
        # print('sin:{}'.format(sin(j1)))
        z = round(height, 6)
        x = round(length * self.cos(j1), 6)
        y = round(length * self.sin(j1) - P, 6)
        # print('y:{}'.format(y))

        # print('123valid:{},x:{},y:{:f},z:{},lenghth:{},height:{},alpha:{}'.format(valid,x,y,z,round(length,2),round(height,2),alpha))

        return valid, x, y, z

    def to_servo_value(self, deg1, deg2, deg3, deg4):
        ep = self.ep
        e1 = self.e1
        e2 = self.e2
        e3 = self.e3
        e4 = self.e4
        e1d = self.e1d
        e2d = self.e2d
        e3d = self.e3d
        e4d = self.e4d
        e = self.e
        if e1d == 1:
            v1 = (e * deg1 + ep + e1)
        else:
            v1 = 1000 - (e * deg1 + ep + e1)
        if e2d == 1:
            v2 = (e * deg2 + ep + e2)
        else:
            v2 = 1000 - (e * deg2 + ep + e2)
        if e3d == 1:
            v3 = (e * deg3 + ep + e3)
        else:
            v3 = 1000 - (e * deg3 + ep + e3)
        if e4d == 1:
            v4 = (e * deg4 - ep + e4)
        else:
            v4 = 1000 - (e * deg4 + ep + e4)
        if v1 >= 1200:
            v1 = 1200
        if v2 >= 1200:
            v2 = 1200
        if v3 >= 1200:
            v3 = 1200
        if v4 >= 1200:
            v4 = 1200
        if v1 <= 0:
            v1 = 0
        if v2 <= 0:
            v2 = 0
        if v3 <= 0:
            v3 = 0
        if v4 <= 0:
            v4 = 0
        # ('v1:{},v2:{},v3:{},v4:{}'.format(v1,v2,v3,v4))
        return v1, v2, v3, v4

    # 后四个参数为舵机修正角度，尤其4号舵机，目前是固定垂直向下
    def xyz_Kinematic(self, t, x, y, z, se1, se2, se3, se4):
        y = y - 1.6

        try:
            valid, deg1, deg2, deg3, deg4 = self.backward_kinematics(x, y, z)
            if valid:
                valid, x1, y1, z1 = self.forward_kinematics(deg1, deg2, deg3, deg4)
                v1, v2, v3, v4 = self.to_servo_value(deg1 + se1, deg2 + se2, deg3 + se3, deg4 + se4)
                if abs(x1 - x) > 0.5 or abs(y1 - y) > 0.5 or abs(z1 - z) > 0.5:
                    pass
                else:
                    self.board.bus_servo_set_position(t, [[1, int(v1)], [2, int(v2)], [3, int(v3)], [4, int(v4)]])


        except:
            print("角度解算失败")
        time.sleep(t + 0.1)

    def angle_Kinematic(self, t, deg1, deg2, deg3, deg4):
        v1, v2, v3, v4 = self.to_servo_value(deg1, deg2, deg3, deg4)
        valid, x, y, z = self.forward_kinematics(deg1, deg2, deg3, deg4)
        # print('valid:{},x:{},y:{:f},z:{}'.format(valid,round(x,2),round(y,2),round(z,2)))
        self.board.bus_servo_set_position(t, [[1, int(v1)], [2, int(v2)], [3, int(v3)], [4, int(v4)]])
        time.sleep(t + 0.1)

    def servo_enable_torque(self, enable):
        if enable:
            for _id in (1, 5):
                self.board.bus_servo_enable_torque(_id, 1)
        else:
            for _id in (1, 5):
                self.board.bus_servo_enable_torque(_id, 0)

    def set_arm_servos_position(self, t, deg1, deg2, deg3, deg4):
        self.board.bus_servo_set_position(t, [[1, deg1], [2, deg2], [3, deg3], [4, deg4]])


# 定义一个夹爪
class Gripper:
    def __init__(self, board) -> None:
        self.board = board

    def action(self, duration, servo_degree, servo_id=1):
        """
        机械展执行动作的函数，指定持续时间、舵机角度和可选的舵机ID。

        参数:
            duration (int): 动作持续时间。
            servo_degree (int): 舵机角度。
            servo_id (int, optional): 舵机 ID。默认为 1。
            
        返回:
            None
        """
        deg = Misc.setRange(servo_degree, 0, 180)  # 将输入限制在0-180度
        pulse = int(Misc.map(deg, 0, 180, 500, 2500))  # 将角度转换为脉冲
        self.board.pwm_servo_set_position(duration, [[servo_id, pulse]])

    def read_position(self, servo_id=1):
        """
        读取机械爪舵机角度和可选的舵机ID。

        参数:  
            servo_id (int, optional): 舵机 ID。默认为 1。
            
        返回:
            servo_degree (int): 舵机角度。
        """
        pulse = self.board.pwm_servo_read_position(servo_id)
        servo_degree = int(Misc.map(pulse, 500, 2500, 0, 180))
        return servo_degree


class Unibot:

    def __init__(self):
        self.board = Board()
        self.board.enable_reception()
        self.chassis = MecanumChassis(self.board)
        self.gripper = Gripper(self.board)
        self.params = Device_Config('/root/unibot/robot_param_init.txt')

        servo_init_error_default = self.params.readconfsectionkeyvalue('SERVO_ERR_INIT')
        servo_init_direction_default = self.params.readconfsectionkeyvalue('SERVO_DIR_INIT')
        self.left_holder_servo_position = self.params.readconfsectionkeyvalue('LEFT_PUT_ROUND')
        self.right_holder_servo_position = self.params.readconfsectionkeyvalue('LEFT_GET_ROUND')
        self.robotic_arm = RoboticArm(self.board, servo_init_error_default, servo_init_direction_default)
        self.camera = Camera()

    def get_battery(self):
        return self.board.get_battery()

    def follow_line(self, point_index):
        img = self.camera.get_frame()
        ls, lsc, img = self.camera.detect_vertical_black_line(img)
        self.camera.show_frame(img)
        try:
            return ls[point_index - 1][0]
        except:
            return -1

    # 旋转机器人寻找线
    def rotate_find_line(self, rotate_speed, endpointnum, point):
        self.robotic_arm.angle_Kinematic(0.3, 88, 40, -30, 90)
        self.chassis.move(0, 0, rotate_speed)
        img = self.camera.get_frame()

        while True:
            img = self.camera.get_frame()
            ls, lsc, img = self.camera.detect_vertical_black_line(img)
            print(lsc)
            self.camera.show_frame(img)
            ans = 0
            for i in range(5):
                if ls[i][0] is not None:
                    if endpointnum < lsc[i] < 100:
                        ans += 1
            print(ans)
            if ans >= point:
                break

        self.chassis.stop()

    def translational_move_find_line(self, endpointnum=45, point=3):
        # endpointnum数值表示黑点构成的线宽，与摄像头的高低位置相关
        # point数值表示需要对齐的点点数量
        img = self.camera.get_frame()
        ls, lsc, img = self.camera.detect_vertical_black_line(img)
        self.camera.show_frame(img)
        ans = 0
        for i in range(5):
            if ls[i][0] is not None:
                if endpointnum < lsc[i] < 100:
                    ans += 1
            if ans >= point:
                find_line = True
            else:
                find_line = False
        return find_line

    # 前后移动，寻找水平的黑线
    def move_find_line(self, endpointnum=200):
        img = self.camera.get_frame()
        ls, lsc, img = self.camera.detect_vertical_black_line(img)
        self.camera.show_frame(img)
        if lsc[3] > endpointnum:
            return True
        else:
            return False

    def arm_to_holder(self, direction):
        if direction == 'left':
            self.board.bus_servo_set_position(1, [[1, self.left_holder_servo_position['angle1']],
                                                  [2, self.left_holder_servo_position['angle2']],
                                                  [3, self.left_holder_servo_position['angle3']],
                                                  [4, self.left_holder_servo_position['angle4']]])

        elif direction == 'right':
            self.board.bus_servo_set_position(1, [[1, self.right_holder_servo_position['angle1']],
                                                  [2, self.right_holder_servo_position['angle2']],
                                                  [3, self.right_holder_servo_position['angle3']],
                                                  [4, self.right_holder_servo_position['angle4']]])

    def align_object(self, p_x, p_y,target_area: int = 5000):
        color_flag = 3
        cx = -1
        cy = -1
        for index in range(0, 3):
            frame = self.camera.get_frame()
        while color_flag == 3:
            color_flag = self.camera.detect_object_color(10, target_area)
            print(color_flag)
        ans = 0
        print("颜色：", color_flag)
        while True:
            cx, cy = self.camera.detect_object_center(color_flag, target_area)
            if cx != -1 and cy != -1:
                print(cx,cy)
                error_x = cx - 160
                error_y = cy - 120
                px = error_x * p_x
                py = error_y * p_y
                self.board.set_motor_speed([[1, px - py], [2, px + py], [3, -px - py], [4, -px + py]])
                if abs(cx - 160) <= 4 and abs(cy - 120) <= 4:
                    ans += 1
                else:
                    ans = 0
                if ans >= 10:
                    self.chassis.stop()
                    break

        print("矫正结束")


if __name__ == '__main__':
    my = Unibot()

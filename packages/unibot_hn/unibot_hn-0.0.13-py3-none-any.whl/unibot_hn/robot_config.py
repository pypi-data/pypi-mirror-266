
'''
读取配置文件
'''
import configparser

class Device_Config:
    def __init__(self, filename):
        self.filename = filename
        # 创建 ConfigParser 对象
        self.config = configparser.ConfigParser()
        ## 从配置文件中读取参数
        self.config.read(self.filename)

    #读取section下的option值 
    #需要字符串
    #返回整数
    def readconftoint(self, section, option):
        return int(self.config[section][option])

    #读取整个section
    def readconfallsection(self):
        return self.config.section()

    #读取指定section下的option名字
    def readconfsection(self,section):
        return self.config.options(section)

    #读取指定section下的所有值,返回的是字典
    def readconfsectionkeyvalue(self,section):
        setname = self.readconfsection(section)
        rs = {}
        for name in setname:
            value = self.readconftoint(section,name)
            rs[name] = value
        return rs

    #读取指定section下的所有值,返回的是列表
    def readconfsectionvalue(self,section):
        setname = self.readconfsection(section)
        rs = []
        for name in setname:
            value = self.readconftoint(section,name)
            rs.append(value)
        return rs

    #修改section下的option值 
    #会转化为字符串
    def setconf(self,section,option,value):
        try:
            self.config.set(section,option,str(int(value)))
            self.config.write(open(self.filename, 'w'))
            print("设置成功")
        except:
            print("设置失败")
 
     
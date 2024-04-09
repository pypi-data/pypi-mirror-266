import time
from airtest.core.api import *
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
import ddddocr
from dzwl.fun_util import fun_util
class WebBasePage:
    @classmethod
    def login_web(cls,imagePath):
        WebBasePage.openUrl(cls.url)
        code = cls.verificationCode(cls.imgelement_xpath, 'xpath',imagePath)
        cls.sendKeys(cls.code_xpath, 'xpath', code)
        cls.sendKeys(cls.username_xpath, 'xpath', cls.username)
        cls.sendKeys(cls.password_xpath, 'xpath', cls.password)
        cls.click(cls.login_xpath, 'text')
        while True:
            try:
                cls.waitUntil(EC.url_to_be(cls.url_to_be))
                cls.driver.maximize_window()
                break
            except:
                code = cls.verificationCode(cls.imgelement_xpath, 'xpath', imagePath)
                cls.sendKeys(cls.code_xpath, 'xpath', code)
                cls.click(cls.login_xpath, 'text')


    @classmethod
    def openUrl(cls,url):
        fun_util.logView("打开地址：" +url)
        cls.driver.get(url)


    #刷新页面
    @classmethod
    def refreshPage(cls):
        fun_util.logView("刷新页面")
        cls.driver.refresh()

    # 查找并返回元素
    @classmethod
    def findElement(cls,loc,type):
        try:
            if type == 'xpath':
                pass
            if type == 'text':
                loc = '//*[normalize-space(text())="'+loc+'"]'
            if type == 'partialText':
                loc = '//*[contains(text(),"'+loc+'")]'
            element = cls.waitUntil(EC.presence_of_element_located((By.XPATH, loc)))
            #element_to_be_clickable
            #presence_of_element_located
            #visibility_of_element_located
            #visibility_of
            return element
        except:
            fun_util.logView("发现元素失败:%s" % loc + ',类型：'+type)
            pytest.assume(False)
            return False

    @classmethod
    def waitUntil(cls,content,timeout = 5):
        wait = WebDriverWait(cls.driver, timeout)
        return wait.until(content)

    @classmethod
    def sendKeys(cls,loc,type,value):
        element = cls.findElement(loc, type)
        cls.driver.execute_script("arguments[0].focus();", element)
        element.clear()
        cls.waitUntil(lambda driver: element.get_attribute('value') == '')
        element.send_keys(value)
        cls.waitUntil(lambda driver: element.get_attribute('value') == str(value))
        cls.blur(loc,type)
        fun_util.logView("输入:%s" % value)

    @classmethod
    def jsExcute(cls,value):
        cls.driver.execute_script(value)
        fun_util.logView("点击:%s" % value)
    @classmethod
    def click(cls,loc,type):
        element = cls.findElement(loc, type)
        cls.driver.execute_script("arguments[0].click();", element)
        fun_util.logView("点击:%s" % loc)
    #取消focus
    @classmethod
    def blur(cls,loc,type):
        element = cls.findElement(loc, type)
        cls.driver.execute_script("arguments[0].blur();", element)



    #判断元素是否存在
    @classmethod
    def assertElement(cls,loc,type):
        try:
            if cls.waitUntil(lambda driver: cls.findElement(str(loc),type)):
                fun_util.logView("断言:%s-成功" % loc + ',类型：'+type)
                pytest.assume(True)
        except:
            fun_util.logView("断言-失败:%s" % loc + ',类型：'+type)
            pytest.assume(False)

    #数量断言
    @classmethod
    def assertEquals(cls,num1,num2,type='and'):
        if type == 'and':
            try:
                if cls.waitUntil(lambda driver: str(num1) == str(num2)):
                    fun_util.logView("比较断言相等-成功：%s" % num1)
                    pytest.assume(True)
            except:
                fun_util.logView(f"比较断言不相等-失败：{num1}，{num2}")
                pytest.assume(False)
        if type == 'not':
            try:
                if cls.waitUntil(lambda driver: str(num1) == str(num2)):
                    fun_util.logView("比较断言相等-失败：%s" % num1)
                    pytest.assume(False)
            except:
                fun_util.logView(f"比较断言不相等-成功：{num1}，{num2}")
                pytest.assume(True)



    @classmethod
    def verificationCode(cls,imgPath,type,savePath):
        while True:
            cls.driver.screenshot(savePath+'printscreen.png')
            imgelement = cls.findElement(imgPath,type)
            location = imgelement.location
            # 获取验证码的长宽
            size = imgelement.size
            # 写成我们需要截取的位置坐标
            #电脑屏幕缩放比例系数
            coefficient = 1
            rangle = (int(location['x'])*coefficient,
                      int(location['y'])*coefficient,
                      int(location['x'] + size['width'])*coefficient,
                      int(location['y'] + size['height'])*coefficient)
            i = Image.open(savePath+'printscreen.png')
            fimg = i.crop(rangle)
            fimg = fimg.convert('RGB')
            # 保存我们截下来的验证码图片，并读取验证码内容
            fimg.save(savePath+'code.png', quality=95, subsampling=0, compress_level=0)
            ocr = ddddocr.DdddOcr()
            with open(savePath+'code.png', 'rb') as f:
                img_bytes = f.read()
                res = ocr.classification(img_bytes)
            print('原始验证码' + res)
            if len(res) == 4 and res.isdigit():
                print('识别正确'+res)
                break
            else:
                cls.click(imgPath,type)
                time.sleep(1)
        print('返回正确验证码' + res)
        return res
class MobileBasePage:
    @classmethod
    def locator(self, loc, type):
        if type == 'text':
            self.poco(text=loc).wait_for_appearance(timeout=10)
            fun_util.logView("元素定位-成功(text)：" + str(loc))
            return True
        if type == 'name':
            self.poco(name=loc).wait_for_appearance(timeout=10)
            fun_util.logView("元素定位-成功(name)：" + str(loc))
            return True
        if type == 'image':
            if exists(loc):
                fun_util.logView("元素定位-成功(image)：" + str(loc))
                return True
        else:
            fun_util.logView("不存在元素类型：类型为：" +type+"，属性为："+str(loc))
            pytest.assume(False)
            return False
    @classmethod
    def click(self, loc, type):
        if self.locator(loc, type):
            if type == 'text':
                self.poco(text=loc).click()
                fun_util.logView("点击元素(text)：" + str(loc))
                return True

            if type == 'name':
                self.poco(name=loc).click()
                fun_util.logView("点击元素(name)：" + str(loc))
                return True

            if type == 'image':
                touch(loc)
                fun_util.logView("点击元素(image)：" + str(loc))
                return True

        else:
            fun_util.logView("点击元素-失败：" + str(loc) + type)
            pytest.assume(False)
            return False
    @classmethod
    def setValue(self,loc,value,type):
        if self.locator(loc, type):
            if type == 'name':
                input_box = self.poco(name=loc)
                input_box.setattr("text", value)
                fun_util.logView("元素赋值-成功(name)：" + str(loc))
            if type == 'text':
                input_box = self.poco(text=loc)
                input_box.setattr("text", value)
                fun_util.logView("元素赋值-成功(text)：" + str(loc))
        else:
            fun_util.logView("元素赋值-失败：" + str(loc) + type)
            pytest.assume(False)
    @classmethod
    def inputValueAirtest(self,loc,value,type):
        if self.click(loc, type):
            if type == 'name':
                text(value)
                fun_util.logView("元素赋值-成功(name)：" + str(loc))
            if type == 'text':
                text(value)
                fun_util.logView("元素赋值-成功(text)：" + str(loc))
            if type == 'image':
                text(value)
                fun_util.logView("元素赋值-成功(image)：" + str(loc))
        else:
            fun_util.logView("元素赋值-失败：" + str(loc) + type)
            pytest.assume(False)
    @classmethod
    def inputValuePoco(self,loc,value,type):
        if self.click(loc, type):
            if type == 'name':
                self.poco(name=loc).set_text(value)
                fun_util.logView("元素赋值-成功(name)：" + str(loc))
            if type == 'text':
                self.poco(text=loc).set_text(value)
                fun_util.logView("元素赋值-成功(text)：" + str(loc))
        else:
            fun_util.logView("元素赋值-失败：" + str(loc) + type)
            pytest.assume(False)

import copy
import requests
from dzwl.fun_util import fun_util,DateEncoder
import os
import yaml
from string import Template
import json
from Config.config import CommonConfig

class requsts_util:
    session = requests.session()
    @classmethod

    def send_request(self,method,url,data,headers,**kwargs):
        method = str(method).lower()
        try:
            if method == 'get':
                rep = requsts_util.session.request(method=method, url=url, params=data,headers = headers,**kwargs)
            elif method == 'delete':
                rep = requsts_util.session.delete(url=url, params=data,headers = headers,**kwargs)
            else:
                if 'form' in str(headers):
                    rep = requsts_util.session.request(method=method, url=url, data=data,headers= headers, **kwargs)
                else:
                    rep = requsts_util.session.request(method=method, url=url, json=data,headers= headers, **kwargs)
        except Exception as e:
            print('无法连接:'+str(e))
        else:
            if rep.status_code==200:
                resp = json.loads(rep.text)
                return resp
            else:
                print('请求状态异常：'+str(rep.status_code))

    @classmethod

    def excute_interface(self,caseinfo,domain):
        #循环读取yml中配置的接口参数
            #caseinfo是个dic，通过caseinfo.keys()获取key，使用list()转为list类型，取下标0即可，yml测试数据的动态管理
            #caseinfo_key = list(caseinfo.keys())[0]
            #从config文件中读取domain与接口地址拼接,login接口可能用别的域名，判断一下
            url = domain + caseinfo['path']
            #读取请求类型
            method = caseinfo['method']
            #读取请求数据
            data = caseinfo['data']
            #读取请求头
            headers = caseinfo['headers']
            #读取描述
            description = caseinfo['description']
            #发送请求
            resp = self.send_request(method=method,url=url,data=data,headers=headers)
            print('\n')
            fun_util.logView('描述：'+description)
            fun_util.logView('请求url：'+url)
            fun_util.logView('请求header：'+json.dumps(headers,indent = 4,ensure_ascii=False))
            fun_util.logView('请求body：'+json.dumps(data,indent = 4,ensure_ascii=False,cls=DateEncoder))
            fun_util.logView('返回：'+json.dumps(resp,indent = 4,ensure_ascii=False))
            if 'assert_type' in caseinfo and 'is_assert' in caseinfo:
                # 读取断言类型
                assert_type = caseinfo['assert_type']
                # 读取断言信息
                is_assert = caseinfo['is_assert']
                fun_util.check_assert(is_assert,resp,assert_type)

            print('----------------------------------------------------------------------------------------------------------')
            return resp

class yaml_util:
    #读取extract.yml文件
    rootPath = CommonConfig.rootPath
    @classmethod
    def read_extract_yaml(self,key):
        with open(self.rootPath+"/Common/common_var.yml",mode='r',encoding='utf-8') as f:
            value = yaml.load(stream=f,Loader=yaml.FullLoader)
            return value[key];

    @classmethod
    def write_extract_yaml(self,data):
        file_path = os.path.join(self.rootPath, "Common", "common_var.yml")

        # 读取文件中的所有数据
        with open(file_path, mode='r', encoding='utf-8') as f:
            all_data = yaml.safe_load(f) or {}
        # 将传入的数据转换为字典格式，并更新到all_data中
        for d in data:
            for key_data in d.keys():
                if key_data in all_data:
                    all_data[key_data]=d[key_data]
                else:
                    all_data.update(d)
        # 将所有数据写入文件中
        with open(file_path, mode='w', encoding='utf-8') as f:
            yaml.dump(data=all_data, stream=f, allow_unicode=True)

    @classmethod
    #清除extract.ym1文件
    def clean_extract_yaml(self) :
        with open(self.rootPath+"/Common/common_var.yml",mode='w',encoding='utf-8') as f:
            f.truncate()
    @classmethod
    #读取测试用例的yml文件
    def read_testcase_yaml(self,yaml_name):
        with open(self.rootPath+yaml_name,mode='r',encoding='utf-8') as f:
            value = yaml.load(stream=f,Loader=yaml.FullLoader)
            return value;

    @classmethod
    #写入测试用例的yml文件
    def write_testcase_yaml(self,caseinfo,content) :
        caseinfo_tmp = copy.deepcopy(caseinfo)
        def replace_value(d, key, new_value):
            for k, v in d.items():
                #if k == key and ('$' in str(d[k]) or '$' in k):
                if k == key:
                    d[k] = new_value
                elif isinstance(v, dict):
                    replace_value(v, key, new_value)
        for cont in content:
            for c in cont:
                replace_value(caseinfo_tmp, c, cont[c])
        return caseinfo_tmp

    @classmethod
    #写入测试用例的yml文件
    def remove_testcase_yaml(self,caseinfo,content) :
        caseinfo_tmp = copy.deepcopy(caseinfo)

        def remove_name_items(dictionary,cont):
            new_dictionary = {}
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    new_dictionary[key] = remove_name_items(value,cont)
                elif key != cont:
                    new_dictionary[key] = value
            return new_dictionary

        for cont in content:
            caseinfo_tmp = remove_name_items(caseinfo_tmp, cont)
        return caseinfo_tmp




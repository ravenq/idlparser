#!/usr/bin/env python
#_*_ coding: utf-8_*_
"""
Copyright 2015 flw_dream@126.com

Licensed under the Apache License, Version 2.0 (the "License")
 
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import os, sys
import re
sys.path.append("..") 
from idlparser.idlparser import IdlParser
from django.template import Context, Template

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings") # to make the django happy

g_map_type = {
        'BSTR':r'LPCTSTR',
        'BSTR*':r'wstring&',
        'VALIANT_BOOL':r'BOOL',
        'VALIANT_BOOL*':r'BOOL&'
    }

g_re_bstr = re.compile(r'\Abstr(?P<name>\w+)\Z')
g_re_pbstr = re.compile(r'\Apbstr(?P<name>\w+)\Z')

g_replace_bstr = r'lpsz\g<name>'
g_replace_pbstr = r'str\g<name>'

class CppMaker(object):
    '''
    1. 根据 idl 文件生成接口代理
    2. 使用 Django 解析引擎，渲染模板，Django: https://www.djangoproject.com/
        代理文件模板为 template.h/template.cpp
    3. 参数类型映射：
        BSTR            LPCTSTR
        BSTR*           wstring&
        VALIANT_BOOL    BOOL
        VALIANT_BOOL*   BOOL&
    4. 文件生成规则：
        一个接口生成一个.h和.cpp文件，文件名称为增加后缀 Proxy
        例如：IZoeStdDict --> IZoeStdDictProxy.h/IZoeStdDictProxy.cpp
        代理类名称为加前缀 C 加后缀 Proxy
        例如：ZoeStdDict --> CIZoeStdDictProxy
    '''
    def __init__(self, tpl_hpp = 'template.h', tpl_cpp = 'template.cpp', out_dir = 'out', factory = 'EMRFactory'):
        self.tpl_hpp = tpl_hpp
        self.tpl_cpp = tpl_cpp
        self.out_dir = out_dir
        self.factory = factory
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
    def make_hpp(self, i_obj):
        self.__pre_make(i_obj)
        
        tpl =  self.__readfile(self.tpl_hpp)
        t = Template(tpl)
        c = Context({'object':i_obj})
        ret = t.render(c)
        
        ret = self.__after_make(ret)
        self.__out(str, i_obj.name + '.h',)
        
    def make_cpp(self, i_obj):
        self.__pre_make(i_obj)
        
        tpl =  self.__readfile(self.tpl_cpp)
        t = Template(tpl)
        c = Context({'object':i_obj, 'factory':self.factory})
        ret = t.render(c)
        
        ret = self.__after_make(ret)
        self.__out(str, i_obj.name + '.cpp')

    def __pre_make(self, i_obj):
        '''
        在生成代理前完成类型替换
        '''
        for m_obj in i_obj.methods:
            for p_obj in m_obj.params:
                self.__map_param_type(p_obj)
                self.__map_param_name(p_obj)

    def __map_param_type(self, p_obj):
        strType = p_obj.type.strip()
        if strType in g_map_type.keys():
            p_obj.type = g_map_type[strType]

    def __map_param_name(self, p_obj):
        strName = p_obj.name.strip()
        p_obj.name = g_re_bstr.sub(g_replace_bstr, strName)
        if strName == p_obj.name:
             p_obj.name = g_re_pbstr.sub(g_replace_pbstr, strName)
    
    def __after_make(self, ret):
        return ret.replace('&amp;', '&')
    
    def __readfile(self, strPath):
        file = open(strPath, 'r')
        ret = file.read()
        file.close()
        return ret
        
    def __out(self, str, name):
        str_path = os.path.join(self.out_dir, name)
        file = open(str_path, 'w')
        file.write(str)
        file.close()
        
if __name__ == '__main__':
    def inputparam(index, prompt, default='', options=None, nullable=True):
        if len(sys.argv) > index:
            ret = sys.argv[index]
        else:
            ret = raw_input(prompt)
            
        if ret == '':
            ret = default
        
        if ret == '' and not nullable:
            print 'not allow null\m'
            ret = inputparam(index, prompt, default, options, nullable)
            
        if options is not None and ret not in options:
            print 'select one of the options please!\n'
            ret = inputparam(index, prompt, default, options, nullable)
            
        return ret
    
    f_option = ('EMRFactory', 'HISFactory')
    idlfile = inputparam(1, 'input the idle file path: ', 'D:\GitHub\idlparser\zserver.idl', None, False)
    factory = inputparam(2, 'input the factory(EMRFactory/HISFactory): ', 'EMRFactory', f_option, False)
    out_dir = inputparam(3, 'input the out directory(default: out): ', 'out', f_option, False)
    
    parser = IdlParser()
    idl_obj = parser.parse(idlfile)
    
    cppmaker = CppMaker(factory = factory)
    print len(idl_obj.interfaces)
    for i_obj in idl_obj.interfaces:
        cppmaker.make_hpp(i_obj)
        cppmaker.make_cpp(i_obj)
        



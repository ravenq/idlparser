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
    u'BSTR':u'LPCTSTR',
    u'BSTR*':u'wstring&',
    u'VARIANT_BOOL':u'BOOL',
    u'VARIANT_BOOL*':u'BOOL&',
    u'LONG':u'LONG',
    u'LONG*':u'LONG&',
    u'int':u'int',
    }
    
g_map_type_com = {
    u'BSTR':u'CComBSTR',
    u'BSTR*':u'CComBSTR',
    u'VARIANT_BOOL':u'VARIANT_BOOL',
    u'VARIANT_BOOL*':u'VARIANT_BOOL',
    u'LONG':u'LONG',
    u'LONG*':u'LONG',
    u'int':u'int',
}

g_map_defaultval_bool = {
    u'0':u'FALSE',
    u'-1':u'TRUE',
}

g_re_bstr = re.compile(u'\Abstr(?P<name>\w+)\Z')
g_re_pbstr = re.compile(u'\Apbstr(?P<name>\w+)\Z')
g_re_isout = re.compile(u'\Aout\s*,*\s*\w*\Z')
g_re_isaddress = re.compile(u'\A\w+\*\Z') #一般和 isout 一致

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
        self.__out(ret, i_obj.name + '.h',)
        
    def make_cpp(self, i_obj):
        self.__pre_make(i_obj)
        
        tpl =  self.__readfile(self.tpl_cpp)
        t = Template(tpl)
        c = Context({'object':i_obj, 'factory':self.factory})
        ret = t.render(c)
        
        ret = self.__after_make(ret)
        self.__out(ret, i_obj.name + '.cpp')

    def __pre_make(self, i_obj):
        '''
        在生成代理前完成预生成处理
        '''
        for m_obj in i_obj.methods:
            # 参数类型及名称处理
            for p_obj in m_obj.params:
                self.__map_param_type(p_obj)
                self.__map_param_name(p_obj)
                p_obj.com_name = u'com_' + p_obj.proxy_name
                p_obj.is_out = g_re_isout.match(p_obj.io_type) is not None
                p_obj.is_address = g_re_isaddress.match(p_obj.type) is not None

            # 参数列表
            self.__make_params_list(m_obj)
            
            # 参数调用列表
            self.__make_params_list_invoke(m_obj)

            # 函数体
            self.__make_impl(i_obj.name, m_obj)

    def __make_params_list(self, m_obj):
        def __make_params_list_impl(m_obj, format):
            temp = []
            for p_obj in m_obj.params:
                defaultval = p_obj.defaultval
                if p_obj.defaultval and p_obj.proxy_type == u'BOOL':
                    defaultval = g_map_defaultval_bool[p_obj.defaultval]

                if p_obj.defaultval:
                    temp.append(format % (p_obj.proxy_type, p_obj.proxy_name, defaultval))
                else:
                    temp.append(u'%s %s' % (p_obj.proxy_type, p_obj.proxy_name))

            return u', '.join(temp)

        m_obj.params_list = __make_params_list_impl(m_obj, u'%s %s = %s')
        m_obj.params_list_impl = __make_params_list_impl(m_obj, u'%s %s /* = %s */')

    def __make_params_list_invoke(self, m_obj):
        temp = []
        for p_obj in m_obj.params:
            if p_obj.is_address:
                temp.append(u'&%s' % p_obj.com_name)
            else:
                temp.append(p_obj.com_name)
            
        m_obj.params_list_invoke = u', '.join(temp)

    def __make_impl(self, i_name, m_obj):
        temp = u''
        for p_obj in m_obj.params:
            if p_obj.is_address:
                temp += u'%s %s;\n\t\t' % (p_obj.com_type, p_obj.com_name)
            else:
                temp += u'%s %s(%s);\n\t\t' % (p_obj.com_type, p_obj.com_name, p_obj.proxy_name)
        
        temp += u'''\n\t\tCComPtr<%s> sp;\n\t\tC%s::Instance().CreateObject(IID_%s, (void**)&sp);\n\t\tCHECK_THROW(sp->%s(%s));\n\n''' % (i_name, self.factory, i_name, m_obj.name, m_obj.params_list_invoke)
        for p_obj in m_obj.params:
            if p_obj.is_out:
                if p_obj.proxy_type == u'wstring&':
                    temp += u'\t\tif(%s != NULL)%s = %s;\n' % (p_obj.com_name, p_obj.proxy_name, p_obj.com_name)
                elif p_obj.proxy_type == u'BOOL&':
                    temp += u'\t\t%s = %s ? TRUE : FALSE;\n' % (p_obj.proxy_name, p_obj.com_name)
                else:
                    temp += u'\t\t%s = %s;\n' % (p_obj.proxy_name, p_obj.com_name)
        m_obj.impl = temp;

    def __map_param_type(self, p_obj):
        p_obj.type = p_obj.type.strip()
        p_obj.proxy_type = g_map_type[p_obj.type]
        p_obj.com_type = g_map_type_com[p_obj.type]

    def __map_param_name(self, p_obj):
        p_obj.name = p_obj.name.strip()
        if g_re_bstr.match(p_obj.name):
            p_obj.proxy_name = g_re_bstr.sub(g_replace_bstr, p_obj.name)
        elif g_re_pbstr.match(p_obj.name):
            p_obj.proxy_name = g_re_pbstr.sub(g_replace_pbstr, p_obj.name)
        else:
            p_obj.proxy_name = p_obj.name
    
    def __after_make(self, ret):
        ret = ret.replace(u'&amp;', u'&')
        ret = ret.replace(u'&lt;', u'<')
        ret = ret.replace(u'&gt;', u'>')
        
        return ret
    
    def __readfile(self, strPath):
        file = open(strPath, 'r')
        ret = file.read()
        file.close()
        return ret
        
    def __out(self, str_result, name):
        str_path = os.path.join(self.out_dir, name)
        file = open(str_path, 'w')
        file.write(str_result.encode('gb2312'))
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
            print 'not allow null'
            ret = inputparam(index, prompt, default, options, nullable)
            
        if options is not None and ret not in options:
            print 'select one of the options please!'
            ret = inputparam(index, prompt, default, options, nullable)
            
        return ret
    
    f_option = ('EMRFactory', 'HISFactory')
    idlfile = inputparam(1, 'input the idle file path: ', 'zserver.idl', None, False)
    factory = inputparam(2, 'input the factory(EMRFactory/HISFactory) defualt(EMRFactory): ', 'EMRFactory', f_option, False)
    out_dir = inputparam(3, 'input the out directory(default: out): ', 'out', None, False)
    
    parser = IdlParser()
    idl_obj = parser.parse(idlfile)
    
    cppmaker = CppMaker(factory = factory)
    for i_obj in idl_obj.interfaces:
        cppmaker.make_hpp(i_obj)
        cppmaker.make_cpp(i_obj)
        



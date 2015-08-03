# -*- coding: utf-8 -*-
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

p_obj_str = u'\[\w+,*\s*\w*\]\s*\w+\**\s*\w+'
m_obj_str = u'\[id\(\d+\)\s*,\s*helpstring\("[a-zA-Z0-9_\u4e00-\u9fa5\s]*"\)\]\s*HRESULT\s*\w+\((?:' + p_obj_str + u'\s*\,*\s*)+\);'
a_obj_str = u'\[\s*object,\s*uuid\([a-zA-Z0-9\-]+\),\s*dual,\s*nonextensible,\s*helpstring\("[a-zA-Z0-9_\u4e00-\u9fa5\s]*"\),\s*pointer_default\(unique\)\s*\]'
i_obj_str = a_obj_str + u'\s*interface\s*\w+\s*:\s*\w+\s*\{\s*(?:' + m_obj_str + u'\s*)*\};'

re_p_obj = re.compile(p_obj_str)
re_m_obj = re.compile(m_obj_str)
re_a_obj = re.compile(a_obj_str)
re_i_obj = re.compile(i_obj_str)

p_obj_str_g = u'\[(?P<p_io_type>\w+,*\s*\w*)\]\s*(?P<p_type>\w+\**)\s*(?P<p_name>\w+)'
m_obj_str_g = u'\[id\((?P<m_id>\d+)\)\s*,\s*helpstring\("(?P<m_helpstr>[a-zA-Z0-9_\u4e00-\u9fa5\s]*)"\)\]\s*HRESULT\s*(?P<m_name>\w+)\((?P<params>' + p_obj_str + u'\s*\,*\s*)+\);'
a_obj_str_g = u'\[object,\s?uuid\((?P<a_uuid>[a-zA-Z0-9\-]+)\),\s?dual,\s?nonextensible,\s?helpstring\("(?P<a_helpstr>[a-zA-Z0-9_\u4e00-\u9fa5\s]*)"\),\s?pointer_default\(unique\)\s*\]'
i_obj_str_g = a_obj_str + u'\s*interface\s*(?P<i_name>\w+)\s*:\s*(?P<i_parent>\w+)\s*\{\s*(?:' + m_obj_str + u'\s*)*\};' 

re_p_obj_g = re.compile(p_obj_str_g)
re_m_obj_g = re.compile(m_obj_str_g)
re_a_obj_g = re.compile(a_obj_str_g)
re_i_obj_g = re.compile(i_obj_str_g)

class Attr(object):
    '''
    the base attribute class
    '''
    pass
    
class InterfaceAttr(Attr):
    '''
    the attribute of the interface
    '''
    pass

class InterfaceObj(object):
    '''
    the interface object
    '''
    def __init__(self, name, parent, methods):
        self.name = name
        self.parent = parent
        self.methods = methods 
    
class IdlObj(object):
    '''
    idl object class
    '''
    interfaces = []
    def __init__(self, interfaces):
        self.interfaces = interfaces
   
class MethodObj(object):
    '''
    the methode object
    '''
    def __init__(self, id, helpstr, name, params):
        self.id = id
        self.helpstr = helpstr
        self.name = name
        self.params = params
        
class ParamObj(object):
    '''
    the param object
    '''
    def __init__(self, io_type, type, name, defaultval=''):
        self.io_type = io_type
        self.type = type
        self.name = name
        self.defaultval = defaultval
        
class IdlError(Exception):
    pass
        
class IdlParser(object):
    '''
    the idl parser
    '''
    def __init__(self):
        pass
        
    def __find_obj(self, src_str, re_no_g):
        return re_no_g.findall(src_str)

    def parse(self, idlfile, str_code='gb2312'):
        file = open(idlfile)
        stridl = file.read().decode(str_code)
        print type(stridl)
        file.close()
        
        i_str_arr = self.__find_obj(stridl, re_i_obj)
        if i_str_arr is None:
            raise IdlError('find the interface object fail, check format of the idl string.')
        
        interfaces = []
        for i_str in i_str_arr:
            i_obj = self.__parse_interface(i_str)
            if i_obj is None:
                raise IdlError('parse interface object fail, string: ' + i_str)
            else:
                interfaces.append(i_obj)
                
        return IdlObj(interfaces)

    def __parse_interface(self, i_str):
        i_a_arr = re_a_obj.findall(i_str) #TODO: attribute
        i_m_arr = re_m_obj.findall(i_str)
        
        methods = []
        if i_m_arr is not None:
            for m_str in i_m_arr:
                m_obj = self.__parse_methods(m_str)
                if m_obj is None:
                    raise IdlError('parse method object fail, string: ' + m_str)
                else:
                    methods.append(m_obj)

        ma = re_i_obj_g.match(i_str)
        ret = ma.groupdict()
        
        iname = ret['i_name']
        iparent = ret['i_parent']
        
        return InterfaceObj(iname, iparent, methods)
        
    def __parse_methods(self, m_str):
        p_arr = re_p_obj.findall(m_str)
        params = []
        if p_arr is not None:
            for p_str in p_arr:
                p_obj = self.__parse_params(p_str)
                if p_obj is None:
                    raise IdlError('parse param object fail, string: ' + p_str)
                else:
                    params.append(p_obj)

        ma = re_m_obj_g.match(m_str)
        ret = ma.groupdict()
        
        id = ret['m_id']
        helpstr = ret['m_helpstr']
        name = ret['m_name']
        
        return MethodObj(id, helpstr, name, params)
        
        
    def __parse_params(self, p_str):
        ma = re_p_obj_g.match(p_str)
        ret = ma.groupdict()
        
        io_type = ret['p_io_type']
        type = ret['p_type']
        name = ret['p_name']
        
        return ParamObj(io_type, type, name, '') # TODO: defaultval
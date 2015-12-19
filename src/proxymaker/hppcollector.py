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

g_re_f_name = re.compile(u'\A(?P<name>\w+).idl\Z')
g_replace_f_name = r'\g<name>'
g_re_i_name = re.compile(u'\AI(?P<name>\w+)\Z')
g_replace_i_name = r'\g<name>'

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
    
    idlfile = inputparam(1, 'input the idle file path: ', '', None, False)
    idl_name = os.path.basename(idlfile)
    idl_name = os.path.splitext(idl_name)[0]
    out_file = u'%s.h' % idl_name
    out_file = inputparam(2, 'input the out file name(default: %s): ' % out_file, out_file, None, True)
    
    parser = IdlParser()
    idl_obj = parser.parse(idlfile)

    macro = u'__%s_H__' % idl_name.upper()
    temp = u'#ifndef %s\n#define %s\n\n' % (macro, macro)
    for i_obj in idl_obj.interfaces:
        i_obj.proxy_name = g_re_i_name.sub(g_replace_i_name, i_obj.name)
        temp += u'#include <%s>\n' % (i_obj.proxy_name + u'Proxy.h')
    
    temp += u'\n#endif //!%s' % macro
    #str_path = os.path.join(self.out_dir, name)
    file = open(out_file, 'w')
    file.write(temp.encode('gb2312'))
    file.close()
        



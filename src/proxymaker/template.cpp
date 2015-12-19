// 此代码页由脚本生成，如需手动更改请注意再次生成覆盖
#include "../stdafx.h"
#include "{{ object.proxy_name.lower }}proxy.h"
#include <{{ factory.lower }}.h>

{% for m_obj in object.methods %}
BOOL C{{ object.proxy_name }}Proxy::{{ m_obj.name }}({{ m_obj.params_list_impl }}{% if m_obj.params_list_impl %}, {% endif %}wstring& strMsg)
{
    try
    {
        {{ m_obj.impl }}
    }
    catch (CEMRException& e)
    {
        strMsg = e.wwhat();
        return FALSE;
    }
    catch (...)
    {
        strMsg = L"未知错误";
        return FALSE;
    }

    return TRUE;
}

{% endfor %}

C{{ object.proxy_name }}Proxy::C{{ object.proxy_name }}Proxy(void)
{
}


C{{ object.proxy_name }}Proxy::~C{{ object.proxy_name }}Proxy(void)
{
}

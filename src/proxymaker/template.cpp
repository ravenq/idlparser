#include "../stdafx.h"
#include "{{ object.name.lower }}.h"
#include <{{ factory.lower }}.h>

{% for m_obj in object.methods %}
BOOL C{{ object.name }}Proxy::{{ m_obj.name }}({{ m_obj.params_list_impl }}{% if m_obj.params_list_impl %}, {% endif %}wstring* pStrMsg)
{
    try
    {
        {{ m_obj.impl }}
    }
    catch (CEMRException& e)
    {
        if(pStrMsg != NULL)
            *pStrMsg = e.wwhat();
        
        return FALSE;
    }
    catch (...)
    {
        if(pStrMsg != NULL) 
            *pStrMsg = L"未知错误";
        
        return FALSE;
    }

    return TRUE;
}

{% endfor %}

C{{ object.name }}Proxy::C{{ object.name }}Proxy(void)
{
}


C{{ object.name }}Proxy::~C{{ object.name }}Proxy(void)
{
}

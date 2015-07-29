#include "stdafx.h"
#include "{{ object.name.lower }}.h"
#include <{{ factory.lower }}.h>

{% for m_obj in object.methods %}
HRESULT C{{ object.name }}Proxy::{{ m_obj.name }}({% for param in m_obj.params %}{{ param.type }} {{ param.name }}{%if not forloop.last %}, {% endif %}{% endfor %})
{
    {% for param in m_obj.params%}
        {% if param.type == "LPCTSTR" or param.type == "wstring" %}
        CComBSTR com_{{ param.name }}({{ param.name }});
        {% elif param.type == "wstring&" %}
        CComBSTR com_{{ param.name }};
        {% elif param.type == "BOOL" %}
        VARIANT_BOOL com_{{ param.name }} = {{ param.name }} ? VARIANT_TRUE : VARIANT_FALSE;
        {% endif %}
    {% endfor %}
    
        CComPtr<{{ object.name }}> sp;
        C{{ factory }}::Instance().CreateObject(IID_{{ object.name }}, (void**)&sp);

        HRESULT rt = sp->{{ m_obj.name }}({% for param in m_obj.params %}{% if param.io_type == "out,retval" or param.io_type == "out, retval" %}&{%endif%}com_{{ param.name }}{%if not forloop.last %}, {% endif %}{% endfor %});
    {% for param in m_obj.params%}
        {% if param.io_type == "out,retval" or param.io_type == "out, retval" %}
        {{ param.name }} = com_{{ param.name }}
        {% endif %}
    {% endfor %}

        return rt;
}

{% endfor %}

C{{ object.name }}Proxy::C{{ object.name }}Proxy(void)
{
}


C{{ object.name }}Proxy::~C{{ object.name }}Proxy(void)
{
}

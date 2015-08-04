#include "stdafx.h"
#include "{{ object.name.lower }}.h"
#include <{{ factory.lower }}.h>

{% for m_obj in object.methods %}
HRESULT C{{ object.name }}Proxy::{{ m_obj.name }}({{ m_obj.params_list_impl }})
{
    {{ m_obj.impl }}
}

{% endfor %}

C{{ object.name }}Proxy::C{{ object.name }}Proxy(void)
{
}


C{{ object.name }}Proxy::~C{{ object.name }}Proxy(void)
{
}

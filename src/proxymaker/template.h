#ifndef __{{ object.name.upper }}_PROXY_H__
#define __{{ object.name.upper }}_PROXY_H__

#include "../basedefine.h"

class ZOE_PROXY_API C{{ object.name }}Proxy
{
public:
{% for m_obj in object.methods %}
	static BOOL {{ m_obj.name }}({{ m_obj.params_list }}{% if m_obj.params_list_impl %}, {% endif %}wstring* pStrMsg = NULL);
{% endfor %}
protected:
	C{{ object.name }}Proxy(void);
	~C{{ object.name }}Proxy(void);
};

#endif //!__{{ object.name.upper }}_PROXY_H__

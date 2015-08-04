#ifndef __{{ object.name.upper }}_PROXY_H__
#define __{{ object.name.upper }}_PROXY_H__

#include "ZemrServerProxyGlobal.h"

class SERVER_PROXY_API C{{ object.name }}Proxy
{
public:
{% for m_obj in object.methods %}
	static HRESULT {{ m_obj.name }}({{ m_obj.params_list }});
{% endfor %}
protected:
	C{{ object.name }}Proxy(void);
	~C{{ object.name }}Proxy(void);
};

#endif //!__{{ object.name.upper }}_PROXY_H__

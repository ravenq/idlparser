#ifndef __{{ object.name.upper }}_PROXY_H__
#define __{{ object.name.upper }}_PROXY_H__

#include "ZemrServerProxyGlobal.h"

class SERVER_PROXY_API C{{ object.name }}Proxy
{
public:
{% for method in object.methods %}
	static HRESULT {{ method.name }}({% for param in method.params %}{{ param.type }} {{ param.name }}, {%if forloop.last%}{{ param.type }} {{ param.name }}{%endif%}{% endfor %});
{% endfor %}
protected:
	C{{ object.name }}Proxy(void);
	~C{{ object.name }}Proxy(void);
};

#endif //!__{{ object.name.upper }}_PROXY_H__

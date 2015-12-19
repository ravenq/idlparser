// 此代码页由脚本生成，如需手动更改请注意再次生成覆盖
#ifndef __{{ object.proxy_name.upper }}_PROXY_H__
#define __{{ object.proxy_name.upper }}_PROXY_H__

#include "../basedefine.h"

class ZOE_PROXY_API C{{ object.proxy_name }}Proxy
{
public:
{% for m_obj in object.methods %}
	static BOOL {{ m_obj.name }}({{ m_obj.params_list }}{% if m_obj.params_list_impl %}, {% endif %}wstring& strMsg);
{% endfor %}
protected:
	C{{ object.proxy_name }}Proxy(void);
	~C{{ object.proxy_name }}Proxy(void);
};

#endif //!__{{ object.proxy_name.upper }}_PROXY_H__

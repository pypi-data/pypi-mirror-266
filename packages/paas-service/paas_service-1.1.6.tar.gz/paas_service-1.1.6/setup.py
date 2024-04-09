# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['paas_service',
 'paas_service.auth',
 'paas_service.management',
 'paas_service.management.commands',
 'paas_service.migrations']

package_data = \
{'': ['*']}

install_requires = \
['blue-krill>=1.0.15', 'django-translated-fields', 'jsonfield', 'pyjwt']

setup_kwargs = {
    'name': 'paas-service',
    'version': '1.1.6',
    'description': 'A Django application for developing BK-PaaS add-on services.',
    'long_description': '# Paas Service\n\n蓝鲸 PaaS 平台增强服务框架\n\n\n## 版本历史\n\n详见 `CHANGES.md`。\n\n## 使用指南\n\n1. 更新 settings：\n```python\nINSTALLED_APPS = [\n    ...\n    \'paas_service\',\n    ...\n]\n\nMIDDLEWARE = [\n    ...\n    \'paas_service.auth.middleware.VerifiedClientMiddleware\',\n    ...\n]\n\n# 数据库敏感字段加密 Key\nBKKRILL_ENCRYPT_SECRET_KEY = base64.b64encode(b\'\\x01\' * 32)\n\n# 与 PaaS 平台通信的 JWT 信息\nPAAS_SERVICE_JWT_CLIENTS = [\n    {\n        "iss": "paas-v3",\n        "key": "123..........",\n        "algorithm": "HS256",\n    },\n]\n\n# 增强服务供应商类\nPAAS_SERVICE_PROVIDER_CLS = "svc_xxx.vendor.provider.Provider"\n# 增强服务实例信息渲染函数\nPAAS_SERVICE_SVC_INSTANCE_RENDER_FUNC = "svc_xxx.vendor.render.render_instance_data"\n\n# 设置语言，注意：目前国际化只支持: 简体中文 和 English\nLANGUAGE_CODE = \'zh-cn\'\n\nLANGUAGES = [("zh-cn", "简体中文"), ("en", "English")]\n```\n\n2. 单元测试\n\n首先，安装 pytest、pytest-django。\n\n然后执行 `make test` 运行所有单元测试。\n',
    'author': 'blueking',
    'author_email': 'blueking@tencent.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<3.11',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_animalvoice',
 'nonebot_plugin_animalvoice.AnimalVoice',
 'nonebot_plugin_animalvoice.Cheru']

package_data = \
{'': ['*']}

install_requires = \
['nonebot2>=2.2.0,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-animalvoice',
    'version': '0.2.0',
    'description': '✨Nonebot兽语译者插件✨',
    'long_description': '<div align="center">\n  \n  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>\n  <br>\n  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>\n\n\n# nonebot_plugin_animalVoice\n  \n_✨Nonebot兽语译者插件✨_\n\n---\n  \n<a href="./LICENSE">\n    <img src="https://img.shields.io/github/license/ANGJustinl/nonebot_plugin_animalVoice" alt="license">\n</a>\n<a href="https://pypi.python.org/pypi/nonebot_plugin_animalVoice">\n    <img src="https://img.shields.io/pypi/v/nonebot_plugin_animalVoice.svg" alt="pypi">\n</a>\n<a href="https://www.python.org">\n    <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">\n</a>\n\n---  \n </div> \n  \n## ✔ 使用例\n\n![3`$HP~HVN%SK(IV@2HO7X{M](https://user-images.githubusercontent.com/96008766/210118707-b00e90ff-ce8c-4fdb-bcd9-f3a18c2ebc50.png)\n\n![OYJ5N2~Z@XZ)B6FL %MEIKA](https://user-images.githubusercontent.com/96008766/210118729-8e8a6ff0-f911-4514-aac9-a87f714051e9.png)\n  \n## 💿 安装\n\n### 1. nb-cli安装（推荐）\nbot根目录下打开命令行，执行nb命令安装插件，插件配置会自动添加至配置文件 \n \n```\nnb plugin install nonebot_plugin_animalVoice\n```\n\n### 2. pip安装\n\n```\npip install nonebot_plugin_animalVoice --upgrade\n\n```  \n\n打开 nonebot2 项目的 ```bot.py``` 文件, 在其中写入  \n```nonebot.load_plugin(\'nonebot_plugin_animalVoice\')```  \n  \n或在bot路径```pyproject.toml```的```[tool.nonebot]```的```plugins```中添加```nonebot_plugin_animalVoice```即可  \npyproject.toml配置例如： \n\n``` \n\n[tool.nonebot]\nplugin_dirs = ["src/plugins"]\nplugins = ["nonebot_plugin_animalVoice","xxxxx"]\n\n```\n\n\n## 🎉 使用\n### 指令表\n| 指令 | 需要@ | 范围 | 说明 |\n|:-----:|:----:|:----:|:----:|\n| [兽音加密]/[convert] | 否 | 群聊/私聊 | 发送需要加密的文字 |\n| [兽音解密]/[deconvert] | 否 | 群聊/私聊 | 发送需要解密的文字 |\n| [切噜一下]/[cherulize] | 否 | 群聊/私聊 | 发送需要解密的文字 |\n| [切噜～]/[decherulize] | 否 | 群聊/私聊 | 发送需要解密的文字 |\n\n\n**注意**\n\n默认情况下, 您应该在指令前加上命令前缀, 通常是 /\n\n\n### 🧡特别感谢 \n\nHoshinoBot: https://github.com/Ice-Cirno/HoshinoBot 提供了切噜切噜的算法\n',
    'author': 'angjustinl',
    'author_email': 'angjustin@163.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

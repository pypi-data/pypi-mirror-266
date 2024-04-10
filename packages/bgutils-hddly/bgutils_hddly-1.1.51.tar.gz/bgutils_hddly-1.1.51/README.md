# 概括
bgutils是一个适用于bigdata.hddly.cn大数据实验室的工具包
## 说明
本报名字为*packer*,使用方法包括数据库连接工具mysqlUtil,mongoUtil,文件上传工具ftpUtils...

### 打包方法
生成requirements.txt
pip install pipreqs -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
### 参数说明
pipreqs ./ --encoding=utf8
安装setuptools& wheel
python -m pip install --upgrade setuptools wheel -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
### 参数说明
安装twine
python -m pip install --upgrade twine pip install pipreqs -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
打包
python setup.py sdist bdist_wheel
#如何设置开通pypi两因素认证2FA
pip install -U sphinx -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
pip install use_2to3 -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
pip install pyppi -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
pyppi register --two-factor

发布
dipython -m twine upload -u goodym -p ywq****** --repository-url https://upload.pypi.org/legacy/  dist/*
### 安装方法
pip install -r requirements.txt
或
pip install -r requirements.txt  -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
### 参数说明

### 使用安装
pip install bgutils-hddly
pip install --upgrade bgutils-hddly
pip install --default-timeout=100 --upgrade bgutils-hddly
### 错误反馈
### 发布到国源pip源

### 查看版本
pip3 show bgutils-hddly

### 卸载版本
pip uninstall bgutils-hddly

### 安装依赖
pip3 install redis -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com

python.exe -m pip install --upgrade pip -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
pip uninstall bgutils-hddly
pip install bgutils-hddly  -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com

### Gitlab切换
由于 jihulab.com进入收费，我们即将切换到自建git服务器上，切换方法如：
先查看否已切换
```
git remote get-url origin
结果如：
D:\soft\gitlab\common>git remote get-url origin
https://gitee.com/big-data-lab/common
```
使用资源管理器进入scrapy目录，在地址栏中输入cmd进入命令行，运行：
```
git remote set-url origin http://home.hddly.cn:8093/biglab-share/scrapy.git
```
同样，使用资源管理器进入common目录，在地址栏中输入cmd进入命令行，运行：
```
git remote set-url origin http://home.hddly.cn:8093/big-data-lab/common.git

git config --global user.name "yuxm"
git config --global user.email "8083693@qq.com"
git config --global credential.helper

```


如何设置开通pypi两因素认证2FA
要在PyPI上设置两因素认证（2FA），你需要一个支持两因素认证的身份验证器应用，如Google Authenticator。以下是设置步骤的简要概述和示例代码：

安装twofactor库（如果尚未安装）：

pip install twofactor

运行twofactor以生成一组身份验证器提示，并使用身份验证器扫描这些提示。

import twofactor
twofactor.enable_totp_authentication('goodym@163.com')

使用你的身份验证器应用显示的代码，并在PyPI上启用两因素认证。

完成身份验证器的设置后，你将收到一个密钥，将其提供给twofactor.enable_totp_authentication函数。

登录PyPI，转到账户设置并启用两因素认证。

在提示时提供从身份验证器应用程序获得的一次性代码。

注意：这个过程不涉及直接编写代码来设置两因素认证。twofactor库用于在PyPI启用两因素认证后管理身份验证器。在PyPI的网站上手动设置两因素认证，并在提示时提供生成的一次性代码。

提示：AI自动生成，仅供参考
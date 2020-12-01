### How to Run

### 小程序appid配置

#### weixin/settings.py

##### 	七牛存储的配置，用来上传图片

QINIU_ACCESS_TOKEN = 'xxxxx'

QINIU_KEY = 'xxxxxx'

QINIU_BUCKET = 'image'

QINIU_DOMAIN = 'http://image.shiguofu.cn'

##### 小程序的appid 等配置

XCX_APPID = 'wxxxxxx'

XCX_APPSEC = 'cxxxxxxx'

TOKEN = 'xxxxxxxx'

AESKEY = 'xxxxxxx'

### 安装部署

1. 安装依赖
在需要部署的机器上运行以下命令
```
sudo ./scripts/install_deps.sh
```

2. 配置文件

conf/目录下的
localhost  -- 本机部署运行
release --- 线上发布运行
test  -- 测试

修改conf/test中的ip与用户名/密码

3. 部署运行
```
cd conf && fab test deploy
```


> windows下开发注意：
> 1. windows下换行符是\r\n, linux 下是\n，因此在windows下需要设置git 换行符不转换
> git config core.autocrlf false
> 2. 目标主机必须是linux，否则会失败
> 3. 目标机首次运行需要安装依赖，包括JDK;脚本 scripts/install_deps.sh


4. 一些问题
uwsgi 启动会出现以下错误
```
Listen queue size is greater than the system max net.core.somaxconn
```
使用以下命令更改内核参数，临时生效
```
echo 2048 > /proc/sys/net/core/somaxconn
```
修改 /etc/sysctl.conf 在末尾加上
```
net.core.somaxconn = 2048
```
永久生效
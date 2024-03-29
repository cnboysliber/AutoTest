## 自动化测试系统
平台技术：python + flask + mysql + redis + jquery + html实现的前后端分离框架
用例运行可批次化运行、单独运行，批次运行使用的是线程池方式
支持报表定时邮件发送指定人员
### 1.部署方式：
  安装依赖包： pip install -r requirements.txt
  线上环境配置：
  <br>
  默认启动即可(python AutoTest.py或uwsgi启动)
  <br>
  <br>
  开发环境配置（可以pycharm设置里配置启动参数即可）:
  <br>
  python AutoTest.py devel
  
### 2.支持测试内容：
目前只支持HTTP接口测试，可以对同一个域名自定义DNS解析，实现相同用例同时测试不同环境

### 3.用例中接口参数化设置

在接口中可以设置动态参数，配置规则是：
接口支持在URL/包头/json内容中自定义参数预留位，稍后在用例中可以为预留位指定参数值

方法为：使用${}将需要预定义参数的地方包裹起来

json例子:

```
{ "head":{ "a": 1, "param1": ${param1} }, "body": { "b": 2, "param2": ${param1} } }
```

其中param1及param2为需要替换的预留参数位, 使用${param1}以及${param2}代替

动态参数支持默认值设置，如上设置param1的默认值我们可以${param1==default}这样设置，default就是param1默认值

### 4.接口支持自定义加密方式：
 如果测试的项目接口需要签名或者加密，可以在自动化项目代码中加入响应的加密算法，然后配置把加密方法名称配置到加密表格中<br/>
 在定义接口时，就可配置对应的加密方式





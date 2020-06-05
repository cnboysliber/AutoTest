## 自动化测试系统

### 部署方式：
  安装依赖包： pip install -r requirement.txt
  线上环境配置：
  <br>
  默认启动即可(python AutoTest.py或uwsgi启动)
  <br>
  <br>
  开发环境配置（可以pycharm设置里配置启动参数即可）:
  <br>
  python AutoTest.py devel
  
### 支持测试内容：
目前只支持HTTP接口测试，可以对同一个域名自定义DNS解析，实现相同用例同时测试不同环境

# JDSF Python Demo

## 项目说明

* 本项目为JDSF Python demo 项目，使用的 web 框架为 flask。
  
## 环境准备

* 项目使用Python 2.7 开发 使用 pip 进行包管理 ，请在试用前准备好相应的环境，如果测试环境已经安装了 [open-tracing-python-flask](https://github.com/opentracing-contrib/python-flask)  和 [jaeger-client-python](https://github.com/jaegertracing/jaeger-client-python) 推荐在开发环境安装 `virtualenv` 然后使用包管理安装本 demo 需要安装的包

* 如果使用 PyCharm 进行开发，不要使用默认的 flask 调试环境配置 ，因`flask run` 命令无法运行`__name__ == '__main__'`一些代码中指定的端口等配置，如果需要请修改启动部分代码。

## 项目结构

|-dome_client  
|-demo_server  
|-README.md

其中 demo_client 是服务的消费者  
demo_server 是服务的生产者  
README.md 此描述文件

## 项目依赖类库说明

* opentracing_instrumentation： opentracing api 库

* python-consul： 注册中心 consul api 库

* pyYaml： Python 读取 YAML 配置文件类库

* requests： Python HttpClient 请求类库，在项目中封装成为负载请求客户端

* jaeger-client： opentracing jaeger api 实现库，实现了 opentraing 1.0版本，在此文档编写时还未发布实现opentraing 2.0 api 的类库，因此在项目中约束了版本。

* Flask-OpenTracing：flask opentracing api 类库，实现了请求拦截，自动生成请求 span 的功能 因新版本实现了 opentracing 2.0 版本的 api 与jaeger-client 不兼容因此项目引用了一个指定的老版本。

## 配置及使用说明

* 配置文件在项目的 config 目录下的 appConfig.yaml 文件，具体的说明如下：

```yaml
consul:
  config:
    schema: http # 注册中心使用协议
    port: 8500   # 注册中心端口
    address: 10.12.209.43 # 注册中心地址
  discover:
    config:
      serviceName: python-consul-demo # 项目在注册中心注册的服务名称
      preferIpAddress: true           # 是否使用 ip 地址注册
      healthCheckUrl: /api/health/check  # 健康检查调用的 url 地址
      instanceId: python-consul-demo-1   # 实例 id
app:
  config:
    serviceName: python-consul-demo  # 应用名称，会放在调用链内展示的服务名
    serviceIpAddress: 10.12.140.173  # 服务启动的地址，会注册在注册中心中
    servicePort: 19300               # 项目启动端口号
trace:
  config:
    simpleType: probabilistic  # 采样模式
    simpleRate: 1              # 采样率
    traceUDPAddress: 127.0.0.1 # 调用链 udp 模式 sender 发送地址
    traceUDPPort: 5775         # 调用链 udp 模式 sender 的端口号
```

* 此项目默认需要在本机启动 jaeger agent，如果需要进行修改 jaeger 相关配置请查看下面的说明。

## 代码运行及调试

* 在运行过程中需要安装类库

```Shell
pip install opentracing_instrumentation
pip install python-consul
pip install pyYaml
pip install requests
pip install jaeger-client==3.2.0
pip install Flask-OpenTracing==0.1.8
```

安装上面的类库 ，然后启动应用即可，如果无法调用注册中心和调用链请使用 如下命令启动应用

```Shell
    python app.py
```

使用此命令可以使用老版本的 app.run() 模式启动 flask 应用而非 flask run 的方式。

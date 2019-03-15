import yaml


class ConsulDiscoverConfig(object):
    """
     consul discover config properties ,
     prefer_ip_address :  bool ,if is true use config ip address registry service else
     use system host for registry
     instance_id: registry instance id
     service_name : the registry service name .if is `None` use the app config service name
    """
    def __init__(self, prefer_ip_address, instance_id, service_name, health_check_url):
        self.prefer_ip_address = prefer_ip_address
        self.instance_id = instance_id
        self.service_name = service_name
        self.health_check_url = health_check_url

    def __str__(self):
        return 'ConsulDiscoverConfig({service_name},{prefer_ip_address},{instance_id},{health_check_url})'.format(
            service_name=self.service_name,
            prefer_ip_address=self.prefer_ip_address,
            instance_id=self.instance_id,
            health_check_url=self.health_check_url
        )

    @classmethod
    def from_yaml_dic(cls, yaml_load_dic):
        service_name = yaml_load_dic['consul']['discover']['config']['serviceName']
        prefer_ip_address = yaml_load_dic['consul']['discover']['config']['preferIpAddress']
        instance_id = yaml_load_dic['consul']['discover']['config']['instanceId']
        health_check_url = yaml_load_dic['consul']['discover']['config']['healthCheckUrl']
        return ConsulDiscoverConfig(prefer_ip_address, instance_id, service_name, health_check_url)

    @classmethod
    def load_config(cls, config_yaml_path='./config/appConfig.yaml'):
        f = open(config_yaml_path)
        y = yaml.load(f, Loader=yaml.SafeLoader)
        return ConsulDiscoverConfig.from_yaml_dic(y)


class AppConfig(object):
    def __init__(self, service_name , service_ip_address, service_port):
        self.service_name = service_name
        self.service_ip_address = service_ip_address
        self.service_port = service_port

    def __str__(self):
        return 'AppConfig({service_name},{service_ip_address},{service_port})'.format(
                                                                service_name=self.service_name,
                                                                service_ip_address=self.service_ip_address,
                                                                service_port=str(self.service_port))

    @classmethod
    def from_yaml_dic(cls, yaml_load_dic):
        service_name = yaml_load_dic['app']['config']['serviceName']
        service_ip_address = yaml_load_dic['app']['config']['serviceIpAddress']
        service_port = yaml_load_dic['app']['config']['servicePort']
        return AppConfig(service_name,service_ip_address,service_port)

    @classmethod
    def load_config(cls, config_yaml_path='./config/appConfig.yaml'):
        f = open(config_yaml_path)
        y = yaml.load(f, Loader=yaml.SafeLoader)
        return AppConfig.from_yaml_dic(y)


class ConsulConfig(object):
    def __init__(self,address, schema='http', port=8500):
        self.address = address
        self.schema = schema
        self.port = port

    def __str__(self):
        return 'ConsulConfig({schema},{address},{port})'.format(schema=self.schema,
                                                                address=self.address,
                                                                port=str(self.port))

    def to_yaml_dic(self):
        return {'address': self.address, 'schema': self.schema, 'port': self.port}

    @classmethod
    def from_yaml_dic(cls,yaml_load_dic):
        schema = yaml_load_dic['consul']['config']['schema']
        if schema is None:
            schema = 'http'
        port = yaml_load_dic['consul']['config']['port']
        if port is None:
            port = 8500
        return ConsulConfig(yaml_load_dic['consul']['config']['address'], schema, port)


    @classmethod
    def load_config(cls, config_yaml_path='./config/appConfig.yaml'):
        f = open(config_yaml_path)
        y = yaml.load(f, Loader=yaml.SafeLoader)
        return ConsulConfig.from_yaml_dic(y)

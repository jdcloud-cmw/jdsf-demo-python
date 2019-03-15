import datetime
import random
import threading

import consul
from loadbalance.consulconfig import ConsulConfig, ConsulDiscoverConfig, AppConfig
from tool.networktool import *

service_cache = {}


def reload_service_cache():
    if service_cache is not None and len(service_cache)>0:
        for key in service_cache.keys():
            RegistryService.load_remote_service_cache(key)


class RegistryService(object):
    def __init__(self):
        consul_discover_config = ConsulDiscoverConfig.load_config()
        app_config = AppConfig.load_config()
        self.consul_discover_config = consul_discover_config
        self.app_config = app_config

    def registry_service(self, consul_schema=None, consul_address=None, consul_port=None):
        consul_client = RegistryService.get_consul_client(consul_schema, consul_address, consul_port)
        if self.consul_discover_config.prefer_ip_address:
            if self.app_config.service_ip_address is not None:
                service_ip_address = self.app_config.service_ip_address
            else:
                service_ip_address = get_host_ip()
        else:
            service_ip_address = get_host_name()
        service_port = self.app_config.service_port
        health_check_url = self.consul_discover_config.health_check_url
        service_name = self.consul_discover_config.service_name
        if service_name is None:
            service_name = self.app_config.service_name
        instance_id = self.consul_discover_config.instance_id
        if instance_id is None:
            instance_id = service_name + str(service_port) + random.uniform(1, 20)
        check_url = "http://" + service_ip_address + ":" + str(service_port) + health_check_url
        check = consul.Check.http(check_url, "10s")
        consul_client.agent.service.register(service_name, instance_id,
                                             address=service_ip_address,
                                             port=service_port,
                                             check=check)
        timer = threading.Timer(5, reload_service_cache)
        timer.start()

    @classmethod
    def get_consul_client(cls, consul_schema=None, consul_address=None, consul_port=None):
        consul_config = ConsulConfig.load_config()
        if consul_schema is not None:
            consul_config.schema = consul_schema
        if consul_address is not None:
            consul_config.address = consul_address
        if consul_port is not None:
            consul_config.port = consul_port
        host = consul_config.address
        scheme = consul_config.schema
        port = consul_config.port
        consul_client = consul.Consul(host, port, None, scheme)
        return consul_client

    @classmethod
    def load_remote_service_cache(cls, service_name):
        health_service = RegistryService.get_health_service(service_name)
        if health_service is not None and len(health_service[1])>0:
            cache_service_info = CacheServiceInfo(service_name=service_name)
            for service in health_service[1]:
                health_service_info = HealthServiceInfo(service_name=service['Service']['Service'],
                                                        instance_id=service['Service']['ID'],
                                                        service_host=service['Service']['Address'],
                                                        service_port=service['Service']['Port'])
                cache_service_info.add_service(health_service_info)
            service_cache[service_name] = cache_service_info

    @classmethod
    def get_health_service(cls,service_name):
        consul_client = RegistryService.get_consul_client()
        health_service = consul_client.health.service(service_name, passing=True)
        if health_service is not None:
            return health_service


class HealthServiceInfo(object):
    def __init__(self, service_name, instance_id, service_host, service_port):
        self.service_name = service_name
        self.instance_id = instance_id
        self.service_host = service_host
        self.service_port = service_port

    def __str__(self):
        return 'HealthServiceInfo({service_name},{instance_id},{service_host},{service_port})'.format(
            service_name=self.service_name,
            service_host=self.service_host,
            service_port=self.service_port,
            instance_id=self.instance_id
        )


class CacheServiceInfo(object):
    def __init__(self, service_name):
        self.update_time = datetime.datetime.now()
        self.service_name = service_name
        self.services = []

    def add_service(self, health_service_info):
        self.services.append(health_service_info)

    def get_service(self):
        service_instance_count = len(self.services)
        if service_instance_count > 0:
            index = random.uniform(0, service_instance_count)
            service = self.services[int(index)]
            return service
        else:
            health_service = RegistryService.get_health_service(self.service_name)
            if health_service is not None:
                self.services = []
                for service in health_service[1]:
                    health_service_info = HealthServiceInfo(service_name=service['Service']['Service'],
                                                            instance_id=service['Service']['ID'],
                                                            service_host=service['Service']['Address'],
                                                            service_port=service['Service']['Port'])
                    self.update_time = datetime.datetime.now()
                    self.services.append(health_service_info)
                index = random.uniform(0, len(self.services))
                return self.services[int(index)]
            else:
                return None

    def __str__(self):
        return 'CacheServiceInfo({service_name},{update_time},{services})'.format(
            service_name=self.service_name,
            update_time=self.update_time,
            services=self.services
        )

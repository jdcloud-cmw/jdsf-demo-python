import logging

import yaml
from jaeger_client import Config
from loadbalance.consulconfig import AppConfig


class OpenTraceConfig(object):
    def __init__(self, simple_type, simple_rate, trace_udp_address,
                 trace_udp_port, trace_http_address, trace_http_port):
        self.simple_type = simple_type
        self.simple_rate = simple_rate
        self.trace_udp_address = trace_udp_address
        self.trace_udp_port = trace_udp_port
        self.trace_http_address = trace_http_address
        self.trace_http_port = trace_http_port

    def __str__(self):
        return 'OpenTraceConfig({simple_type},{simple_rate},{trace_udp_address},{trace_udp_port},' \
               '{trace_http_address},{trace_http_port})'.format(simple_type=self.simple_type,
                                                                simple_rate=self.simple_rate,
                                                                trace_udp_address=self.trace_udp_address,
                                                                trace_udp_port=self.trace_udp_port,
                                                                trace_http_address=self.trace_http_address,
                                                                trace_http_port=self.trace_http_port)

    @classmethod
    def from_yaml_dic(cls, yaml_load_dic):
        trace_udp_address = ""
        trace_udp_port = 0
        trace_http_address = ""
        trace_http_port = 0
        simple_type = yaml_load_dic['trace']['config']['simpleType']
        simple_rate = yaml_load_dic['trace']['config']['simpleRate']
        if 'traceUDPAddress' in yaml_load_dic['trace']['config'].keys():
            trace_udp_address = yaml_load_dic['trace']['config']['traceUDPAddress']
        if 'traceUDPPort' in yaml_load_dic['trace']['config'].keys():
            trace_udp_port = yaml_load_dic['trace']['config']['traceUDPPort']
        if 'traceHttpAddress' in yaml_load_dic['trace']['config'].keys():
            trace_http_address = yaml_load_dic['trace']['config']['traceHttpAddress']
        if 'traceHttpPort' in yaml_load_dic['trace']['config'].keys():
            trace_http_port = yaml_load_dic['trace']['config']['traceHttpPort']
        return OpenTraceConfig(simple_type, simple_rate, trace_udp_address, trace_udp_port, trace_http_address,
                               trace_http_port)

    @classmethod
    def load_config(cls, config_yaml_path='./config/appConfig.yaml'):
        f = open(config_yaml_path)
        y = yaml.load(f, Loader=yaml.SafeLoader)
        return OpenTraceConfig.from_yaml_dic(y)


def initialize_tracer(config_file_path):
    app_config = AppConfig.load_config(config_file_path)
    if config_file_path is None:
        trace_config = OpenTraceConfig.load_config()
    else:
        trace_config = OpenTraceConfig.load_config(config_file_path)
    log_level = logging.DEBUG
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)
    # Create configuration object with enabled logging and sampling of all requests.
    config = Config(config={'sampler': {'type': trace_config.simple_type, 'param': trace_config.simple_rate},
                            'logging': True,
                            'local_agent':
                            # Also, provide a hostname of Jaeger instance to send traces to.
                                {'reporting_host': trace_config.trace_udp_address}},
                    # Service name can be arbitrary string describing this particular web service.
                    service_name=app_config.service_name)
    return config.initialize_tracer()


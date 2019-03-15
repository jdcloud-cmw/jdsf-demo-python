from urlparse import urlparse
import re
import requests

from loadbalance.registryservice import service_cache, RegistryService


class LoadBalanceSession(requests.Session):
    def send(self, request, **kwargs):
        url = request.url
        res = urlparse(url)
        if res is not None:
            if re.match(r'((?:(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d)\\.){3}(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d))',
                        res.netloc,
                        re.M | re.I):
                return super(LoadBalanceSession, self).send(request, **kwargs)
            else:
                request_domain = res.netloc
                if request_domain not in service_cache.keys():
                    RegistryService.load_remote_service_cache(request_domain)
                if request_domain in  service_cache.keys() and service_cache[request_domain] is not None:
                    health_request_service = service_cache[request_domain].get_service()
                    request_address = health_request_service.service_host
                    request_port = health_request_service.service_port
                    # res.netloc = request_address
                    # res.port = request_port
                    port_str = ''
                    if request_port is not None and request_port > 0:
                        port_str = ':' + str(request_port)
                    service_request_url = res.scheme + '://' + request_address + port_str + res.path
                    if res.query is not None and len(res.query) > 0:
                        service_request_url = service_request_url + "?" + res.query
                    if res.fragment is not None and len(res.fragment) > 0:
                        service_request_url = service_request_url + "#" + res.fragment
                    request.url = service_request_url
                    return super(LoadBalanceSession, self).send(request, **kwargs)
                else:
                    return super(LoadBalanceSession, self).send(request, **kwargs)

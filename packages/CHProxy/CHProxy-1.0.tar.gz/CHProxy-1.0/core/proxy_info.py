class ProxyInfo(object):
    proxy_id: int
    ip: str
    http_port: str
    http_port_secured: str
    s5_port: str
    s5_port_secured: str
    expire_at_timestamp: str
    province: str
    city: str
    carrier: str

    def __init__(self, data: dict):
        if 'id' in data:
            self.proxy_id = data['id']
        if "proxy_id" in data:
            self.proxy_id = data['proxy_id']
        self.ip = data['ip']
        if 'http_port' in data:
            self.http_port = data['http_port']
        if 'http_port_secured' in data:
            self.http_port_secured = data['http_port_secured']
        if 's5_port' in data:
            self.s5_port = data['s5_port']
        if 's5_port_secured' in data:
            self.s5_port_secured = data['s5_port_secured']
        self.expire_at_timestamp = data['expire_at_timestamp']
        if "filter" in data:
            self.province = data['filter']['province']
            self.city = data['filter']['city']
            self.carrier = data['filter']['carrier']
        if "province" in data:
            self.province = data['province']
        if "city" in data:
            self.city = data['city']
        if "carrier" in data:
            self.carrier = data['carrier']

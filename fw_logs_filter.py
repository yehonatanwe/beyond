import abc
import consts
import ipaddress
import re
from logging import getLogger


logger = getLogger(consts.LOGGER)


class IpRange:

    def __init__(self, start, end):
        self.start = ipaddress.ip_address(start)
        self.end = ipaddress.ip_address(end)

    def __contains__(self, item):
        if not isinstance(item, ipaddress.IPv4Address) or not isinstance(
                item, ipaddress.IPv6Address):
            return False
        return self.start < item < self.end


class FwLogFilter(abc.ABC):

    def __init__(self, filter_type, values, field=None):
        self.filter_response = False
        self.set_filter_response(filter_type)
        self.values = []
        self.construct_values(values)
        self.field = field

    def set_filter_response(self, filter_type):
        if filter_type == 'include':
            self.filter_response = False
        elif filter_type == 'exclude':
            self.filter_response = True
        else:
            raise Exception(f'Unknown filter type: {filter_type}')

    @abc.abstractmethod
    def construct_values(self, values):
        pass

    @abc.abstractmethod
    def apply_filter(self, fw_log):
        pass


class IpFilter(FwLogFilter, abc.ABC):

    def __init__(self, filter_type, values):
        super().__init__(filter_type, values)
        if not self.field:
            self.field = 'SRC'

    def apply_filter(self, fw_log):
        log_ip = getattr(fw_log, self.field, None)
        if log_ip is None:
            return not self.filter_response
        log_ip = ipaddress.ip_address(log_ip)
        for container in self.values:
            if log_ip in container:
                return self.filter_response
        return not self.filter_response


class SingleIpFilter(IpFilter):

    def construct_values(self, values):
        self.values = [values.split(',')]


class IpRangeFilter(IpFilter):

    def construct_values(self, values):
        for v in values:
            s, e = v.split('-')
            self.values.append(IpRange(s, e))


class SubnetFilter(IpFilter):

    def construct_values(self, values):
        for v in values:
            self.values.append(ipaddress.ip_network(v))


class RegexFilter(FwLogFilter):

    def construct_values(self, values):
        self.values.append('|'.join(values))

    def apply_filter(self, fw_log):
        log_str = getattr(fw_log, self.field, None)
        if log_str is None:
            return not self.filter_response
        for regex in self.values:
            if re.match(regex, log_str):
                return self.filter_response
        return not self.filter_response


class UserFilter(RegexFilter):

    def __init__(self, filter_type, values):
        super().__init__(filter_type, values)
        if not self.field:
            self.field = 'USER'


class FwLogFilterApplier:

    FILTERS = {
        'ip': SingleIpFilter,
        'range': IpRangeFilter,
        'subnet': SubnetFilter,
        'user': RegexFilter
    }

    def __init__(self, filters):
        self.filters = []
        if filters:
            for filter_name, values in filters:
                self.filters.append(self.filter_factory(filter_name, values))

    def filter_factory(self, filter_name, values):
        filter_type, filter_attr = filter_name.lower().split('_')
        filter_obj = self.FILTERS.get(filter_type)
        if not filter_obj:
            raise Exception(f'Unknown filter attribute: {filter_attr}')
        return filter_obj(filter_type, values)

    def filter_log(self, fw_log):
        if not self.filters:
            return False
        return any(f.apply_filter(fw_log) for f in self.filters)

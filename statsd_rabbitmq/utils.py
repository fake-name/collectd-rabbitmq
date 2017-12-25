# -*- coding: iso-8859-15 -*-

# Copyright (c) 2014 The New York Times Company
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Module that contains utility classes and functions """

import re
import logging
import json
from urllib.parse import urlparse

def load_config(config_file_path):
    """
    Converts a collectd configuration into rabbitmq configuration.
    """
    conf_logger = logging.getLogger('Main.StatsModule.Setup')
    conf_logger.debug('Configuring RabbitMQ Plugin')
    data_to_ignore = dict()
    scheme = 'http'
    validate_certs = True
    vhost_prefix = None

    with open(config_file_path, "r") as fp:
        conf_data = json.load(fp)

    print(conf_data)

    for conf_key, conf_value in conf_data.items():
        conf_logger.debug("%s = %s", conf_key, conf_value)
        if conf_value:
            if conf_key == 'StatsdAddress':
                statsd_host = conf_value
            elif conf_key == 'StatsdPort':
                statsd_port = conf_value
            elif conf_key == 'StatsdPrefix':
                statsd_prefix = conf_value
            elif conf_key == 'Username':
                username = conf_value
            elif conf_key == 'Password':
                password = conf_value
            elif conf_key == 'Host':
                host = conf_value
            elif conf_key == 'Port':
                port = conf_value
            elif conf_key == 'Realm':
                realm = conf_value
            elif conf_key == 'Scheme':
                scheme = conf_value
            elif conf_key == 'VHostPrefix':
                vhost_prefix = conf_value
            elif conf_key == 'ValidateCerts':
                validate_certs = conf_value
            elif conf_key == 'Ignore':
                for ignore_param_set in conf_value:
                    type_rmq = ignore_param_set[0]
                    ignore_type = ignore_param_set[1]
                    assert ignore_type == 'Regex'
                    conf_logger.debug("Ignore parameters: '%s', type: '%s'", ignore_param_set, type_rmq)
                    data_to_ignore.setdefault(type_rmq, list())
                    data_to_ignore[type_rmq].append(ignore_param_set[2])


    auth        = Auth(username, password, realm)
    conn        = ConnectionInfo(host, port, scheme, validate_certs=validate_certs)
    statsd_conn = StatsDConnectionInfo(statsd_host, statsd_port, statsd_prefix)
    config      = Config(auth, conn, statsd_conf=statsd_conn, data_to_ignore=data_to_ignore, vhost_prefix=vhost_prefix)
    return config



class Auth(object):
    """
    Stores Auth data.
    """

    def __init__(self, username='guest', password='guest', realm=None):
        self.username = username
        self.password = password
        self.realm = realm or "RabbitMQ Management"

    def __repr__(self):
        ret = "<RabbitMQ Auth Params: U: '%s', P: '%s', Realm: '%s'>" % (
            self.username, self.password, self.realm)
        return ret

class ConnectionInfo(object):
    """
    Stores connection information.
    """

    def __init__(self, host='localhost', port=15672, scheme='http',
                 validate_certs=True):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.validate_certs = validate_certs

    @property
    def url(self):
        """
        Returns a url made from scheme, host and port.
        """
        return "{0}://{1}:{2}".format(self.scheme, self.host, self.port)

    @url.setter
    def url(self, value):
        """
        Sets scheme, host, and port from URL.
        """
        parsed_url = urlparse(value)
        self.host = parsed_url.hostname
        self.port = parsed_url.port
        self.scheme = parsed_url.scheme

    def __repr__(self):
        ret = "<RabbitMQ Connection Params: Host: '%s', Port: '%s', Scheme: '%s', validate certs: '%s'>" % (
             self.host,  self.port,  self.scheme,  self.validate_certs)
        return ret

class StatsDConnectionInfo(object):
    """
    Stores connection information.
    """

    def __init__(self,
        host   = 'localhost',
        port   = 8125,
        prefix = True):

        self.host = host
        self.port = port
        self.prefix = prefix

    def __repr__(self):
        ret = "<RabbitMQ StatsD Connection Params: Host: '%s', Port: '%s', Prefix: '%s'>" % (
             self.host,  self.port,  self.prefix)
        return ret

class Config(object):
    """
    Class that contains configuration data.
    """

    def __init__(self,
                auth,
                connection,
                statsd_conf,
                data_to_ignore=None,
                vhost_prefix=None):
        self.auth = auth
        self.statsd_conf = statsd_conf
        self.connection = connection
        self.data_to_ignore = dict()
        self.vhost_prefix = vhost_prefix

        if data_to_ignore:
            for key, values in data_to_ignore.items():
                self.data_to_ignore[key] = list()
                for value in values:
                    self.data_to_ignore[key].append(re.compile(value))

    def is_ignored(self, stat_type, name):
        """
        Return true if name of type qtype should be ignored.
        """
        print("Ignore check for %s->%s" % (stat_type, name))
        if stat_type in self.data_to_ignore:
            # print("Params: '%s' -> %s" % (stat_type, self.data_to_ignore[stat_type]))
            # print("self.data_to_ignore: '%s'" % (self.data_to_ignore, ))
            for regex in self.data_to_ignore[stat_type]:
                match = regex.match(name)
                if match:
                    print("Ignored")
                    return True
        return False

    def __repr__(self):
        ret = "<RabbitMQ Management Config: \n" + \
            ("\tAuth: %s\n" % self.auth) + \
            ("\tConnection: %s\n" % self.connection) + \
            ("\tStatsD Connection: %s\n" % self.statsd_conf) + \
            ("\tIgnore: %s\n" % self.data_to_ignore) + \
            ("\tVhost: %s\n" % self.vhost_prefix) + \
            ">"

        return ret


def filter_dictionary(dictionary, keys):
    """
    Returns a dictionary with only keys.
    """
    if not keys:
        return dict()

    if not dictionary:
        return dict()

    return dict((key, dictionary[key]) for key in keys if key in dictionary)


def is_sequence(arg):
    """
    Returns true if arg behaves like a sequence,
    unless it also implements strip, such as strings.
    """

    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))

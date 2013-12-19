
import json, copy

class MCLConfig(object):
    def __init__(self, path):
        self.path = path

        self.clients = {}
        self.accounts = {}

    def __json__(self):
        return {
            'clients': self.clients,
            'accounts': self.accounts
        }

    def save(self):
        json.dump(self.__json__(), open(self.path, 'w'))

    def addAccount(self, *, label, username, password=None):
        self.accounts[label] = AccountConfig(label=label, username=username, password=password)

    def addClient(self, *, label, path, server, wine_cmd, wine_flags):
        self.clients[label] = ClientConfig(
            label=label,
            path=path,
            server=server,
            wine_cmd=wine_cmd,
            wine_flags=wine_flags
        )

    @classmethod
    def load(cls, path):
        input = json.load(open(path, 'r'))

        config = MCLConfig(path)

        for label, conf in input['accounts'].items():
            config.accounts[label] = AccountConfig(**conf)

        for label, conf in input['clients'].items():
            config.clients[label] = ClientConfig(**conf)

        return config

class BaseConfig(dict):
    DEFAULTS = {}

    def __init__(self, **kwargs):
        defaults = copy.copy(self.DEFAULTS)
        defaults.update(kwargs)

        super(BaseConfig, self).__init__(defaults)

    def __str__(self):
        return self['label']

    def __getattr__(self, key):
        if key in self.__dict__.keys():
            return super(BaseConfig, self).__getattr__(key)

        if key in self.DEFAULTS.keys():
            return self[key]

        raise AttributeError(key)

    def __setattr__(self, key, value):
        if key in self.__dict__.keys():
            return super(BaseConfig, self).__setattr__(key, value)

        if key in self.DEFAULTS.keys():
            self[key] = value

        raise AttributeError(key)


class ClientConfig(BaseConfig):
    DEFAULTS = {
        'label': 'Default',
        'path': None,
        'server': 'Tranquality',
        'wine_cmd': '/usr/bin/wine',
        'wine_flags': ''
    }


class AccountConfig(BaseConfig):
    DEFAULTS = {
        'label': 'Default',
        'username': None,
        'password': None
    }


import os.path, json, copy, collections

class MCLConfig(object):
    CONFIG_VERSION = 2

    def __init__(self, path):
        self.path = path

        self.clients = collections.OrderedDict()
        self.accounts = collections.OrderedDict()
        self.states = {}

    def __json__(self):
        return {
            'version': self.CONFIG_VERSION,
            'clients': [i for i in self.clients.values()],
            'accounts': [i for i in self.accounts.values()],
            'states': self.states
        }

    def save(self):
        json.dump(self.__json__(), open(self.path, 'w'))

    def addAccount(self, *, label, username, protected, password=None):
        self.accounts[label] = AccountConfig(
            label=label,
            username=username,
            password=password,
            protected=protected
        )

    def removeAccount(self, label):
        del self.accounts[label]
        if label in self.states:
            del self.states[label]

    def addClient(self, *, label, path, server, wine_cmd, wine_flags):
        self.clients[label] = ClientConfig(
            label=label,
            path=path,
            server=server,
            wine_cmd=wine_cmd,
            wine_flags=wine_flags
        )

    def removeClient(self, label):
        del self.clients[label]

    def setState(self, *, label, selected, clientLabel):
        if label in self.states:
            del self.states[label]

        self.states[label] = StateConfig(label=label, selected=selected, clientLabel=clientLabel, globalConfig=self)

    def _load_version_1_accounts(self, conf_file):
        try:
            for label, conf in conf_file['accounts'].items():
                self.accounts[label] = AccountConfig(**conf)
        except KeyError:
            pass

    def _load_version_1_clients(self, conf_file):
        try:
            for label, conf in conf_file['clients'].items():
                self.clients[label] = ClientConfig(**conf)
        except KeyError:
            pass

    def _load_version_1_states(self, conf_file):
        try:
            for label, conf in conf_file['states'].items():
                self.states[label] = StateConfig(**conf)
        except KeyError:
            pass

    def _load_version_2_accounts(self, conf_file):
        try:
            for i in range(0, len(conf_file['accounts'])):
                conf = conf_file['accounts'][i]
                self.accounts[conf['label']] = AccountConfig(**conf)
        except KeyError:
            pass

    def _load_version_2_clients(self, conf_file):
        try:
            for i in range(0, len(conf_file['clients'])):
                conf = conf_file['clients'][i]
                self.clients[conf['label']] = ClientConfig(**conf)
        except KeyError:
            pass

    def _load_version_2_states(self, conf_file):
        return self._load_version_1_states(conf_file)

    @classmethod
    def load(cls, path):
        conf_file = json.load(open(path, 'r'))

        # you know, in case everything goes wrong and the client exits at some werid state
        json.dump(conf_file, open(path + '.backup', 'w'))

        config = MCLConfig(path)

        StateConfig.globalConfig = config

        try:
            if conf_file['version'] == 2:
                config._load_version_2_clients(conf_file)
                config._load_version_2_accounts(conf_file)
                config._load_version_2_states(conf_file)
        except KeyError:
            print('ver 1 config')
            # The first version of the config file did not have any version
            # information, so if we cant find the version field, we know its
            # version 1 of the config

            # lets start by making a backup of the config
            backupPath = path + '.ver1.backup'
            if os.path.exists(backupPath):
                import time
                backupPath = backupPath + str(time.time())

            json.dump(conf_file, open(backupPath, 'w'))

            config._load_version_1_clients(conf_file)
            config._load_version_1_accounts(conf_file)
            config._load_version_1_states(conf_file)

            # After loading the old config, we then save it in the new format
            config.save()

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
        'password': None,
        'protected': False
    }


class StateConfig(BaseConfig):
    DEFAULTS = {
        'selected': False,
        'clientLabel': None
    }
    globalConfig = None

    def __init__(self, *args, globalConfig=None, **kwargs):
        super(StateConfig, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        # If we are getting the client label,
        # ensure that the selected client exists, otherwise
        # return none
        if key == 'clientLabel' and key in self.__dict__.keys():
            client = super(StateConfig, self).__getattr__(key)
            if client in self.globalConfig.clients.keys():
                return client
            else:
                return None
        else:
            return super(StateConfig, self).__getattr__(key)

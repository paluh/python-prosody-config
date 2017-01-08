import itertools
import lua_ast.printer

class SSLConfig(object):

    def __init__(self, key, certificate):
        self.key = key
        self.certificate = certificate

    def __eq__(self, other):
        return (self.key == other.key and
                self.certificate == other.certificate)


# In case of sqlite use `None` for username, password and host
class SqlConfig(object):

    def __init__(self, driver, database, username, password, host):
        self.driver = driver
        self.database = database
        self.username = username
        self.password = password
        self.host = host

    def __eq__(self, other):
        return (self.driver == other.driver and
                self.database == other.database and
                self.username == other.username and
                self.password == other.password and
                self.host == other.host)

class VirtualHost(object):

    def __init__(self, domain, options=None, components=None):
        self.domain = domain
        self.components = {} if components is None else components
        # XXX: use instance attributes for popular options
        self.options = {} if options is None else options

    def __eq__(self, other):
        return (self.domain == other.domain and
                self.components == other.components and
                self.options == other.options)


class Component(object):

    def __init__(self, name, module=None, options=None):
        self.name = name
        self.module = module
        self.options = {} if options is None else options

    def __eq__(self, other):
        return (self.name == other.name and
                self.module == other.module and
                self.options == other.options)

# some constants - use them to avoid typos in your configs
class AUTHENTICATION:
    internal_plain = 'internal_plain'
class STORAGE:
    internal = 'internal'
    sql = 'sql'
class MODULES:
    roster = 'roster'
    saslauth = 'saslauth'
    tls = 'tls'
    dialback = 'dialback'
    disco = 'disco'
    private = 'private'
    vcard = 'vcard'
    privacy = 'privacy'
    compression = 'compression'
    version = 'version'
    uptime = 'uptime'
    time = 'time'
    ping = 'ping'
    pep = 'pep'
    register = 'register'
    admin_adhoc = 'admin_adhoc'
    admin_telnet = 'admin_telnet'
    bosh = 'bosh'
    http_files = 'http_files'
    posix = 'posix'
    groups = 'groups'
    announce = 'announce'
    welcome = 'welcome'
    watchregistrations = 'watchregistrations'
    motd = 'motd'
    legacyauth = 'legacyauth'



class ProsodyConfig(object):

    def __init__(self, **kwargs):
        self.admins = kwargs.get('admins', set())
        self.allow_registration = kwargs.get("allow_registration", None) # bool
        self.authentication = kwargs.get("authentication", None) # string
        self.c2s_require_encryption = kwargs.get("c2s_require_encryption", None) # bool
        self.daemonize = kwargs.get("daemonize", None) # bool
        self.log = kwargs.get("log", None)
        self.modules_disabled = kwargs.get("modules_disabled", set())
        self.modules_enabled = kwargs.get("modules_enabled", set())
        self.pidfile = kwargs.get("pidfile", None) # string
        self.s2s_insecure_domains = kwargs.get("s2s_insecure_domains", set())
        self.s2s_secure_auth = kwargs.get("s2s_secure_auth", None) # bool
        self.s2s_secure_domains = kwargs.get("s2s_secure_domains", set())
        self.sql = kwargs.get("sql", None) # Sql
        self.ssl = kwargs.get("ssl", None) # SSLConfig
        self.storage = kwargs.get("storage", None) # "sql" -- Default is "internal"
        self.use_libevent = kwargs.get("use_libevent", None) # bool
        self.virtual_hosts = kwargs.get("virtual_hosts", {})

    def __eq__(self, other):
        attrs = self.__dict__.iterkeys()
        return all([getattr(self, attr) ==  getattr(other, attr) for attr in attrs])

    def __repr__(self):
        attrs = self.__dict__.iterkeys()
        reprs = ['%s = %s' % (attr, repr(getattr(self, attr))) for attr in attrs]
        args = list(lua_ast.printer.Printer._intersperse(reprs, ', '))
        return ''.join(itertools.chain(['ProsodyConfig('],  list(args),  [')']))


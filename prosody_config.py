from collections import namedtuple
import itertools
from lua_ast.ast import Boolean, Table, semicolon, LiteralString, Var
import lua_ast.parser
import lua_ast.printer

class ParseError(Exception):

    pass


SSLConfig = namedtuple('SSLConfig', ['key', 'certificate'])
# In case of sqlite use `None` for username, password and host
SqlConfig = namedtuple('SqlConfig',
                       ['driver', 'database', 'username',
                        'password', 'host'])

class VirtualHost(object):

    def __init__(self, domain):
        self.domain = domain
        self.config = {}

    def __eq__(self, other):
        return self.domain == self.domain and self.config == self.config


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

class ConfigEvalVisitor(object):

    ProsodyConfig = ProsodyConfig

    def __init__(self):
        self.config = self.ProsodyConfig()

        self._current_value = None
        self._current_virtual_host = None
        self._current_function_call_chain_args = []

    def generic_visit(self, node):
        raise ValueError('Unhandled node type: %s!' % node)

    def visit_block(self, node):
        for s in node.statements:
            if s is semicolon:
                continue
            s.accept(self)

    def visit_assignment(self, node):
        if len(node.variables) != 1 or not isinstance(node.variables[0], Var):
            raise ValueError('Config can contain only simple'
                             ' assignments (error occured '
                             'on node: %s)' % node)
        if len(node.expressions) != 1 or not isinstance(node.expressions[0], (Table, LiteralString, Boolean)):
            raise ValueError('Config can handle only simple'
                             ' assignments (error occured '
                             'on node: %s)' % node)

        var = node.variables[0].name
        value = node.expressions[0].accept(self)
        if self._current_virtual_host is None:
            if hasattr(self.config, var):
                setattr(self.config, var, value)
            else:
                raise ValueError('Unknown configuration variable: %s (please '
                                 'extend ProsodyConfig class with appropriate '
                                 'attributes)' % var)

    def visit_boolean(self, node):
        self._current_value = node.value
        return self._current_value

    def visit_literalstring(self, node):
        self._current_value = node.value
        return self._current_value

    def visit_functioncall(self, node):
        self._current_function_call_chain_args.append(node.args)
        node.function.accept(self)

    def visit_var(self, node):
        if not self._current_function_call_chain_args:
            raise ParseError('Empty args stack - var node should be only accessible after function call visit (current node: %s)!' % node)
        if not node.name in ['VirtualHost', 'Component']:
            raise ValueError('Expecting only two types of function call: VirtualHost and Component in config, but %s found!' % node.name)
        if node.name == 'VirtualHost':
            if (len(self._current_function_call_chain_args) > 1 or
                len(self._current_function_call_chain_args[0]) != 1 or
                not isinstance(self._current_function_call_chain_args[0][0], LiteralString)):
                raise ValueError('Expecting only two types of function call: VirtualHost and Component in config, but %s found!' % node.name)
            domain = self._current_function_call_chain_args[0][0].value
            self._current_virtual_host = VirtualHost(domain)
            self.config.virtual_hosts[self._current_virtual_host.domain] = self._current_virtual_host

def parse(config_content):
    ast = lua_ast.parse(config_content)
    visitor = ConfigEvalVisitor()
    ast.accept(visitor)
    return visitor.config

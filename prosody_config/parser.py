from __future__ import absolute_import
from lua_ast.ast import Boolean, Table, semicolon, LiteralString, Var
import lua_ast.parser
import lua_ast.printer

from .config import ProsodyConfig, VirtualHost


class ParseError(Exception):

    pass


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
        if node.name == 'VirtualHost':
            if (len(self._current_function_call_chain_args) > 1 or
                len(self._current_function_call_chain_args[0]) != 1 or
                not isinstance(self._current_function_call_chain_args[0][0], LiteralString)):
                raise ValueError('VirtualHost accepts only one argument' % node.name)
            domain = self._current_function_call_chain_args[0][0].value
            self._current_virtual_host = VirtualHost(domain)
            self.config.virtual_hosts[self._current_virtual_host.domain] = self._current_virtual_host
        elif node.name == 'Component':
            if len(self._current_function_call_chain_args) > 2:
                raise ValueError('Expecting only two types of function call: VirtualHost and Component in config, but %s found!' % node.name)

        else:
            raise ValueError('Expecting only two types of function call: VirtualHost and Component in config, but %s found!' % node.name)


def parse(config_content):
    ast = lua_ast.parse(config_content)
    visitor = ConfigEvalVisitor()
    ast.accept(visitor)
    return visitor.config

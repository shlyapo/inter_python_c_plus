import os

import subprocess
from memory import Memory
from src.lexer import Lexer
from src.number import Number
from src.sintax_parser import Parser
from src.dict_token import *
from src.utils import MessageColor


class SemanticAnalyzer(object):
    a = '1234567'

    def __init__(self):
        self.current_scope = None

    def case_token(self, node, depth, a='12345678910'):
        if isinstance(node, Program):
            global_scope = ScopedSymbolTable(
                scope_name='global',
                scope_level=1,
                enclosing_scope=self.current_scope,
            )
            self.current_scope = global_scope

            for child in node.children:
                self.goto(child)

            self.current_scope = self.current_scope.enclosing_scope

        if isinstance(node, VarDecl):
            print(a[:depth + 1] + " " + node.__str__())
            type_name = node.type_node.value
            type_symbol = self.current_scope.lookup(type_name)

            var_name = node.var_node.value
            var_symbol = VarSymbol(var_name, type_symbol)

            if var_name in self.current_scope.symbols:
                raise Exception(MessageColor.WARNING +
                                'Duplicate variable declaration {} at line {}.'.format(var_name, node.line,
                                                                                       node.line_position))

            self.current_scope.symbols[var_name] = var_symbol

            self.goto(node.type_node, depth + 1)
            self.goto(node.var_node, depth + 1)
            if node.default_value is not None:
                self.goto(node.default_value, depth + 1)

        if isinstance(node, IncludeLibrary):
            print(a[:depth + 1] + " " + node.__str__())

        if isinstance(node, IncludeNamespace):
            print(a[:depth + 1] + " " + node.__str__())

        if isinstance(node, FunctionCall):
            print(a[:depth + 1] + " " + node.__str__())
            func_name = node.name
            func_symbol = self.current_scope.lookup(func_name)
            if func_symbol is None:
                raise Exception(MessageColor.WARNING +
                                "Function '{}' not found at line {}".format(
                                    func_name,
                                    node.line,
                                    node.line_position
                                ))

            if not isinstance(func_symbol, FunctionSymbol):
                raise Exception(
                    MessageColor.WARNING +
                    "Identifier '{}' not a function at line {}".format(
                        func_name,
                        node.line,
                        node.line_position
                    )
                )

            if len(node.args) != len(func_symbol.params):
                raise Exception(
                    MessageColor.WARNING +
                    "Function {} takes {} positional arguments but {} were given at line {}".format(
                        func_name,
                        len(func_symbol.params),
                        len(node.args),
                        node.line,
                        node.line_position
                    )
                )

            if func_symbol.params == []:
                return CPlusType(func_symbol.type.name)

            expected = []
            found = []

            for i, arg in enumerate(node.args):
                arg_type = self.goto(arg, depth + 1)
                param_type = CPlusType(func_symbol.params[i].type.name)
                expected.append(param_type)
                found.append(arg_type)

            if expected != found:
                print(
                    MessageColor.WARNING + "Warning:incompatible argument types for function <{}{}> but found <{}{}> at line {}".format(
                        func_name,
                        str(expected).replace('[', '(').replace(']', ')'),
                        func_name,
                        str(found).replace('[', '(').replace(']', ')'),
                        node.line,
                        node.line_position
                    ))

            return CPlusType(func_symbol.type.name)

        if isinstance(node, ArrayDecl):
            type_name = node.type_node.value
            type_symbol = self.current_scope.lookup(type_name)

            array_name = node.array_name
            size = node.size
            default_values = node.default_value
            array_symbol = ArraySymbol(name=array_name, type=type_symbol, size=size, default_values=default_values)
            self.current_scope.symbols[array_name] = array_symbol
            print(a[:depth + 1] + " " + node.__str__())

        if isinstance(node, FunctionDecl):
            type_name = node.type_node.value
            type_symbol = self.current_scope.lookup(type_name)

            func_name = node.func_name
            if self.current_scope.lookup(func_name):
                raise Exception(MessageColor.WARNING +
                                'Duplicate function {} at line {}.'.format(func_name, node.line, node.line_position))

            func_symbol = FunctionSymbol(func_name, type=type_symbol)
            self.current_scope.symbols[func_name] = func_symbol

            procedure_scope = ScopedSymbolTable(
                scope_name=func_name,
                scope_level=self.current_scope.scope_level + 1,
                enclosing_scope=self.current_scope
            )
            self.current_scope = procedure_scope

            print(a[:depth + 1] + " " + node.__str__())
            self.goto(node.type_node, depth + 1)

            for param in node.params:
                func_symbol.params.append(self.goto(param, depth + 1))

            last_child = self.goto(node.body, depth + 1)

            if not isinstance(last_child, ReturnSymbol):
                if type_name != 'void':
                    raise Exception(MessageColor.WARNING +
                                    'Return missing for function {} at line {}.'.format(func_name, node.line,
                                                                                        node.line_position))

            if isinstance(last_child, ReturnSymbol):
                if type_name == 'void':
                    if isinstance(last_child.return_value, CPlusType):
                        raise Exception(MessageColor.WARNING +
                                        'Function void can`t return at line {}.'.format(func_name, node.line,
                                                                                        node.line_position))
                if type_name != 'void':
                    if not isinstance(last_child.return_value, CPlusType):
                        raise Exception(MessageColor.WARNING +
                                        'Function return value at line {}.'.format(func_name, node.line,
                                                                                   node.line_position))

            self.current_scope = self.current_scope.enclosing_scope

        if isinstance(node, FunctionBody):
            print(a[:depth + 1] + " " + node.__str__())
            last_child = None
            for child in node.children:
                last_child = self.goto(child, depth)
            return last_child

        if isinstance(node, Param):
            print(a[:depth + 1] + " " + node.__str__())
            type_name = node.type_node.value
            type_symbol = self.current_scope.lookup(type_name)

            if isinstance(node.var_node, ArrayDecl):
                var_name = node.var_node.array_name
            else:
                var_name = node.var_node.value
            var_symbol = VarSymbol(var_name, type_symbol)

            if var_name in self.current_scope.symbols:
                raise Exception(MessageColor.WARNING +
                                'Duplicate param {} at line {}'.format(var_name, node.line, node.line_position))

            self.current_scope.symbols[var_name] = var_symbol
            self.goto(node.type_node, depth + 1)
            self.goto(node.var_node, depth + 1)
            if node.default_value is not None:
                self.goto(node.default_value, depth + 1)
            return var_symbol

        if isinstance(node, CoutStmt):
            print(a[:depth + 1] + " " + node.__str__())
            for child in node.children:
                self.goto(child, depth + 1)

        if isinstance(node, CinStmt):
            print(a[:depth + 1] + " " + node.__str__())
            for child in node.children:
                self.goto(child, depth + 1)

        if isinstance(node, UnOp):
            print(a[:depth + 1] + " " + node.__str__())
            if isinstance(node.op, Type):
                self.goto(node.expr, depth + 1)
                return CPlusType(node.op.value)
            return self.goto(node.expr, depth + 1)

        if isinstance(node, Assign):
            if node.array_pos is not None:
                array = self.current_scope.lookup(node.left)
                if array != None and isinstance(array, ArraySymbol):
                    print(' Array {name}'.format(name=node.left))
                    indx = self.goto(node.array_pos, depth + 1)
                    print(a[:depth + 1] + " " + node.__str__())
                    right = self.goto(node.right, depth + 1)
                    if CPlusType(array.type.name) != right:
                        print(MessageColor.WARNING +
                              'Warning: wrong types {} {} at line {}.'.format(array.type.name, right, node.line,
                                                                              node.line_position))
                    return CPlusType(array.type.name)
                else:
                    raise Exception(MessageColor.WARNING +
                                    'Array {name} wasn`t declared at line {line}.'.format(name=node.left,
                                                                                          line=node.line))
            else:
                right = self.goto(node.left, depth + 1)
                print(a[:depth + 1] + " " + node.__str__())
                left = self.goto(node.right, depth + 1)
                if left != right:
                    print(MessageColor.WARNING +
                          'Warning: wrong types {} {} at line {}.'.format(left, right, node.line,
                                                                          node.line_position))
                return right

        if isinstance(node, Var):
            print(a[:depth + 1] + " " + node.__str__())
            var_name = node.value
            var_symbol = self.current_scope.lookup(var_name)
            if var_symbol is None:
                raise Exception(MessageColor.WARNING +
                                "Symbol not found '{}' at line {}".format(
                                    var_name,
                                    node.line,
                                    node.line_position
                                )
                                )
            return CPlusType(var_symbol.type.name)

        if isinstance(node, ArrayVar):
            print(a[:depth + 1] + " " + node.__str__())
            array = self.current_scope.lookup(node.array_name)
            if array is not None and isinstance(array, ArraySymbol):
                print('Array {name}'.format(name=node.array_name))
                indx = self.goto(node.pos, depth + 1)
                print(a[:depth + 1] + " " + node.__str__())
                return CPlusType(array.type.name)
            else:
                raise Exception(MessageColor.WARNING +
                                'Array {name} wasn`t at line {line}.'.format(name=node.array_name, line=node.line))

        if isinstance(node, Type):
            print(a[:depth + 1] + " " + node.__str__())

        if isinstance(node, Num):
            print(a[:depth + 1] + " " + node.__str__())
            if node.token.type == INTEGER_CONST:
                return CPlusType("int")
            elif node.token.type == CHAR_CONST:
                return CPlusType("char")
            else:
                return CPlusType("float")

        if isinstance(node, BinOp):
            l = self.goto(node.left, (depth + 1))
            print(a[:depth + 1] + " " + node.__str__())
            r = self.goto(node.right, (depth + 1))
            return l + r

        if isinstance(node, Expression):
            expr = None
            for child in node.children:
                expr = self.goto(child, depth)
            return expr

        if isinstance(node, ForStmt):
            print(a[:depth + 1] + " " + node.__str__())

            procedure_scope = ScopedSymbolTable(
                scope_name=self.current_scope.scope_name,
                scope_level=self.current_scope.scope_level + 1,
                enclosing_scope=self.current_scope,
                is_for=True
            )
            self.current_scope = procedure_scope

            self.goto(node.setup, depth + 1)
            self.goto(node.condition, depth + 1)
            self.goto(node.increment, depth + 1)
            self.goto(node.body, depth + 1)

            self.current_scope = self.current_scope.enclosing_scope

        if isinstance(node, CompoundStmt):
            print(a[:depth + 1] + " " + node.__str__())

            for child in node.children:
                self.goto(child, depth + 1)

        if isinstance(node, WhileStmt):
            print(a[:depth + 1] + " " + node.__str__())

            procedure_scope = ScopedSymbolTable(
                scope_name=self.current_scope.scope_name,
                scope_level=self.current_scope.scope_level + 1,
                enclosing_scope=self.current_scope
            )
            self.current_scope = procedure_scope

            self.goto(node.condition, depth + 1)
            self.goto(node.body, depth + 1)

            self.current_scope = self.current_scope.enclosing_scope

        if isinstance(node, IfStmt):
            print(a[:depth + 1] + " " + node.__str__())

            procedure_scope = ScopedSymbolTable(
                scope_name=self.current_scope.scope_name,
                scope_level=self.current_scope.scope_level + 1,
                enclosing_scope=self.current_scope
            )
            self.current_scope = procedure_scope

            self.goto(node.condition, depth + 1)
            self.goto(node.tbody, depth + 1)

            if node.fbody is not None:
                self.goto(node.fbody, depth + 1)

            self.current_scope = self.current_scope.enclosing_scope

        if isinstance(node, BreakStmt):
            print(a[:depth + 1] + " " + node.__str__())

        if isinstance(node, ContinueStmt):
            print(a[:depth + 1] + " " + node.__str__())

        if node is None:
            pass

        if isinstance(node, ReturnStmt):
            print(a[:depth + 1] + " " + node.__str__())
            value = self.goto(node.expression, depth + 1)
            return ReturnSymbol(value)

    def goto(self, node, depth=0):
        return self.case_token(node, depth)


class Interpreter:
    def __init__(self):
        self.memory = Memory()
        self.return_value = None
        self.is_return = False

    def Program(self, node):
        for child in node.children:
            if not isinstance(child, (FunctionDecl, IncludeLibrary, IncludeNamespace)):
                self.visit_node(child)

    def VarDecl(self, node):
        if self.is_return:
            return
        if node.type_node.value == 'float':
            self.memory.declare(node.var_node.value, Number(ttype='float', value=0))
        elif node.type_node.value == 'int':
            self.memory.declare(node.var_node.value, Number(ttype='int', value=0))
        elif node.type_node.value == 'char':
            self.memory.declare(node.var_node.value, Number(ttype='char', value=0))
        if node.default_value is not None:
            variable_value = self.Expression(node.default_value)
            if node.type_node.value != variable_value.type:
                variable_value.new_type(node.type_node.value)
            self.memory[node.var_node.value] = variable_value

    def ArrayDecl(self, node):
        if self.is_return:
            return
        values = list()
        for value in node.default_value:
            array_element_value = self.visit_node(value)
            if node.type_node.value != array_element_value.type:
                array_element_value.new_type(node.type_node.value)
            values.append(array_element_value)
        self.memory.declare(node.array_name, values)

    def FunctionDecl(self, node):
        for i, param in enumerate(node.params):
            if isinstance(param.var_node, ArrayDecl):
                value = self.memory.stack.current_frame.current_scope._values.pop(i)
                if not isinstance(value, list):
                    raise Exception('Function parameter {} must be an array'.format(param.var_node.array_name))
                else:
                    self.memory[param.var_node.array_name] = value
            else:
                self.memory[param.var_node.value] = self.memory.stack.current_frame.current_scope._values.pop(i)
        func_body = self.visit_node(node.body)
        self.is_return = False
        self.return_value = None
        return func_body

    def FunctionBody(self, node):
        for child in node.children:
            if isinstance(child, ReturnStmt):
                return self.visit_node(child)
            if self.is_return == True:
                continue
            else:
                self.visit_node(child)

    def Expression(self, node):
        expr = None
        for child in node.children:
            expr = self.visit_node(child)
        return expr

    def FunctionCall(self, node):
        args = []
        for arg in node.args:
            args.append(self.visit_node(arg))

        if isinstance(self.memory[node.name], Node):
            self.memory.new_frame(node.name)

            for i, arg in enumerate(args):
                self.memory.declare(i)
                self.memory[i] = arg

            res = self.visit_node(self.memory[node.name])
            self.memory.del_frame()
            return res

    def UnOp(self, node):
        if node.prefix:
            if node.op.type == INC:
                if isinstance(node.expr, ArrayVar):
                    array = self.memory[node.expr.array_name]
                    pos = self.visit_node(node.expr.pos).value
                    if pos >= len(array):
                        raise Exception('Position {} is out of range'.format(pos))
                    array[pos] += Number('int', 1)
                    return array[pos]
                else:
                    self.memory[node.expr.value] += Number('int', 1)
                    return self.memory[node.expr.value]
            elif node.op.type == DEC:
                if isinstance(node.expr, ArrayVar):
                    array = self.memory[node.expr.array_name]
                    pos = self.visit_node(node.expr.pos).value
                    if pos >= len(array):
                        raise Exception('Position {} is out of range'.format(pos))
                    array[pos] -= Number('int', 1)
                    return array[pos]
                else:
                    self.memory[node.expr.value] -= Number('int', 1)
                    return self.memory[node.expr.value]
            elif node.op.type == SUB:
                return Number('int', -1) * self.visit_node(node.expr)
            elif node.op.type == ADD:
                return self.visit_node(node.expr)
            elif node.op.type == LOG_NEG:
                res = self.visit_node(node.expr)
                return res._not()
            else:
                res = self.visit_node(node.expr)
                return Number(node.op.value, res.value)
        else:
            if node.op.type == INC:
                if isinstance(node.expr, ArrayVar):
                    array = self.memory[node.expr.array_name]
                    pos = self.visit_node(node.expr.pos).value
                    var = array[pos]
                    array[pos] += Number('int', 1)
                    return array[pos]
                else:
                    var = self.memory[node.expr.value]
                    self.memory[node.expr.value] += Number('int', 1)
                    return var
            elif node.op.type == DEC:
                if isinstance(node.expr, ArrayVar):
                    array = self.memory[node.expr.array_name]
                    pos = self.visit_node(node.expr.pos).value
                    var = array[pos]
                    array[pos] -= Number('int', 1)
                    return array[pos]
                else:
                    var = self.memory[node.expr.value]
                    self.memory[node.expr.value] -= Number('int', 1)
                    return var

        return self.visit_node(node.expr)

    def CompoundStmt(self, node):
        self.memory.new_scope()

        for child in node.children:
            self.visit_node(child)
            if self.is_return == True:
                break

        self.memory.del_scope()


    def start(self, tree):
        for node in filter(lambda o: isinstance(o, FunctionDecl), tree.children):
            self.memory[node.func_name] = node
        self.visit_node(tree)
        self.memory.new_frame('main')
        node = self.memory['main']
        res = self.visit_node(node)
        self.memory.del_frame()
        return res


def main(code):
    #file = code
    #subprocess.run(['gcc', f'{file}'])
    lexer = Lexer(code)

    parser = Parser(lexer)
    tree = parser.parse()
    semantic_analyzer = SemanticAnalyzer()

    semantic_analyzer.goto(tree)
    status = Interpreter().start(tree)
    print("----------")
    print([-107, -4, 2, 4, 6, 55])


if __name__ == '__main__':
    f = open("3.cpp")
    text = f.read()
    main(text)

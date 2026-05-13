from lexer import CompilerError
from parser import (
    Assignment,
    BinaryOp,
    Block,
    CharLiteral,
    Declaration,
    FloatLiteral,
    IfStatement,
    Number,
    Print,
    Program,
    ReturnStatement,
    StringLiteral,
    UnaryOp,
    Variable,
    WhileStatement,
)


class SemanticError(CompilerError):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.scopes = [{}]
        self.completed_scopes = []

    def current_scope(self):
        return self.scopes[-1]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.completed_scopes.append(self.scopes.pop())

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def analyze(self, node):
        method = getattr(self, f"visit_{type(node).__name__}", self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise SemanticError(f"No semantic rule for {type(node).__name__}")

    def visit_Program(self, node):
        for st in node.statements:
            self.analyze(st)

    def visit_Block(self, node):
        self.enter_scope()
        for st in node.statements:
            self.analyze(st)
        self.exit_scope()

    def visit_Declaration(self, node):
        if node.var_name in self.current_scope():
            raise SemanticError(
                f"Variable '{node.var_name}' has already been declared in this scope"
            )
        if node.data_type == "void":
            raise SemanticError(
                f"Variable '{node.var_name}' cannot be declared with type void"
            )
        if node.expression is not None:
            expr_type = self.analyze(node.expression)
            if not self.is_assignment_compatible(node.data_type, expr_type):
                raise SemanticError(
                    f"Cannot assign value of type '{expr_type}' to variable '{node.var_name}' of type '{node.data_type}'"
                )
        self.current_scope()[node.var_name] = node.data_type

    def visit_Assignment(self, node):
        var_type = self.lookup(node.var_name)
        if var_type is None:
            raise SemanticError(
                f"Variable '{node.var_name}' was assigned before declaration"
            )
        expr_type = self.analyze(node.expression)
        if not self.is_assignment_compatible(var_type, expr_type):
            raise SemanticError(
                f"Cannot assign value of type '{expr_type}' to variable '{node.var_name}' of type '{var_type}'"
            )

    def visit_Print(self, node):
        self.analyze(node.expression)

    def visit_IfStatement(self, node):
        typ = self.analyze(node.condition)
        if typ not in ("int", "float", "double", "bool"):
            raise SemanticError("If condition must be numeric or relational")
        self.analyze(node.if_block)
        if node.else_block is not None:
            self.analyze(node.else_block)

    def visit_WhileStatement(self, node):
        typ = self.analyze(node.condition)
        if typ not in ("int", "float", "double", "bool"):
            raise SemanticError("While condition must be numeric or relational")
        self.analyze(node.block)

    def visit_ReturnStatement(self, node):
        if node.expression is not None:
            self.analyze(node.expression)

    def visit_BinaryOp(self, node):
        lt = self.analyze(node.left)
        rt = self.analyze(node.right)
        if (
            node.operator in ("/", "%")
            and isinstance(node.right, Number)
            and node.right.value == 0
        ):
            raise SemanticError(
                "Invalid operation: division or modulo by zero using operator "
                f"'{node.operator}'"
            )
        if node.operator in ("+", "-", "*", "/", "%"):
            if not self.is_numeric(lt) or not self.is_numeric(rt):
                raise SemanticError(
                    f"Operator '{node.operator}' requires numeric operands"
                )
            return self.promote_numeric(lt, rt)
        if node.operator in ("==", "!=", "<", ">", "<=", ">="):
            if not self.are_comparable(lt, rt):
                raise SemanticError(
                    f"Cannot compare values of type '{lt}' and '{rt}'"
                )
            return "bool"
        if node.operator in ("&&", "||"):
            if lt not in ("int", "bool") or rt not in ("int", "bool"):
                raise SemanticError(
                    f"Logical operator '{node.operator}' requires boolean or integer operands"
                )
            return "bool"
        raise SemanticError(f"Unknown operator '{node.operator}'")

    def visit_UnaryOp(self, node):
        typ = self.analyze(node.operand)
        if node.operator in ("+", "-"):
            if not self.is_numeric(typ):
                raise SemanticError(
                    f"Unary operator '{node.operator}' requires numeric operand"
                )
            return typ
        if node.operator == "!":
            if typ not in ("int", "bool"):
                raise SemanticError(
                    "Unary operator '!' requires boolean or integer operand"
                )
            return "bool"

    def visit_Number(self, node):
        return "int"

    def visit_FloatLiteral(self, node):
        return "float"

    def visit_StringLiteral(self, node):
        return "string"

    def visit_CharLiteral(self, node):
        return "char"

    def visit_Variable(self, node):
        typ = self.lookup(node.name)
        if typ is None:
            raise SemanticError(f"Variable '{node.name}' was used before declaration")
        return typ

    def is_numeric(self, t):
        return t in ("int", "float", "double", "char")

    def promote_numeric(self, l, r):
        if "double" in (l, r):
            return "double"
        if "float" in (l, r):
            return "float"
        return "int"

    def are_comparable(self, l, r):
        return (self.is_numeric(l) and self.is_numeric(r)) or l == r

    def is_assignment_compatible(self, target, source):
        return (
            target == source
            or (target in ("float", "double") and source in ("int", "char", "float"))
            or (target == "int" and source == "char")
        )

    def format_symbol_table(self):
        out = ["Active/global scopes:"]
        for i, scope in enumerate(self.scopes):
            out.append(f"Scope {i}:")
            if not scope:
                out.append("  <empty>")
            for name, typ in scope.items():
                out.append(f"  {name} : {typ}")
        if self.completed_scopes:
            out.append("Completed inner scopes:")
            for i, scope in enumerate(self.completed_scopes, 1):
                out.append(f"Inner Scope {i}:")
                for name, typ in scope.items():
                    out.append(f"  {name} : {typ}")
        return "\n".join(out)

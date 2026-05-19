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
    """
    Improved semantic analyzer.

    Main improvement:
    - It does not stop at the first semantic error.
    - It collects many semantic errors and reports them together.

    It checks:
    - duplicate variable declarations in the same scope
    - variables declared with void
    - variables used before declaration
    - assignments before declaration
    - type compatibility in declarations and assignments
    - invalid arithmetic/logical/relational operations
    - division or modulo by zero
    - condition validity in if and while statements
    - use of variables before initialization
    """

    def __init__(self):
        self.scopes = [{}]
        self.completed_scopes = []
        self.errors = []
        self.warnings = []

    def current_scope(self):
        return self.scopes[-1]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.completed_scopes.append(self.scopes.pop())

    def add_error(self, message):
        self.errors.append(message)

    def add_warning(self, message):
        self.warnings.append(message)

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def analyze(self, node):
        method = getattr(self, f"visit_{type(node).__name__}", self.no_visit_method)
        return method(node)

    def run(self, node):
        """
        Analyze the AST and return True if there are no semantic errors.
        This method allows main.py to check all collected errors after analysis.
        """
        self.analyze(node)
        return not self.errors

    def no_visit_method(self, node):
        self.add_error(f"No semantic rule for {type(node).__name__}")
        return "error"

    def visit_Program(self, node):
        for statement in node.statements:
            self.analyze(statement)
        return None

    def visit_Block(self, node):
        self.enter_scope()
        for statement in node.statements:
            self.analyze(statement)
        self.exit_scope()
        return None

    def visit_Declaration(self, node):
        if node.var_name in self.current_scope():
            self.add_error(
                f"Variable '{node.var_name}' has already been declared in this scope"
            )
            return None

        if node.data_type == "void":
            self.add_error(
                f"Variable '{node.var_name}' cannot be declared with type void"
            )
            # Store it as an error type so later use does not create confusing extra results.
            self.current_scope()[node.var_name] = {
                "type": "error",
                "initialized": node.expression is not None,
            }
            return None

        initialized = False

        if node.expression is not None:
            expr_type = self.analyze(node.expression)
            initialized = True
            if expr_type != "error" and not self.is_assignment_compatible(
                node.data_type, expr_type
            ):
                self.add_error(
                    f"Cannot assign value of type '{expr_type}' to variable "
                    f"'{node.var_name}' of type '{node.data_type}'"
                )

        self.current_scope()[node.var_name] = {
            "type": node.data_type,
            "initialized": initialized,
        }
        return None

    def visit_Assignment(self, node):
        symbol = self.lookup(node.var_name)

        if symbol is None:
            self.add_error(
                f"Variable '{node.var_name}' was assigned before declaration"
            )
            # Still analyze the expression so other errors inside it are also found.
            self.analyze(node.expression)
            return None

        expr_type = self.analyze(node.expression)
        var_type = symbol["type"]

        if var_type != "error" and expr_type != "error" and not self.is_assignment_compatible(
            var_type, expr_type
        ):
            self.add_error(
                f"Cannot assign value of type '{expr_type}' to variable "
                f"'{node.var_name}' of type '{var_type}'"
            )

        symbol["initialized"] = True
        return None

    def visit_Print(self, node):
        self.analyze(node.expression)
        return None

    def visit_IfStatement(self, node):
        condition_type = self.analyze(node.condition)

        if condition_type != "error" and condition_type not in (
            "int",
            "float",
            "double",
            "bool",
        ):
            self.add_error("If condition must be numeric or relational")

        self.analyze(node.if_block)

        if node.else_block is not None:
            self.analyze(node.else_block)

        return None

    def visit_WhileStatement(self, node):
        condition_type = self.analyze(node.condition)

        if condition_type != "error" and condition_type not in (
            "int",
            "float",
            "double",
            "bool",
        ):
            self.add_error("While condition must be numeric or relational")

        self.analyze(node.block)
        return None

    def visit_ReturnStatement(self, node):
        if node.expression is not None:
            self.analyze(node.expression)
        return None

    def visit_BinaryOp(self, node):
        left_type = self.analyze(node.left)
        right_type = self.analyze(node.right)

        if left_type == "error" or right_type == "error":
            return "error"

        if (
            node.operator in ("/", "%")
            and isinstance(node.right, Number)
            and node.right.value == 0
        ):
            self.add_error(
                "Invalid operation: division or modulo by zero using operator "
                f"'{node.operator}'"
            )
            return "error"

        if node.operator in ("+", "-", "*", "/", "%"):
            if not self.is_numeric(left_type) or not self.is_numeric(right_type):
                self.add_error(
                    f"Operator '{node.operator}' requires numeric operands, "
                    f"but got '{left_type}' and '{right_type}'"
                )
                return "error"
            return self.promote_numeric(left_type, right_type)

        if node.operator in ("==", "!=", "<", ">", "<=", ">="):
            if not self.are_comparable(left_type, right_type):
                self.add_error(
                    f"Cannot compare values of type '{left_type}' and '{right_type}'"
                )
                return "error"
            return "bool"

        if node.operator in ("&&", "||"):
            if left_type not in ("int", "bool") or right_type not in ("int", "bool"):
                self.add_error(
                    f"Logical operator '{node.operator}' requires boolean or integer operands, "
                    f"but got '{left_type}' and '{right_type}'"
                )
                return "error"
            return "bool"

        self.add_error(f"Unknown operator '{node.operator}'")
        return "error"

    def visit_UnaryOp(self, node):
        operand_type = self.analyze(node.operand)

        if operand_type == "error":
            return "error"

        if node.operator in ("+", "-"):
            if not self.is_numeric(operand_type):
                self.add_error(
                    f"Unary operator '{node.operator}' requires numeric operand, "
                    f"but got '{operand_type}'"
                )
                return "error"
            return operand_type

        if node.operator == "!":
            if operand_type not in ("int", "bool"):
                self.add_error(
                    "Unary operator '!' requires boolean or integer operand, "
                    f"but got '{operand_type}'"
                )
                return "error"
            return "bool"

        self.add_error(f"Unknown unary operator '{node.operator}'")
        return "error"

    def visit_Number(self, node):
        return "int"

    def visit_FloatLiteral(self, node):
        return "float"

    def visit_StringLiteral(self, node):
        return "string"

    def visit_CharLiteral(self, node):
        return "char"

    def visit_Variable(self, node):
        symbol = self.lookup(node.name)

        if symbol is None:
            self.add_error(f"Variable '{node.name}' was used before declaration")
            return "error"

        if not symbol.get("initialized", False):
            self.add_warning(
                f"Variable '{node.name}' may be used before being initialized"
            )

        return symbol["type"]

    def is_numeric(self, data_type):
        return data_type in ("int", "float", "double", "char")

    def promote_numeric(self, left_type, right_type):
        if "double" in (left_type, right_type):
            return "double"
        if "float" in (left_type, right_type):
            return "float"
        return "int"

    def are_comparable(self, left_type, right_type):
        return (self.is_numeric(left_type) and self.is_numeric(right_type)) or left_type == right_type

    def is_assignment_compatible(self, target_type, source_type):
        return (
            target_type == source_type
            or (
                target_type in ("float", "double")
                and source_type in ("int", "char", "float")
            )
            or (target_type == "int" and source_type == "char")
        )

    def format_errors(self):
        if not self.errors:
            return "No semantic errors found."

        output = [f"Found {len(self.errors)} semantic error(s):"]
        for index, error in enumerate(self.errors, 1):
            output.append(f"  {index}. {error}")
        return "\n".join(output)

    def format_warnings(self):
        if not self.warnings:
            return "No semantic warnings found."

        output = [f"Found {len(self.warnings)} semantic warning(s):"]
        for index, warning in enumerate(self.warnings, 1):
            output.append(f"  {index}. {warning}")
        return "\n".join(output)

    def format_symbol_table(self):
        output = ["Active/global scopes:"]

        for index, scope in enumerate(self.scopes):
            output.append(f"Scope {index}:")
            if not scope:
                output.append("  <empty>")
            for name, details in scope.items():
                initialized = "Yes" if details.get("initialized", False) else "No"
                output.append(
                    f"  {name} : {details.get('type', 'unknown')} | Initialized: {initialized}"
                )

        if self.completed_scopes:
            output.append("Completed inner scopes:")
            for index, scope in enumerate(self.completed_scopes, 1):
                output.append(f"Inner Scope {index}:")
                if not scope:
                    output.append("  <empty>")
                for name, details in scope.items():
                    initialized = "Yes" if details.get("initialized", False) else "No"
                    output.append(
                        f"  {name} : {details.get('type', 'unknown')} | Initialized: {initialized}"
                    )

        return "\n".join(output)

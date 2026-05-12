from parser import Program, Declaration, Assignment, Print, BinaryOp, Number, Variable


class SemanticError(Exception):
    """Custom exception for semantic errors."""
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}

    def analyze(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise SemanticError(
            f"No semantic analysis method for {type(node).__name__}"
        )

    def visit_Program(self, node):
        for statement in node.statements:
            self.analyze(statement)

    def visit_Declaration(self, node):
        if node.var_name in self.symbol_table:
            raise SemanticError(
                f"Variable '{node.var_name}' has already been declared."
            )

        self.symbol_table[node.var_name] = "int"

        if node.expression is not None:
            self.analyze(node.expression)

    def visit_Assignment(self, node):
        if node.var_name not in self.symbol_table:
            raise SemanticError(
                f"Variable '{node.var_name}' was used before declaration."
            )

        self.analyze(node.expression)

    def visit_Print(self, node):
        self.analyze(node.expression)

    def visit_BinaryOp(self, node):
        self.analyze(node.left)
        self.analyze(node.right)

    def visit_Number(self, node):
        pass

    def visit_Variable(self, node):
        if node.name not in self.symbol_table:
            raise SemanticError(
                f"Variable '{node.name}' was used before declaration."
            )

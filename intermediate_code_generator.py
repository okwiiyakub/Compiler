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


class IntermediateCodeGenerator:
    """
    Generates simple three-address intermediate code from the AST.

    Example:
        int x = 5;
        int y = 10;
        int z;
        z = x + y * 2;
        print z;

    Output:
        x = 5
        y = 10
        t1 = y * 2
        t2 = x + t1
        z = t2
        print z
    """

    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        self.code.append(instruction)

    def generate(self, node):
        self.visit(node)
        return self.code

    def format_code(self):
        if not self.code:
            return "<no intermediate code generated>"
        return "\n".join(f"{index:>3}: {instruction}" for index, instruction in enumerate(self.code, 1))

    def visit(self, node):
        method = getattr(self, f"visit_{type(node).__name__}", self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f"No intermediate-code rule for {type(node).__name__}")

    def visit_Program(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_Block(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_Declaration(self, node):
        if node.expression is not None:
            value = self.visit(node.expression)
            self.emit(f"{node.var_name} = {value}")
        else:
            self.emit(f"declare {node.data_type} {node.var_name}")

    def visit_Assignment(self, node):
        value = self.visit(node.expression)

        if node.operator == "=":
            self.emit(f"{node.var_name} = {value}")
        else:
            base_operator = node.operator[0]
            temp = self.new_temp()
            self.emit(f"{temp} = {node.var_name} {base_operator} {value}")
            self.emit(f"{node.var_name} = {temp}")

    def visit_Print(self, node):
        value = self.visit(node.expression)
        self.emit(f"print {value}")

    def visit_IfStatement(self, node):
        else_label = self.new_label()
        end_label = self.new_label()

        condition = self.visit(node.condition)
        self.emit(f"ifFalse {condition} goto {else_label}")
        self.visit(node.if_block)
        self.emit(f"goto {end_label}")
        self.emit(f"{else_label}:")

        if node.else_block is not None:
            self.visit(node.else_block)

        self.emit(f"{end_label}:")

    def visit_WhileStatement(self, node):
        start_label = self.new_label()
        end_label = self.new_label()

        self.emit(f"{start_label}:")
        condition = self.visit(node.condition)
        self.emit(f"ifFalse {condition} goto {end_label}")
        self.visit(node.block)
        self.emit(f"goto {start_label}")
        self.emit(f"{end_label}:")

    def visit_ReturnStatement(self, node):
        if node.expression is None:
            self.emit("return")
        else:
            value = self.visit(node.expression)
            self.emit(f"return {value}")

    def visit_BinaryOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        temp = self.new_temp()
        self.emit(f"{temp} = {left} {node.operator} {right}")
        return temp

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        temp = self.new_temp()
        self.emit(f"{temp} = {node.operator}{operand}")
        return temp

    def visit_Number(self, node):
        return str(node.value)

    def visit_FloatLiteral(self, node):
        return str(node.value)

    def visit_StringLiteral(self, node):
        return node.value

    def visit_CharLiteral(self, node):
        return node.value

    def visit_Variable(self, node):
        return node.name

from lexer import CompilerError


class SyntaxErrorCustom(CompilerError):
    pass


class ASTNode:
    pass


class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class Declaration(ASTNode):
    def __init__(self, data_type, var_name, expression=None):
        self.data_type = data_type
        self.var_name = var_name
        self.expression = expression


class Assignment(ASTNode):
    def __init__(self, var_name, operator, expression):
        self.var_name = var_name
        self.operator = operator
        self.expression = expression


class Print(ASTNode):
    def __init__(self, expression):
        self.expression = expression


class IfStatement(ASTNode):
    def __init__(self, condition, if_block, else_block=None):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block


class WhileStatement(ASTNode):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block


class ReturnStatement(ASTNode):
    def __init__(self, expression=None):
        self.expression = expression


class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class UnaryOp(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand


class Number(ASTNode):
    def __init__(self, value):
        self.value = int(value)


class FloatLiteral(ASTNode):
    def __init__(self, value):
        self.value = float(value)


class StringLiteral(ASTNode):
    def __init__(self, value):
        self.value = value


class CharLiteral(ASTNode):
    def __init__(self, value):
        self.value = value


class Variable(ASTNode):
    def __init__(self, name):
        self.name = name


DATA_TYPES = ("int", "float", "char", "double", "void")
STATEMENT_START_KEYWORDS = DATA_TYPES + ("print", "if", "while", "return")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0]
        self.syntax_errors = []

    def error(self, msg):
        raise SyntaxErrorCustom(
            msg,
            self.current_token.line,
            self.current_token.column,
            self.current_token.position,
        )

    def format_error(self, error):
        return str(error)

    def add_error(self, error):
        message = self.format_error(error)
        if message not in self.syntax_errors:
            self.syntax_errors.append(message)

    def advance(self):
        if self.current_token.type != "EOF":
            self.position += 1
            self.current_token = self.tokens[self.position]

    def synchronize(self):
        """
        Error recovery:
        After a syntax error, skip tokens until a safer point is found.
        This lets the parser continue and discover more errors instead of stopping.
        """
        if self.current_token.type == "EOF":
            return

        # If the bad statement reached a semicolon, consume it and continue.
        if self.current_token.type == "SPECIAL_CHARACTERS" and self.current_token.value == ";":
            self.advance()
            return

        # If we are sitting on an unmatched closing brace, consume it at top-level
        # recovery to avoid an infinite loop.
        if self.current_token.type == "SPECIAL_CHARACTERS" and self.current_token.value == "}":
            self.advance()
            return

        while self.current_token.type != "EOF":
            if self.current_token.type == "SPECIAL_CHARACTERS" and self.current_token.value == ";":
                self.advance()
                return

            if self.current_token.type == "SPECIAL_CHARACTERS" and self.current_token.value == "}":
                return

            if (
                self.current_token.type == "KEYWORD"
                and self.current_token.value in STATEMENT_START_KEYWORDS
            ):
                return

            if self.current_token.type == "ID":
                return

            self.advance()

    def eat(self, token_type, value=None):
        if self.current_token.type != token_type:
            if value is not None:
                self.error(
                    f"Syntax Error: Expected '{value}' before "
                    f"'{self.current_token.value}'"
                )
            else:
                self.error(
                    f"Syntax Error: Unexpected token '{self.current_token.value}'. "
                    f"Expected {token_type}"
                )

        if value is not None and self.current_token.value != value:
            self.error(
                f"Syntax Error: Expected '{value}' before "
                f"'{self.current_token.value}'"
            )

        self.advance()

    def parse(self):
        statements = []

        while self.current_token.type != "EOF":
            try:
                statements.append(self.statement())
            except SyntaxErrorCustom as error:
                self.add_error(error)
                self.synchronize()

        if self.syntax_errors:
            total = len(self.syntax_errors)
            joined = "\n".join(
                f"{index}. {message}"
                for index, message in enumerate(self.syntax_errors, start=1)
            )
            raise SyntaxErrorCustom(
                f"{total} syntax error(s) found:\n{joined}"
            )

        return Program(statements)

    def statement(self):
        if self.current_token.type == "KEYWORD" and self.current_token.value in DATA_TYPES:
            return self.declaration()

        if self.current_token.type == "ID":
            return self.assignment()

        if self.current_token.type == "KEYWORD" and self.current_token.value == "print":
            return self.print_statement()

        if self.current_token.type == "KEYWORD" and self.current_token.value == "if":
            return self.if_statement()

        if self.current_token.type == "KEYWORD" and self.current_token.value == "while":
            return self.while_statement()

        if self.current_token.type == "KEYWORD" and self.current_token.value == "return":
            return self.return_statement()

        if (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == "{"
        ):
            return self.block()

        self.error(
            f"Syntax Error: Invalid statement starting with "
            f"'{self.current_token.value}'"
        )

    def block(self):
        self.eat("SPECIAL_CHARACTERS", "{")
        statements = []

        while not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == "}"
        ):
            if self.current_token.type == "EOF":
                self.add_error(
                    SyntaxErrorCustom(
                        "Syntax Error: Missing closing brace '}' before end of file",
                        self.current_token.line,
                        self.current_token.column,
                        self.current_token.position,
                    )
                )
                return Block(statements)

            try:
                statements.append(self.statement())
            except SyntaxErrorCustom as error:
                self.add_error(error)
                # Inside a block, do not consume the closing brace during recovery.
                if (
                    self.current_token.type == "SPECIAL_CHARACTERS"
                    and self.current_token.value == "}"
                ):
                    break
                self.synchronize()

        self.eat("SPECIAL_CHARACTERS", "}")
        return Block(statements)

    def declaration(self):
        data_type = self.current_token.value
        self.eat("KEYWORD")

        if self.current_token.type != "ID":
            self.error(
                f"Syntax Error: Expected variable name after data type '{data_type}'"
            )

        var_name = self.current_token.value
        self.eat("ID")

        expr = None

        if self.current_token.type == "OPERATORS" and self.current_token.value == "=":
            self.eat("OPERATORS", "=")
            expr = self.expression()

        if not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == ";"
        ):
            self.error(
                f"Syntax Error: Missing ';' after declaration of variable '{var_name}'"
            )

        self.eat("SPECIAL_CHARACTERS", ";")
        return Declaration(data_type, var_name, expr)

    def assignment(self):
        var_name = self.current_token.value
        self.eat("ID")

        if (
            self.current_token.type != "OPERATORS"
            or self.current_token.value not in ("=", "+=", "-=", "*=", "/=", "%=")
        ):
            self.error(
                f"Syntax Error: Expected assignment operator after variable '{var_name}'"
            )

        op = self.current_token.value
        self.eat("OPERATORS", op)

        expr = self.expression()

        if not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == ";"
        ):
            self.error(
                f"Syntax Error: Missing ';' after assignment to variable '{var_name}'"
            )

        self.eat("SPECIAL_CHARACTERS", ";")
        return Assignment(var_name, op, expr)

    def print_statement(self):
        self.eat("KEYWORD", "print")

        expr = self.expression()

        if not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == ";"
        ):
            self.error("Syntax Error: Missing ';' after print statement")

        self.eat("SPECIAL_CHARACTERS", ";")
        return Print(expr)

    def if_statement(self):
        self.eat("KEYWORD", "if")

        if not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == "("
        ):
            self.error("Syntax Error: Missing '(' after 'if'")

        self.eat("SPECIAL_CHARACTERS", "(")

        cond = self.expression()

        if not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == ")"
        ):
            self.error("Syntax Error: Missing ')' after if condition")

        self.eat("SPECIAL_CHARACTERS", ")")

        if not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == "{"
        ):
            self.error("Syntax Error: Expected '{' to start if block")

        ifblk = self.block()
        elseblk = None

        if self.current_token.type == "KEYWORD" and self.current_token.value == "else":
            self.eat("KEYWORD", "else")
            if not (
                self.current_token.type == "SPECIAL_CHARACTERS"
                and self.current_token.value == "{"
            ):
                self.error("Syntax Error: Expected '{' to start else block")
            elseblk = self.block()

        return IfStatement(cond, ifblk, elseblk)

    def while_statement(self):
        self.eat("KEYWORD", "while")

        if not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == "("
        ):
            self.error("Syntax Error: Missing '(' after 'while'")

        self.eat("SPECIAL_CHARACTERS", "(")

        cond = self.expression()

        if not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == ")"
        ):
            self.error("Syntax Error: Missing ')' after while condition")

        self.eat("SPECIAL_CHARACTERS", ")")

        if not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == "{"
        ):
            self.error("Syntax Error: Expected '{' to start while block")

        return WhileStatement(cond, self.block())

    def return_statement(self):
        self.eat("KEYWORD", "return")

        expr = None

        if not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == ";"
        ):
            expr = self.expression()

        if not (
            self.current_token.type == "SPECIAL_CHARACTERS"
            and self.current_token.value == ";"
        ):
            self.error("Syntax Error: Missing ';' after return statement")

        self.eat("SPECIAL_CHARACTERS", ";")
        return ReturnStatement(expr)

    def expression(self):
        return self.logical_or()

    def logical_or(self):
        left = self.logical_and()

        while self.current_token.type == "OPERATORS" and self.current_token.value == "||":
            op = self.current_token.value
            self.eat("OPERATORS", op)
            left = BinaryOp(left, op, self.logical_and())

        return left

    def logical_and(self):
        left = self.relational_expression()

        while self.current_token.type == "OPERATORS" and self.current_token.value == "&&":
            op = self.current_token.value
            self.eat("OPERATORS", op)
            left = BinaryOp(left, op, self.relational_expression())

        return left

    def relational_expression(self):
        left = self.additive_expression()

        while self.current_token.type == "OPERATORS" and self.current_token.value in (
            "==",
            "!=",
            "<",
            ">",
            "<=",
            ">=",
        ):
            op = self.current_token.value
            self.eat("OPERATORS", op)
            left = BinaryOp(left, op, self.additive_expression())

        return left

    def additive_expression(self):
        left = self.term()

        while self.current_token.type == "OPERATORS" and self.current_token.value in (
            "+",
            "-",
        ):
            op = self.current_token.value
            self.eat("OPERATORS", op)
            left = BinaryOp(left, op, self.term())

        return left

    def term(self):
        left = self.factor()

        while self.current_token.type == "OPERATORS" and self.current_token.value in (
            "*",
            "/",
            "%",
        ):
            op = self.current_token.value
            self.eat("OPERATORS", op)
            left = BinaryOp(left, op, self.factor())

        return left

    def factor(self):
        tok = self.current_token

        if tok.type == "OPERATORS" and tok.value in ("!", "-", "+"):
            op = tok.value
            self.eat("OPERATORS", op)
            return UnaryOp(op, self.factor())

        if tok.type == "NUMBER":
            self.eat("NUMBER")
            return Number(tok.value)

        if tok.type == "FLOAT_LITERAL":
            self.eat("FLOAT_LITERAL")
            return FloatLiteral(tok.value)

        if tok.type == "STRING_LITERAL":
            self.eat("STRING_LITERAL")
            return StringLiteral(tok.value)

        if tok.type == "CHAR_LITERAL":
            self.eat("CHAR_LITERAL")
            return CharLiteral(tok.value)

        if tok.type == "ID":
            self.eat("ID")
            return Variable(tok.value)

        if tok.type == "SPECIAL_CHARACTERS" and tok.value == "(":
            self.eat("SPECIAL_CHARACTERS", "(")
            node = self.expression()

            if not (
                self.current_token.type == "SPECIAL_CHARACTERS"
                and self.current_token.value == ")"
            ):
                self.error("Syntax Error: Missing ')' after expression")

            self.eat("SPECIAL_CHARACTERS", ")")
            return node

        self.error(f"Syntax Error: Invalid expression near '{tok.value}'")

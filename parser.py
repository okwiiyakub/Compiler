from lexer import lexer


# ============================================================
# SYNTAX ANALYZER / PARSER
# ============================================================
#
# Grammar used:
#
# Program → StatementList
#
# StatementList → Statement StatementList
# StatementList → ε
#
# Statement → Declaration
# Statement → Assignment
# Statement → PrintStatement
#
# Declaration → int ID ;
# Declaration → int ID = Expression ;
#
# Assignment → ID = Expression ;
#
# PrintStatement → print Expression ;
#
# Expression → Term ExpressionPrime
#
# ExpressionPrime → + Term ExpressionPrime
# ExpressionPrime → - Term ExpressionPrime
# ExpressionPrime → ε
#
# Term → Factor TermPrime
#
# TermPrime → * Factor TermPrime
# TermPrime → / Factor TermPrime
# TermPrime → ε
#
# Factor → NUMBER
# Factor → ID
# Factor → ( Expression )
# ============================================================


class ASTNode:
    pass


class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class Declaration(ASTNode):
    def __init__(self, var_name, expression=None):
        self.var_name = var_name
        self.expression = expression


class Assignment(ASTNode):
    def __init__(self, var_name, expression):
        self.var_name = var_name
        self.expression = expression


class Print(ASTNode):
    def __init__(self, expression):
        self.expression = expression


class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class Number(ASTNode):
    def __init__(self, value):
        self.value = int(value)


class Variable(ASTNode):
    def __init__(self, name):
        self.name = name


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[self.position]

    def eat(self, token_type, value=None):
        if self.current_token.type != token_type:
            raise SyntaxError(
                f"Syntax Error: Expected token type {token_type}, "
                f"but got {self.current_token.type}"
            )

        if value is not None and self.current_token.value != value:
            raise SyntaxError(
                f"Syntax Error: Expected '{value}', "
                f"but got '{self.current_token.value}'"
            )

        self.position += 1
        self.current_token = self.tokens[self.position]

    def parse(self):
        statements = []

        while self.current_token.type != "EOF":
            statements.append(self.statement())

        return Program(statements)

    def statement(self):
        if self.current_token.type == "KEYWORD" and self.current_token.value == "int":
            return self.declaration()

        elif self.current_token.type == "ID":
            return self.assignment()

        elif self.current_token.type == "KEYWORD" and self.current_token.value == "print":
            return self.print_statement()

        else:
            raise SyntaxError(
                f"Syntax Error: Invalid statement starting with '{self.current_token.value}'"
            )

    def declaration(self):
        self.eat("KEYWORD", "int")

        var_name = self.current_token.value
        self.eat("ID")

        expression = None

        if self.current_token.type == "OPERATORS" and self.current_token.value == "=":
            self.eat("OPERATORS", "=")
            expression = self.expression()

        self.eat("SPECIAL_CHARACTERS", ";")
        return Declaration(var_name, expression)

    def assignment(self):
        var_name = self.current_token.value
        self.eat("ID")

        self.eat("OPERATORS", "=")

        expression = self.expression()

        self.eat("SPECIAL_CHARACTERS", ";")
        return Assignment(var_name, expression)

    def print_statement(self):
        self.eat("KEYWORD", "print")

        expression = self.expression()

        self.eat("SPECIAL_CHARACTERS", ";")
        return Print(expression)

    def expression(self):
        left = self.term()
        return self.expression_prime(left)

    def expression_prime(self, left):
        if self.current_token.type == "OPERATORS" and self.current_token.value in ("+", "-"):
            operator = self.current_token.value
            self.eat("OPERATORS", operator)

            right = self.term()
            new_left = BinaryOp(left, operator, right)

            return self.expression_prime(new_left)

        return left

    def term(self):
        left = self.factor()
        return self.term_prime(left)

    def term_prime(self, left):
        if self.current_token.type == "OPERATORS" and self.current_token.value in ("*", "/"):
            operator = self.current_token.value
            self.eat("OPERATORS", operator)

            right = self.factor()
            new_left = BinaryOp(left, operator, right)

            return self.term_prime(new_left)

        return left

    def factor(self):
        token = self.current_token

        if token.type == "NUMBER":
            self.eat("NUMBER")
            return Number(token.value)

        elif token.type == "ID":
            self.eat("ID")
            return Variable(token.value)

        elif token.type == "SPECIAL_CHARACTERS" and token.value == "(":
            self.eat("SPECIAL_CHARACTERS", "(")

            node = self.expression()

            self.eat("SPECIAL_CHARACTERS", ")")
            return node

        else:
            raise SyntaxError(
                f"Syntax Error: Invalid factor '{token.value}'"
            )

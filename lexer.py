import re
from collections import defaultdict


# ============================================================
# LEXICAL ANALYZER
# ============================================================
# This phase reads source code and converts it into tokens.
#
# Adjustments made:
# 1. int and print are both KEYWORD tokens.
# 2. ;, (, and ) are SPECIAL_CHARACTERS.
# 3. +, -, *, /, and = are OPERATORS.
# 4. Token output can be grouped in table form.
# ============================================================


TOKEN_SPECIFICATION = [
    ("NUMBER",              r"\d+"),
    ("KEYWORD",             r"\b(int|print)\b"),
    ("ID",                  r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OPERATORS",           r"[+\-*/=]"),
    ("SPECIAL_CHARACTERS",  r"[;()]"),
    ("SKIP",                r"[ \t\n]+"),
    ("MISMATCH",            r"."),
]


class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


def lexer(source_code):
    tokens = []

    pattern = "|".join(
        f"(?P<{name}>{regex})" for name, regex in TOKEN_SPECIFICATION
    )

    for match in re.finditer(pattern, source_code):
        token_type = match.lastgroup
        value = match.group()

        if token_type == "SKIP":
            continue

        elif token_type == "MISMATCH":
            raise SyntaxError(f"Lexical Error: Unexpected character '{value}'")

        else:
            tokens.append(Token(token_type, value))

    tokens.append(Token("EOF", "EOF"))
    return tokens


def display_tokens_grouped(tokens):
    grouped_tokens = defaultdict(list)

    for token in tokens:
        if token.type != "EOF":
            grouped_tokens[token.type].append(token.value)

    print("+----------------------+------------------------------+")
    print("| Token Type           | Lexemes                      |")
    print("+----------------------+------------------------------+")

    for token_type, values in grouped_tokens.items():
        unique_values = sorted(set(values))
        lexemes = ", ".join(unique_values)
        print(f"| {token_type:<20} | {lexemes:<28} |")

    print("+----------------------+------------------------------+")

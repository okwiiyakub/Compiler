import re
from collections import defaultdict

class CompilerError(Exception):
    def __init__(self, message, line=None, column=None, position=None):
        self.message = message
        self.line = line
        self.column = column
        self.position = position
    def __str__(self):
        parts=[]
        if self.line is not None: parts.append(f"line {self.line}")
        if self.column is not None: parts.append(f"column {self.column}")
        if self.position is not None: parts.append(f"position {self.position}")
        return f"{self.message} at " + ", ".join(parts) if parts else self.message

class LexicalError(CompilerError): pass

class Token:
    def __init__(self, token_type, value, line, column, position):
        self.type=token_type; self.value=value; self.line=line; self.column=column; self.position=position
    def __repr__(self):
        return f"Token({self.type}, {self.value}, line={self.line}, column={self.column})"

TOKEN_SPECIFICATION = [
    ("COMMENT", r"//.*|/\*[\s\S]*?\*/"),
    ("STRING_LITERAL", r'"([^"\\]|\\.)*"'),
    ("CHAR_LITERAL", r"'([^'\\]|\\.)'"),
    ("FLOAT_LITERAL", r"\d+\.\d+"),
    ("NUMBER", r"\d+"),
    ("KEYWORD", r"\b(int|float|char|double|void|if|else|while|for|return|break|continue|print)\b"),
    ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OPERATORS", r"==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|%=|&&|\|\||[+\-*/%=<>!]"),
    ("SPECIAL_CHARACTERS", r"[;,\{\}\(\)\[\]]"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    ("MISMATCH", r"."),
]

def lexer(source_code):
    tokens=[]
    pattern="|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_SPECIFICATION)
    line=1; line_start=0
    for match in re.finditer(pattern, source_code):
        token_type=match.lastgroup; value=match.group(); position=match.start(); column=position-line_start+1
        if token_type=="NEWLINE":
            line+=1; line_start=match.end(); continue
        if token_type=="SKIP": continue
        if token_type=="COMMENT":
            line += value.count("\n")
            if "\n" in value: line_start = match.end() - len(value.rsplit("\n",1)[-1])
            continue
        if token_type=="MISMATCH":
            raise LexicalError(f"Unexpected character '{value}'", line, column, position)
        tokens.append(Token(token_type,value,line,column,position))
    tokens.append(Token("EOF","EOF",line,1,len(source_code)))
    return tokens

def display_tokens_grouped(tokens):
    grouped=defaultdict(list)
    for token in tokens:
        if token.type!="EOF": grouped[token.type].append(token.value)
    out=["+----------------------+------------------------------------------------------+", "| Token Type           | Lexemes                                              |", "+----------------------+------------------------------------------------------+"]
    for token_type, values in grouped.items():
        lexemes=", ".join(sorted(set(values)))
        out.append(f"| {token_type:<20} | {lexemes:<52} |")
    out.append("+----------------------+------------------------------------------------------+")
    return "\n".join(out)

def display_tokens_detailed(tokens):
    out=["+----------------------+----------------+------+--------+----------+", "| Token Type           | Lexeme         | Line | Column | Position |", "+----------------------+----------------+------+--------+----------+"]
    for token in tokens:
        if token.type!="EOF":
            out.append(f"| {token.type:<20} | {token.value:<14} | {token.line:<4} | {token.column:<6} | {token.position:<8} |")
    out.append("+----------------------+----------------+------+--------+----------+")
    return "\n".join(out)

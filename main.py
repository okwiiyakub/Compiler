from lexer import lexer, display_tokens_grouped
from parser import Parser
from semantic_analyzer import SemanticAnalyzer, SemanticError
from ast_visualizer import plot_ast


source_code = """
int x = 5;
int y = 10;
int z;
z = x + y * 2;
print z;
"""


print("SOURCE CODE")
print(source_code)


print("\n1. LEXICAL ANALYSIS")

try:
    tokens = lexer(source_code)

    print("Status: PASSED")
    print("Grouped Token Table:")
    display_tokens_grouped(tokens)

except SyntaxError as error:
    print("Status: FAILED")
    print("Error Type: Lexical Error")
    print(f"Message: {error}")
    print("Compilation stopped during lexical analysis.")
    exit()


print("\n2. SYNTAX ANALYSIS")

try:
    parser = Parser(tokens)
    compiler_ast = parser.parse()

    print("Status: PASSED")
    print("Message: Syntax analysis completed successfully.")
    print("AST generated successfully.")

    try:
        plot_ast(compiler_ast)
    except Exception as image_error:
        print("Warning: AST image was not generated.")
        print(f"Reason: {image_error}")
        print("Tip: Install Graphviz software and add it to PATH.")

except SyntaxError as error:
    print("Status: FAILED")
    print("Error Type: Syntax Error")
    print(f"Message: {error}")
    print("Compilation stopped during syntax analysis.")
    exit()


print("\n3. SEMANTIC ANALYSIS")

try:
    semantic_analyzer = SemanticAnalyzer()
    semantic_analyzer.analyze(compiler_ast)

    print("Status: PASSED")
    print("Message: Semantic analysis completed successfully.")
    print("Symbol Table:")

    for variable, data_type in semantic_analyzer.symbol_table.items():
        print(f"  {variable} : {data_type}")

except SemanticError as error:
    print("Status: FAILED")
    print("Error Type: Semantic Error")
    print(f"Message: {error}")
    print("Compilation stopped during semantic analysis.")
    exit()


print("\nFRONTEND COMPILATION COMPLETED SUCCESSFULLY.")
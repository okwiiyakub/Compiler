from lexer import lexer, display_tokens_grouped, display_tokens_detailed, LexicalError
from parser import Parser, SyntaxErrorCustom
from semantic_analyzer import SemanticAnalyzer, SemanticError
from intermediate_code_generator import IntermediateCodeGenerator


def compile_source(source_code, generate_ast_image=False):
    output = []
    output.append("SOURCE LANGUAGE: Expanded Mini C-like Language")
    output.append("FRONTEND OUTPUT: Tokens, Abstract Syntax Tree, Symbol Table, and Intermediate Code")
    output.append("=" * 70)

    try:
        output.append("\n1. LEXICAL ANALYSIS")
        tokens = lexer(source_code)
        output.append("Status: PASSED")
        output.append("\nGrouped Token Table:")
        output.append(display_tokens_grouped(tokens))
        output.append("\nDetailed Token Table:")
        output.append(display_tokens_detailed(tokens))
    except LexicalError as error:
        output += [
            "Status: FAILED",
            "Error Type: Lexical Error",
            f"Message: {error}",
        ]
        return "\n".join(output)

    try:
        output.append("\n2. SYNTAX ANALYSIS")
        parser = Parser(tokens)
        compiler_ast = parser.parse()

        output += [
            "Status: PASSED",
            "Message: Syntax analysis completed successfully.",
            "AST generated successfully.",
        ]

        if generate_ast_image:
            try:
                from ast_visualizer import plot_ast

                output.append(f"AST image generated: {plot_ast(compiler_ast)}")
            except Exception as image_error:
                output.append("Warning: AST image was not generated.")
                output.append(f"Reason: {image_error}")

    except SyntaxErrorCustom as error:
        output += [
            "Status: FAILED",
            "Error Type: Syntax Error(s)",
            f"Message: {error}",
        ]
        return "\n".join(output)

    try:
        output.append("\n3. SEMANTIC ANALYSIS")
        analyzer = SemanticAnalyzer()
        semantic_ok = analyzer.run(compiler_ast)

        if semantic_ok:
            output += [
                "Status: PASSED",
                "Message: Semantic analysis completed successfully.",
            ]
        else:
            output += [
                "Status: FAILED",
                "Error Type: Semantic Error(s)",
                analyzer.format_errors(),
            ]

        if analyzer.warnings:
            output.append("\nSemantic Warning(s):")
            output.append(analyzer.format_warnings())

        output += [
            "\nSymbol Table:",
            analyzer.format_symbol_table(),
        ]

        if not semantic_ok:
            return "\n".join(output)

    except SemanticError as error:
        output += [
            "Status: FAILED",
            "Error Type: Semantic Error",
            f"Message: {error}",
        ]
        return "\n".join(output)

    try:
        output.append("\n4. INTERMEDIATE CODE GENERATION")
        generator = IntermediateCodeGenerator()
        generator.generate(compiler_ast)
        output += [
            "Status: PASSED",
            "Message: Intermediate code generated successfully.",
            "\nThree-Address Code:",
            generator.format_code(),
        ]
    except Exception as error:
        output += [
            "Status: FAILED",
            "Error Type: Intermediate Code Generation Error",
            f"Message: {error}",
        ]
        return "\n".join(output)

    output.append("\nFRONTEND COMPILATION COMPLETED SUCCESSFULLY.")
    return "\n".join(output)


if __name__ == "__main__":
    print("Enter source code for the Expanded Mini C-like Language.")
    print("Press ENTER on an empty line to compile.")
    print("-" * 70)

    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    print()
    print(compile_source("\n".join(lines), generate_ast_image=True))

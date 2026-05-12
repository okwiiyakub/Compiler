from graphviz import Digraph
from parser import Program, Declaration, Assignment, Print, BinaryOp, Number, Variable


# ============================================================
# AST VISUALIZER
# ============================================================
# This file generates only the Abstract Syntax Tree.
# It is optional, but helpful for presentation.
# ============================================================


def plot_ast(root, filename="ast"):
    dot = Digraph(comment="Abstract Syntax Tree")
    dot.attr(rankdir="TB")

    counter = [0]

    def add_node(label):
        node_id = str(counter[0])
        counter[0] += 1
        dot.node(node_id, label)
        return node_id

    def visit(node):
        if isinstance(node, Program):
            node_id = add_node("Program")

            for statement in node.statements:
                child_id = visit(statement)
                dot.edge(node_id, child_id)

            return node_id

        elif isinstance(node, Declaration):
            node_id = add_node(f"Declaration\\n{node.var_name}")

            if node.expression is not None:
                expr_id = visit(node.expression)
                dot.edge(node_id, expr_id)

            return node_id

        elif isinstance(node, Assignment):
            node_id = add_node(f"Assignment\\n{node.var_name}")

            expr_id = visit(node.expression)
            dot.edge(node_id, expr_id)

            return node_id

        elif isinstance(node, Print):
            node_id = add_node("Print")

            expr_id = visit(node.expression)
            dot.edge(node_id, expr_id)

            return node_id

        elif isinstance(node, BinaryOp):
            node_id = add_node(node.operator)

            left_id = visit(node.left)
            right_id = visit(node.right)

            dot.edge(node_id, left_id)
            dot.edge(node_id, right_id)

            return node_id

        elif isinstance(node, Number):
            return add_node(str(node.value))

        elif isinstance(node, Variable):
            return add_node(node.name)

        else:
            raise Exception(f"Unknown AST node: {type(node).__name__}")

    visit(root)

    dot.render(filename, format="png", cleanup=True)
    print(f"AST saved as {filename}.png")

from graphviz import Digraph
from parser import Program, Block, Declaration, Assignment, Print, IfStatement, WhileStatement, ReturnStatement, BinaryOp, UnaryOp, Number, FloatLiteral, StringLiteral, CharLiteral, Variable

def plot_ast(root, filename="ast"):
    dot=Digraph(comment="Abstract Syntax Tree"); dot.attr(rankdir="TB"); counter=[0]
    def add(label):
        nid=str(counter[0]); counter[0]+=1; dot.node(nid,label); return nid
    def visit(node):
        if isinstance(node,Program):
            nid=add("Program")
            for s in node.statements: dot.edge(nid,visit(s))
            return nid
        if isinstance(node,Block):
            nid=add("Block")
            for s in node.statements: dot.edge(nid,visit(s))
            return nid
        if isinstance(node,Declaration):
            nid=add(f"Declaration\n{node.data_type} {node.var_name}")
            if node.expression is not None: dot.edge(nid,visit(node.expression))
            return nid
        if isinstance(node,Assignment):
            nid=add(f"Assignment\n{node.var_name} {node.operator}"); dot.edge(nid,visit(node.expression)); return nid
        if isinstance(node,Print):
            nid=add("Print"); dot.edge(nid,visit(node.expression)); return nid
        if isinstance(node,IfStatement):
            nid=add("If"); dot.edge(nid,visit(node.condition),label="condition"); dot.edge(nid,visit(node.if_block),label="if")
            if node.else_block is not None: dot.edge(nid,visit(node.else_block),label="else")
            return nid
        if isinstance(node,WhileStatement):
            nid=add("While"); dot.edge(nid,visit(node.condition),label="condition"); dot.edge(nid,visit(node.block),label="body"); return nid
        if isinstance(node,ReturnStatement):
            nid=add("Return")
            if node.expression is not None: dot.edge(nid,visit(node.expression))
            return nid
        if isinstance(node,BinaryOp):
            nid=add(node.operator); dot.edge(nid,visit(node.left)); dot.edge(nid,visit(node.right)); return nid
        if isinstance(node,UnaryOp):
            nid=add(f"Unary {node.operator}"); dot.edge(nid,visit(node.operand)); return nid
        if isinstance(node,(Number,FloatLiteral)): return add(str(node.value))
        if isinstance(node,(StringLiteral,CharLiteral)): return add(node.value)
        if isinstance(node,Variable): return add(node.name)
        raise Exception(f"Unknown AST node: {type(node).__name__}")
    visit(root); dot.render(filename,format="png",cleanup=True); return f"{filename}.png"

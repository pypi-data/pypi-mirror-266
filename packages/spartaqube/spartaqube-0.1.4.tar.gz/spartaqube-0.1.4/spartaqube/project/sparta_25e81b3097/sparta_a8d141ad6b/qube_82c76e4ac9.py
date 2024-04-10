import ast
def sparta_1c32cb2bab(script_text):
	A=set();B=ast.parse(script_text)
	class C(ast.NodeVisitor):
		def visit_Assign(C,node):
			for B in node.targets:
				if isinstance(B,ast.Name):A.add(B.id)
	D=C();D.visit(B);return list(A)
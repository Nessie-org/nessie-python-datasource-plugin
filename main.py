import ast
from pathlib import Path

from nessie_api.models import Graph, GraphType, Node, Edge, Attribute


def python_file_to_graph(py_file: str | Path) -> Graph:
    """
    Parse a Python file and represent its structural elements as a graph.

    Nodes represent modules, classes, functions, and global variables.
    Edges represent "contains" (module->class, class->method) and
    "calls" relationships between functions/methods.
    """
    with open(py_file, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    graph = Graph(GraphType.DIRECTED)

    node_map: dict[str, Node] = {}

    def add_node(node_id: str, **attrs) -> Node:
        if node_id not in node_map:
            node = Node(node_id)
            for k, v in attrs.items():
                node.add_attribute(Attribute(k, v))
            graph.add_node(node)
            node_map[node_id] = node
        return node_map[node_id]

    class ParentVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_class = None
            self.current_function = None

        def visit_ClassDef(self, node: ast.ClassDef):
            cls_node = add_node(f"class:{node.name}", type="class")
            if self.current_class:
                # nested class
                edge_id = f"edge:{self.current_class.id}->{cls_node.id}"
                if edge_id not in graph._edges:
                    graph.add_edge(
                        Edge(
                            edge_id,
                            self.current_class,
                            cls_node,
                            {"relationship": Attribute("relationship", "nested_class")},
                        )
                    )
            self.current_class = cls_node
            self.generic_visit(node)
            self.current_class = None

        def visit_FunctionDef(self, node: ast.FunctionDef):
            func_node = add_node(f"func:{node.name}", type="function")
            parent = self.current_class if self.current_class else None
            if parent:
                # class method
                edge_id = f"edge:{parent.id}->{func_node.id}"
                if edge_id not in graph._edges:
                    graph.add_edge(
                        Edge(
                            edge_id,
                            parent,
                            func_node,
                            {"relationship": Attribute("relationship", "method")},
                        )
                    )
            else:
                # module-level function
                mod_node = add_node(f"module:{py_file}", type="module")
                edge_id = f"edge:{mod_node.id}->{func_node.id}"
                if edge_id not in graph._edges:
                    graph.add_edge(
                        Edge(
                            edge_id,
                            mod_node,
                            func_node,
                            {"relationship": Attribute("relationship", "function")},
                        )
                    )
            self.current_function = func_node
            self.generic_visit(node)
            self.current_function = None

        def visit_Call(self, node: ast.Call):
            if isinstance(node.func, ast.Name) and self.current_function:
                called_name = f"func:{node.func.id}"
                called_node = add_node(called_name, type="function")
                edge_id = f"edge:{self.current_function.id}->{called_node.id}"
                if edge_id not in graph._edges:
                    graph.add_edge(
                        Edge(
                            edge_id,
                            self.current_function,
                            called_node,
                            {"relationship": Attribute("relationship", "calls")},
                        )
                    )
            self.generic_visit(node)

    visitor = ParentVisitor()
    visitor.visit(tree)

    return graph


if __name__ == "__main__":
    import json

    print(json.dumps(python_file_to_graph("main.py").to_dict(), indent=2))

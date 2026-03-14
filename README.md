# nessie-python-datasource-plugin

A [Nessie](https://github.com/Nessie-org) plugin that parses a Python source file and loads its structure as a graph — turning modules, classes, functions, and their relationships into nodes and edges you can explore in the Nessie UI.

> **Version:** 0.1.0 &nbsp;|&nbsp; **Python:** 3.14+ &nbsp;|&nbsp; **License:** see `LICENSE`

---

## What It Does

Given a path to any `.py` file, the plugin uses Python's built-in `ast` module to walk the syntax tree and build a directed graph where:

**Nodes** represent structural elements, each tagged with a `type` attribute:

| Node ID format | `type` attribute | Represents |
|---|---|---|
| `module:<filename>` | `module` | The file itself |
| `class:<ClassName>` | `class` | A class definition |
| `func:<func_name>` | `function` | A function or method |

**Edges** represent relationships between those elements:

| Relationship | Meaning |
|---|---|
| `function` | Module → top-level function it defines |
| `method` | Class → method it contains |
| `nested_class` | Class → nested class inside it |
| `calls` | Function → another function it calls |

The resulting graph is a `nessie-api` `Graph` object, ready to be visualised or filtered in a Nessie workspace.

---

## Installation

**Via pip:**

```bash
pip install git+https://github.com/Nessie-org/nessie-python-datasource-plugin.git
```

**Via uv** (recommended for development):

```bash
git clone https://github.com/Nessie-org/nessie-python-datasource-plugin.git
cd nessie-python-datasource-plugin
uv sync
```

The only runtime dependency is [`nessie-api`](https://github.com/Nessie-org/nessie-api), pulled directly from GitHub.

---

## Usage

### As a Nessie Plugin

The plugin registers itself automatically via the `nessie_plugins` entry point:

```toml
# pyproject.toml
[project.entry-points.nessie_plugins]
source_python = "nessie_python_datasource_plugin:get_plugin_data"
```

When installed, Nessie will discover it on startup. In the UI, select the **"Python sourcing plugin"** and provide a **Python file path** when prompted — that's the only required setup value.

The plugin handles the `load_graph` action, which creates a new workspace from the parsed graph.

### Standalone / Quick Test

Run `main.py` to parse a file and print the resulting graph as JSON:

```bash
python main.py
```

By default it parses itself (`main.py`). To parse a different file, import the function directly:

```python
from src.nessie_python_datasource_plugin import python_file_to_graph
from nessie_api.models import Action

action = Action(name="load_graph", payload={"Python file path": "path/to/your_file.py"})
graph = python_file_to_graph(action, context)

print(graph)
# Graph(name=your_file.py, type=directed, nodes=N, edges=M)
```

---

## Project Structure

```
nessie-python-datasource-plugin/
├── main.py                                     Quick-run demo
├── pyproject.toml
└── src/
    └── nessie_python_datasource_plugin/
        └── __init__.py                         Plugin logic + entry point factory
```

---

## Development

```bash
uv sync --group dev      # install dev dependencies (pytest, ruff, mypy, coverage)
ruff check src/          # lint
mypy src/                # type-check
pytest                   # run tests
```

---

## How It Fits Into Nessie

```
Your .py file
     │
     ▼
ast.parse()  ──►  ParentVisitor  ──►  Graph (nodes + edges)
                                           │
                                           ▼
                                    Nessie Workspace
                              (filterable, visualisable)
```

This plugin is a **data source** — responsible only for loading data into a workspace. Filtering, visualisation, and further interaction are handled by other Nessie components via the `Context` protocol.

if __name__ == "__main__":
    import json

    from src.nessie_python_datasource_plugin import python_file_to_graph

    print(json.dumps(python_file_to_graph("main.py").to_dict(), indent=2))

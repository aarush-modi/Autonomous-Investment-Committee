def _python_type_to_json(python_type):
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
    }
    return type_map.get(python_type, "string")

def tool (description: str):
    def decorator(func):
        func.tool_name = func.__name__
        properties = {}
        for param_name, param_type in func.__annotations__.items():
            if param_name == "return":
                continue
            properties[param_name] = {"type": _python_type_to_json(param_type)}
        required = [name for name in func.__annotations__ if name != "return"]
        func.schema = {"name": func.__name__, "description": description, "input_schema": {"type": "object", "properties": properties,"required": required}}
        return func
    return decorator



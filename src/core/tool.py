def _python_type_to_json(python_type):
    match python_type:
        case str:
            return "string"
        case int:
            return "integer"
        case float:
            return "number"
        case bool:
            return "boolean"
        case _:
            return "string"

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



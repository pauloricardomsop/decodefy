import json
import sys
import re

def generate_dart_class(class_name, data):
    dart_classes = []
    dart_class = f'class {class_name} ' + '{\n'

    # Generate class fields
    for key, value in data.items():
        dart_class += f'  {get_dart_type(key, value)}? {key};\n'  # Add "?" symbol to make the variables optional

    # Generate constructor
    constructor_params = ', '.join([f'this.{key}' for key in data.keys()])
    dart_class += f'\n  {class_name}({{{constructor_params}}});\n'  # Add braces around parameters

    # Generate fromJson named constructor
    dart_class += f'\n  {class_name}.fromJson(Map<String, dynamic> json)'
    dart_class += '{\n'
    for key, value in data.items():
        if isinstance(value, dict):
            nested_class_name = key[0].upper() + key[1:]
            dart_class += f'    {key} = json["{key}"] != null ? {nested_class_name}.fromJson(json["{key}"]) : null;\n'
            nested_class = generate_dart_class(nested_class_name, value)
            dart_classes.append(nested_class)
        elif isinstance(value, list):
            list_value = value[0]
            if isinstance(list_value, dict):
                nested_class_name = key[0].upper() + key[1:]
                nested_class_list_name = f'{key}List'
                dart_class += f'    {key} = json["{key}"] != null ? List<{nested_class_name}>.from(json["{key}"].map((x) => {nested_class_name}.fromJson(x))) : null;\n'
                nested_class = generate_dart_class(nested_class_name, list_value)
                dart_classes.append(nested_class)
        else:
            if isinstance(value, str):
                dart_class += f'    {key} = json["{key}"] ?? "";\n'  # Treat null value for String variables
            elif isinstance(value, int):
                dart_class += f'    {key} = json["{key}"] ?? 0;\n'  # Treat null value for int variables
            elif isinstance(value, float):
                dart_class += f'    {key} = json["{key}"] ?? 0.0;\n'  # Treat null value for double variables
            elif isinstance(value, bool):
                dart_class += f'    {key} = json["{key}"] ?? false;\n'  # Treat null value for boolean variables
            else:
                dart_class += f'    {key} = json["{key}"];\n'
    dart_class += '  }\n'

    # Generate toJson method
    dart_class += f'\n  Map<String, dynamic> toJson() => '
    dart_class += '{' + ', '.join([f'"{key}": {to_json_value(key, value)}' for key, value in data.items()]) + '};\n'

    dart_class += '}\n'
    dart_classes.append(dart_class)

    return '\n\n'.join(reversed(dart_classes)) 

def get_dart_type(key, value):
    if isinstance(value, int):
        return 'int'
    elif isinstance(value, float):
        return 'double'
    elif isinstance(value, bool):
        return 'bool'
    elif isinstance(value, dict):
        return key[0].upper() + key[1:]  # Use the key name as the model name
    elif isinstance(value, list):
        if len(value) > 0:
            return 'List<{}>'.format(get_dart_type(key, value[0]))
        else:
            return 'List<dynamic>'
    else:
        return 'String'

def to_json_value(key, value):
    if isinstance(value, dict):
        return f'{key} != null ? {key}!.toJson() : null'
    elif isinstance(value, list):
        if len(value) > 0 and isinstance(value[0], dict):
            return f'{key} != null ? {key}!.map((item) => item.toJson()).toList() : null'
    return key

def from_json_value(key, value):
    if isinstance(value, dict):
        nested_class_name = key[0].upper() + key[1:]
        return f'{nested_class_name}.fromJson(json["{key}"])'
    elif isinstance(value, list):
        if len(value) > 0 and isinstance(value[0], dict):
            nested_class_name = key[0].upper() + key[1:]
            return f'List<{nested_class_name}>.from(json["{key}"].map((item) => {nested_class_name}.fromJson(item)))'
    return f'json["{key}"]'

def pascal_to_snake_case(string):
    # Insert an underscore before any uppercase letter
    snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', string)
    # Convert the string to lowercase
    snake_case = snake_case.lower()
    return snake_case

# Check if the correct number of command-line arguments is provided
if len(sys.argv) != 3:
    print("Usage: python script_name.py <class_name> <json_data>")
    sys.exit(1)

# Extract the command-line arguments
class_name = sys.argv[1]
json_data = sys.argv[2]

# Load the JSON data
try:
    data = json.loads(json_data)
except json.JSONDecodeError as e:
    print("Invalid JSON data:", e)
    sys.exit(1)

# Generate the Dart class
dart_classes = generate_dart_class(class_name, data)

# Write the Dart class to a file
file_name = pascal_to_snake_case(class_name) + "_model.dart"
with open(file_name, "w") as f:
    f.write(dart_classes)

print(f"Generated {file_name}")

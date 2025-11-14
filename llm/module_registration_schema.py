OUTPUT_SCHEMA = {
    "total_modules": 1,
    "modules": [
        {
            "module_name": "Module name (string)",
            "functions": [
                {
                    "python_name": "Python function name (string)",
                    "c_function_name": "C function name (string)",
                    "param_format": "Parameter format string (string, e.g., 'l', 'si', 'O')",
                    "param_types": ["Parameter type list (list of string, e.g., 'long', 'string', 'int', 'PyObject*')"],
                    "param_count": "Parameter count (int)",
                    "return_type": "Return type (string, e.g., 'None', 'int', 'PyObject*')"
                }
            ]
        }
    ]
}


MODULE_SCHEMA = {
    "module_name": "string",
    "functions": [
        {
            "python_name": "string",
            "c_function_name": "string",
            "param_format": "string",
            "param_types": ["string"],
            "param_count": "int",
            "return_type": "string"
        }
    ]
}


PARAM_FORMAT_MAPPING = {
    "s": "string (char*)",
    "s#": "string with length (char*, int)",
    "z": "string or None (char*)",
    "z#": "string or None with length (char*, int)",
    "u": "unicode string (Py_UNICODE*)",
    "u#": "unicode string with length (Py_UNICODE*, int)",
    "i": "int",
    "b": "unsigned char",
    "h": "short",
    "l": "long",
    "k": "unsigned long",
    "L": "long long",
    "K": "unsigned long long",
    "f": "float",
    "d": "double",
    "D": "complex (Py_complex)",
    "c": "char (length 1)",
    "C": "int (character code)",
    "O": "PyObject*",
    "O!": "PyObject* (with type check)",
    "O&": "PyObject* (with converter function)",
    "w*": "read-write buffer (Py_buffer*)",
    "es": "encoded string",
    "et": "encoded string with encoding",
    "es#": "encoded string with length",
    "et#": "encoded string with encoding and length",
}


def get_schema_string() -> str:
    import json
    return json.dumps(OUTPUT_SCHEMA, indent=2, ensure_ascii=False)
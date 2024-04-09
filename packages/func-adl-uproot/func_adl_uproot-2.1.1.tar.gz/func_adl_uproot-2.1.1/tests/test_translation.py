import ast

from func_adl_uproot import generate_function


def test_generate_function_string():
    python_source = "EventDataset()"
    python_ast = ast.parse(python_source)
    function = generate_function(python_ast)
    assert function('tests/scalars_tree_file.root', 'tree').fields == [
        'int_branch',
        'long_branch',
        'float_branch',
        'double_branch',
        'bool_branch',
    ]


def test_generate_function_list():
    python_source = "EventDataset()"
    python_ast = ast.parse(python_source)
    function = generate_function(python_ast)
    assert function(['tests/scalars_tree_file.root'], 'tree').fields == [
        'int_branch',
        'long_branch',
        'float_branch',
        'double_branch',
        'bool_branch',
    ]


def test_generate_function_override_file():
    python_source = "EventDataset(None)"
    python_ast = ast.parse(python_source)
    function = generate_function(python_ast)
    assert function(['tests/scalars_tree_file.root'], 'tree').fields == [
        'int_branch',
        'long_branch',
        'float_branch',
        'double_branch',
        'bool_branch',
    ]


def test_generate_function_override_file_and_tree():
    python_source = "EventDataset(None, None)"
    python_ast = ast.parse(python_source)
    function = generate_function(python_ast)
    assert function(['tests/scalars_tree_file.root'], 'tree').fields == [
        'int_branch',
        'long_branch',
        'float_branch',
        'double_branch',
        'bool_branch',
    ]

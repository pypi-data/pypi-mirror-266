import ast

import qastle

from func_adl_uproot import python_ast_to_python_source


def assert_identical_source(python_source):
    python_ast = qastle.insert_linq_nodes(ast.parse(python_source))
    rep = python_ast_to_python_source(python_ast)
    assert rep == python_source


def assert_identical_literal(python_literal):
    python_source = repr(python_literal)
    assert_identical_source(python_source)


def assert_equivalent_source(python_source):
    python_ast = ast.parse(python_source)
    rep = python_ast_to_python_source(python_ast)
    assert ast.dump(ast.parse(rep)) == ast.dump(python_ast)


def assert_modified_source(initial_source, final_source):
    python_ast = qastle.insert_linq_nodes(ast.parse(initial_source))
    rep = python_ast_to_python_source(python_ast)
    assert rep == final_source


def test_literals():
    assert_identical_literal('')
    assert_identical_literal('a')
    assert_identical_literal(0)
    assert_identical_literal(1)
    assert_identical_literal(())
    assert_identical_literal((1,))
    assert_identical_literal((1, 2))
    assert_identical_literal([])
    assert_identical_literal([1])
    assert_identical_literal([1, 2])
    assert_identical_literal({})
    assert_identical_literal({1: 2})
    assert_identical_literal({1: 2, 3: 4})
    assert_identical_literal(True)
    assert_identical_literal(False)
    assert_identical_literal(None)


def test_builtins():
    assert_identical_source('abs')
    assert_identical_source('all')
    assert_identical_source('any')
    assert_identical_source('len')
    assert_identical_source('max')
    assert_identical_source('min')
    assert_identical_source('sum')


def test_allowed_modules():
    assert_identical_source('np')


def test_unary_ops():
    assert_equivalent_source('+1')
    assert_identical_source('(-1)')
    assert_modified_source('not True', 'np.logical_not(True)')


def test_binary_ops():
    assert_identical_source('(1 + 2)')
    assert_identical_source('(1 - 2)')
    assert_identical_source('(1 * 2)')
    assert_identical_source('(1 / 2)')
    assert_identical_source('(1 % 2)')
    assert_identical_source('(1 ** 2)')
    assert_identical_source('(1 // 2)')
    assert_identical_source('(1 & 2)')
    assert_identical_source('(1 | 2)')
    assert_identical_source('(1 ^ 2)')
    assert_identical_source('(1 << 2)')
    assert_identical_source('(1 >> 2)')


def test_boolean_ops():
    assert_modified_source('True and False', 'functools.reduce(np.logical_and, [True, False])')
    assert_modified_source(
        'True and False and False', 'functools.reduce(np.logical_and, [True, False, False])'
    )
    assert_modified_source('True or False', 'functools.reduce(np.logical_or, [True, False])')
    assert_modified_source(
        'True or False or False', 'functools.reduce(np.logical_or, [True, False, False])'
    )


def test_comparison_ops():
    assert_identical_source('(1 == 2)')
    assert_identical_source('(1 != 2)')
    assert_identical_source('(1 < 2)')
    assert_identical_source('(1 <= 2)')
    assert_identical_source('(1 > 2)')
    assert_identical_source('(1 >= 2)')
    assert_identical_source('(1 is 2)')
    assert_identical_source('(1 is not 2)')
    assert_modified_source('(1 in [2])', 'functools.reduce(np.logical_or, [(2 == 1)])')
    assert_modified_source(
        '(1 not in [2])', 'np.logical_not(functools.reduce(np.logical_or, [(2 == 1)]))'
    )
    assert_modified_source('(1 < 2 < 3)', '((1 < 2) & (2 < 3))')
    assert_modified_source('(1 < 2 < 3 < 4)', '((1 < 2) & (2 < 3) & (3 < 4))')


def test_conditional():
    assert_modified_source(
        '1 if True else 0',
        (
            'dak.where(True, dak.full_like(dak.unzip(True)[0], 1, dtype=type(1)),'
            + ' dak.full_like(dak.unzip(True)[0], 0, dtype=type(0)))'
        ),
    )


def test_subscripts():
    assert_identical_source("abs['a']")
    assert_modified_source(
        'abs[0]', ('(abs[abs.fields[0]]' + ' if isinstance(abs, dak.Array) else abs[0])')
    )
    assert_modified_source(
        'abs[abs]',
        (
            '(abs[abs.fields[abs]]'
            + ' if isinstance(abs, dak.Array)'
            + ' and (isinstance(abs, int) or isinstance(abs, slice))'
            + ' else abs[abs])'
        ),
    )
    assert_modified_source(
        'abs[:]', ('(abs[abs.fields[:]]' + ' if isinstance(abs, dak.Array) else abs[:])')
    )
    assert_modified_source(
        'abs[1:4:2]',
        ('(abs[abs.fields[1:4:2]]' + ' if isinstance(abs, dak.Array) else abs[1:4:2])'),
    )


def test_attribute():
    assert_modified_source('abs.a', "abs.a")


def test_lambda():
    assert_identical_source('(lambda: None)')
    assert_identical_source('(lambda x: x)')
    assert_identical_source('(lambda x, y: (x + y))')


def test_call():
    assert_identical_source('abs()')
    assert_identical_source('abs(1)')
    assert_identical_source('abs(1, 2)')

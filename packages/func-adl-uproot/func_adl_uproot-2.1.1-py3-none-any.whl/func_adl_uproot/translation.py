import copy

import qastle

from .transformer import PythonSourceGeneratorTransformer
from .transformer import branch_filter_name, input_filenames_argument_name, tree_name_argument_name

# Adapted from https://github.com/CoffeaTeam/coffea/blob/v2024.4.0/src/coffea/util.py#L217-L248
remove_not_interpretable_source = (
    '    def '
    + branch_filter_name
    + '''(branch):
        if isinstance(branch.interpretation, uproot.interpretation.identify.uproot.AsGrouped):
            for name, interpretation in branch.interpretation.subbranches.items():
                if isinstance(
                        interpretation, uproot.interpretation.identify.UnknownInterpretation
                    ):
                    logging.getLogger(__name__).warning(
                        f"Skipping {branch.name} as it is not interpretable by Uproot"
                    )
                    return False
        if isinstance(branch.interpretation, uproot.interpretation.identify.UnknownInterpretation):
            logging.getLogger(__name__).warning(
                f"Skipping {branch.name} as it is not interpretable by Uproot"
            )
            return False
        try:
            _ = branch.interpretation.awkward_form(None)
        except uproot.interpretation.objects.CannotBeAwkward:
            logging.getLogger(__name__).warning(
                f"Skipping {branch.name} as it cannot be represented as an Awkward array"
            )
            return False
        else:
            return True

'''
)


def python_ast_to_python_source(python_ast):
    return PythonSourceGeneratorTransformer().get_rep(python_ast)


def generate_python_source(ast, function_name='run_query'):
    if isinstance(ast, str):
        python_ast = qastle.text_ast_to_python_ast(ast)
    else:
        python_ast = copy.deepcopy(ast)
    python_ast = qastle.insert_linq_nodes(python_ast)
    source = (
        'def '
        + function_name
        + '('
        + input_filenames_argument_name
        + '=None, '
        + tree_name_argument_name
        + '=None):\n'
    )
    source += '    import functools, logging, numpy as np, dask_awkward as dak, uproot, vector\n'
    source += '    vector.register_awkward()\n\n'
    source += remove_not_interpretable_source
    source += '    return ' + python_ast_to_python_source(python_ast) + '.compute()\n'
    return source


def generate_function(ast, function_name='run_query'):
    source = generate_python_source(ast)
    exec(source)
    return eval(function_name)

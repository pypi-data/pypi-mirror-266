from ast import parse

from func_adl import EventDataset
from qastle import unwrap_ast

from .executor import ast_executor


class UprootDataset(EventDataset):
    def __init__(self, filenames=None, treename=None):
        super(UprootDataset, self).__init__()
        self._q_ast.args = [unwrap_ast(parse(repr(filenames))), unwrap_ast(parse(repr(treename)))]

    @staticmethod
    async def execute_result_async(ast, *args, **kwargs):
        return ast_executor(ast)

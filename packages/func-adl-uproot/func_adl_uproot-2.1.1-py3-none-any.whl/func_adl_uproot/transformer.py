import ast
import sys

from qastle import Contains, Select


allowed_modules = ['np']

input_filenames_argument_name = 'input_filenames'
tree_name_argument_name = 'tree_name'
branch_filter_name = '_remove_not_interpretable'

unary_op_dict = {ast.UAdd: '+', ast.USub: '-', ast.Invert: '~'}

bin_op_dict = {
    ast.Add: '+',
    ast.Sub: '-',
    ast.Mult: '*',
    ast.Div: '/',
    ast.FloorDiv: '//',
    ast.Mod: '%',
    ast.Pow: '**',
    ast.LShift: '<<',
    ast.RShift: '>>',
    ast.BitOr: '|',
    ast.BitXor: '^',
    ast.BitAnd: '&',
}

bool_op_dict = {ast.And: 'np.logical_and', ast.Or: 'np.logical_or'}

compare_op_dict = {
    ast.Eq: '==',
    ast.NotEq: '!=',
    ast.Lt: '<',
    ast.LtE: '<=',
    ast.Gt: '>',
    ast.GtE: '>=',
    ast.Is: 'is',
    ast.IsNot: 'is not',
    ast.In: 'in',
    ast.NotIn: 'not in',
}


def nonemin(a):
    non_none_a = [x for x in a if x is not None]
    return min(non_none_a, default=None)


class PythonSourceGeneratorTransformer(ast.NodeTransformer):
    def __init__(self):
        self._id_depths = {}
        self._projection_stack = []

    def visit(self, node):
        if hasattr(node, 'rep'):
            return node
        else:
            return super(PythonSourceGeneratorTransformer, self).visit(node)

    def generic_visit(self, node):
        if hasattr(node, 'rep'):
            return node
        else:
            return super(PythonSourceGeneratorTransformer, self).generic_visit(node)

    def get_rep(self, node):
        if node is None:
            return ''
        if not hasattr(node, 'rep'):
            node = self.visit(node)
        return node.rep

    def visit_Module(self, node):
        if len(node.body) < 1:
            node.rep = ''
            node._depth = None
        else:
            node.rep = self.get_rep(node.body[0])
            node._depth = node.body[0]._depth
        return node

    def visit_Expr(self, node):
        node.rep = self.get_rep(node.value)
        node._depth = node.value._depth
        return node

    def visit_Constant(self, node):
        node.rep = repr(node.value)
        node._depth = None
        return node

    def visit_Num(self, node):
        node.rep = repr(node.n)
        if node.n < 0:
            node.rep = '(' + node.rep + ')'
        node._depth = None
        return node

    def visit_Str(self, node):
        node.rep = repr(node.s)
        node._depth = None
        return node

    def visit_List(self, node):
        node.rep = '[' + ', '.join(self.get_rep(element) for element in node.elts) + ']'
        if len(node.elts) == 0:
            node._depth = None
        else:
            node._depth = node.elts[0]._depth
        return node

    def visit_Tuple(self, node):
        node.rep = '(' + ', '.join(self.get_rep(element) for element in node.elts)
        if len(node.elts) == 1:
            node.rep += ','
        node.rep += ')'
        node._depth = nonemin([elt._depth for elt in node.elts])
        return node

    def visit_Dict(self, node):
        node.rep = (
            '{'
            + ', '.join(
                self.get_rep(key) + ': ' + self.get_rep(value)
                for key, value in zip(node.keys, node.values)
            )
            + '}'
        )
        node._depth = nonemin([value._depth for value in node.values])
        return node

    def resolve_id(self, id):
        if id in self._id_depths or id in allowed_modules or id in __builtins__:
            return id
        else:
            raise NameError('Unknown id: ' + id)

    def visit_Name(self, node):
        if hasattr(node, 'ctx') and isinstance(node.ctx, ast.Param):
            node.rep = node.id
        else:
            node.rep = self.resolve_id(node.id)
            # builtins and modules will not be in _id_depths
            if node.rep not in self._id_depths:
                node._depth = None
            else:
                node._depth = self._id_depths[node.rep][-1]
        return node

    def visit_NameConstant(self, node):
        node.rep = repr(node.value)
        node._depth = None
        return node

    def visit_UnaryOp(self, node):
        if type(node.op) is ast.Not:
            node.rep = 'np.logical_not(' + self.get_rep(node.operand) + ')'
            node._depth = node.operand._depth
            return node
        if type(node.op) not in unary_op_dict:
            raise SyntaxError('Unimplemented unary operation: ' + node.op)
        operator_rep = unary_op_dict[type(node.op)]
        operand_rep = self.get_rep(node.operand)
        node.rep = '(' + operator_rep + operand_rep + ')'
        node._depth = node.operand._depth
        return node

    def visit_BinOp(self, node):
        left_rep = self.get_rep(node.left)
        if type(node.op) not in bin_op_dict:
            raise SyntaxError('Unimplemented binary operation: ' + node.op)
        operator_rep = bin_op_dict[type(node.op)]
        right_rep = self.get_rep(node.right)
        node.rep = '(' + left_rep + ' ' + operator_rep + ' ' + right_rep + ')'
        node._depth = nonemin([node.left._depth, node.right._depth])
        return node

    def visit_BoolOp(self, node):
        if type(node.op) not in bool_op_dict:
            raise SyntaxError('Unimplemented boolean operation: ' + node.op)
        bool_op_func = bool_op_dict[type(node.op)]
        node.rep = (
            'functools.reduce('
            + bool_op_func
            + ', ['
            + ', '.join([self.get_rep(value) for value in node.values])
            + '])'
        )
        node._depth = nonemin([value._depth for value in node.values])
        return node

    def visit_Compare(self, node):
        comparison_reps = []
        full_comparators = [node.left] + node.comparators
        for left, operator, right in zip(full_comparators[:-1], node.ops, full_comparators[1:]):
            if isinstance(operator, ast.In):
                contains_node = Contains(source=right, value=left)
                comparison_reps.append(self.get_rep(contains_node))
            elif isinstance(operator, ast.NotIn):
                contains_node = Contains(source=right, value=left)
                not_node = ast.UnaryOp(op=ast.Not(), operand=contains_node)
                comparison_reps.append(self.get_rep(not_node))
            else:
                if type(operator) not in compare_op_dict:
                    raise SyntaxError('Unimplemented comparison operation: ' + operator)
                left_rep = self.get_rep(left)
                operator_rep = compare_op_dict[type(operator)]
                right_rep = self.get_rep(right)
                comparison_reps.append('(' + left_rep + ' ' + operator_rep + ' ' + right_rep + ')')
        node.rep = ' & '.join(comparison_reps)
        if len(node.ops) > 1:
            node.rep = '(' + node.rep + ')'
        node._depth = nonemin([comparator._depth for comparator in full_comparators])
        return node

    def _broadcast_value(self, array_node, value_node):
        if isinstance(value_node, (ast.Constant, ast.Num, ast.Str)):
            value_node.rep = (
                'dak.full_like(dak.unzip('
                + self.get_rep(array_node)
                + ')[0], '
                + self.get_rep(value_node)
                + ', dtype=type('
                + self.get_rep(value_node)
                + '))'
            )
            value_node._depth = array_node
        return value_node

    def visit_IfExp(self, node):
        node.body = self._broadcast_value(node.test, node.body)
        node.orelse = self._broadcast_value(node.test, node.orelse)
        node.rep = (
            'dak.where('
            + self.get_rep(node.test)
            + ', '
            + self.get_rep(node.body)
            + ', '
            + self.get_rep(node.orelse)
            + ')'
        )
        node._depth = node.test._depth
        return node

    def visit_Index(self, node):
        node.rep = self.get_rep(node.value)
        node._depth = None
        return node

    def visit_Slice(self, node):
        lower_rep = self.get_rep(node.lower)
        upper_rep = self.get_rep(node.upper)
        node.rep = lower_rep + ':' + upper_rep
        step_rep = self.get_rep(node.step)
        if step_rep != '':
            node.rep += ':' + step_rep
        node._depth = None
        return node

    def visit_ExtSlice(self, node):
        node.rep = self.get_rep(ast.Tuple(elts=node.dims))
        node._depth = None
        return node

    def visit_Subscript(self, node):
        value_rep = self.get_rep(node.value)
        slice_rep = self.get_rep(node.slice)
        if hasattr(node, 'short_circuit') and node.short_circuit is True:
            node.rep = value_rep + '[' + slice_rep + ']'
        else:
            if isinstance(node.slice, ast.Slice):
                node.rep = (
                    '('
                    + value_rep
                    + '['
                    + value_rep
                    + '.fields['
                    + slice_rep
                    + ']]'
                    + ' if isinstance('
                    + value_rep
                    + ', dak.Array)'
                    + ' else '
                    + value_rep
                    + '['
                    + slice_rep
                    + '])'
                )
            elif isinstance(node.slice, ast.Tuple) or (
                (sys.version_info[0] == 3 and sys.version_info[1] < 9)
                and isinstance(node.slice, ast.ExtSlice)
            ):
                raise NotImplementedError('Multidimensional slices are not supported')
            else:
                if (sys.version_info[0] == 3 and sys.version_info[1] < 9) and isinstance(
                    node.slice, ast.Index
                ):
                    slice_value = node.slice.value
                else:
                    slice_value = node.slice
                try:
                    slice_eval = ast.literal_eval(slice_value)
                    if isinstance(slice_eval, int):
                        node.rep = (
                            '('
                            + value_rep
                            + '['
                            + value_rep
                            + '.fields['
                            + slice_rep
                            + ']]'
                            + ' if isinstance('
                            + value_rep
                            + ', dak.Array)'
                            + ' else '
                            + value_rep
                            + '['
                            + slice_rep
                            + '])'
                        )
                    else:
                        node.rep = value_rep + '[' + slice_rep + ']'
                except ValueError:
                    node.rep = (
                        '('
                        + value_rep
                        + '['
                        + value_rep
                        + '.fields['
                        + slice_rep
                        + ']]'
                        + ' if isinstance('
                        + value_rep
                        + ', dak.Array)'
                        + ' and (isinstance('
                        + slice_rep
                        + ', int)'
                        + ' or isinstance('
                        + slice_rep
                        + ', slice))'
                        + ' else '
                        + value_rep
                        + '['
                        + slice_rep
                        + '])'
                    )
        node._depth = node.value._depth
        return node

    def visit_Attribute(self, node):
        node.rep = self.get_rep(node.value) + '.' + node.attr
        node._depth = node.value._depth
        return node

    def visit_Lambda(self, node):
        arg_strs = [self.get_rep(arg_node) for arg_node in node.args.args]
        args_rep = ', '.join(arg_strs)
        for arg_str, arg_node in zip(arg_strs, node.args.args):
            if arg_str not in self._id_depths:
                self._id_depths[arg_str] = []
            self._id_depths[arg_str].append(arg_node._depth)
        body_rep = self.get_rep(node.body)
        node.rep = '(lambda'
        if args_rep != '':
            node.rep += ' '
        node.rep += args_rep + ': ' + body_rep + ')'
        for arg_str in arg_strs:
            del self._id_depths[arg_str][-1]
            if len(self._id_depths[arg_str]) == 0:
                del self._id_depths[arg_str]
        node._depth = None
        return node

    def visit_arg(self, node):
        node.rep = node.arg
        if not hasattr(node, '_depth'):
            node._depth = None
        return node

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'EventDataset':
            if len(node.args) > 2:
                raise TypeError(
                    'EventDataset() should have no more than two arguments, found '
                    + str(len(node.args))
                )
            node._depth = 0
            if len(node.args) >= 1:
                if hasattr(node.args[0], 'elts'):
                    urls = node.args[0].elts
                else:
                    urls = [node.args[0]]
                urls = [ast.literal_eval(url) for url in urls]
                urls = [url for url in urls if url is not None]
                source_rep = (
                    input_filenames_argument_name
                    + ' '
                    + 'if '
                    + input_filenames_argument_name
                    + ' is not None '
                    + 'else '
                    + repr(urls)
                )
            else:
                source_rep = input_filenames_argument_name
            source_rep = (
                '(lambda source: [source] if isinstance(source, str) else source)('
                + source_rep
                + ')'
            )
            if len(node.args) >= 2:
                local_tree_name_rep = self.get_rep(node.args[1])
            else:
                local_tree_name_rep = (
                    '(lambda key_array: '
                    + "key_array[key_array[:, 1] == 'TTree'][:, 0])("
                    + 'np.atleast_2d((lambda classnames:'
                    + ' np.hstack([list(classnames.keys()),'
                    + ' list(classnames.values())]))'
                    + '(uproot.open({'
                    + source_rep
                    + '[0]: None}).classnames())'
                    + '))[0]'
                )
            tree_name_rep = (
                tree_name_argument_name
                + ' '
                + 'if '
                + tree_name_argument_name
                + ' is not None '
                + 'else '
                + local_tree_name_rep
            )
            node.rep = (
                '(lambda input_files, tree_name_to_use: '
                + "(logging.getLogger(__name__).info('Using treename='"
                + ' + repr(tree_name_to_use)),'
                + ' uproot.dask({input_file: tree_name_to_use'
                + ' for input_file in input_files}, filter_branch='
                + branch_filter_name
                + '))[1])'
                + '('
                + source_rep
                + ', '
                + tree_name_rep
                + ')'
            )
        else:
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'ToFourMomentum':
                value_rep = self.get_rep(node.func.value)
                node.rep = (
                    'dak.with_name(dak.zip('
                    + value_rep
                    + ') if isinstance('
                    + value_rep
                    + ', dict) else '
                    + value_rep
                    + ", 'Momentum4D')"
                )
                node._depth = node.func.value._depth
            elif isinstance(node.func, ast.Attribute) and node.func.attr == 'ToFourMomenta':
                node.rep = 'dak.with_name(' + self.get_rep(node.func.value) + ", 'Momentum4D')"
                node._depth = node.func.value._depth
            else:
                func_rep = self.get_rep(node.func)
                args_rep = ', '.join(self.get_rep(arg) for arg in node.args)
                node.rep = func_rep + '(' + args_rep + ')'
                if len(node.args) == 0:
                    node._depth = None
                else:
                    node._depth = node.args[0]._depth
        return node

    def visit_Select(self, node):
        if type(node.selector) is not ast.Lambda:
            raise TypeError(
                'Argument to Select() must be a lambda function, found ' + node.selector
            )
        if len(node.selector.args.args) != 1:
            raise TypeError(
                'Lambda function in Select() must have exactly one argument, found '
                + len(node.selector.args.args)
            )
        self.visit(node.source)
        self._projection_stack.append(node.selector.args.args[0].arg)
        node.selector.args.args[0]._depth = node.source._depth + 1
        node.selector.body = self._broadcast_value(node.selector.args.args[0], node.selector.body)
        if (
            isinstance(node.source, ast.Name) and node.source.id in self._projection_stack[:-2]
        ) or (
            isinstance(node.source, ast.Attribute)
            and isinstance(node.source.value, ast.Name)
            and node.source.value.id in self._projection_stack[:-2]
        ):
            rep1 = self._projection_stack[-2]
            arg_node_1 = ast.arg(arg=rep1)
            arg_node_1._depth = self._id_depths[rep1][-1]
            lambda_node = ast.Lambda(
                args=ast.arguments(args=[arg_node_1, node.selector.args.args[0]]),
                body=node.selector.body,
            )
            call_rep = (
                self.get_rep(lambda_node)
                + '(*dak.unzip(dak.cartesian(('
                + rep1
                + ', '
                + self.get_rep(node.source)
                + '), axis='
                + repr(node.source._depth)
                + ', nested=True)))'
            )
            depth_limit = node.source._depth + 2
            node._depth = node.selector.args.args[0]._depth
        else:
            call_node = ast.Call(func=node.selector, args=[node.source])
            call_rep = self.get_rep(call_node)
            depth_limit = node.source._depth + 1
            node._depth = node.source._depth
        select_rep = (
            '(lambda selection:'
            + ' dak.zip({key: (dak.zip(value, depth_limit=(None if len(value) == 1 else '
            + repr(depth_limit)
            + ')) if isinstance(value, dict) else value) for key, value in selection.items()'
            + '} if isinstance(selection, dict) else selection,'
            + ' depth_limit=(None if len(selection) == 1 else '
            + repr(depth_limit)
            + ')) if not isinstance(selection, dak.Array) else selection)('
            + call_rep
            + ')'
        )
        self._projection_stack.pop()
        node.rep = select_rep
        return node

    def visit_SelectMany(self, node):
        if type(node.selector) is not ast.Lambda:
            raise TypeError(
                'Argument to SelectMany() must be a lambda function, found ' + node.selector
            )
        if len(node.selector.args.args) != 1:
            raise TypeError(
                'Lambda function in SelectMany() must have exactly one argument, '
                'found ' + len(node.selector.args.args)
            )
        self.visit_Select(node)
        node.rep = 'dak.flatten(' + node.rep + ', axis=' + repr(node._depth + 1) + ')'
        return node

    def visit_Where(self, node):
        if type(node.predicate) is not ast.Lambda:
            raise TypeError(
                'Argument to Where() must be a lambda function, found ' + node.predicate
            )
        if len(node.predicate.args.args) != 1:
            raise TypeError(
                'Lambda function in Where() must have exactly one argument, found '
                + len(node.predicate.args.args)
            )
        self.visit(node.source)
        node.predicate.args.args[0]._depth = node.source._depth + 1
        subscriptable = node.predicate.args.args[0].arg
        self._projection_stack.append(subscriptable)
        if sys.version_info[0] == 3 and sys.version_info[1] < 9:
            slice_node = ast.Index(node.predicate.body)
        else:
            slice_node = node.predicate.body
        node.predicate.body = ast.Subscript(
            value=ast.Name(id=subscriptable), slice=slice_node, short_circuit=True
        )
        call_node = ast.Call(func=node.predicate, args=[node.source])
        node.rep = self.get_rep(call_node)
        node._depth = node.source._depth
        self._projection_stack.pop()
        return node

    def visit_All(self, node):
        select_node = Select(source=node.source, selector=node.predicate)
        self.visit(select_node)
        node._depth = select_node._depth
        node.rep = 'dak.all(' + self.get_rep(select_node) + ', axis=' + repr(node._depth) + ')'
        return node

    def visit_Any(self, node):
        select_node = Select(source=node.source, selector=node.predicate)
        self.visit(select_node)
        node._depth = select_node._depth
        node.rep = 'dak.any(' + self.get_rep(select_node) + ', axis=' + repr(node._depth) + ')'
        return node

    def visit_Concat(self, node):
        tuple_node = ast.Tuple(elts=[node.first, node.second])
        self.visit(tuple_node)
        node._depth = tuple_node._depth
        node.rep = (
            'dak.concatenate(' + self.get_rep(tuple_node) + ', axis=' + repr(node._depth) + ')'
        )
        return node

    def visit_Zip(self, node):
        self.visit(node.source)
        node._depth = node.source._depth
        node.rep = (
            'dak.zip(' + self.get_rep(node.source) + ', depth_limit=' + repr(node._depth + 1) + ')'
        )
        return node

    def visit_Count(self, node):
        self.visit(node.source)
        node._depth = node.source._depth
        node.rep = 'dak.num(' + self.get_rep(node.source) + ', axis=' + repr(node._depth) + ')'
        return node

    def visit_Min(self, node):
        self.visit(node.source)
        node._depth = node.source._depth
        node.rep = 'dak.min(' + self.get_rep(node.source) + ', axis=' + repr(node._depth) + ')'
        return node

    def visit_Max(self, node):
        self.visit(node.source)
        node._depth = node.source._depth
        node.rep = 'dak.max(' + self.get_rep(node.source) + ', axis=' + repr(node._depth) + ')'
        return node

    def visit_Sum(self, node):
        self.visit(node.source)
        node._depth = node.source._depth
        node.rep = 'dak.sum(' + self.get_rep(node.source) + ', axis=' + repr(node._depth) + ')'
        return node

    def visit_Choose(self, node):
        self.visit(node.source)
        node._depth = node.source._depth
        combinations_rep = (
            'dak.combinations('
            + self.get_rep(node.source)
            + ', '
            + self.get_rep(node.n)
            + ', axis='
            + repr(node._depth)
            + ')'
        )
        node.rep = (
            'dak.concatenate([dak.singletons(i, axis='
            + str(node._depth)
            + ') for i in dak.unzip('
            + combinations_rep
            + ')], axis='
            + str(node._depth + 1)
            + ')'
        )
        return node

    def visit_OrderBy(self, node, ascending=True):
        if type(node.key_selector) is not ast.Lambda:
            raise TypeError(
                'Argument to OrderBy() must be a lambda function, found '
                + str(type(node.key_selector))
            )
        if len(node.key_selector.args.args) != 1:
            raise TypeError(
                'Lambda function in OrderBy() must have exactly one argument, found '
                + str(len(node.key_selector.args.args))
            )
        self.visit(node.source)
        node.key_selector.args.args[0]._depth = node.source._depth + 1
        subscriptable = node.key_selector.args.args[0].arg
        self.visit(node.key_selector)
        delattr(node.key_selector, 'rep')
        node.key_selector.body.rep = (
            'dak.argsort('
            + self.get_rep(node.key_selector.body)
            + ', axis='
            + repr(node.source._depth)
            + ', ascending='
            + str(ascending)
            + ')'
        )
        if sys.version_info[0] == 3 and sys.version_info[1] < 9:
            slice_node = ast.Index(node.key_selector.body)
        else:
            slice_node = node.key_selector.body
        node.key_selector.body = ast.Subscript(
            value=ast.Name(id=subscriptable), slice=slice_node, short_circuit=True
        )
        call_node = ast.Call(func=node.key_selector, args=[node.source])
        node.rep = self.get_rep(call_node)
        node._depth = node.source._depth
        return node

    def visit_OrderByDescending(self, node):
        if type(node.key_selector) is not ast.Lambda:
            raise TypeError(
                'Argument to OrderByDescending() must be a lambda function, found '
                + str(type(node.key_selector))
            )
        if len(node.key_selector.args.args) != 1:
            raise TypeError(
                'Lambda function in OrderByDescending() must have exactly one'
                + 'argument, found '
                + str(len(node.key_selector.args.args))
            )
        node = self.visit_OrderBy(node, ascending=False)
        return node

    def visit_First(self, node):
        self.visit(node.source)
        node._depth = node.source._depth
        node.rep = self.get_rep(node.source) + '[' + ':, ' * node._depth + '0]'
        return node

    def visit_ElementAt(self, node):
        self.visit(node.source)
        node._depth = node.source._depth
        node.rep = (
            self.get_rep(node.source) + '[' + ':, ' * node._depth + self.get_rep(node.index) + ']'
        )
        return node

    def visit_Contains(self, node):
        self.visit(node.source)
        node._depth = node.source._depth
        if isinstance(node.source, (ast.List, ast.Tuple)):
            comparison_nodes = [
                ast.Compare(left=elt, ops=[ast.Eq()], comparators=[node.value])
                for elt in node.source.elts
            ]
            or_node = ast.BoolOp(op=ast.Or(), values=comparison_nodes)
            node.rep = self.get_rep(or_node)
        elif isinstance(node.value, (ast.List, ast.Tuple)):
            comparison_nodes = ast.List(
                elts=[
                    ast.Compare(left=elt, ops=[ast.Eq()], comparators=[node.source])
                    for elt in node.value.elts
                ]
            )
            or_node = ast.BoolOp(op=ast.Or(), values=comparison_nodes)
            node.rep = self.get_rep(or_node)
        else:
            tuple_rep = self.get_rep(ast.Tuple(elts=[node.value, node.source]))
            condition_rep = (
                'if isinstance('
                + self.get_rep(node.value)
                + ', dak.Array) and isinstance('
                + self.get_rep(node.source)
                + ', dak.Array) and getattr('
                + self.get_rep(node.value)
                + ", 'ndim') >= getattr("
                + self.get_rep(node.source)
                + ", 'ndim')"
            )
            comparators_rep = (
                '*dak.unzip(dak.cartesian('
                + tuple_rep
                + ',  axis='
                + repr(node._depth)
                + ', nested=True)) '
                + condition_rep
                + ' else '
                + tuple_rep
            )
            compare_rep = '(lambda x, y: x == y)(' + comparators_rep + ')'
            any_axis_rep = repr(node._depth) + ' + (1 ' + condition_rep + ' else 0)'
            node.rep = 'dak.any(' + compare_rep + ', axis=' + any_axis_rep + ')'
        return node

    def visit_Last(self, node):
        self.visit(node.source)
        node._depth = node.source._depth
        node.rep = self.get_rep(node.source) + '[' + ':, ' * node._depth + ' - 1]'
        return node

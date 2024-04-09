from func_adl_uproot import UprootDataset


def test_uproot_dataset():
    ds = UprootDataset('tests/scalars_tree_file.root')
    assert ds.value().fields == [
        'int_branch',
        'long_branch',
        'float_branch',
        'double_branch',
        'bool_branch',
    ]

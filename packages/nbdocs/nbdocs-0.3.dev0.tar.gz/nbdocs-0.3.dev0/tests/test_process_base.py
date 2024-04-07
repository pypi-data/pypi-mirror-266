import copy
from nbdocs.convert import MdConverter
from nbdocs.tests.base import create_test_nb, create_test_outputs

converter = MdConverter()
test_nb = create_test_nb(code_source="some_code", code_outputs=create_test_outputs())
result_1 = """\
<!-- cell #0 code -->
```
some_code
```
<details open> <summary>output</summary>  

    - test/plain in output


    - text in stdout (stream) output


    
![png](output_1_2.png)
    

</details>
"""

expected_md_cells = (
    "<!-- cell #0 code -->\n\n\n```\nsome_code\n```\n\n\n    - test/plain in output\n\n\n    - text in stdout (stream) output\n\n\n    \n![png](output_1_2.png)\n    \n\n",
)


def test_preprocess_nb():
    """test preprocess_nb"""
    nb = copy.deepcopy(test_nb)
    converter.preprocess_nb(nb)
    assert len(nb.cells) == 2


def test_nb2mdcells():
    """test nb2mdcells"""
    nb = copy.deepcopy(test_nb)
    md_cells, _ = converter.nb2mdcells(nb)
    assert len(md_cells) == 1
    assert md_cells == expected_md_cells


def test_base():
    """test base convert"""
    nb = copy.deepcopy(test_nb)
    md, _ = converter.from_nb(nb)
    assert md == result_1

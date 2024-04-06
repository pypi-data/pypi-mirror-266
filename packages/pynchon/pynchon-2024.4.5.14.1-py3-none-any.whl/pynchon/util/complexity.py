""" pynchon.util.complexity
"""

import os
import ast
import sys
from collections import OrderedDict

import griffe
import mccabe

from pynchon import annotate, constants
from pynchon.abcs import Path
from pynchon.util import lme

WORKING_DIR = Path(".")
LOGGER = lme.get_logger(__name__)

GLYPH_COMPLEXITY = constants.GLYPH_COMPLEXITY


def clean_text(txt: str) -> str:
    """ """
    return "\n".join([line for line in txt.split("\n") if line.strip()])


def get_module_name_from_package(pkg_name):
    """ """
    import pkg_resources as pkg  # included in setuptools package

    metadata_dir = pkg.get_distribution(pkg_name).egg_info
    metadata_dir = Path(metadata_dir)
    with open(str(metadata_dir / "top_level.txt")) as fhandle:
        names = fhandle.read().rstrip().split("\n")
    return names[0]


def get_module(package: str = "", file: str = ""):
    """
    :param package: str:  (Default value = "")
    :param file: str:  (Default value = "")
    """
    if not bool(package) ^ bool(file):
        err = "Expected --file or --package, but not both"
        raise RuntimeError(err)
    if file:
        file = os.path.abspath(file)
        new_path = os.path.dirname(file)
        assert os.path.exists(file)
        LOGGER.warning(f"modifying sys.path to include {new_path}")
        sys.path.append(new_path)
        package = os.path.splitext(os.path.basename(file))[0]
        working_dir = os.path.dirname(file)
    else:
        working_dir = WORKING_DIR
    loader = griffe.loader.GriffeLoader()
    mod_name = get_module_name_from_package(package)
    module = loader.load_module(mod_name)
    annotate.module(package, module, working_dir=working_dir)
    return module


def get_refs(working_dir=None, module=None) -> dict:
    """

    :param working_dir: Default value = None)
    :param module: Default value = None)

    """
    refs = dict(
        classes={
            k: v for k, v in module.classes.items() if not module.classes[k].is_alias
        },
        modules={
            k: v for k, v in module.modules.items() if not module.modules[k].is_alias
        },
        functions=OrderedDict(
            [
                [k, v]
                for k, v in sorted(module.functions.items())
                if not module.functions[k].is_alias
            ]
        ),
    )
    for name, kls in refs["classes"].items():
        annotate.klass(name, kls)
    for name, mod in refs["modules"].items():
        annotate.module(name, mod, working_dir=working_dir)
    for name, fxn in refs["functions"].items():
        annotate.function(name, fxn)
    return refs


def visit_module(
    output=[],
    stats={},
    module=None,
    template=None,
    visited=[],
    exclude: list = [],
    module_name=None,
    working_dir=WORKING_DIR,
):
    """
    Recursive visitor for this package, submodules, classes, functions, etc

    :param output: Default value = [])
    :param stats: Default value = {})
    :param module: Default value = None)
    :param template: Default value = None)
    :param visited: Default value = [])
    :param exclude: list:  (Default value = [])
    :param module_name: Default value = None)
    :param working_dir: Default value = WORKING_DIR)
    :param exclude: list:  (Default value = [])

    """
    if any([module_name.split(".")[-1].startswith("_"), module_name in exclude]):
        LOGGER.debug(f"skipping module: {module_name}")
        return output
    annotate.module(module_name, module, working_dir=working_dir)
    refs = get_refs(working_dir=working_dir, module=module)
    # LOGGER.debug(f"exclude: {exclude}")
    LOGGER.debug(f"rendering module: {module_name}")
    # import IPython; IPython.embed()
    rendered = template.render(
        griffe=griffe,
        stats=stats,
        working_dir=working_dir,
        module_name=module_name,
        module=module,
        names=[
            x
            for x in module.members.keys()
            if not any([x in exclude, x.startswith("_")])
        ],
        **refs,
    )
    output.append(clean_text(rendered))
    for name, sub in refs["modules"].items():
        if sub in visited:
            continue
        visit_module(
            output=output,
            module=sub,
            working_dir=working_dir,
            module_name=f"{module_name}.{name}",
            visited=visited + [module],
            exclude=exclude,
            template=template,
        )
    return output


class Checker(mccabe.McCabeChecker):
    """ """

    def run(self):
        if self.max_complexity < 0:
            return
        visitor = mccabe.PathGraphingAstVisitor()
        visitor.preorder(self.tree, visitor)
        for graph in visitor.graphs.values():
            tmp = graph.complexity()
            if tmp > self.max_complexity:
                text = self._error_tmpl % (graph.entity, tmp)
                yield tmp, graph.lineno, graph.column, text, type(self)


def complexity(code: str = None, fname: str = None, threshold: int = 7):
    """

    :param code: str:  (Default value = None)
    :param fname: str:  (Default value = None)
    :param threshold: int:  (Default value = 7)
    :param code: str:  (Default value = None)
    :param fname: str:  (Default value = None)
    :param threshold: int:  (Default value = 7)

    """
    threshold = 7
    try:
        tree = compile(code, fname, "exec", ast.PyCF_ONLY_AST)
    except SyntaxError:
        e = sys.exc_info()[1]
        sys.stderr.write(f"Unable to parse {fname}: {e}\n")
        return 0
    complex = []
    Checker.max_complexity = threshold
    for complexity, lineno, _offset, text, check in Checker(tree, fname).run():
        complex.append(
            dict(
                file=os.path.relpath(fname),
                lineno=lineno,
                # text=text,
                score=complexity,
            )
        )
    out = []
    for admonition in complex:
        out.append(
            dict(
                glyph=GLYPH_COMPLEXITY,
                hover=f'score {admonition["score"]} / {threshold}',
                link=f'/{admonition["file"]}#L{admonition["lineno"]}',
            )
        )
    return out

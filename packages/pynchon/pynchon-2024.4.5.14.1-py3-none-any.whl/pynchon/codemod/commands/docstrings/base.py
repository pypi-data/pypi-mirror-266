""" pynchon.codemod.docstrings.base """

import argparse

from libcst.codemod import CodemodContext

from pynchon.util import lme

LOGGER = lme.get_logger(__name__)

from libcst.codemod import ContextAwareTransformer


class base(ContextAwareTransformer):  # VisitorBasedCodemodCommand):
    DESCRIPTION: str = """\n\tAbstract, don't use this directly"""

    def __init__(
        self,
        context: CodemodContext,
        # formatter: str = "black",
        # parameter_count: Optional[int] = None,
        # argument_count: Optional[int] = None,
    ) -> None:
        super().__init__(context)
        # self.parameter_count: int = parameter_count or presets["parameter_count"]
        # self.argument_count: int = argument_count or presets["argument_count"]

    @staticmethod
    def add_args(arg_parser: argparse.ArgumentParser) -> None:  # noqa
        """ """
        # arg_parser.add_argument(
        #     "--formatter",
        #     dest="formatter",
        #     metavar="FORMATTER",
        #     help="Formatter to target (e.g. yapf or black)",
        #     type=str,
        #     default="black",
        # )
        # arg_parser.add_argument(
        #     "--paramter-count",
        #     dest="parameter_count",
        #     metavar="PARAMETER_COUNT",
        #     help="Minimal number of parameters for us to add trailing comma",
        #     type=int,
        #     default=None,
        # )
        # arg_parser.add_argument(
        #     "--argument-count",
        #     dest="argument_count",
        #     metavar="ARGUMENT_COUNT",
        #     help="Minimal number of arguments for us to add trailing comma",
        #     type=int,
        #     default=None,
        # )

    # def leave_Parameters(
    #     self,
    #     original_node: cst.Parameters,
    #     updated_node: cst.Parameters,
    # ) -> cst.Parameters:
    # skip = (
    #     #
    #     self.parameter_count is None
    #     or len(updated_node.params) < self.parameter_count
    #     or (
    #         len(updated_node.params) == 1
    #         and updated_node.params[0].name.value in {"self", "cls"}
    #     )
    # )
    # if skip:
    #     return updated_node
    # else:
    #     last_param = updated_node.params[-1]
    #     return updated_node.with_changes(
    #         params=(
    #             *updated_node.params[:-1],
    #             last_param.with_changes(comma=cst.Comma()),
    #         ),
    #     )

    # def leave_SimpleString(
    #     self, onode, unode
    # ):
    #     import IPython; IPython.embed()

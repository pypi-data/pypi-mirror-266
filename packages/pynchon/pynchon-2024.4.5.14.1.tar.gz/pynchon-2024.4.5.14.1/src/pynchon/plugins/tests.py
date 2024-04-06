""" pynchon.plugins.tests
"""

from fleks import typing

from pynchon.util import lme

from pynchon import abcs, events, models  # noqa

LOGGER = lme.get_logger(__name__)


#
# class TestSuite(typing.BaseModel):
#     suite_name: str = typing.Field(default=None)
#     root: abcs.ResourceType = typing.Field(default=None, help="")
#     container: typing.Dict=typing.Field(default={}, help="")
#
# class DocTestSuite(TestSuite):
#     pass
#
#
class TestConfig(abcs.Config):
    # class Config:
    # arbitrary_types_allowed = True
    # include = 'suites'.split()
    config_key: typing.ClassVar[str] = "tests"


#     markdown: bool = typing.Field(
#         default=True,
#         # help='Configuration for testing markdown under {{docs/root}}',
#     )
#     html: bool = typing.Field(
#         default=False,
#         help='Configuration for testing HTML under {{docs/root}}',
#     )
#     suites: typing.List[TestSuite] = typing.Field(default=[])
#
#     @property
#     def suites(self):
#         tmp = self.__dict__.get("suites", [])
#         suite_names = [x.name for x in tmp]
#         if self.markdown and "markdown" not in suite_names:
#             LOGGER.critical("`markdown` is set but suite not found.  adding it..")
#             from pynchon.config import git
#
#             tmp += [TestSuite(name="markdown", root=git.root)]
#         return tmp
#         #     coverage={},
#         #     suite_patterns=[],
#         #     # suites={
#         #     #     "{{tests.root}}/units/": {
#         #     #           name:...
#         #     #           descr:...
#         #     #           runner:...
#         #     #      }
#         #     # }
#         #     root=None,
#


class Tests(models.Planner):
    """Management tool for project tests"""

    config_class = TestConfig
    name = "test"
    cli_name = "test"
    cli_label = "Project Tools"

    def _test_md(self, fname):
        """ """
        cfg = self.config
        LOGGER.warning(f"testing markdown: {fname}")

    # @cli.click.flag(
    #     "--markdown",
    # )
    # @cli.click.flag(
    #     "--html",
    # )
    # @cli.click.option(
    #     "--suffix",
    # )
    # @cli.options.plan
    # @cli.click.argument('file',default=None, required=False)
    def docs(
        self,
        markdown: bool = False,
        html: bool = False,
        suffix: str = None,
        should_plan: bool = False,
        file: str = None,
    ):
        """
        Run doc-tests for this project
        """
        files = [file] if file else self.list()
        plan = self.Plan()
        dct = {}
        for file in files:
            sfx = abcs.Path(file).suffix
            if sfx not in dct:
                dct[sfx] = []
            dct[sfx] += [file]
        if markdown:
            assert not any([file, suffix, html])
            suffix = ".md"
            files = dct[".md"]
        elif html:
            assert not any([file, suffix, markdown])
            suffix = ".html"

        if suffix:
            assert not file
            dct = {suffix: dct[suffix]}
        tmp = {}
        for suffix in dct.keys():
            hname = f"_test_{suffix[1:].replace('.', '_')}"
            suffix_handler = getattr(self, hname, None)
            if suffix_handler is None:
                LOGGER.critical(
                    f"missing doctest handler for {suffix}, {self.__class__.__name__}.{hname} is not present"
                )
            else:
                tmp[suffix_handler] = dct[suffix]
        dct = tmp

        for hdlr, flist in dct.items():
            for fname in flist:
                plan.append(
                    self.goal(
                        type="doctest",
                        resource=fname,
                        # command=f"pynchon parse markdown"
                        callable=hdlr,
                    )
                )

        if should_plan:
            return plan

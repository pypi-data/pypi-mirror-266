""" pynchon.plugins.markdown
"""

import marko
from fleks import tagging

from pynchon import abcs, api, cli, events, models  # noqa
from pynchon.util import files, lme, text, typing  # noqa

LOGGER = lme.get_logger(__name__)

ElementList = typing.List[typing.Dict]


class Markdown(models.DockerWrapper, models.Planner):
    """Markdown Tools"""

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "markdown"
        goals: typing.List[str] = typing.Field(
            default=[], description="Extra goals related to markdown"
        )
        include_patterns: typing.List[str] = typing.Field(
            default=[], description="Patterns to include"
        )
        exclude_patterns: typing.List[str] = typing.Field(
            default=[], description="File globs to exclude from listing"
        )
        root: typing.Union[str, abcs.Path, None] = typing.Field(
            default=None, description=""
        )
        linter_docker_image: str = typing.Field(
            default="peterdavehello/markdownlint",
            description="Container to use for markdown linter",
        )
        linter_args: typing.List[str] = typing.Field(
            description="Arguments to pass to `linter_docker_image`",
            default=[
                "--disable MD013",  # line-length
                "--disable MD045",  # Images should have alternate text
                "--disable MD033",  # Allow HTML
                "--disable MD041",  # first-line-h1
                "--disable MD042",  # No empty links
                "--fix",
            ],
        )
        goals: typing.List[typing.Dict] = typing.Field(default=[], description="")

    name = "markdown"
    cli_name = "markdown"
    cli_label = "Docs Tools"
    priority = 0

    @tagging.tags(click_aliases=["ls"])
    def list(self, changes=False):
        """
        Lists affected resources (**.md) for this project
        """
        default = self[:"project"]
        proj_conf = self[:"project.subproject":default]
        project_root = proj_conf.get("root", None) or self[:"git.root":"."]
        # project_root = proj_conf.get("root", None) or '.'
        globs = [
            abcs.Path(project_root).joinpath("**/*.md"),
        ]
        self.logger.debug(f"search patterns are {globs}")
        result = files.find_globs(globs)
        self.logger.debug(f"found {len(result)} j2 files (pre-filter)")
        excludes = self["exclude_patterns"]
        self.logger.debug(f"filtering search with {len(excludes)} excludes")
        result = [p for p in result if not p.match_any_glob(excludes)]
        self.logger.debug(f"found {len(result)} j2 files (post-filter)")
        if not result:
            err = f"{self.__class__.__name__} is active, but found no .j2 files!"
            self.logger.critical(err)
        return result

    @cli.click.argument("paths", nargs=-1)
    def normalize(self, paths):
        """Use `markdownlint` to normalize input paths"""
        docker_image = self["linter_docker_image"]
        linter_args = " ".join(self["linter_args"])
        goals = []
        for path in paths:
            goals.append(
                self.goal(
                    resource=path,
                    type="normalize",
                    command=(
                        f"docker run -v `pwd`:/workspace "
                        f"-w /workspace {docker_image} "
                        f"markdownlint {linter_args} {path}"
                    ),
                )
            )
        return self.apply(plan=self.plan(goals=goals))

    @cli.click.argument("paths", nargs=-1)
    @tagging.tags(click_aliases=["show"])
    def preview(self, paths):
        """
        Previews markdown in the terminal
        """
        # FIXME?: rich doesn't link hypertext.  patch upstream?
        from rich.console import Console
        from rich.markdown import Markdown

        console = Console()
        for p in paths:
            with open(p) as fhandle:
                md = Markdown(fhandle.read())
                console.print(md)
        # FIXME: glow is awesome but using it from docker seems to strip color
        # viewer_docker_image: str = typing.Field(
        #     default='charmcli/glow',
        #     help="Container to use for markdown console viewer")
        # docker_image = self["viewer_docker_image"]
        #         # viewer_args = " ".join(self["viewer_args"])
        #         return self._run_docker(
        #                         f"docker run -t -v `pwd`:/workspace "
        #                         f"-w /workspace {docker_image} "
        #                         f" {' '.join(paths)}"
        #                     )

    @cli.click.flag("-p", "--python", help="only python codeblocks")
    @cli.click.flag("-b", "--bash", help="only bash codeblocks")
    @cli.click.argument("file")
    def doctest(
        self,
        file: str = None,
        python: bool = False,
        bash: bool = False,
    ) -> ElementList:
        """Runs doctest for fenced code inside the given markdown files"""
        assert python or bash
        element_lst = self.parse(file=file, python=python, bash=bash)
        if not element_lst:
            LOGGER.critical(f"filtered element list is empty! {element_lst}")

        def _doctest(element):
            LOGGER.critical(element)
            child = element["children"][0]
            assert child["element"] == "raw_text"
            script: str = child["children"]
            raise Exception(script)
            # return #shil.invoke(script,...))

        for el in element_lst:
            el.update(_doctest(el))
        return element_lst

    @tagging.tags(click_aliases=["parse.markdown"])
    @cli.click.flag("-c", "--codeblocks", help="only codeblocks")
    @cli.click.flag("-p", "--python", help="only python codeblocks")
    @cli.click.flag("-b", "--bash", help="only bash codeblocks")
    @cli.click.flag("-l", "--links", help="only links")
    @cli.click.flag("--all", "-a", help="run for each file found by `list`")
    @cli.click.argument("files", nargs=-1)
    def parse(
        self,
        files: typing.Tuple = tuple(),
        all: bool = False,
        codeblocks: bool = False,
        python: bool = False,
        links: bool = False,
        bash: bool = False,
    ) -> ElementList:
        """Parses given markdown file into JSON"""
        from bs4 import BeautifulSoup  # noqa
        from marko.ast_renderer import ASTRenderer  # noqa

        codeblocks = codeblocks or python or bash
        assert files or all and not (files and all)
        if files:
            files = list(files)
        else:
            files = self.list()
            LOGGER.warning(f"parsing all markdown from: {files} ")
        out = {}
        for file in files:
            LOGGER.warning(f"parsing: {file}")
            file = str(file)
            with open(file) as fhandle:
                content = fhandle.read()
            if links:
                parsed = marko.Markdown()(content)
                soup = BeautifulSoup(parsed, features="html.parser")
                out[file] = []
                for a in soup.find_all("a", href=True):
                    this_link = a["href"]
                    if this_link.strip() == "#":
                        LOGGER.warning(f"{file}: has placeholder link '#' ")
                    else:
                        out[file] += [this_link]
            else:
                parsed = marko.Markdown(renderer=ASTRenderer)(content)
                children = parsed["children"]
                out[file] = []
                for child in children:
                    if child.get("element") == "fenced_code":
                        lang = child.get("lang")
                        if lang is not None:
                            out[file] += [child]
                LOGGER.critical(child)
                if python:
                    out[file] += [ch for ch in out if child.get("lang") == "python"]
                if bash:
                    out[file] += [ch for ch in out if child.get("lang") == "bash"]
        return {k: v for k, v in out.items() if v}

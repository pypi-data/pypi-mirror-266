""" pynchon.util.files
"""

import re
import glob
import functools

import shil

from pynchon import abcs, cli

from pynchon.util import lme, os, typing  # noqa

from .diff import diff, diff_percent, diff_report  # noqa

LOGGER = lme.get_logger(__name__)


@cli.click.argument("prepend_file", nargs=1)
@cli.click.argument("target_file", nargs=1)
@cli.click.option(
    "--clean",
    is_flag=True,
    default=False,
    help="when provided, prepend_file will be removed afterwards",
)
def is_prefix(
    prepend_file: str = None,
    target_file: str = None,
    clean: bool = False,  # noqa
) -> str:
    """
    True if given file already prepends given target
    """
    with open(prepend_file) as fhandle:
        prep_c = fhandle.read()
    with open(target_file) as fhandle:
        target_c = fhandle.read()
    return target_c.lstrip().startswith(prep_c.lstrip())


@cli.click.argument("prepend_file", nargs=1)
@cli.click.argument("target_file", nargs=1)
@cli.click.option(
    "--clean",
    is_flag=True,
    default=False,
    help="when provided, prepend_file will be removed afterwards",
)
def prepend(
    prepend_file: str = None,
    target_file: str = None,
    clean: bool = False,  # noqa
) -> bool:
    """
    Prepends given file contents to given target
    """
    if not is_prefix(prepend_file=prepend_file, target_file=target_file):
        with open(prepend_file) as fhandle:
            prep_c = fhandle.read()
        with open(target_file) as fhandle:
            target_c = fhandle.read()
        with open(target_file, "w") as fhandle:
            fhandle.write(f"""{prep_c}\n{target_c}""".lstrip())
        return True
    return False


def find_suffix(root: str = "", suffix: str = "") -> typing.StringMaybe:
    """ """
    assert root and suffix
    return shil.invoke(f"{root} -type f -name *.{suffix}", strict=True).stdout.split(
        "\n"
    )


@functools.lru_cache(maxsize=None)
def get_git_root(path: str = ".") -> typing.StringMaybe:
    """ """
    path = abcs.Path(path).absolute()
    tmp = path / ".git"
    if tmp.exists():
        return tmp
    elif not path:
        return None
    else:
        try:
            return get_git_root(path.parents[0])
        except IndexError:
            LOGGER.warning(f"Could not find a git-root for '{path}'")


def find_src(
    src_root: str,
    exclude_patterns=[],
    quiet: bool = False,
) -> list:
    """ """
    exclude_patterns = set(list(map(re.compile, exclude_patterns)))
    globs = [
        abcs.Path(src_root).joinpath("**/*"),
    ]
    quiet or LOGGER.info(f"finding src under {globs}")
    globs = [glob.glob(str(x), recursive=True) for x in globs]
    matches = functools.reduce(lambda x, y: x + y, globs)
    matches = [str(x.absolute()) for x in map(abcs.Path, matches) if not x.is_dir()]
    # LOGGER.debug(matches)
    matches = [
        m for m in matches if not any([p.match(str(m)) for p in exclude_patterns])
    ]
    return matches


@typing.validate_arguments
def find_globs(
    globs: typing.List[abcs.Path],
    includes=[],
    logger: object = None,
    quiet: bool = False,
) -> typing.List[str]:
    """ """
    logger = logger or LOGGER
    quiet or logger.info(f"finding files matching {globs}")
    globs = [glob.glob(str(x), recursive=True) for x in globs]
    matches = functools.reduce(lambda x, y: x + y, globs, [])
    for i, m in enumerate(matches):
        for d in includes:
            if abcs.Path(d).has_file(m):
                includes.append(m)
    result = []
    for m in matches:
        assert m
        if m not in includes:
            result.append(abcs.Path(m))
    return result


def dumps(
    content: str = None, file: str = None, quiet: bool = True, logger=LOGGER.info
) -> None:
    """ """
    quiet or logger(f"\n{content}")
    with open(file, "w") as fhandle:
        fhandle.write(content)
    quiet or logger(f'Wrote "{file}"')

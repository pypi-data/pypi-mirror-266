""" pynchon.util.text.loadf

    Helpers for loading data structures from files
"""

import os

import tomli as tomllib  # NB: tomllib only available in py3.11
from fleks.cli import click, options

from pynchon.util.os import invoke
from pynchon.util.text import loads

from pynchon.util import lme, text, typing  # noqa

LOGGER = lme.get_logger(__name__)


def loadf(file=None, content=None):
    """ """
    if file:
        assert not content
        if not os.path.exists(file):
            raise ValueError(f"file @ {file} is missing!")
        with open(file) as fhandle:
            content = fhandle.read()
    return content


@click.argument("file", nargs=1)
def ini(file):
    """Parses ini file and returns JSON

    :param file:

    """
    import configparser

    parser = configparser.ConfigParser()
    parser.read(file)
    ini_conf = {section: dict(parser.items(section)) for section in parser.sections()}
    return ini_conf


def yaml(fname: str) -> typing.Dict:
    """parses yaml file and returns JSON
    :param *args:
    :param **kwargs:
    """
    from pynchon.util.text import loads

    with open(fname) as fhandle:
        contents = fhandle.read()
    return loads.yaml(contents)


@click.argument("file", nargs=1)
def toml(file: str = None, strict: bool = True):
    """Parses toml file and returns JSON

    :param file: str:  (Default value = None)
    :param strict: bool:  (Default value = True)
    """

    config = {}
    if not os.path.exists(file):
        err = f"Cannot load config from nonexistent path @ `{file}`"
        LOGGER.critical(err)
        if strict:
            raise
        else:
            return config
    with open(file, "rb") as f:
        try:
            config = tomllib.load(f)
        except (tomllib.TOMLDecodeError,) as exc:
            LOGGER.critical(f"cannot decode data from toml @ {file}")
            raise
    return config


# @click.argument("file", nargs=1)
# def json5(file: str = '',) -> dict:
#     """
#     loads json5 from file
#     """
#     assert file
#     if not os.path.exists(file):
#         raise ValueError(f'file @ {file} is missing!')
#     with open(file, 'r') as fhandle:
#         content = fhandle.read()
#     data = loads.json5(content)
#     return data


@click.option(
    "--wrap-with-key",
    "wrapper_key",
    help="when set, wraps output as `{WRAPPER_KEY:output}`",
    default="",
)
@options.output
@options.should_print
@click.option("--pull", help="when provided, this key will be output", default="")
@click.option(
    "--push-data", help="(string) this raw data will be added to output", default=""
)
@click.option(
    "--push-file-data",
    help="(filename) contents of file will be added to output",
    default="",
)
@click.option(
    "--push-json-data",
    help="(string) jsonified data will be added to output",
    default="",
)
@click.option(
    "--push-command-output", help="command's stdout will be added to output", default=""
)
@click.option("--under-key", help="required with --push commands", default="")
@click.argument("files", nargs=-1)
def json5(
    file: str = "",
    files: typing.List[str] = [],
    output: str = "",
    should_print: bool = False,
    wrapper_key: str = "",
    pull: str = "",
    push_data: str = "",
    push_file_data: str = "",
    push_json_data: str = "",
    push_command_output: str = "",
    under_key: str = "",
) -> None:
    """Parses JSON-5 file(s) and outputs json. Pipe friendly.

    If multiple files are provided, files will
    be merged (with overwrites) in the order provided.

    Several other options are available for common post-processing tasks.

    :param output: str:  (Default value = '')
    :param should_print: bool:  (Default value = False)
    :param file: str:  (Default value = '')
    :param files: typing.List[str]:  (Default value = [])
    :param wrapper_key: str:  (Default value = '')
    :param pull: str:  (Default value = '')
    :param push_data: str:  (Default value = '')
    :param push_file_data: str:  (Default value = '')
    :param push_json_data: str:  (Default value = '')
    :param push_command_output: str:  (Default value = '')
    :param under_key: str:  (Default value = '')
    :param output: str:  (Default value = '')
    :param should_print: bool:  (Default value = False)
    :param file: str:  (Default value = '')
    :param files: typing.List[str]:  (Default value = [])
    :param wrapper_key: str:  (Default value = '')
    :param pull: str:  (Default value = '')
    :param push_data: str:  (Default value = '')
    :param push_file_data: str:  (Default value = '')
    :param push_json_data: str:  (Default value = '')
    :param push_command_output: str:  (Default value = '')
    :param under_key: str:  (Default value = '')

    """
    out: typing.Dict[str, typing.Any] = {}
    files = files or (file and [file]) or []
    for file in files:
        with open(file) as fhandle:
            obj = loads.json5(fhandle.read())
        out = {**out, **obj}

    push_args = [push_data, push_file_data, push_json_data, push_command_output]
    if any(push_args):
        assert under_key
        assert under_key not in out, f"content already has key@{under_key}!"
        assert (
            sum([1 for x in push_args if x]) == 1
        ), "only one --push arg can be provided!"
        if push_data:
            assert isinstance(push_data, (str,))
            push = push_data
        elif push_command_output:
            cmd = invoke(push_command_output)
            if cmd.succeeded:
                push = cmd.stdout
            else:
                err = cmd.stderr
                LOGGER.critical(err)
                raise SystemExit(1)
        elif push_json_data:
            push = loads.json5(content=push_json_data)
        elif push_file_data:
            err = f"file@{push_file_data} doesnt exist"
            assert os.path.exists(push_file_data), err
            with open(push_file_data) as fhandle:
                push = fhandle.read()
        out[under_key] = push

    if wrapper_key:
        # NB: must remain after push
        out = {wrapper_key: out}

    if pull:
        out = out[pull]
        # similar to `jq -r`.
        # we don't want quoted strings, but
        # if the value is complex, we need json-encoding
        if not isinstance(out, (str,)):
            msg = text.to_json(out)
        else:
            msg = str(out)
    else:
        msg = text.to_json(out)
    output = output or "/dev/stdout"
    print(msg, file=open(output, "w"))
    if should_print and output != "/dev/stdout":
        print(msg)
    return out


@options.strict
@click.argument("file", nargs=1)
def json(file: str = "", content: str = "", strict: bool = True) -> dict:
    """loads json to python dictionary from given file or string

    :param file: str:  (Default value = '')
    :param content: str:  (Default value = '')
    :param strict: bool:  (Default value = True)
    :param file: str:  (Default value = '')
    :param content: str:  (Default value = '')
    :param strict: bool:  (Default value = True)

    """
    content = content or text.loadf.loadf(file=file, content=content)
    try:
        data = loads.json(content)
        # data = pyjson5.loads(content)
    # except (pyjson5.Json5EOF,) as exc:
    except (ValueError,) as exc:
        LOGGER.critical(f"Cannot parse json from {file}!")
        raise
    return data

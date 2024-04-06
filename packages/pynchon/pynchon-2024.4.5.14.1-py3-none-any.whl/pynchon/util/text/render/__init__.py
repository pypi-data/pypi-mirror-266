""" pynchon.util.text.render

    Helpers for rendering content
"""

import os
import sys

from fleks.cli import click, options
from fleks.util.tagging import tags

from pynchon.util.os import invoke

from pynchon.util import lme, text, typing  # noqa

LOGGER = lme.get_logger(__name__)

from pynchon.api import render as api
from pynchon.util.text import loadf, loads


@typing.validate_arguments
def jinja(
    text: str = "",
    file: str = "?",
    context: dict = {},
    includes: typing.List[str] = [],
    strict: bool = True,
):
    """Renders jinja-templates (with support for includes)

    :param text: str:  (Default value = "")
    :param file: str:  (Default value = "?")
    :param context: dict:  (Default value = {})
    :param strict: bool:  (Default value = True)
    :param includes: typing.List[str]:  (Default value = [])

    """
    import jinja2

    template = api.get_template_from_string(
        text,
        env=api.get_jinja_env(*includes),
        template_name=file,
    )
    context = {
        # FIXME: try to santize this
        **dict(os.environ.items()),
        **dict(__template__=file),
        **context,
    }
    try:
        return template.render(**context)
    except (jinja2.exceptions.UndefinedError,) as exc:
        LOGGER.critical(f"Undefined exception: {exc}")
        LOGGER.critical(f"Jinja context: {list(context.keys())}")
        # import IPython; IPython.embed()
        raise
    except (jinja2.exceptions.TemplateNotFound,) as exc:
        LOGGER.critical(f"Template exception: {exc}")
        LOGGER.critical(f"Jinja-includes: {includes}")
        err = getattr(exc, "templates", exc.message)
        LOGGER.critical(f"Problem template: {err}")
        raise


@typing.validate_arguments
def jinja_loadf(
    file: str,
    context: typing.Dict = {},
    includes: typing.List[str] = [],
    strict: bool = True,
    quiet: bool = False,
) -> str:
    """
    :param file: str:
    :param context: typing.Dict:  (Default value = {})
    :param includes: typing.List[str]:  (Default value = [])
    :param strict: bool:  (Default value = True)
    :param quiet: bool:  (Default value = False)
    """
    context = {} if context is None else context
    LOGGER.debug(f"Running with one file: {file} (strict={strict})")
    with open(file) as fhandle:
        content = fhandle.read()
    quiet and LOGGER.debug(f"render context: \n{text.to_json(context)}")
    tmp = list(context.keys())
    quiet and LOGGER.debug(f"Rendering with context:\n{text.to_json(tmp)}")
    content = jinja(text=content, file=file, context=context, includes=includes)
    # template = api.get_template(
    #     from_string=text,
    #     env=api.get_jinja_env(*includes))
    return content


@options.output
@options.should_print
@options.includes
@click.option("--context", help="context literal.  must be JSON")
@click.option("--context-file", help="context file.  must be JSON")
@click.argument("file", nargs=1)
@tags(
    click_aliases=["jinja"],
)
def jinja_file(
    file: str,
    output: typing.StringMaybe = "",
    should_print: typing.Bool = False,
    context: typing.Dict = {},
    context_file: typing.Dict = {},
    includes: typing.List[str] = [],
    strict: bool = True,
) -> str:
    """Renders jinja2 file (supports includes, custom filters)"""
    if isinstance(context, (str,)):
        LOGGER.warning("provided `context` is a string, loading it as JSON")
        context = loads.json(context)

    if context_file:
        assert not context
        context = loadf.json(context_file)

    content = jinja_loadf(
        file=file,
        context=context,
        includes=includes,
        strict=strict,
    )
    assert output
    output = os.path.splitext(output)
    if output[-1] == ".j2":
        output = output[0]
    else:
        output = "".join(output)
    LOGGER.warning(f"writing output to {output or sys.stdout.name}")
    from pynchon import abcs

    test = all([abcs.Path(output).exists(), output, output not in ["/dev/stdout", "-"]])
    if test:
        with open(output) as fhandle:
            before = fhandle.read()
    else:
        before = None
    fhandle = open(output, "w") if output else sys.stdout
    content = f"{content}\n"
    fhandle.write(content)
    fhandle.close()
    if before and content == before:
        LOGGER.critical(f"content in {output} did not change")
    return content


@options.output
@options.should_print
@click.option("--context", help="context file.  must be JSON")
@click.argument("file", nargs=1)
@tags(
    click_aliases=["j2"],
)
def j2cli(
    output: str, should_print: bool, file: str, context: str, format: str = "json"
) -> None:
    """
    A wrapper on the `j2` command (j2cli must be installed)
    Renders the named file, using the given context-file.

    NB: No support for jinja-includes or custom filters.

        :param output: str:
        :param should_print: bool:
        :param file: str:
        :param context: str:
        :param format: str:  (Default value = 'json')
    """
    cmd = f"j2 --format {format} {file} {context}"
    result = invoke(cmd)
    if not result.succeeded:
        LOGGER.critical(f"failed to execute: {cmd}")
        raise SystemExit(1)
    result = result.stdout
    assert result
    tmp = file.replace(".j2", "")
    if tmp.endswith(".json") or tmp.endswith(".json5"):
        LOGGER.debug(f"target @ {file} appears to be specifying json.")
        LOGGER.debug("loading as if json5 before display..")
        result = text.loads.json5(content=result)
        result = text.to_json(result)
    msg = result
    print(msg, file=open(output, "w"))
    if should_print and output != "/dev/stdout":
        print(msg)


# assign utils back to sibling modules for convenience
# FIXME: is this smart?
loadf.jinja = jinja
loads.jinja = jinja

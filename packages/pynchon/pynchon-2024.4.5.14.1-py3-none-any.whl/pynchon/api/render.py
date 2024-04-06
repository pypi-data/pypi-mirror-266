""" pynchon.api.render

    Basically this is core jinja-rendering stuff.

    Looking for CLI entrypoints?  See pynchon.util.text.render
    Looking for the JinjaPlugin?  See pynchon.plugins.jinja
"""

import os
import functools

from jinja2 import Environment  # Template,; UndefinedError,
from jinja2 import FileSystemLoader, StrictUndefined

from pynchon import abcs, constants, events
from pynchon.util.os import invoke

import jinja2  # noqa

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


def is_templated(txt: str = "") -> bool:
    """ """
    return txt is not None and ("{{" in txt and "}}" in txt)


def dictionary(input, context):
    """
    :param context:
    """
    from pynchon.abcs.visitor import JinjaDict

    return JinjaDict(input).render(context)


@functools.lru_cache(maxsize=None)
def get_jinja_filters():
    def strip_empty_lines(s):
        lines = s.split("\n")
        filtered_lines = [line for line in lines if line.strip() != ""]
        return "\n".join(filtered_lines)

    return dict(
        Path=abcs.Path,
        strip_empty_lines=strip_empty_lines,
    )


@functools.lru_cache(maxsize=None)
def get_jinja_globals():
    """ """
    events.lifecycle.send(__name__, msg="finalizing jinja globals")

    def is_markdown_list_item(text: str):
        return text.rstrip().startswith("* ")

    def invoke_helper(*args, **kwargs) -> typing.StringMaybe:
        """A jinja filter/extension"""
        strict = kwargs.pop("strict", True)
        out = invoke(*args, **kwargs)
        if not out.succeeded:
            raise Exception(out)
        return out.stdout

    def markdown_toc(fname: str, level=None):
        """ """
        import markdown

        with open(fname) as fhandle:
            contents = fhandle.read()
        md = markdown.Markdown(
            extensions=["toc", "fenced_code"],
            extension_configs={"toc": {"toc_depth": level}},
        )
        html = md.convert(contents)
        return md.toc

    # markdown-toc --type github  --no-write docs/blog/ambient-calculus-1.md
    # assert fname
    # fname = abcs.Path(fname)
    # assert fname.exists()
    # # script = abcs.Path(pynchon.__file__).parents[0] / "scripts" / "gh-md-toc.sh"
    # result = invoke(
    #     f"markdown-toc --type github --no-write {fname}",
    #     command_logger=LOGGER.critical
    # )
    # assert result.succeeded
    # return result.stdout
    return dict(
        str=str,
        sh=invoke_helper,
        bash=invoke_helper,
        is_markdown_list_item=is_markdown_list_item,
        invoke=invoke_helper,
        map=map,
        markdown_toc=markdown_toc,
        eval=eval,
        env=os.getenv,
        filter=filter,
    )


def get_jinja_includes(*includes):
    """ """
    includes = list(includes)
    includes += list(constants.PYNCHON_CORE_INCLUDES_DIRS)

    return [abcs.Path(t) for t in includes]


@functools.lru_cache(maxsize=None)
def get_jinja_env(*includes, quiet: bool = False):
    """ """
    events.lifecycle.send(__name__, msg="finalizing jinja-Env")
    includes = get_jinja_includes(*includes)
    for template_dir in includes:
        if not template_dir.exists:
            err = f"template directory @ `{template_dir}` does not exist"
            raise ValueError(err)
    # includes and (not quiet) and LOGGER.warning(f"Includes: {includes}")
    env = Environment(
        loader=FileSystemLoader([str(t) for t in includes]),
        undefined=StrictUndefined,
        # trim_blocks=True,
        # lstrip_blocks=True
    )

    # from jinja2 import Environment, FileSystemLoader
    # Function to include a template
    def include_template(template_name):
        # env = Environment(loader=FileSystemLoader('templates'))  # Assuming templates are in 'templates' directory
        template = env.get_template(template_name)
        return template.render()

    env.filters["include"] = include_template

    env.filters.update(**get_jinja_filters())
    env.pynchon_includes = includes

    env.globals.update(**get_jinja_globals())

    known_templates = list(map(abcs.Path, set(env.loader.list_templates())))

    if known_templates:
        from pynchon.util import text as util_text

        msg = "Known template search paths (includes folders only): "
        tmp = list({p.parents[0] for p in known_templates})
        LOGGER.info(msg + util_text.to_json(tmp))
    return env


def get_template(
    template_name: typing.Union[str, abcs.Path] = None,
    env=None,
    from_string: str = None,
    **jinja_context,
):
    """ """
    env = env or get_jinja_env()
    if isinstance(template_name, (abcs.Path,)):
        template_path = template_name
        template_name = str(template_name)
    elif template_name:
        template_path = abcs.Path(template_name)
    else:
        template_path = None
    try:
        if from_string:
            template = env.from_string(from_string)
        else:
            LOGGER.info(f"Looking up {template_path}")
            template = env.get_template(template_name)
    except (jinja2.exceptions.TemplateNotFound,) as exc:
        LOGGER.critical(f"Template exception: {exc}")
        LOGGER.critical(f"Jinja-includes: {env.pynchon_includes}")
        err = getattr(exc, "templates", exc.message)
        LOGGER.critical(f"Problem template: {err}")
        raise
    jinja_context.update(__template__=template_path)
    all_extensions = filter(
        None, template_path.name[template_path.name.find(".") :].split(".")
    )
    if template_path and "md" in all_extensions:
        LOGGER.warning("template is markdown, trying to parse metadata")
        import markdown

        from pynchon.util.text import loads

        try:
            # https://python-markdown.github.io/extensions/meta_data/#accessing-the-meta-data
            md = markdown.Markdown(extensions=["meta"])
            html = md.convert(open(template_name).read())
            md_meta = md.Meta
            md_meta and LOGGER.warning(f"extracted metadata: {md_meta}")
            # the metadata extension doesn't really do much parsing,
            # so we treat it here as potentially yaml
            tmp = {}
            for k, v in md_meta.items():
                z = "\n".join(v)
                tmp.update(**loads.yaml(f"{k}: {z}"))
            md_meta = tmp
            jinja_context.update(**md_meta)
        except (Exception,) as exc:
            LOGGER.warning(f"failed extracting markdown metadata: {exc}")

    def panic():
        raise Exception(jinja_context)

    def jinja_debug():
        LOGGER.critical(f"jinja_debug: {jinja_context}")
        return str(jinja_context)

    env.globals.update(
        jinja_debug=jinja_debug,
        panic=panic,
    )

    template.render = functools.partial(template.render, **jinja_context)
    return template


def get_template_from_string(content, **kwargs):
    """ """
    return get_template(from_string=content, **kwargs)


def get_template_from_file(
    file: str = None,
    **kwargs,
):
    """
    :param file: str = None:
    :param **kwargs:
    """
    with open(file) as fhandle:
        content = fhandle.read()
    return get_template_from_string(content, file=file, **kwargs)


def clean_whitespace(txt: str):
    # return txt
    return "\n".join([x for x in txt.split("\n") if x.strip()])

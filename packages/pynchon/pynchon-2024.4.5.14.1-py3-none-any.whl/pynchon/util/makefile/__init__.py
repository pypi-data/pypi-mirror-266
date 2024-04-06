""" pynchon.util.makefile
"""

import os
import re

from pynchon import abcs, cli
from pynchon.util.os import invoke

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)
zzz = "#  recipe to execute (from '"
vvv = "# Variables"
fff = "# files hash-table stats:"


@cli.click.argument("makefile")
def database(makefile: str = "", make="make") -> typing.List[str]:
    """
    Get database for Makefile (i.e. 'make --print-data-base')
    """
    assert makefile
    tmp = abcs.Path(makefile)
    if not all(
        [
            tmp.exists,
            tmp.is_file,
        ]
    ):
        raise ValueError(f"{makefile} does not exist")
    else:
        LOGGER.warning(f"parsing makefile @ {makefile}")
    cmd = f"{make} --print-data-base -pqRrs -f {makefile}"
    resp = invoke(cmd)
    out = resp.stdout.split("\n")
    return out


def _test(x):
    """ """
    return all(
        [
            ":" in x.strip(),
            not x.startswith("#"),
            not x.startswith("."),
            not x.startswith("\t"),
        ]
    )


def _get_prov_line(body):
    # zzz = "#  recipe to execute (from '"
    pline = [x for x in body if zzz in x]
    pline = pline[0] if pline else None
    return pline


def _get_file(body=None, makefile=None):
    pline = _get_prov_line(body)
    if pline:
        return pline.split(zzz)[-1].split("'")[0]
    else:
        return str(makefile)


@cli.click.argument("makefile")
def parse(makefile: str = None, bodies=False, **kwargs):
    """
    Parse Makefile to JSON.  Includes targets/prereq detail
    """
    assert os.path.exists(makefile)
    wd = abcs.Path(".")
    db = database(makefile, **kwargs)
    original = open(makefile).readlines()
    variables_start = db.index(vvv)
    variables_end = db.index("", variables_start + 2)
    vars = db[variables_start:variables_end]
    db = db[variables_end:]
    implicit_rule_start = db.index("# Implicit Rules")
    file_rule_start = db.index("# Files")
    file_rule_end = db.index(fff)
    for i, line in enumerate(db[implicit_rule_start:]):
        if "implicit rules, " in line and line.endswith(" terminal."):
            implicit_rule_end = implicit_rule_start + i
            break
    else:
        LOGGER.critical("cannot find `implicit_rule_end`!")
        implicit_rule_end = implicit_rule_start
    implicit_targets_section = db[implicit_rule_start:implicit_rule_end]
    file_targets_section = db[file_rule_start:file_rule_end]
    file_target_names = list(filter(_test, file_targets_section))
    implicit_target_names = list(filter(_test, implicit_targets_section))
    targets = file_target_names + implicit_target_names
    out = {}
    for tline in targets:
        bits = tline.split(":")
        target_name = bits.pop(0)
        childs = ":".join(bits)
        type = "implicit" if tline in implicit_targets_section else "file"
        # NB: line nos are from reformatted output, not original file
        line_start = db.index(tline)
        line_end = db.index("", line_start)
        body = db[line_start:line_end]
        pline = _get_prov_line(body)
        file = _get_file(body=body, makefile=makefile)
        if pline:
            # take advice from make's database.
            # we return this because it's authoritative,
            # but actually sometimes it's wrong.  this returns
            # the first like of the target that's tab-indented,
            # but sometimes make macros like `ifeq` are not indented..
            lineno = pline.split("', line ")[-1].split("):")[0]
        else:
            try:
                lineno = original.index(tline)
            except ValueError:
                LOGGER.critical(f"cant find {tline} in {file}, parametric?")
                # target_name
                lineno = None
        lineno = lineno and (int(lineno) - 1)
        prereqs = [x for x in childs.split() if x.strip()]
        out[target_name] = dict(
            file=file,
            lineno=lineno,
            body=body,
            type=type,
            docs=[x[len("\t@#") :] for x in body if x.startswith("\t@#")],
            prereqs=prereqs,
        )
        if type == "implicit":
            regex = target_name.replace("%", ".*")
            out[target_name].update(regex=regex)
    for target_name, tmeta in out.items():
        if "regex" in tmeta:
            implementors = []
            for impl in out:
                if impl != target_name and re.compile(tmeta["regex"]).match(impl):
                    implementors.append(impl)
            tmeta["implementors"] = implementors

    for target_name, tmeta in out.items():
        real_body = [
            b
            for b in tmeta["body"][1:]
            if not b.startswith("#") and not b.startswith("@#")
        ]
        if not real_body:
            LOGGER.critical(f"missing body for: {target_name}")
            for chain in out:
                if target_name in out[chain].get("implementors", []):
                    tmeta["chain"] = chain
            if len(tmeta["prereqs"]) == 1:
                tmeta["chain"] = tmeta["prereqs"][0]

    if not bodies:
        tmp = {}
        for k, v in out.items():
            v.pop("body", [])
            tmp[k] = v
        out = tmp
    return out


parser = parse

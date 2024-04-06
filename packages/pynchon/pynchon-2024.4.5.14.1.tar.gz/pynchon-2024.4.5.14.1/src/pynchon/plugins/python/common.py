"""
"""

from pynchon import abcs, models  # noqa


class PythonPlanner(models.Planner):
    cli_label = "Python Tools"
    cli_description = (
        "Code transforms, docs, & boilerplate generation for Python projects"
    )

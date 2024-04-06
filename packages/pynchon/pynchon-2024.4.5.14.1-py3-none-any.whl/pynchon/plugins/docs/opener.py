"""
"""

import webbrowser

from pynchon import abcs
from pynchon.util import lme

LOGGER = lme.get_logger(__name__)


class OpenerMixin:
    """
    Helper for opening project documentation-files
    inside a webbrowser.  We use a modified version
    of `grip`[1] for this which is called `gripe`[2].

    How this actually works depends on the file-types
    involved, because whereas `grip` works natively to
    render markdown as github-flavored markdown, it
    ignores other types by default.  The `gripe` tool
    adds a special /__raw__ endpoint for other kinds of
    static content.

    (In the future other file-types like `.dot` for raw
    graphviz might be supported, but for now you'll still
    have to render those to png to see a picture.)
    """

    def _open_grip(self, file: str = None):
        """
        :param file: str:  (Default value = None)
        """
        pfile = abcs.Path(file).absolute()
        relf = pfile.relative_to(abcs.Path(self.git_root))
        port = self.server.port
        if port is None:
            LOGGER.critical("no server yet..")
            self.serve()
            import time

            time.sleep(3)
            return self._open_grip(file=file)
        grip_url = f"http://localhost:{port}/{relf}"
        LOGGER.warning(f"opening {grip_url}")
        return dict(url=grip_url, browser=webbrowser.open(grip_url))

    _open__md = _open_grip
    _open__mmd = _open_grip

    def _open_raw(self, file: str = None, server=None):
        """
        :param file: str:  (Default value = None)
        :param server: Default value = None)
        """
        # relf = file.absolute().relative_to(abcs.Path(self.git_root))
        import webbrowser

        return webbrowser.open(
            f"file://{file.absolute()}"
        )  # return self._open_grip(abcs.Path("__raw__") / relf)

    _open__html = _open_raw
    _open__png = _open_raw
    _open__jpg = _open_raw
    _open__jpeg = _open_raw
    _open__gif = _open_raw
    _open__svg = _open_raw
    _open__htm = _open__html
    _open__pdf = _open_raw

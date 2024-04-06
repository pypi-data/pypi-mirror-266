""" pynchon.plugins.git
"""

from fleks import tagging

from pynchon import abcs, models
from pynchon.util import files, lme, os, typing

LOGGER = lme.get_logger(__name__)


class GitConfig(abcs.Config):
    """ """

    config_key: typing.ClassVar[str] = "git"

    def _run(self, cmd, log_command=False, **kwargs):
        """
        :param cmd: param log_command:  (Default value = False)
        :param log_command:  (Default value = False)
        :param **kwargs:
        """
        if self.root:
            pre = f"cd {self.root} && " if self.root else ""
            return os.invoke(f"{pre}{cmd}", log_command=log_command, **kwargs)

    #
    # @memoized_property
    # def default_remote_branch(self) -> typing.StringMaybe:
    #     """ """
    #     tmp = self._run("git remote show origin " "| sed -n '/HEAD branch/s/.*: //p'")
    #     if tmp and tmp.succeeded:
    #         return tmp.stdout.strip() or None

    @property
    def root(self) -> typing.StringMaybe:
        """Root path for this git project"""
        tmp = self.__dict__.get("_root")
        if tmp:
            return tmp
        tmp = files.get_git_root(abcs.Path("."))
        return tmp and tmp.parents[0]

    @property
    def repo(self) -> typing.StringMaybe:
        """Repo name for this git project"""
        if "repo" not in self.__dict__:
            cmd = self._run("git config --get remote.origin.url")
            self.__dict__.update(
                repo=cmd and (cmd.stdout.strip() if cmd.succeeded else None)
            )
        return self.__dict__["repo"]

    @property
    def is_github(self) -> typing.Bool:
        """True if this is a github repository"""
        tmp = "git@github https://github.com http://github.com".split()
        return self.repo and any([self.repo.startswith(x) for x in tmp])

    @property
    def github_org(self) -> typing.StringMaybe:
        """Name of this github organization"""
        if self.is_github:
            tmp = self.repo.split(":")[-1]
            try:
                org, _repo_name = tmp.split("/")
            except (ValueError,):
                return None
            return org

    @property
    def repo_name(self) -> typing.StringMaybe:
        """Repository name"""
        if self.repo:
            tmp = self.repo.split(":")[-1]
            try:
                _org, repo_name = tmp.split("/")
            except (ValueError,):
                return None
            repo_name = repo_name.split(".git")[0]
            return repo_name

    @property
    def repo_url(self) -> typing.StringMaybe:
        """Repository URL"""
        if all([self.github_org, self.repo_name]):
            return f"https://github.com/{self.github_org}/{self.repo_name}"

    @property
    def branch_name(self) -> typing.StringMaybe:
        """Name of current branch"""
        if "branch_name" not in self.__dict__:
            cmd = self._run("git rev-parse --abbrev-ref HEAD")
            tmp = cmd and cmd.succeeded and cmd.stdout.strip()
            self.__dict__.update(branch_name=tmp or None)
        return self.__dict__["branch_name"]

    @property
    def hash(self) -> typing.StringMaybe:
        """Current git hash"""
        if "hash" not in self.__dict__:
            cmd = self._run("git rev-parse HEAD")
            tmp = cmd and cmd.succeeded and cmd.stdout.strip()
            self.__dict__.update(hash=tmp or None)
        return self.__dict__["hash"]


@tagging.tags(click_aliases=["g"])
class Git(models.Provider):
    """Context for git"""

    priority = -2
    name = "git"
    config_class = GitConfig

    @tagging.tags(click_aliases=["ls"])
    def list(self, changes=False) -> typing.List[abcs.Path]:
        """lists files tracked by git"""
        if changes:
            return self.status()["modified"]
        else:
            cmd = self.config._run("git ls-files")
            lines = [line.lstrip().strip() for line in cmd.stdout.split("\n")]
            lines = [filter(None, line.split(" ")) for line in lines if line]
            return [abcs.Path(p) for p in lines]

    @property
    def modified(self) -> typing.List[abcs.Path]:
        """ """
        return self.status().get("modified", [])

    @tagging.tags(click_aliases=["st", "stat"])
    def status(self) -> typing.Dict:
        """JSON version of `git status` for this project"""
        cmd = self.config._run("git status --short")
        lines = [line.lstrip().strip() for line in cmd.stdout.split("\n")]
        lines = [list(filter(None, line.split(" "))) for line in lines if line]
        lines = [line for line in lines if len(line) == 2]
        abspaths = []
        for code, fname in lines:
            abspaths.append((code, abcs.Path(self.config.root) / abcs.Path(fname)))
        modified = [p for (code, p) in abspaths if code.strip() == "M"]
        return dict(modified=modified)

""" pynchon.util.docker
"""

import functools

from pynchon.util import lme, os

LOGGER = lme.get_logger(__name__)


class DockerCtx:
    def _run(
        self,
        command=None,
        entrypoint=None,
        working_dir=None,
        volumes={},
        workspace=False,
        **invoke_kwargs,
    ):
        entrypoint = entrypoint and f"--entrypoint {entrypoint}"
        entrypoint = entrypoint or ""
        if workspace:
            assert not working_dir
            working_dir = "/workspace"
            volumes["`pwd`"] = "/workspace"
        working_dir = working_dir and f"-w {working_dir}"
        working_dir = working_dir or ""
        volumes = [f"-v {k}:{v}" for k, v in volumes.items()]
        volumes = " ".join(volumes)
        volumes = volumes.strip()
        shcmd = f"docker run {working_dir} {volumes} {entrypoint} {self.tag} {command}"
        return os.invoke(shcmd, **invoke_kwargs)

    def __call__(
        self, command=None, entrypoint=None, script=None, **docker_or_invoke_kwargs
    ):
        """

        :param command: Default value = None)
        :param entrypoint: Default value = None)
        :param script: Default value = None)
        :param **docker_or_invoke_kwargs:

        """
        command = command or self.command
        script = script or self.script
        msg = self.init()
        LOGGER.debug("init result: {msg}")
        if script:
            fscript = ".tmp.docker.script"
            with open(fscript, "w") as fhandle:
                fhandle.write(script)
            entrypoint = entrypoint or (self.has_bash and "bash")
            entrypoint = entrypoint or (self.has_sh and "sh")
            if not entrypoint:
                raise Exception('container is missing "bash" & "sh"; cannot run script')
            return self._run(
                workspace=True,
                entrypoint=entrypoint,
                command=f"-x ./{fscript}",
                **docker_or_invoke_kwargs,
            )
        elif command:
            return self._run(command=command, workspace=True, **docker_or_invoke_kwargs)
        else:
            raise RuntimeError(f"not sure how to {self}.__call__ ")

    run = __call__

    def __init__(self, dockerfile: str = None):
        self.dockerfile = dockerfile and dockerfile.lstrip()
        self.command = None
        self.script = None

    @property
    def name(self):
        hash = ""  # FIXME
        raise NotImplementedError()
        # return f"same"

    @property
    def tag(self):
        return f"{self.name}:latest"

    @property
    def file(self):
        return f".tmp.dockerfile.{self.name}"

    @property
    def fhandle(self):
        return open(self.file, "w")

    def _run_bool(self, *args, **kwargs):
        return self._run(*args, **kwargs).succeeded

    def init(self):
        """ """
        if self.dockerfile:
            return self.init_dockerfile()
        elif self.tag:
            LOGGER.warning(
                f"i have tag {self.tag}, but can't be sure it's built or pulled"
            )
            return False
        else:
            raise RuntimeError(f"not sure how to init {self}")

    def init_dockerfile(self):
        """ """
        assert self.dockerfile
        LOGGER.warning(f"writing to {self.file}")
        print(self.dockerfile, file=self.fhandle)
        result = os.slurp_json(f"docker images {self.tag}" + " --format '{{json .}}'")
        if not result:
            LOGGER.warning(f'no container found for "{self.name}"')
            cmd = os.invoke(f"docker build --tag '{self.tag}' . -f {self.file}")
        else:
            LOGGER.warning("already have an image: ")
            LOGGER.warning(result)
        return result

    @property
    def has_sh(self):
        # return os.invoke(f'docker run --entrypoint sh {self.tag} -c "echo"').succeeded
        return self._run_bool(entrypoint="sh", command='-c "echo"')

    @property
    def has_bash(self):
        return self._run_bool(entrypoint="bash", command='-c "echo"')


def Dockerfile(txt, **kwargs):
    return functools.partial(DockerCtx, dockerfile=txt, **kwargs)()


if __name__ == "__main__":
    result = Dockerfile("""FROM python:3.8-alpine""").run(
        script='printf "{}"', load_json=True
    )
    result.json

    # def docker_fxn():
    #     """FROM python:3.8-alpine"""
    #     return "python --help"
    # Dockerfile(docker_fxn.__doc__)(docker_fxn)

    # class docker_cls:
    #     """FROM python:3.8-alpine"""
    #     script = "python --help"

    # os.docker_ctx(dockerfile='..', script='..')
    #
    # print(result)
    # print(result.stdout)
    # print(result.stderr)

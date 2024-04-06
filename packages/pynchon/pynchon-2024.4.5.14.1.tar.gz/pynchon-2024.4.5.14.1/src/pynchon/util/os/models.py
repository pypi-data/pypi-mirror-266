""" pynchon.util.os.models
"""

# import os
# import subprocess
#
# from pynchon.util import lme
#
# LOGGER = lme.get_logger("pynchon.util.os")
#
# from fleks import app, meta
#
#
# class InvocationResult(meta.NamedTuple, metaclass=meta.namespace):
#     cmd: str = ""
#     stdin: str = ""
#     interactive: bool = False
#     large_output: bool = False
#     log_command: bool = True
#     environment: dict = {}
#     log_stdin: bool = True
#     system: bool = False
#     load_json: bool = False
#     json: dict = False
#     failed: bool = None
#     failure: bool = None
#     succeeded: bool = None
#     success: bool = None
#     stdout: str = ""
#     stderr: str = ""
#     pid: int = -1
#     shell: bool = False
#     strict: bool = False
#
#     def __rich__(self):
#         def status_string():
#             if self.succeeded is None:
#                 return "??"
#             return "[cyan]=> [green]ok" if self.succeeded else "[red]failed"
#
#         import shil
#
#         if self.log_command:
#             msg = f"running command: (system={self.system})\n  {self.cmd}"
#             fmt = shil.shfmt(self.cmd)
#             LOGGER.warning(msg)
#             syntax = app.Syntax(f"{fmt}", "bash", line_numbers=False, word_wrap=True)
#             panel = app.Panel(
#                 syntax,
#                 title=(
#                     f"{self.__class__.__name__} from "
#                     f"pid {self.pid} {status_string()}"
#                 ),
#                 title_align="left",
#                 subtitle=app.Text("✔", style="green")
#                 if self.success
#                 else app.Text("❌", style="red"),
#             )
#             lme.CONSOLE.print(panel)
#
#
# class Invocation(meta.NamedTuple, metaclass=meta.namespace):
#     cmd: str = ""
#     stdin: str = ""
#     strict: bool = False
#     shell: bool = False
#     interactive: bool = False
#     large_output: bool = False
#     log_command: bool = True
#     environment: dict = {}
#     log_stdin: bool = True
#     system: bool = False
#     load_json: bool = False
#
#     def __call__(self):
#         LOGGER.warning(self.cmd)
#         if self.system:
#             assert not self.stdin and not self.interactive
#             error = os.system(self.cmd)
#             return InvocationResult(
#                 **{
#                     **self._dict,
#                     **dict(
#                         failed=bool(error),
#                         failure=bool(error),
#                         success=not bool(error),
#                         succeeded=not bool(error),
#                         stdout="<os.system>",
#                         stdin="<os.system>",
#                     ),
#                 }
#             )
#         exec_kwargs = dict(
#             shell=True,
#             env={**{k: v for k, v in os.environ.items()}, **self.environment},
#         )
#         if self.stdin:
#             msg = "command will receive pipe:\n{}"
#             self.log_stdin and LOGGER.debug(msg.format(self.stdin))
#             exec_kwargs.update(
#                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
#             )
#             LOGGER.critical([self.cmd, exec_kwargs])
#             exec_cmd = subprocess.Popen(self.cmd, **exec_kwargs)
#             exec_cmd.stdin.write(self.stdin.encode("utf-8"))
#             exec_cmd.wait()
#             exec_cmd.stdin.close()
#         else:
#             if not self.interactive:
#                 exec_kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             exec_cmd = subprocess.Popen(self.cmd, **exec_kwargs)
#             exec_cmd.wait()
#         if exec_cmd.stdout:
#             exec_cmd.hstdout = exec_cmd.stdout
#             exec_cmd.stdout = (
#                 "<LargeOutput>"
#                 if self.large_output
#                 else exec_cmd.stdout.read().decode("utf-8")
#             )
#             exec_cmd.hstdout.close()
#         else:
#             exec_cmd.stdout = "<Interactive>"
#         if exec_cmd.stderr:
#             exec_cmd.hstderr = exec_cmd.stderr
#             exec_cmd.stderr = exec_cmd.stderr.read().decode("utf-8")
#             exec_cmd.hstderr.close()
#         exec_cmd.failed = exec_cmd.returncode > 0
#         exec_cmd.succeeded = not exec_cmd.failed
#         exec_cmd.success = exec_cmd.succeeded
#         exec_cmd.failure = exec_cmd.failed
#         loaded_json = None
#         if self.load_json:
#             if exec_cmd.failed:
#                 err = f"{self} did not succeed; cannot return JSON from failure"
#                 LOGGER.critical(err)
#                 LOGGER.critical(exec_cmd.stderr)
#                 raise RuntimeError(err)
#             import json
#
#             try:
#                 loaded_json = json.loads(exec_cmd.stdout)
#             except (json.decoder.JSONDecodeError,) as exc:
#                 loaded_json = dict(error=str(exc))
#         if self.strict and not exec_cmd.succeeded:
#             LOGGER.critical(f"Invocation failed and strict={self.strict}")
#             # raise InvocationError
#             LOGGER.critical(exec_cmd.stderr)
#             raise RuntimeError(exec_cmd.stderr)
#         return InvocationResult(
#             **{
#                 **self._dict,
#                 **dict(
#                     pid=exec_cmd.pid,
#                     failed=exec_cmd.failed,
#                     failure=exec_cmd.failure,
#                     success=exec_cmd.success,
#                     succeeded=exec_cmd.succeeded,
#                     stdout=exec_cmd.stdout,
#                     stderr=exec_cmd.stderr,
#                     json=loaded_json,
#                 ),
#             }
#         )

<table>
  <tr>
    <td colspan=2><strong>
    pynchon
      </strong>&nbsp;&nbsp;&nbsp;&nbsp;
    </td>
  </tr>
  <tr>
    <td width=15%><img src=docs/img/icon.png style="width:150px"></td>
    <td>
      <br/><br/>
      <a href=https://pypi.python.org/pypi/pynchon/><img src="https://img.shields.io/pypi/l/pynchon.svg"></a>
      <a href=https://pypi.python.org/pypi/pynchon/><img src="https://badge.fury.io/py/pynchon.svg"></a>
      <a href="https://github.com/elo-enterprises/pynchon/actions/workflows/python-publish.yml"><img src="https://github.com/elo-enterprises/pynchon/actions/workflows/python-publish.yml/badge.svg"></a><a href="https://github.com/elo-enterprises/pynchon/actions/workflows/python-test.yml"><img src="https://github.com/elo-enterprises/pynchon/actions/workflows/python-test.yml/badge.svg"></a>
    </td>
  </tr>
</table>

---------------------------------------------------------------------------------

<div class="toc">
<ul>
<li><a href="#overview">Overview</a></li>
<li><a href="#features">Features</a></li>
<li><a href="#installation">Installation</a></li>
<li><a href="#quick-start">Quick Start</a></li>
</ul>
</div>


---------------------------------------------------------------------------------

## Overview

Pynchon is a library, tool, and extensible framework that helps with generating documentation, working with diagrams, rendering templates, and maybe other aspects of project management.  It's useful in general but has extra features for working with python projects, including helpers for code-transformation and autogenerating documentation.

This code is still experimental and interface stability is not yet guaranteed.. make sure to pin pynchon at specific versions for your project.

---------------------------------------------------------------------------------

## Features

* Terraform-style plan / apply workflows
* Some support for parallel execution in applies
* Tight integration with [Jinja](#) for rendering templates
* Plugin framework for extensions
* Plugins have config
* Helpers for parsing Markdown, INI, JSON, JSON5 and TOML
* Support for diagramming tools like [Mermaid](#mermaid-plugin), [DrawIO](#drawio-plugin), & [pandoc](#pandoc-plugin)
* Friendly output for machines and for humans

---------------------------------------------------------------------------------

## Installation

Pynchon is on PyPI, so to get the latest:

```bash
pip install pynchon
```

Or, for developers:

```bash
# for ssh
git clone git@github.com:elo-enterprises/pynchon.git

# or for http
# git clone https://github.com/elo-enterprises/pynchon

cd pynchon
pip install -e .
```

---------------------------------------------------------------------------------

## Quick Start

### Utility Invocation

If you're more interested in tools than a framework, some functionality is available without completely loading pynchon.

For this you can use module-invocations like `python -mpynchon.util.text ..`. For example:

```bash
# Helpers for loading/converting config from many file formats:
$ python -mpynchon.util.text loadf --help
Usage: python -m pynchon.util.text loadf [OPTIONS] COMMAND [ARGS]...

  pynchon.util.text.loadf CLI

Options:
  --help  Show this message and exit.

Commands:
  ini    Parses ini file and returns JSON :param file:
  json   loads json to python dictionary from given file or string :param...
  json5  Parses JSON-5 file(s) and outputs json.
  loadf
  toml   Parses toml file and returns JSON :param file: str: (Default...
  yaml   parses yaml file and returns JSON :param *args: :param **kwargs:


# Helpers for rendering Jinja templates
$ python -mpynchon.util.text render jinja --help
Usage: python -m pynchon.util.text render jinja [OPTIONS] FILE

  Alias for `jinja_file`

Options:
  -o, --output TEXT    output file to write.  (optional)
  --print              if set, displays result on stdout even when `--output
                       <file>` is passed
  --include TEXT       path to use for template-root / includes
  --context TEXT       context literal.  must be JSON
  --context-file TEXT  context file.  must be JSON
  --help               Show this message and exit.

```

### CLI, Plugins, & Config

For most functionality, you'll want to use the main `pynchon` tool.  Here, that functionality is provided via plugins, where every plugin is a subcommand for the main CLI.  There are several plugins which are provided by default, and you can see the plugins in use with the following command:

```bash
# Shows the default plugin list, with no pynchon config present
$ pynchon plugins list
[
  "git",
  "core",
  "src",
  "markdown",
  "github",
  "docs",
  "json",
  "parse",
  "gen",
  "render",
  "project",
  "globals",
  "python",
  "jinja",
  "pattern"
]


# Add mermaid plugin, which is non-default, using the command-line.
# Note that this is still without any file-based config
$ pynchon --plugins mermaid mermaid --help
Usage: pynchon mermaid [OPTIONS] COMMAND [ARGS]...

  Finds & renders Mermaid diagram files

Options:
  --help  Show this message and exit.

Commands:
  cfg     Shows current config for this plugin
  list    Find mermaid diagrams under `{{project_root}}/**/*.mmd`
  ls      (alias for `ls`)
  plan    Run planning for this plugin
  render  Renders mermaid diagram to image
  run     Passes given command through to docker-image this plugin wraps

```

To get started with file-based config, run `pynchon init` in your project folder to create `.pynchon.json5`.  From here you can modify `pynchon.plugins` to use a custom set of plugins, and configure the plugins as well.

Every plugin has config, which can be overriden, which may include defaults, or which is dynamically determined from the current context.  To show current plugin config, you can always use `pynchon <plugin_name> cfg`.  Below are some examples with the `github` plugin (see the [Github Plugin docs](#github-plugin) for more information about this plugin in particular.)

```bash

# Outside of a github repository,
# config is empty and not very interesting
$ pynchon github cfg
{
  "enterprise": false,
  "actions": [],
  "org_name": null,
  "org_url": null,
  "raw_url": null,
  "repo_ssh_url": null,
  "repo_url": null
}

# Inside of a github repository,
# lots of useful information
$ pynchon github cfg
{
  "enterprise": false,
  "actions": [ ... ],
  "org_name": "elo-enterprises",
  "org_url": "https://github.com/elo-enterprises",
  "raw_url": "https://raw.githubusercontent.com/elo-enterprises/pynchon",
  "repo_ssh_url": "git@github.com:elo-enterprises/pynchon.git",
  "repo_url": "https://github.com/elo-enterprises/pynchon"
}
```

You can see the the configuration schema for any given plugin like this:

```bash

# default output is JSON schema
$ pynchon plugin schema github
{
  "title": "github",
  "type": "object",
  "properties": {
    "apply_hooks": {
      "title": "Apply Hooks",
      "description": "Hooks to run before/after `apply` for this plugin",
      "default": [],
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "enterprise": {
      "title": "Enterprise",
      "default": false,
      "type": "boolean"
    }
  }
}

# markdown output is also supported
$ pynchon plugin schema github --markdown

# you can also pipe markdown output into the preview tool
$ pynchon plugin schema github --markdown | pynchon markdown preview /dev/stdin
```

---------------------------------------------------------------------------------

### Jinja Plugin

There's tight integration with the [jinja templating library](https://jinja.palletsprojects.com/en/3.1.x/), and defaults for rendering includes, default variables, etc can be configured via `.pynchon.json5`.  See the configuration schema below:

 
* **jinja.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **jinja.file_glob:** *(optional <class 'str'>)*
    * Where to find jinja templates
    * Value is **user-configurable**, with default `*.j2`  
* **jinja.template_includes:** *(optional typing.List[str])*
    * Where to find files for use with Jinja's `include` blocks
    * Value is **user-configurable**, with no default  
* **jinja.vars:** *(optional typing.Dict[str, str])*
    * Extra variables for template rendering
    * Value is **user-configurable**, with no default  
* **jinja.exclude_patterns:** *(optional )*
    * File patterns to exclude from resource-listing 
    * Value is **just-in-time** 


**Crucially, the jinja context also includes the entire pynchon configuration stack for all plugins,** i.e. the current output of `pynchon cfg`.  This gives it access to context provided by other plugins.  For example the `{{github.repo_url}}` variable can be used in templates, and will be rendered as expected whenever the [Github Plugin](#github-plugin) is present and ready.

Here's a typical workflow:

```bash
# find *.j2 files under the project directory
$ pynchon jinja list

# make a plan to render every file that was returned by `list` above.
# this will use the jinja plugin config in `.pynchon.json5` to determine
# appropriate calls to `pynchon jinja render ...`
$ pynchon jinja plan

# Render every jinja template we can find.
$ pynchon jinja apply
```

---------------------------------------------------------------------------------



### Dockerhub Plugin

```bash
$ pynchon dockerhub --help
Usage: pynchon dockerhub [OPTIONS] COMMAND [ARGS]...

  Context for Dockerhub

Options:
  --help  Show this message and exit.

Commands:
  cfg   Shows current config for this plugin
  open  Open this dockerhub project's webpage

```

 
* **dockerhub.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **dockerhub.org_name:** *(typing.Optional[str])*
    * (No description provided)
    * Value is **user-configurable**, with no default  
* **dockerhub.repo_name:** *(typing.Optional[str])*
    * (No description provided)
    * Value is **user-configurable**, with no default  
* **dockerhub.org_url:** *(optional <class 'str'>)*
    * (Missing docstring for property)
    * Value is **just-in-time**  
* **dockerhub.repo_url:** *(optional <class 'str'>)*
    * (Missing docstring for property)
    * Value is **just-in-time** 


---------------------------------------------------------------------------------


### Github Plugin

```bash
$ pynchon github --help
Usage: pynchon github [OPTIONS] COMMAND [ARGS]...

  Tools for working with GitHub

Options:
  --help  Show this message and exit.

Commands:
  cfg           Shows current config for this plugin
  clone         Clones a single repo from this project's org ..
  clone-org     Clones an entire github-org ..
  code-owners   Describes code-owners for changes or for working-dir ..
  codeowners    (alias for `codeowners`)
  open          Opens org/repo github in a webbrowser ..
  pr            (alias for `pr`)
  pull-request  Creates a pull-request from this branch ..

```

 
* **github.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **github.enterprise:** *(optional <class 'bool'>)*
    * (No description provided)
    * Value is **user-configurable**, with no default  
* **github.actions:** *(optional typing.List[typing.Dict])*
    * Github Action information 
    * Value is **just-in-time**  
* **github.org_name:** *(typing.Optional[str])*
    * Org name 
    * Value is **just-in-time**  
* **github.org_url:** *(typing.Optional[str])*
    * Org URL 
    * Value is **just-in-time**  
* **github.raw_url:** *(optional )*
    * URL for serving raw content 
    * Value is **just-in-time**  
* **github.repo_ssh_url:** *(typing.Optional[str])*
    * Repository SSH URL 
    * Value is **just-in-time**  
* **github.repo_url:** *(typing.Optional[str])*
    * Repository URL 
    * Value is **just-in-time** 


---------------------------------------------------------------------------------


### Git Plugin

```bash
$ pynchon git --help
Usage: pynchon git [OPTIONS] COMMAND [ARGS]...

  Context for git

Options:
  --help  Show this message and exit.

Commands:
  cfg     Shows current config for this plugin
  list    lists files tracked by git
  ls      (alias for `ls`)
  st      (alias for `st`)
  stat    (alias for `stat`)
  status  JSON version of `git status` for this project

```

 
* **git.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **git.branch_name:** *(typing.Optional[str])*
    * Name of current branch 
    * Value is **just-in-time**  
* **git.github_org:** *(typing.Optional[str])*
    * Name of this github organization 
    * Value is **just-in-time**  
* **git.hash:** *(typing.Optional[str])*
    * Current git hash 
    * Value is **just-in-time**  
* **git.is_github:** *(optional <class 'bool'>)*
    * True if this is a github repository 
    * Value is **just-in-time**  
* **git.repo:** *(typing.Optional[str])*
    * Repo name for this git project 
    * Value is **just-in-time**  
* **git.repo_name:** *(typing.Optional[str])*
    * Repository name 
    * Value is **just-in-time**  
* **git.repo_url:** *(typing.Optional[str])*
    * Repository URL 
    * Value is **just-in-time**  
* **git.root:** *(typing.Optional[str])*
    * Root path for this git project 
    * Value is **just-in-time** 


---------------------------------------------------------------------------------


### Pypi Plugin

```bash
$ pynchon pypi --help
Usage: pynchon pypi [OPTIONS] COMMAND [ARGS]...

  Context for PyPI

Options:
  --help  Show this message and exit.

Commands:
  cfg  Shows current config for this plugin

```

 
* **pypi.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **pypi.name:** *(optional <class 'str'>)*
    * (No description provided)
    * Value is **user-configurable**, with default `Public PyPI`  
* **pypi.docs_url:** *(optional <class 'str'>)*
    * (No description provided)
    * Value is **user-configurable**, with default `https://pypi.org/`  
* **pypi.base_url:** *(optional <class 'str'>)*
    * (No description provided)
    * Value is **user-configurable**, with default `https://pypi.org/project`  
* **pypi.project_url:** *(optional )*
    * (Missing docstring for property)
    * Value is **just-in-time** 


---------------------------------------------------------------------------------


### Markdown Plugin

```bash
$ pynchon markdown --help
Usage: pynchon markdown [OPTIONS] COMMAND [ARGS]...

  Markdown Tools

Options:
  --help  Show this message and exit.

Commands:
  apply      Executes the plan for this plugin
  cfg        Shows current config for this plugin
  doctest    Runs doctest for fenced code inside the given markdown files
  list       Lists affected resources (**.md) for this project
  ls         (alias for `ls`)
  normalize  Use `markdownlint` to normalize input paths
  parse      Parses given markdown file into JSON
  plan       Creates a plan for this plugin
  preview    Previews markdown in the terminal
  run        Passes given command through to docker-image this plugin wraps
  show       (alias for `show`)
  to-pdf     (Alias for `pynchon pandoc md-to-pdf`)

```

 
* **markdown.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **markdown.goals:** *(optional typing.List[typing.Dict])*
    * (No description provided)
    * Value is **user-configurable**, with no default  
* **markdown.include_patterns:** *(optional typing.List[str])*
    * Patterns to include
    * Value is **user-configurable**, with no default  
* **markdown.exclude_patterns:** *(optional typing.List[str])*
    * File globs to exclude from listing
    * Value is **user-configurable**, with no default  
* **markdown.root:** *(optional typing.Union[str, pynchon.abcs.path.Path, NoneType])*
    * (No description provided)
    * Value is **user-configurable**, with no default  
* **markdown.linter_docker_image:** *(optional <class 'str'>)*
    * Container to use for markdown linter
    * Value is **user-configurable**, with default `peterdavehello/markdownlint`  
* **markdown.linter_args:** *(optional typing.List[str])*
    * Arguments to pass to `linter_docker_image`
    * Value is **user-configurable**, with default `['--disable MD013', '--disable MD045', '--disable MD033', '--disable MD041', '--disable MD042', '--fix']` 


---------------------------------------------------------------------------------


### Mermaid Plugin

```bash
$ pynchon mermaid --help
Usage: pynchon mermaid [OPTIONS] COMMAND [ARGS]...

  Finds & renders Mermaid diagram files

Options:
  --help  Show this message and exit.

Commands:
  cfg     Shows current config for this plugin
  list    Find mermaid diagrams under `{{project_root}}/**/*.mmd`
  ls      (alias for `ls`)
  plan    Run planning for this plugin
  render  Renders mermaid diagram to image
  run     Passes given command through to docker-image this plugin wraps

```

 
* **mermaid.apply_hooks:** *(optional typing.List[str])*
    * (No description provided)
    * Value is **user-configurable**, with default `['open-after']`  
* **mermaid.docker_image:** *(optional <class 'str'>)*
    * (No description provided)
    * Value is **user-configurable**, with default `ghcr.io/mermaid-js/mermaid-cli/mermaid-cli:10.8.1-beta.15` 


---------------------------------------------------------------------------------


### Pandoc Plugin

```bash
$ pynchon pandoc --help
Usage: pynchon pandoc [OPTIONS] COMMAND [ARGS]...

  Wrapper around `pandoc` docker image

Options:
  --help  Show this message and exit.

Commands:
  apply      Executes the plan for this plugin
  cfg        Shows current config for this plugin
  md-to-pdf  Converts markdown files to PDF with pandoc
  pdflatex
  plan       Creates a plan for this plugin
  run        Passes given command through to docker-image this plugin wraps
  shell      Starts interactive shell for pandoc container

```

 
* **pandoc.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **pandoc.docker_image:** *(optional <class 'str'>)*
    * (No description provided)
    * Value is **user-configurable**, with default `pandoc/extra:latest`  
* **pandoc.docker_args:** *(optional typing.List)*
    * (No description provided)
    * Value is **user-configurable**, with default `['--toc', '--variable fontsize=10pt']`  
* **pandoc.goals:** *(optional typing.List[typing.Dict])*
    * (No description provided)
    * Value is **user-configurable**, with no default 


---------------------------------------------------------------------------------


### Drawio Plugin

```bash
$ pynchon drawio --help
Usage: pynchon drawio [OPTIONS] COMMAND [ARGS]...

  Wrapper for docker-containers that provide the "drawio" diagramming utility

Options:
  --help  Show this message and exit.

Commands:
  apply   Executes the plan for this plugin
  cfg     Shows current config for this plugin
  export  Exports a given .drawio file to some output file/format...
  list    Lists affected resources (*.drawio files) for this project
  ls      (alias for `ls`)
  open    Opens a browser for the container started by `serve`
  plan    Creates a plan for this plugin
  run     Passes given command through to docker-image this plugin wraps
  serve   Runs the drawio-UI in a docker-container

```

 
* **drawio.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **drawio.file_glob:** *(optional <class 'str'>)*
    * Where to find jinja templates
    * Value is **user-configurable**, with default `*.drawio`  
* **drawio.docker_image:** *(optional <class 'str'>)*
    * (No description provided)
    * Value is **user-configurable**, with default `jgraph/drawio`  
* **drawio.http_port:** *(optional <class 'str'>)*
    * (No description provided)
    * Value is **user-configurable**, with default `8080`  
* **drawio.docker_args:** *(optional typing.List)*
    * (No description provided)
    * Value is **user-configurable**, with default `['-it --rm --name=drawio-server']`  
* **drawio.export_docker_image:** *(optional <class 'str'>)*
    * (No description provided)
    * Value is **user-configurable**, with default `rlespinasse/drawio-desktop-headless`  
* **drawio.export_width:** *(optional <class 'int'>)*
    * (No description provided)
    * Value is **user-configurable**, with default `800`  
* **drawio.export_args:** *(optional typing.List)*
    * (No description provided)
    * Value is **user-configurable**, with default `['--export', '--embed-svg-images', '--embed-diagram', '--svg-theme light']` 


---------------------------------------------------------------------------------


### Dot Plugin

```bash
$ pynchon dot --help
Usage: pynchon dot [OPTIONS] COMMAND [ARGS]...

  Finds / Renders (graphviz) dot files for this project

Options:
  --help  Show this message and exit.

Commands:
  apply   Executes the plan for this plugin
  cfg     Shows current config for this plugin
  list
  plan
  render
  run     Passes given command through to docker-image this plugin wraps

```

 
* **dot.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **dot.exclude_patterns:** *(optional typing.List[str])*
    * (No description provided)
    * Value is **user-configurable**, with no default 


---------------------------------------------------------------------------------


### Mkdocs Plugin

```bash
$ pynchon mkdocs --help
Usage: pynchon mkdocs [OPTIONS] COMMAND [ARGS]...

  Mkdocs helper

Options:
  --help  Show this message and exit.

Commands:
  apply  Executes the plan for this plugin
  cfg    Shows current config for this plugin
  list   Lists site-pages based on mkdocs.yml
  ls     (alias for `ls`)
  open   Opens `dev_addr` in a webbrowser
  plan   Runs a plan for this plugin
  serve  Wrapper for `mkdocs serve`

```

 
* **mkdocs.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **mkdocs.blog_posts:** *(optional <class 'list'>)*
    * returns blog posts, iff blogging plugin is installed.
        resulting files, if any, will not include index and
        will be sorted by modification time
        
    * Value is **just-in-time**  
* **mkdocs.config:** *(optional typing.Dict)*
    * returns a dictionary with the current mkdocs configuration
        
    * Value is **just-in-time**  
* **mkdocs.config_file:** *(typing.Optional[str])*
    * returns the path to the mkdocs config-file, if applicable
    * Value is **just-in-time**  
* **mkdocs.drafts:** *(optional )*
    * (Missing docstring for property)
    * Value is **just-in-time**  
* **mkdocs.pages:** *(optional typing.List)*
    * 
    * Value is **just-in-time**  
* **mkdocs.site_relative_url:** *(optional )*
    * (Missing docstring for property)
    * Value is **just-in-time**  
* **mkdocs.tags:** *(optional typing.List)*
    * 
    * Value is **just-in-time** 


---------------------------------------------------------------------------------


### Json Plugin

```bash
$ pynchon json --help
Usage: pynchon json [OPTIONS] COMMAND [ARGS]...

  Tools for working with JSON & JSON5

Options:
  --help  Show this message and exit.

Commands:
  apply  Executes the plan for this plugin
  cfg    Shows current config for this plugin
  plan   Creates a plan for this plugin

```

 
* **json.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default 


---------------------------------------------------------------------------------


### Makefile Plugin

```bash
$ pynchon makefile --help
Usage: pynchon makefile [OPTIONS] COMMAND [ARGS]...

  Visualization and parsing tools for inspecting Makefiles

Options:
  --help  Show this message and exit.

Commands:
  apply    Executes the plan for this plugin
  cfg      Shows current config for this plugin
  mermaid  Renders mermaid diagram for makefile targets
  parse    Parse Makefile to JSON.
  plan     Runs a plan for this plugin
  render   Subcommands for rendering

```

 
* **makefile.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **makefile.file:** *(optional )*
    * (Missing docstring for property)
    * Value is **just-in-time** 


---------------------------------------------------------------------------------


### Parse Plugin

```bash
$ pynchon parse --help
Usage: pynchon parse [OPTIONS] COMMAND [ARGS]...

  Misc tools for parsing

Options:
  --help  Show this message and exit.

Commands:
  cfg       Shows current config for this plugin
  makefile  (Alias for `pynchon makefile parse`)
  markdown  (Alias for `pynchon markdown parse`)

```

 
* **parse.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default 


---------------------------------------------------------------------------------


### Src Plugin

```bash
$ pynchon src --help
Usage: pynchon src [OPTIONS] COMMAND [ARGS]...

  Management tool for project source

Options:
  --help  Show this message and exit.

Commands:
  apply            Executes the plan for this plugin
  cfg              Shows current config for this plugin
  changed          opens changed files
  list             Lists resources associated with this plugin
  list-modified    Lists modified files
  list-transforms  (Alias for `pynchon python-libcst list-transforms`)
  ls               (alias for `ls`)
  open             Helper for opening project source files
  plan             Describe plan for this plugin
  recent           Opens recently changed files
  sorted           (Alias for `pynchon python sorted`)
  transform        (Alias for `pynchon python-libcst run-transform`)

```

 
* **src.apply_hooks:** *(optional typing.List[str])*
    * Hooks to run before/after `apply` for this plugin
    * Value is **user-configurable**, with no default  
* **src.goals:** *(optional typing.List[str])*
    * (No description provided)
    * Value is **user-configurable**, with no default  
* **src.include_patterns:** *(optional typing.List[str])*
    * (No description provided)
    * Value is **user-configurable**, with no default  
* **src.exclude_patterns:** *(optional typing.List[str])*
    * (No description provided)
    * Value is **user-configurable**, with no default  
* **src.root:** *(optional typing.Union[str, pynchon.abcs.path.Path, NoneType])*
    * (No description provided)
    * Value is **user-configurable**, with no default  
* **src.sorted:** *(optional <class 'bool'>)*
    * Whether to sort source code
    * Value is **user-configurable**, with no default 


---------------------------------------------------------------------------------


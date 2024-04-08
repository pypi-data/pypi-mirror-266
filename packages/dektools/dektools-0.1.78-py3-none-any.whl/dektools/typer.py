import os
import sys
import inspect
import typer
from importlib import metadata
from typing_extensions import Annotated
from .dict import dict_merge
from .yaml import yaml


def command_mixin(app, **kwargs):
    def wrapper(func):
        args = ''
        kw = ''
        kw_body = ''
        is_args = True  # skip first which is args
        for name, param in inspect.signature(func).parameters.items():
            if is_args:
                is_args = False
                continue
            if param.default is inspect.Parameter.empty:
                args += f',{name}'
            else:
                kw += f',{name}={repr(param.default)}'
                kw_body += f',{name}={name}'
        locals_ = dict(func=func, typer=typer, trans=lambda xl: [x if x.strip() else f'"{x}"' for x in xl])
        exec(
            f"def {func.__name__}(ctx: typer.Context{args}{kw}): return func(' '.join(trans(ctx.args)){args}{kw_body})",
            locals_)
        return app.command(
            **{
                'context_settings': {"allow_extra_args": True, "ignore_unknown_options": True},
                **kwargs
            }
        )(locals_[func.__name__])

    return wrapper


def command_version(app, name):
    def main(ctx: typer.Context, version: Annotated[bool, typer.Option("--version/--no-version")] = False):
        if ctx.invoked_subcommand is not None:
            return
        if version:
            sys.stdout.write(metadata.version(name.partition(".")[0]))
            return

    return app.callback(invoke_without_command=True)(main)


def multi_options_to_dict(array):
    result = {}
    for item in array:
        items = item.split('=', 1)
        k = items[0].strip()
        if len(items) == 1:
            v = ''
        else:
            v = items[1].strip()
        result[k] = v
    return result


def filter_files(files):
    if files:
        for f in files:
            strict = True
            if f.startswith('?'):
                f = f[1:]
                strict = False
            if not strict and not os.path.isfile(f):
                continue
            yield f


def load_yaml_files(files):
    data = {}
    for file in filter_files(files):
        dict_merge(data, yaml.load(file) or {})
    return data

#############################################################
# no sub command
# @app.callback(invoke_without_command=True)
# def show(ctx: typer.Context, visible=False):
#     if ctx.invoked_subcommand is None:
#         typer.echo(f"Just for no subcommand")

#############################################################
# no accepting args, get args from sys.argv
# @app.command(
#     context_settings=dict(resilient_parsing=True)
# )

#############################################################
# https://typer.tiangolo.com/tutorial/commands/one-or-multiple/#one-command-and-one-callback
# One command and one callback
# @app.callback()
# def callback():
#     pass

#############################################################
# boolean option
# @app.command()
# def show(
#     visible: Annotated[bool, typer.Option("--share/--no-share")] = True
# ):
#     pass

#############################################################
# one option for multi times
# @app.command()
# def push(path: Annotated[Optional[List[str]], typer.Option()] = None):
#     pass

#############################################################
# one argument accepted multi times
# @app.command()
# def pull(paths: List[str]):
#     pass

#############################################################
# default arguments
# @app.command()
# def show(
#     name: Annotated[str, typer.Argument()] = "tests"
# ):
#     pass

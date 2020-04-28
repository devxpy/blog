#!/usr/bin/env python3
import importlib.util
import shutil
import subprocess
from pathlib import Path

import click
import uvicorn
from jinja2 import Environment, FileSystemLoader
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

_global_options = [
    click.option(
        "--templates-dir",
        "-t",
        default="templates",
        type=click.Path(exists=True, file_okay=False, resolve_path=True),
    ),
    click.option("--exclude", "-e"),
    click.option(
        "--context",
        "-c",
        default="context.py",
        type=click.Path(dir_okay=False, resolve_path=True, exists=True),
    ),
    click.option(
        "--static-dir",
        "-s",
        default="static",
        type=click.Path(file_okay=False, resolve_path=True, exists=True),
    ),
]


def global_options(func):
    for option in reversed(_global_options):
        func = option(func)
    return func


@click.group()
def cli():
    pass


class JinjaStaticFiles(StaticFiles):
    def __init__(self, *args, context_file: str, **kwargs):
        self.context_file = context_file
        super().__init__(*args, **kwargs)

    async def get_response(self, path, scope):
        if path.endswith(".html"):
            raise ValueError("Please remove '.html' from the url.")
        return await super().get_response(path, scope)

    async def lookup_path(self, path):
        ret = await super().lookup_path(path)
        if any(ret):
            return ret
        return await super().lookup_path(f"{path}.html")

    def file_response(self, full_path, stat_result, scope, status_code=200):
        text = render_template(full_path, self.directory, self.context_file)
        return HTMLResponse(text, status_code=status_code)


@cli.add_command
@click.command()
@global_options
def serve(templates_dir, context, static_dir):
    static_dir = Path(static_dir)
    templates_dir = Path(templates_dir)
    args = [
        "browser-sync",
        "start",
        "--proxy",
        "localhost:8000",
        "--files",
        f"{templates_dir}/**/*",
        f"{static_dir}/**/*",
    ]
    print("$", " ".join(args))
    subprocess.Popen(args)

    app = Starlette(
        routes=[
            Mount("/static/", StaticFiles(directory=static_dir)),
            Mount(
                "/",
                JinjaStaticFiles(
                    directory=templates_dir, html=True, context_file=context
                ),
            ),
        ],
        debug=True,
    )
    uvicorn.run(app, debug=True)


@cli.add_command
@click.command()
@click.option(
    "--output-dir",
    "-o",
    default="public",
    type=click.Path(file_okay=False, resolve_path=True),
)
@global_options
def build(templates_dir, output_dir, context, static_dir, exclude):
    templates_dir = Path(templates_dir)
    output_dir = Path(output_dir)
    static_dir = Path(static_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    exclude = list(Path(templates_dir).rglob(exclude))

    for src in templates_dir.rglob("*.html"):
        if src in exclude:
            continue
        build_template(src, output_dir, templates_dir, context)

    shutil.rmtree(output_dir / static_dir.name)
    shutil.copytree(static_dir, output_dir / static_dir.name)


def build_template(src, output_dir, templates_dir, context):
    text = render_template(str(src), str(templates_dir), context)

    rel_path = src.relative_to(templates_dir)
    if src.name == "index.html":
        dest = output_dir / rel_path
    else:
        dest = output_dir / rel_path.parent / rel_path.stem
        dest.mkdir(parents=True, exist_ok=True)
        dest = dest / "index.html"

    dest.write_text(text)


def render_template(full_path, directory, context_file):
    env = Environment(loader=FileSystemLoader(directory))

    spec = importlib.util.spec_from_file_location(Path(context_file).name, context_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ctx = mod.get_context(env)

    rel_path = str(Path(full_path).relative_to(directory))
    template = env.get_template(rel_path)

    text = template.render(**ctx)
    return text


if __name__ == "__main__":
    cli()

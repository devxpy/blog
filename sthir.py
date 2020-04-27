#!/usr/bin/env python3
import os
import shutil
import subprocess
import typing
from itertools import chain
from pathlib import Path

import click
import uvicorn
from jinja2 import Environment, FileSystemLoader
from starlette.responses import Response, HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.types import Scope


@click.group()
def cli():
    pass


class JinjaStaticFiles(StaticFiles):
    async def lookup_path(
        self, path: str
    ) -> typing.Tuple[str, typing.Optional[os.stat_result]]:
        # enable lookup of files without the html suffix
        html_files = Path(self.directory).rglob("*.html")
        if path in (f.stem for f in html_files):
            path += ".html"

        return await super().lookup_path(path)

    def file_response(
        self,
        full_path: str,
        stat_result: os.stat_result,
        scope: Scope,
        status_code: int = 200,
    ) -> Response:
        if not full_path.endswith(".html"):
            return super().file_response(full_path, stat_result, scope, status_code)

        text = render_template(full_path, self.directory)
        return HTMLResponse(text, status_code=status_code)


@cli.add_command
@click.command()
@click.argument("SRC", type=click.Path(exists=True, file_okay=False, resolve_path=True))
def serve(src):
    subprocess.Popen(
        ["browser-sync", "start", "--proxy", "localhost:8000", "--files", f"{src}/**/*"]
    )
    app = JinjaStaticFiles(directory=src, html=True)
    uvicorn.run(app)


@cli.add_command
@click.command()
@click.argument("SRC", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.argument("DEST", type=click.Path(file_okay=False, resolve_path=True))
def build(src, dest):
    src = Path(src)
    dest = Path(dest)

    dest.mkdir(parents=True, exist_ok=True)

    for html_src in src.rglob("*.html"):
        text = render_template(str(html_src), str(src))

        rel_path = html_src.relative_to(src)
        if html_src.name == "index.html":
            dest_path = dest / rel_path
        else:
            dest_dir = dest / rel_path.parent / rel_path.stem
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / "index.html"

        dest_path.write_text(text)

    for static_src in chain(src.rglob("*.css"), src.rglob("*.js")):
        rel_path = static_src.relative_to(src)
        static_dest = dest / rel_path
        shutil.copy(static_src, static_dest)


def render_template(full_path, directory):
    env = Environment(loader=FileSystemLoader(directory))
    rel_path = str(Path(full_path).relative_to(directory))
    template = env.get_template(rel_path)
    text = template.render()
    return text


if __name__ == "__main__":
    cli()

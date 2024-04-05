import click

from pathlib import Path
from jupyter_book.cli.main import build as jupyter_book_build

from teachbooks.publish import make_publish

@click.group()
def main():
    """TeachBooks command line tools"""
    pass

@main.command()
@click.argument("path-source", type=click.Path(exists=True, file_okay=True))
@click.option(
    "--publish",
    is_flag=True,
    help="Target publish version of the book. Removes any sections surrounded "
    "by REMOVE-FROM-PUBLISH tags from _config.yml and _toc.yml"
)
@click.option(
    "--process-only",
    is_flag=True,
    help="Only pre-process content, do not build the book"
)
@click.pass_context
def build(ctx, path_source, publish, process_only):
    """Pre-process book contents and run the Jupyter Book build command"""

    strategy = "publish" if publish else "draft"
    echo_info(f"running build with strategy '{strategy}'")

    path_src_folder = Path(path_source).absolute()
    if publish:
        path_conf, path_toc = make_publish(path_src_folder)
    else:
        path_conf, path_toc = None, None

    # Use default arguments for jb build, as we normally do
    if not process_only:
        ctx.invoke(
            jupyter_book_build,
            path_source=path_src_folder,
            config=path_conf,
            toc=path_toc
        )


def echo_info(message: str) -> None:
    """Wrapper for writing to stdout"""
    prefix = click.style("TeachBooks: ", fg="cyan", bold=True)
    click.echo(prefix + message)
    

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  SPDX-License-Identifier: GPL-3.0-only
#  Copyright 2023 drad <sa@adercon.com>

from pprint import pformat

import arrow
import logging
import typer
from rich import box
from rich.console import Console
from rich.table import Table
from tinydb import where

from ibuilder.config.config import get_db
from ibuilder.models import HistoryOnDB, ResultStatus

logger_base = logging.getLogger("default")
logger = logging.LoggerAdapter(logging.getLogger("default"))

app = typer.Typer(help="Interact with build history.")


def completed(item):
    return "✓" if item else "✗"


def version_with_latest(version: str = None, last: bool = False):
    return f"[bold red]✦{version}[/bold red]" if last else version


def history_summary(db):
    """Shows a summary of the history."""

    table = Table(
        title="History Summary", show_header=True, header_style="bold magenta"
    )
    table.add_column("Id", style="dim")
    table.add_column("Date")
    table.add_column("Runtime")
    table.add_column("Result")
    table.add_column("Calling Params")
    table.add_column("B/L/S/P")
    table.add_column("Version")

    history = db.table("history").all()
    if history:
        for r in history:
            r['doc_id'] = str(r.doc_id)
            r['build_logs'] = '' if not 'build_logs' in r else r['build_logs']
            r['tag_source_logs'] = '' if not 'tag_source_logs' in r else r['tag_source_logs']
            r['tag_source_push_logs'] = '' if not 'tag_source_push_logs' in r else r['tag_source_push_logs']
            r['image_push_logs'] = '' if not 'image_push_logs' in r else r['image_push_logs']
            r['image_push_latest_logs'] = '' if not 'image_push_latest_logs' in r else r['image_push_latest_logs']
            h = HistoryOnDB(**r)
            blsp = []
            ver = ""
            if h.run_params:
                blsp.append(completed(h.run_params["build"]["image"]))
                blsp.append(completed(h.run_params["build"]["tag_image_latest"]))
                blsp.append(completed(h.run_params["source"]["tag"]))
                blsp.append(completed(h.run_params["push"]["image"]))
                ver = version_with_latest(h.run_params["build"]["version"], h.last)
            table.add_row(
                h.doc_id,
                arrow.get(h.created).to("local").format("YYYY-MM-DD HH:mm:ss"),
                str(h.runtime),
                h.result,
                h.calling_params,
                "/".join(blsp),
                ver,
            )
        return table
    else:
        typer.echo(typer.style("No Data found.", fg=typer.colors.YELLOW, bold=True))
    return False


def history_detail(db, id):
    """Show history detail (all info for a specific history item)."""

    r = db.table("history").get(doc_id=id)
    r['doc_id'] = str(id)
    h = HistoryOnDB(**r)

    brief = Table(
        title="History Detail",
        show_header=True,
        show_edge=True,
        show_lines=True,
        header_style="bold magenta",
        box=box.SQUARE,
        expand=True,
        pad_edge=False,
        show_footer=False,
        caption_style=None,
    )
    brief.add_column("Id", justify="center", max_width=15, min_width=15)
    brief.add_column("Date", justify="center")
    brief.add_column("Runtime", justify="center")
    brief.add_column("Results", justify="center")
    brief.add_column("", justify="center", ratio=1)
    brief.add_row(
        h.doc_id,
        arrow.get(h.created).to("local").format("YYYY-MM-DD HH:mm:ss"),
        str(h.runtime),
        h.result,
        "",
    )

    table = Table(
        title_style=None,
        show_header=False,
        show_edge=True,
        show_lines=True,
        header_style=None,
        box=box.SQUARE,
    )

    table.add_column(
        "", justify="right", max_width=15, min_width=15, style="bold magenta"
    )
    table.add_column("", justify="left")
    table.add_row("Task Status", ", ".join(h.task_status))
    if h.calling_params:
        table.add_row("Calling Params", h.calling_params)
    if h.run_params:
        table.add_row("Run Params", str(pformat(h.run_params)))
    if h.build_logs:
        table.add_row("Build", h.build_logs)
    if h.tag_source_logs:
        table.add_row("Source Tag", h.tag_source_logs)
    if h.tag_source_push_logs:
        table.add_row("Source Tag Push", h.tag_source_push_logs)
    if h.image_push_logs:
        table.add_row("Push", h.image_push_logs)
    if h.image_push_latest_logs:
        table.add_row("Push Latest", h.image_push_latest_logs)

    return brief, table


def history_prune(db, result):
    """Remove data from history file by result value."""

    h = db.table("history")  # .search(Result.status == 1)
    canceled = h.search(where("result") == result)
    if canceled:
        h.remove(where("result") == result)
        typer.echo(f"Items with result of '{result}' removed, history is now:")
        # show the history table after pruning.
        summary()
        return True
    else:
        typer.echo(
            typer.style(
                f"Nothing to remove, no items matched: '{result}'",
                fg=typer.colors.YELLOW,
                bold=True,
            )
        )
        return False


@app.command()
def summary():
    """Show the history summary."""

    console = Console()
    table = history_summary(get_db())
    if table:
        console.print(table)


@app.command()
def detail(id: int = typer.Option(..., help="id of History item")):
    """Show details for a specific history item."""

    console = Console()
    brief, table = history_detail(get_db(), id)
    console.print(brief)
    console.print(table)


@app.command()
def prune(result: ResultStatus = typer.Option(..., help="result type")):
    """Prune items from the history."""

    history_prune(get_db(), result)

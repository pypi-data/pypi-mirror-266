#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  SPDX-License-Identifier: GPL-3.0-only
#  Copyright 2023 drad <sa@adercon.com>

import logging
import tomli
from datetime import datetime
from os import getenv
from typing import List, Optional

import typer
from rich import print
from rich.console import Console
from tinydb import where

import ibuilder.history
import ibuilder.images
from ibuilder.config.config import (
    APP,
    CALLING_PARAMS,
    RUNDTS,
    get_db,
    get_docker_client,
    get_prj_conf,
    load_prj_conf,
)
from ibuilder.models import History, ResultStatus, TaskStatus, VersionIncrementType
from ibuilder.utils import (
    confirm_data,
    history_last_build,
    image_build,
    image_push,
    image_repush,
    increment_build_version,
    sign_image,
    tag_source,
)

logger_base = logging.getLogger("default")
logger_base.setLevel(logging.getLevelName(getenv("LOG_LEVEL", "INFO")))
logger_base.addHandler(logging.StreamHandler())
logger = logging.LoggerAdapter(logging.getLogger("default"))

app = typer.Typer(
    pretty_exceptions_enable=False,
    help="build, tag, and push images\n\nNOTE: set LOG_LEVEL environment variable to adjust logging (e.g. $ LOG_LEVEL=DEBUG ib build -i minor)"
)
app.add_typer(ibuilder.history.app, name="history")
app.add_typer(ibuilder.images.app, name="images")

_prj = None
_db = None


@app.command()
def build(
    image: bool = typer.Option(None, "--build", help="perform build of image"),
    push: bool = typer.Option(None, "--push", help="push image to registry"),
    # ~ sign: bool = typer.Option(None, "--sign-enabled", help="enable signing of image"),
    source_tag: bool = typer.Option(None, "--source", help="tag source code"),
    version: str = typer.Option(
        None, help="build version (leave blank to auto-generate)"
    ),
    version_increment_type: VersionIncrementType = typer.Option(
        VersionIncrementType.default,
        "--version-increment-type",
        "-i",
        show_default=True,
        help="specify the build version increment type (for auto-generate of build-version only)",
    ),
    no_image: bool = typer.Option(
        None, "--no-build", help="do not perform build of image"
    ),
    no_latest_tag: bool = typer.Option(
        None, "--no-latest", help="do not add the 'latest' tag"
    ),
    no_push: bool = typer.Option(
        None, "--no-push", help="do not push image to registry"
    ),
    no_sign: bool = typer.Option(None, "--no-sign", help="do not sign the image"),
    no_source_tag: bool = typer.Option(
        None, "--no-source", help="do not tag source code"
    ),
):
    """
    Perform a build, tag, or push.
    """

    console = Console()
    logger.debug(f"log level is: {logging.getLevelName(logger.getEffectiveLevel())}")
    client = get_docker_client()

    # check for/set cli overrides.
    _prj.build.image = True if image else _prj.build.image
    _prj.push.image = True if push else _prj.push.image
    _prj.source.tag = True if source_tag else _prj.source.tag

    _prj.build.image = False if no_image else _prj.build.image
    _prj.push.image = False if no_push else _prj.push.image
    _prj.source.tag = False if no_source_tag else _prj.source.tag

    _prj.build.tag_image_latest = (
        False if no_latest_tag else _prj.build.tag_image_latest
    )
    _prj.sign.enabled = False if no_sign else _prj.sign.enabled

    last = history_last_build(_db)
    logger.debug(f"- last build: {last}")
    lbv = None
    if last:
        lbv = last["run_params"]["build"]["version"]
    else:
        lbv = "0.0.0"
    logger.debug(f"- lbv is: {lbv} - vit={version_increment_type}")
    gen_build_version = False
    if not version:
        gen_build_version = True
        logger.debug("- generating build version...")
        version = increment_build_version(version=lbv, vit=version_increment_type)
    logger.debug(f"- building version: {version}")
    # update project version with version we will build.
    _prj.build.version = version
    # NOTICE: mark latest does not count as an 'actionable' item.
    if (
        not _prj.build.image
        and not _prj.push.image
        and not _prj.source.tag
        and not _prj.sign.enabled
    ):
        typer.secho("No actions to perform, cannot continue.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    confirm_data(
        prj=_prj,
        last_build_version=lbv,
        build_version_generated=gen_build_version,
    )

    proceed = typer.confirm("Proceed with build?")
    result_status = ResultStatus.success
    task_status: List[TaskStatus] = []
    if proceed:
        tasks_start = datetime.utcnow()
        build_succeeded = True
        _tag_source_logs = None
        _tag_source_push_logs = None
        _image_push = None
        _image_push_latest = None
        typer.echo("")
        logger.debug("proceeding with build...")
        with console.status("[bold green]Gathering tasks...") as status:
            # build (image)
            if _prj.build.image:
                status.update("building...")
                logger.debug("- build the image...")
                _image_build = image_build(client=client, prj=_prj, app=APP)
                if _image_build:
                    logger.debug(f"- build succeeded with: {_image_build}")
                    console.log("✓ build complete")
                    task_status.append(TaskStatus.build_ok)
                else:
                    build_succeeded = False
                    logger.debug("- build failed...")
                    console.log("✗ build failed")
                    task_status.append(TaskStatus.build_fail)
                    result_status = result_status.build_fail
                    # @TODO: need to handle build fail, stop the process, write history and exit

            # source (tag/push tag)
            # NOTICE: tag source before push as push can fail.
            if build_succeeded and _prj.source.tag:
                status.update("source (tagging)...")
                logger.debug("- tag source...")
                _tag_source_logs, _tag_source_push_logs = tag_source(
                    prj=_prj, app=APP, push_tag=_prj.source.push_tag
                )
                logger.debug(
                    f"- tag source completed with: {_tag_source_logs} (is type={type(_tag_source_logs)}), {_tag_source_push_logs} (is type={type(_tag_source_push_logs)})"
                )
                if _tag_source_logs:
                    console.log("✓ source tag complete")
                    task_status.append(TaskStatus.source_tag_ok)
                else:
                    logger.debug(f"- tag source failed with: {_tag_source_logs.stderr}")
                    console.log("✗ source tag failed")
                    task_status.append(TaskStatus.source_tag_fail)
                    result_status = result_status.source_tag_fail

            # push (image)
            if build_succeeded and _prj.push.image:
                status.update("pushing...")
                logger.debug("- push the image...")
                _image_push, _image_push_latest = image_push(prj=_prj)
                if _image_push:
                    logger.debug("- push succeeded with: {_image_push}")
                    console.log("✓ push complete")
                    task_status.append(TaskStatus.push_ok)
                else:
                    logger.debug("- push failed...")
                    console.log("✗ push failed")
                    task_status.append(TaskStatus.push_fail)
                    result_status = result_status.push_fail

            # NOTE: we need to stop the console.status here as it prevents user
            #  input which is needed for signing (the password).
            status.stop()

            # sign (image)
            if build_succeeded and _prj.sign.enabled:
                status.update("signing...")
                logger.debug("- sign version image...")
                _rc = sign_image(
                    signor=_prj.sign.signor,
                    image=f"{_prj.build.repository}:{_prj.build.version}",
                )
                logger.debug(f"- sign results return={_rc}")
                if _rc is None:
                    # signor not found, error raised in sign_image
                    typer.secho(
                        "Signor not found, are you sure it is installed and your path is correct?",
                        fg=typer.colors.RED,
                    )
                    task_status.append(TaskStatus.sign_fail)
                    console.log("sign failed")
                elif _rc == 0:
                    # singing was ok
                    task_status.append(TaskStatus.sign_ok)
                    if _prj.build.tag_image_latest:
                        logger.debug("- sign latest image...")
                        sign_image(
                            signor=_prj.sign.signor,
                            image=f"{_prj.build.repository}:latest",
                        )
                        task_status.append(TaskStatus.sign_latest_ok)
                    console.log("sign complete")
                else:
                    typer.secho(
                        f"Other error signing image: {_rc}",
                        fg=typer.colors.RED,
                    )
                    console.log("sign failed")
                    task_status.append(TaskStatus.sign_fail)
        typer.echo("")

        # if we did a push and it was successful then set this as 'latest' and
        #  all others to not latest.
        logger.debug("housekeeping...")
        if TaskStatus.push_ok in task_status:
            _db.table("history").update({"last": False})
            logger.debug("clear last history marker")
        runtime = (datetime.utcnow() - tasks_start).total_seconds()
        # create and write the history record.
        h = History(
            created=RUNDTS,
            runtime=runtime,
            result=result_status,
            task_status=task_status,
            calling_params=CALLING_PARAMS,
            run_params=vars(_prj),
            build_logs="\n".join(_image_build) if _image_build else "",
            tag_source_logs=_tag_source_logs.stdout
            if _tag_source_logs and _tag_source_logs.stdout
            else "",
            tag_source_push_logs=_tag_source_push_logs.stdout
            if _tag_source_push_logs and _tag_source_push_logs.stdout
            else "",
            image_push_logs="\n".join(_image_push) if _image_push else "",
            image_push_latest_logs="\n".join(_image_push_latest)
            if _image_push_latest
            else "",
            # ~ sign_logs=_sign_logs,
            last=True
            if result_status == ResultStatus.success
            and TaskStatus.push_ok in task_status
            else False,
        )
        hid = _db.table("history").insert(h.dict())
        logger.debug("add new history record")
        typer.secho(
            f"History: {hid} - {result_status} ({runtime}s) [{', '.join(task_status)}]",
            fg=typer.colors.MAGENTA,
        )
        typer.echo(f"\tView build details with: ib history detail --id {hid}")
    else:
        typer.secho("Not confirmed, build canceled.", fg=typer.colors.MAGENTA)
        if _prj.history.save_request_canceled:
            logger.debug("Saving canceled build request..")
            h = History(
                created=RUNDTS,
                runtime=0,
                result=ResultStatus.user_cancel,
                calling_params=CALLING_PARAMS,
                run_params={},
                last=False,
            )
            hid = _db.table("history").insert(h.dict())
            typer.secho(f"History: {hid}", fg=typer.colors.MAGENTA)
        else:
            logger.debug(
                "Project settings indicate to NOT save canceled build requests..."
            )


@app.command()
def repush(
    last: bool = typer.Option(True, "--last", help="repush from last history item"),
    _id: int = typer.Option(None, "--id", help="id of History item"),
    no_sign: bool = typer.Option(None, "--no-sign", help="do not sign the image"),
):
    """
    Repush a previously built image and sign (unless specified not to sign).
    Note: this repushes and signs only, other tasks (tag, etc.) are not performed.
    """

    # if id is supplied we will use it otherwise we use last.
    r = None
    if _id:
        logger.debug(f"- repush from history for id: {_id}")
        r = _db.table("history").get(doc_id=_id)
        if not r:
            typer.secho(
                f"No history entry found with id: {_id}", fg=typer.colors.YELLOW
            )
    else:
        logger.debug("- repush from history from last")
        r = _db.table("history").search(where("last") == True)[0]  # noqa
        if not r:
            typer.secho("No last history entry found.", fg=typer.colors.YELLOW)

    if r:
        logger.debug(f"- found history record: {r}")
        print(
            f"Repushing from history created on [magenta]{r['created']}[/magenta] which was build version [magenta]{r['run_params']['build']['version']}[/magenta]"
        )
        _sign = False if no_sign else True
        logger.debug(f"- sign image flag is: {_sign}")
        image_repush(r, _sign)


def version_callback(value: bool):
    """
    Show version.
    NOTICE: we load the pyproject.toml here (rather than a config) so its not loaded on normal app usage as it is not needed then.
    """

    import importlib.metadata

    if value:
        _meta = importlib.metadata.metadata('ibuilder')
        _name = _meta["Name"]
        _version = _meta["Version"]
        typer.echo(f"{_name} {_version}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        help="Show application version and exit",
    ),
):
    global _db, _prj

    # load PRJ (project config file)
    load_prj_conf()
    _prj = get_prj_conf()
    _db = get_db()

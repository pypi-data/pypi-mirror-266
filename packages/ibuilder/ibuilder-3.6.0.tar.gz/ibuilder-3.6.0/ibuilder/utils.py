# -*- coding: utf-8 -*-
#  SPDX-License-Identifier: GPL-3.0-only
#  Copyright 2023 drad <sa@adercon.com>

import logging
import shutil
import subprocess  # nosec
from datetime import datetime
from typing import List

import docker
import typer
from packaging.version import parse
from rich import print
from rich.panel import Panel
from tinydb import where

from ibuilder.config.config import CALLING_PARAMS, RUNDTS, get_db, get_docker_client
from ibuilder.config.models import Application, Project
from ibuilder.models import (
    UNITS,
    History,
    ResultStatus,
    TaskStatus,
    VersionIncrementType,
)

logger = logging.getLogger("default")


def approximate_size(size, flag_1024_or_1000=True):
    """
    Get approximate size - converts from bytes to mb/mib.
    """

    mult = 1024 if flag_1024_or_1000 else 1000
    for unit in UNITS[mult]:
        size = size / mult
        if size < mult:
            return "{0:.1f} {1}".format(size, unit)


def history_last_build(db):
    """
    Get the last build from history.
    """

    history = db.table("history").search(where("last") == True)  # noqa
    if history:
        logger.debug("- we have history...")
        return history[0]
    else:
        logger.debug("- no history...")
        return None


def increment_build_version(
    version: str = None, vit: VersionIncrementType = VersionIncrementType.default
):
    """
    Increment build version.
    """

    if version:
        lbv = parse(version).release
        if vit == VersionIncrementType.major:
            return f"{lbv[0] + 1}.{0}.{0}"
        elif vit == VersionIncrementType.minor:
            return f"{lbv[0]}.{lbv[1] + 1}.{0}"
        else:
            return f"{lbv[0]}.{lbv[1]}.{lbv[2] + 1}"
    else:
        return "0.0.1"


def confirm_data(
    prj: Project = None,
    last_build_version: str = None,
    build_version_generated: bool = False,
):
    """
    Show data for user to confirm before building.
    """

    _default_panel_width = 66

    # Build
    _run_options = []
    _run_options.append(label_with_status(label="Build", value=prj.build.image))
    _run_options.append(label_with_status(label="Push", value=prj.push.image))
    _run_options.append(label_with_status(label="Source", value=prj.source.tag))
    _run_options.append(
        label_with_status(label="Latest", value=prj.build.tag_image_latest)
    )
    _run_options.append(label_with_status(label="Sign", value=prj.sign.enabled))

    print(
        Panel(
            f"Version [red][bold]{prj.build.version}[/red][/bold] ({'generated' if build_version_generated else 'manual'}) - last build was [magenta]{last_build_version}[/magenta]\n{' | '.join(_run_options)}",
            title=f"[red]Build: [bold]{prj.config.component}",
            expand=True,
            width=_default_panel_width,
        )
    )

    # Build Info
    _build_info = []
    _build_info.append(f"repo:         {prj.build.repository}")
    _build_info.append(f"base path:    {prj.build.base_path}")
    _build_info.append(f"dockerfile:   {prj.build.dockerfile}")
    _build_info.append(f"args:         {get_build_args(prj)}")
    _build_info.append(f"labels:       {get_build_labels(prj.build.labels)}")
    if prj.build.network_mode:
        _build_info.append(f"network mode: {prj.build.network_mode}")

    print(
        Panel(
            "\n".join(_build_info),
            title="[red]Build",
            expand=True,
            width=_default_panel_width,
        )
    )

    # Push Info
    _push_info = []
    _push_info.append(f"enabled:  {prj.push.image}")
    _push_info.append(
        f"registry: {prj.push.registry.url} (user: {prj.push.registry.username})"
    )

    print(
        Panel(
            "\n".join(_push_info),
            title="[red]Push",
            expand=True,
            width=_default_panel_width,
        )
    )

    # Sign
    _sign_info = []
    _sign_info.append(f"enabled: {prj.sign.enabled}")
    _sign_info.append(f"signor:  {prj.sign.signor}")

    print(
        Panel(
            "\n".join(_sign_info),
            title="[red]Sign",
            expand=True,
            width=_default_panel_width,
        )
    )

    # Source Control
    _push_tag = "[green]Yes[/green]" if prj.source.push_tag else "[red]No[/red]"
    _source_info = []
    _source_info.append(f"enabled: {prj.source.tag}")
    _source_info.append(f"push:    {_push_tag}")

    print(
        Panel(
            "\n".join(_source_info),
            title="[red]Source Control",
            expand=True,
            width=_default_panel_width,
        )
    )


def label_with_status(label: str = None, value: bool = False):
    """
    Get label with status.
    NOTICE: the return uses Rich formatting which needs a rich print or other
      capable renderer.
    """

    _on = "[green][bold]✓[/bold][/green] "
    _off = "[red][bold]✗[/bold][/red] "

    if value:
        return f"{_on}{label}"
    else:
        return f"{_off}{label}"


def get_build_args(prj):
    """
    Convert build args from list to dict.
    NOTE: if BUILD_VERSION is an arg its value will be replaced by the build version.
    """

    r = {}
    for a in prj.build.args:
        if "BUILD_VERSION" in a:
            a["BUILD_VERSION"] = f"{prj.build.version}"

        r.update(a)
    return r


def get_build_labels(labels):
    """
    Convert labels from list to dict.
    """

    r = {}
    for label in labels:
        r.update(label)
    return r


def image_build(client=None, prj: Project = None, app: Application = None):
    """
    Build image using a docker client.
    @RETURN build_logs | None
    """

    logger.debug("- building image...")
    try:
        labels = {"BUILDER": app.name, "BUILDER_VERSION": app.version}
        # add any additional labels specified.
        labels.update(get_build_labels(prj.build.labels))
        logger.debug(f"building with labels: {labels}")
        buildargs = get_build_args(prj)
        logger.debug(f"building with args: {buildargs}")
        tag = f"{prj.build.repository}:{prj.build.version}"
        logger.debug(f"build with tag: {tag}")

        build = client.images.build(
            path=prj.build.base_path,
            dockerfile=prj.build.dockerfile,
            tag=tag,
            buildargs=buildargs,
            labels=labels,
            network_mode=prj.build.network_mode,  # this is needed to get ukse app image to build for assets:precompile (@todo: need to find a better way to do this)
        )
        built_image = build[0]
        built_logs = build[1]
        _build_logs = []
        for r in built_logs:
            # NOTE: there are other types of data in the built_logs (e.g. 'aux', etc.) but we only care about the stream.
            if "stream" in r:
                # typer.echo(f"{' '.join(r['stream'].split()).rstrip()}")
                for line in r["stream"].splitlines():
                    # ~ typer.echo(line)
                    _build_logs.append(line)

        if prj.build.tag_image_latest:
            logger.debug("- tagging image with 'latest'...")
            built_image.tag(f"{prj.build.repository}", "latest")
        return _build_logs
    except docker.errors.BuildError as e:
        typer.secho(
            f"Docker Build Error, cannot continue.\n- details: {e}",
            fg=typer.colors.RED,
            err=True,
        )
        return None
    except docker.errors.APIError as e:
        typer.secho(
            f"Docker API Error, cannot continue.\n- details: {e}",
            fg=typer.colors.RED,
            err=True,
        )
        return None
    except Exception as e:
        typer.secho(
            f"Other Docker Build Error, cannot continue.\n- details: {e}",
            fg=typer.colors.RED,
            err=True,
        )
        return None


def tag_source(prj: Project = None, app: Application = None, push_tag: bool = False):
    """
    Tag source code with build version.
    @RETURN [tag_result, tag_push_result | None]
    """

    _tag_result = None
    _push_tag_result = None
    try:
        tag_name = f"{prj.config.component + '-' if prj.config.component else ''}{prj.build.version}"
        logger.debug(f"- tag source with: {tag_name}")
        tag_calling_params = [
            "git",
            "tag",
            "-a",
            tag_name,
            "-m",
            f"{app.name} created {prj.build.version}",
        ]
        _tag_result = subprocess.run(  # nosec
            tag_calling_params, shell=False, capture_output=True
        )
        # check if we need to push the tag
        if push_tag:
            push_calling_params = ["git", "push", "origin", tag_name]
            _push_tag_result = subprocess.run(  # nosec
                push_calling_params, shell=False, capture_output=True
            )

        return _tag_result, _push_tag_result
    except Exception as e:
        typer.secho(
            f"Error in applying source code tag: {e}", fg=typer.colors.RED, err=True
        )
        return None


def image_registry_login(prj: Project = None):
    """
    Login to image registry.
    """

    client = get_docker_client()
    try:
        client.login(
            username=prj.push.registry.username,
            password=prj.push.registry.password
            if prj.push.registry.password and len(prj.push.registry.password) > 0
            else None,
            registry=prj.push.registry.url,
            dockercfg_path=prj.push.docker_config_path,
        )
        return True
    except Exception as e:
        logger.error(
            f"Registry Login Problem, cannot continue.\n  You likely need to do a 'docker login...' or supply the 'push.registry.password' config variable.\nDetails: {e}"
        )
        return False


def image_push_by_tag(prj: Project = None, tag: str = None):
    """
    Push an image by tag.
    """

    logger.debug(f"- pushing tag: {tag}")
    client = get_docker_client()
    _ret = None
    _push_logs = []
    last_line = ""
    # @TODO: current docker-py does not support content trust logic, [see](https://github.com/docker/docker-py/issues/1773). Once it is supported we will use it!
    #        also note that the only apparent work-around for this is to use subprocess, our issue with that is we would loose streaming of build push data.
    for line in client.images.push(
        repository=prj.build.repository, tag=tag, stream=True, decode=True
    ):
        if "status" in line:
            _push_logs.append(line["status"])
            last_line = line["status"]
    # if success return true, otherwise try again.
    # success line looks like the following
    # 0.7.0: digest: sha256:eda4a046da5d045cf19af68165f7c1c0a9801ed9c711dd6dc277480b6338bf05 size: 2200
    # {tag}: digest: * size: xxx
    logger.debug(f"--> push of {tag} complete.")
    try:
        pr_tag, pr_digest_label, pr_digest, pr_size_label, pr_size = last_line.replace(
            ":", ""
        ).split(" ")
        if pr_tag == tag:
            typer.echo(f"Push of {tag} succeeded!")
            _push_logs.append(f"Push of {tag} succeeded!")
            _ret = _push_logs
        else:
            _push_logs.append(f"Push of {tag} failed!", fg=typer.colors.RED, err=True)
    except ValueError as e:
        typer.secho(f"Push failed with: {e}", fg=typer.colors.RED, err=True)
        _ret = None

    return _ret


def image_push(prj: Project = None):
    """
    Push the built image to the registry.
    @NOTICE: 'latest' tag is only pushed if specified.
    """

    logger.debug("- push image...")
    ret_base = None
    ret_latest = None
    if image_registry_login(prj=prj):
        ret_base = image_push_by_tag(prj=prj, tag=prj.build.version)
        if prj.build.tag_image_latest:
            ret_latest = image_push_by_tag(prj=prj, tag="latest")

    return ret_base, ret_latest


def image_repush(r, sign):
    """
    Repush an image from a history entry and sign.
    """

    _db = get_db()
    tasks_start = datetime.utcnow()
    result_status = ResultStatus.success
    task_status: List[TaskStatus] = []
    prj: Project = Project(**r["run_params"])
    if image_push(prj=prj):
        logger.debug("- repush succeeded...")
        task_status.append(TaskStatus.repush_ok)
        result_status = result_status.success
        # if we have a success then update all other history records to have last=False.
        _db.table("history").update({"last": False})
    else:
        logger.debug("- repush failed...")
        task_status.append(TaskStatus.repush_fail)
        result_status = result_status.push_fail

    # if repush is successful, prj signing is enabled and no_sign is not specified we will sign image.
    if result_status == result_status.success and prj.sign.enabled and sign:
        logger.debug("- sign and push sign...")
        _rc = sign_image(
            signor=prj.sign.signor,
            image=f"{prj.build.repository}:{prj.build.version}",
        )
        logger.debug(f"- sign results return={_rc}")
        if _rc is None:
            # signor not found, error raised in sign_image
            typer.secho(
                "Signor not found, are you sure it is installed and your path is correct?",
                fg=typer.colors.RED,
            )
            task_status.append(TaskStatus.sign_fail)
        elif _rc == 0:
            # singing was ok
            task_status.append(TaskStatus.sign_ok)
            if prj.build.tag_image_latest:
                logger.debug("- sign latest image...")
                sign_image(
                    signor=prj.sign.signor,
                    image=f"{prj.build.repository}:latest",
                )
                task_status.append(TaskStatus.sign_latest_ok)
        else:
            typer.secho(
                f"Other error signing image: {_rc}",
                fg=typer.colors.RED,
            )
            task_status.append(TaskStatus.sign_fail)

    runtime = (datetime.utcnow() - tasks_start).total_seconds()
    # create and write the history record.
    h = History(
        created=RUNDTS,
        runtime=runtime,
        result=result_status,
        task_status=task_status,
        calling_params=CALLING_PARAMS,
        run_params=prj,
        last=True if result_status == ResultStatus.success else False,
    )
    hid = _db.table("history").insert(h.dict())
    typer.echo(
        f"- history: {hid} - {result_status} ({runtime}s) [{', '.join(task_status)}]"
    )


def sign_image(signor: str = None, image: str = None):
    """
    Sign Image
    """

    _cmd = f"{signor}".format(image)
    logger.debug(f"Sign image with command: {_cmd}")

    # check to ensure signor command exists.
    logger.debug(f"- check command: {_cmd.split()[0]}")
    _signor_exists = shutil.which(_cmd.split()[0])  # nosec
    logger.debug(f"  ─⏵ check result: {_signor_exists}")
    if not _signor_exists:
        return None, None, None

    # execute signor command
    _result = subprocess.run(_cmd.split(), capture_output=False)  # nosec
    return _result.returncode

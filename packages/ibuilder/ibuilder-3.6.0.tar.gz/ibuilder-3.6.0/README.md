# README

ibuilder is a [cli](https://en.wikipedia.org/wiki/Command-line_interface) based builder of [docker](https://hub.docker.com/) images. It provides an interface for building and pushing the image, signing images, as well as for tagging source code after build with a build version and other common image tasks.


### Latest Changes

- upgrade to pydantic 2x
- upgraded packages: docker, packaging, pydantic, rich, typer
- changed --version to use importlib.metadata
- removed capturing of sign_logs
- turned off pretty_exceptions (typer/rich)


### NOTICES

- __Next Release Will Require Python 3.11 or Newer__ as we would like to move away from tomllib to address the following:
  + this app uses tomli for toml parsing, python 3.11 has tomllib included which we will move to at some point in the near future. We realize this could be a large burden on users so we have delayed this task until python 3.11 is more widely used.


### Features

- build: build docker images
- push: push images to any container registry
- sign: sign images for container signing and verification
- source control: tag and push when you build an image
- history: retain build history for quick/easy access to past build info
- quick/easy: create an `ibuilder.toml` file and run `ib build -i minor` to build, push, commit to source control and sign a new image

### Requirements

- python 3
- docker: docker must be set up as it is used to build and push the image
- git: (optional) if you use the source-tag feature you will need git installed and your code setup in git (it simply performs a git tag && git push from the working directory)
- image signor: (optional) if you choose to sign images a signor (such as cosign) is needed

### Overview

- setup (see #setup)
- configure (see #configure): place a copy of the `example/.ibuilder.toml` in the same directory as your Dockerfile of the app you want to build and adjust it as needed
- run (see #run): execute ibuilder to build/push/tag a version of your app, its as simple as `ib build`


### Install

We recommend using [pipx](https://github.com/pypa/pipx) to install ibuilder: `pipx install ibuilder`. You can also install via pip: `pip install --user ibuilder`.


### Setup

ibuilder uses a config file to store your setup. Each 'app' you build with ibuilder expects this file to be in the 'root' of the app that you are building. This file contains information such as whether to build, push, tag the image, labels to apply, Dockerfile to use, etc. You can grab an example config file from  [ibuilder/example/.ibuilder.toml](https://gitlab.com/drad/ibuilder/-/blob/master/example/.ibuilder.toml).


### Configure

- create a project config file
  - place a copy of the `example/.ibuilder.toml` file in your project (same directory as your Dockerfile) and configure as needed


### Features

If you create an arg with the name "BUILD_VERSION" its value will be replaced with the build version of the current build. This can be used to pass the build version from ibuilder into your docker environment.


### Run

- basic run: `ib build --version=1.2.3`
  - the above command assumes there is a `.ibuilder.toml` in the current working directory which happens to be in the same directory as the Dockerfile which you wish to build
- change logging level: `LOG_LEVEL=DEBUG ib build...`
  + standard python log levels supported: CRITICAL|ERROR|WARNING|INFO|DEBUG (default is INFO)
View help with `ib --help` or see help for a specific command: `ib build --help`.


### Recommendations

We recommend using docker's configuration storage for reg_auth-* related configuration items as it encrypts sensitive information and is likely already configured (if you have already used `docker login`). If you leave the remaining items empty the default values will be used. This will then try `$HOME/.docker/config.json` and `$HOME/.dockercfg` for your docker config settings. If you do not already have a docker config run `docker login` and it should be created for you. After a successful login you should not need to do anything else for the application as the needed info will be stored in your dockercfg and the app will use it when needed.

If you are signing your images you may want to set the `COSIGN_PASSWORD` environment variable in your `~/.bashrc` or equivalent shell config file to avoid being prompted for your signing password after build and push. It should be noted that you will be prompted twice (if you are pushing both the build version and the `latest` tag of this version) as ib signs both tags of the built image. To avoid this we recommend setting the `COSIGN_PASSWORD` environment variable but please ensure you understand the security implications of doing so.

### Legacy

This project originally started under the name boi - builder of images and as such you may find references to boi and even backward support for boi (e.g. local history database, user config file, etc.).


### Links

- [typer](https://typer.tiangolo.com/)
- [docker](https://pypi.org/project/docker/)
  - [docs](https://docker-py.readthedocs.io/en/stable/)
- [toml](https://pypi.org/project/toml/)
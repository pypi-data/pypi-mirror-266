"""CLI for setup_mongot_repro_env."""
import logging
import os
import sys

import click
import inject
import structlog

from db_contrib_tool.setup_repro_env.download_service import ArtifactDownloadService, DownloadUrl
from db_contrib_tool.usage_analytics import CommandWithUsageTracking

DEFAULT_INSTALL_DIR = os.path.join(os.getcwd(), "build")
VERSIONS = ("latest", "release")
ARCHITECTURES = ("x86_64", "aarch64")
DEFAULT_ARCHITECTURE = "x86_64"
PLATFORMS = ("linux", "macos")
DEFAULT_PLATFORM = "linux"

EXTERNAL_LOGGERS = [
    "evergreen",
    "github",
    "inject",
    "segment",
    "urllib3",
]
LOGGER = structlog.get_logger(__name__)


def setup_logging(debug: bool = False) -> None:
    """
    Enable logging.

    :param debug: Whether to setup debug logging.
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s - %(name)s - %(levelname)s] %(message)s",
        level=log_level,
        stream=sys.stdout,
    )
    for logger in EXTERNAL_LOGGERS:
        logging.getLogger(logger).setLevel(logging.WARNING)
    structlog.configure(logger_factory=structlog.stdlib.LoggerFactory())


@click.command(cls=CommandWithUsageTracking)
@click.pass_context
@click.argument(
    "version",
    nargs=1,
    required=False,
    default="latest",
    type=click.Choice(VERSIONS, case_sensitive=False),
)
@click.option(
    "-i",
    "--installDir",
    "install_dir",
    type=click.Path(),
    default=DEFAULT_INSTALL_DIR,
    help="Directory to install the download archive.",
    show_default=f"`{DEFAULT_INSTALL_DIR}`",
)
@click.option(
    "-p",
    "--platform",
    "_platform",
    default=DEFAULT_PLATFORM,
    type=click.Choice(PLATFORMS, case_sensitive=False),
    help=f"Platform to download. Available platforms are {PLATFORMS}.",
)
@click.option(
    "-a",
    "--architecture",
    default=DEFAULT_ARCHITECTURE,
    type=click.Choice(ARCHITECTURES, case_sensitive=False),
    help="Architecture to download.",
)
def setup_mongot_repro_env(
    ctx: click.Context,
    install_dir: str,
    _platform: str,
    architecture: str,
    version: str,
) -> None:
    """
    Set up Mongot repro environment.

    Downloads and installs particular Mongot versions into install directory.

    Accepts `latest` currently, eventually will accept `release` as well.

    If no version and no architecture are specified the lastest linux_x86_64 binary will be installed.
    """
    # TODO SERVER-85978 support downloading release versions of mongot.
    if version == "release":
        raise ValueError(
            "setup-mongot-repro-env doesn't currently support downloading releases of mongot"
        )
    setup_logging(True)
    primaryUrl = (
        "https://mciuploads.s3.amazonaws.com/fts/atlas-search-localdev/"
        + massage_binary_name(version, architecture, _platform)
    )

    inject.configure()
    artifact_download_service = inject.instance(ArtifactDownloadService)
    artifact_download_service.download_with_retries(
        DownloadUrl(primary=primaryUrl), os.path.abspath(install_dir), True
    )


def massage_binary_name(version: str, architecture: str, platform: str) -> str:
    """
    Return binary name to be referenced in the url passed to download_with_retries.

    10gen/mongot releases binaries to constant/hardcoded S3 links. In other words, each commit to 10gen/mongot
    pushes new binaries to the same set of links. This function processes input parameters to figure out the
    desired binary type (release or latest of given arch + platform combo).

    Until release downloads are supported, possible binary names only include:
    - mongot_latest_linux_x86_64.tgz
    - mongot_latest_linux_aarch64.tgz
    - mongot_latest_macos_x86_64.tgz
    """
    if platform == "macos" and architecture == "aarch64":
        raise ValueError("Mongot doesn't support macos with aarch64 architecture")
    return f"mongot_{version}_{platform}_{architecture}.tgz"

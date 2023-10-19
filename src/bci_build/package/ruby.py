"""Ruby LanguageStack BCI containers."""
from typing import Literal

from .bciclasses import LanguageStackContainer
from .bciclasses import Replacement
from .constants import CAN_BE_LATEST_OS_VERSION
from .constants import OsVersion
from .constants import SupportLevel
from .utils import generate_disk_size_constraints


def _get_ruby_kwargs(ruby_version: Literal["2.5", "3.2"], os_version: OsVersion):
    ruby = f"ruby{ruby_version}"
    ruby_major = ruby_version.split(".")[0]

    return {
        "name": "ruby",
        "package_name": f"ruby-{ruby_version}-image",
        "pretty_name": f"Ruby {ruby_version}",
        "version": ruby_version,
        "additional_versions": [ruby_major],
        "is_latest": os_version in CAN_BE_LATEST_OS_VERSION,
        "os_version": os_version,
        "env": {
            # upstream does this
            "LANG": "C.UTF-8",
            "RUBY_VERSION": "%%rb_ver%%",
            "RUBY_MAJOR": "%%rb_maj%%",
        },
        "replacements_via_service": [
            Replacement(regex_in_build_description="%%rb_ver%%", package_name=ruby),
            Replacement(
                regex_in_build_description="%%rb_maj%%",
                package_name=ruby,
                parse_version="minor",
            ),
        ],
        "package_list": [
            ruby,
            f"{ruby}-rubygem-bundler",
            f"{ruby}-devel",
            # provides getopt, which is required by ruby-common, but OBS doesn't resolve that
            "util-linux",
            "curl",
            "git-core",
            # additional dependencies to build rails, ffi, sqlite3 gems -->
            "gcc-c++",
            "sqlite3-devel",
            "make",
            "awk",
            # additional dependencies supplementing rails
            "timezone",
        ],
        "extra_files": {
            # avoid ftbfs on workers with a root partition with 4GB
            "_constraints": generate_disk_size_constraints(6)
        },
        # as we only ship one ruby version, we want to make sure that binaries belonging
        # to our gems get installed as `bin` and not as `bin.ruby$ruby_version`
        "config_sh_script": "sed -i 's/--format-executable/--no-format-executable/' /etc/gemrc",
    }


RUBY_CONTAINERS = [
    LanguageStackContainer(
        **_get_ruby_kwargs("2.5", OsVersion.SP5),
        support_level=SupportLevel.L3,
    ),
    LanguageStackContainer(
        **_get_ruby_kwargs("2.5", OsVersion.SP6),
        support_level=SupportLevel.L3,
    ),
    LanguageStackContainer(**_get_ruby_kwargs("3.2", OsVersion.TUMBLEWEED)),
]

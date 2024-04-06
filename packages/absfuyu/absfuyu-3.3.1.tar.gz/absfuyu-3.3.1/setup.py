"""
SETUP FILE
----------
"""

import setuptools
import re
from collections import defaultdict


def get_extra_requires(path, add_all=True):
    with open(path) as fp:
        extra_deps = defaultdict(set)
        for k in fp:
            if k.strip() and not k.startswith("#"):
                tags = set()
                if ":" in k:
                    k, v = k.split(":")
                    tags.update(vv.strip() for vv in v.split(","))
                tags.add(re.split("[<=>]", k)[0])
                for t in tags:
                    extra_deps[t].add(k)

        # add tag `all` at the end
        if add_all:
            extra_deps["all"] = set(vv for v in extra_deps.values() for vv in v)

    return extra_deps


setuptools.setup(
    name="absfuyu",
    extras_require=get_extra_requires("extra_requirements.txt"),
)

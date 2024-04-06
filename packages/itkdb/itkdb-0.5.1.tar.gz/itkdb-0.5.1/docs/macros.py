# this file is run via gen-files
# https://github.com/facelessuser/pymdown-extensions/issues/933
from __future__ import annotations

import pymdownx.magiclink

base_url = "https://gitlab.cern.ch"
pymdownx.magiclink.PROVIDER_INFO["gitlab"].update(
    {
        "url": base_url,
        "issue": "%s/{}/{}/issues/{}" % base_url,
        "pull": "%s/{}/{}/merge_requests/{}" % base_url,
        "commit": "%s/{}/{}/commit/{}" % base_url,
        "compare": "%s/{}/{}/compare/{}...{}" % base_url,
    }
)

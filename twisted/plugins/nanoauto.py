# Copyright (c) Moshe Zadka
# See LICENSE for details.

from twisted.application.service import ServiceMaker

serviceMaker = ServiceMaker(
    "Web-based write-only editor",
    "nanoauto.web",
    "An editor which allows writing only",
    "nanoauto",
)

# -*- coding: utf-8 -*-
import os

from typing import List

DEBUG = False

RECIPIANT_LISTS = {
    "all": [
        "5767673ad.company.microsoftonline.com@amer.teams.ms",
        "supervisor1@company.com",
        "supervisor2@company.com",
        "supervisor3@company.com",
        "operator1@company.com",
        "operator2@company.com",
        "operator3@company.com",
        "operator4@company.com",
        "operator5@company.com",
        "operator6@company.com",
        "operator7@company.com",
    ],
    "supervisors": [
        "supervisor1@company.com",
        "supervisor2@company.com",
        "supervisor3@company.com",
    ],
    "operations": [
        "5767673ad.company.microsoftonline.com@amer.teams.ms",
        "operator1@company.com",
        "operator2@company.com",
        "operator3@company.com",
        "operator4@company.com",
        "operator5@company.com",
        "operator6@company.com",
        "operator7@company.com",
    ],
}


def get_recipiant_list(which: str = "operations") -> List[str]:
    """Get a recipiant list for emails."""
    debug = os.getenv("DEBUG")
    if debug and isinstance(debug, str):
        debug = eval(debug)
    else:
        debug = DEBUG

    if debug:
        recip_list = ["user1@company.com"]
    else:
        recip_list = RECIPIANT_LISTS[which]

    return recip_list

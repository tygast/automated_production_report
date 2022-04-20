# -*- coding: utf-8 -*-
"""A set of programs meant to be run on a schedule to generate consumption and production reports for division locations and unit operations"""

__author__ = "User 1"
__license__ = "proprietary"
__copyright__ = "***************"


__version__ = "0.8.0"


__maintainer__ = "User 1"

import os

from dotenv import load_dotenv

load_dotenv()
if os.getenv("DEBUG") is not None:
    print("DEBUG: " + os.getenv("DEBUG"))
else:
    print(os.getenv("DEBUG"))

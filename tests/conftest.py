# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import pytest
import toml


@pytest.fixture
def report_config_folder():
    return Path(__file__).parents[1] / "configs"


@pytest.fixture
def master_config(report_config_folder):
    with (report_config_folder / "config.toml").open() as f:
        config = toml.load(f)
    return config


@pytest.fixture
def flare_config(report_config_folder):
    return None

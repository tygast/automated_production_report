# -*- coding: utf-8 -*-
"""This has end-to-end tests (except for email stuff)"""
from __future__ import annotations

from fake_email import FakeMsg
from reports.controllers import run_report
from reports.services.email import email_utils


def test_master_report(monkeypatch, config):
    """Tests if this the report runs if this errors out then something is wrong"""
    with monkeypatch.context() as m:
        m.setattr(email_utils, "EmailMsg", FakeMsg)
        run_report.generate_master(config)

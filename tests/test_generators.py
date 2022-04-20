# -*- coding: utf-8 -*-
import sys

from reports.models import location_consumption_model, location_production_model

sys.path.append("../reports")


def test_location_consumption_model(config):
    assert location_consumption_model.operation(config)


def test_location_production_model(config):
    assert location_production_model.operation(config)

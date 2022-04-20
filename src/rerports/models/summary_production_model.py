# -*- coding: utf-8 -*-
from __future__ import annotations
import datetime as dt
from collections import defaultdict
import numexpr as ne

from reports.config import get_logger
from reports.templates.daily_plots import product_summary_plot
from hubtools.utilities.tags import GetTags, TAGS
from hubtools.utilities.alter_table import (
    product_calculations,
    calculate_product_totals,
    calculate_cumulative_flows,
    calculate_cumulative_tank_volumes,
    get_location_data,
)
from reports.utilities.log_helper import log_call

logger = get_logger(__name__)

ne.set_num_threads(12)

NAME = GetTags().name
CONNECTION_TYPE = GetTags().connection_type
DESIGNATION = GetTags().designation
TRUCKED = GetTags().trucked
INLET_FLOWRATE = GetTags().inlet_flowrate
DISCHARGE_FLOWRATE = GetTags().discharge_flowrate
PRODUCT_TANK_VOLUME = GetTags().product_tank_volume
PRODUCT_FLOWRATE = GetTags().product_flowrate

FREQ = {"connection_1": 1 / 60, "connection_2": 1}


@log_call(logger=logger)
def operation():
    end_date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - dt.timedelta(days=1)

    product_summary_data = defaultdict(dict)

    upper_product_total = []
    upper_pumped = []
    lower_product_total = []
    lower_pumped = []
    upper_locations = []
    lower_locations = []
    location_type_a = []
    location_type_b = []

    for location, _ in TAGS:
        if INLET_FLOWRATE(location):
            trucked_tags = [INLET_FLOWRATE(location), PRODUCT_TANK_VOLUME(location)]
            nontrucked_tags = [
                INLET_FLOWRATE(location),
                PRODUCT_FLOWRATE(location),
                PRODUCT_TANK_VOLUME(location),
            ]
        else:
            trucked_tags = [DISCHARGE_FLOWRATE(location), PRODUCT_TANK_VOLUME(location)]
            nontrucked_tags = [
                DISCHARGE_FLOWRATE(location),
                PRODUCT_FLOWRATE(location),
                PRODUCT_TANK_VOLUME(location),
            ]
        if TRUCKED(location) == "YES":
            product_data = get_location_data(
                location,
                trucked_tags,
                ["inlet_flowrate", "product_tank_volume"],
                start_date,
                end_date,
                TRUCKED(location),
            )
        else:
            product_data = get_location_data(
                location,
                nontrucked_tags,
                ["inlet_flowrate", "product_flowrate", "product_tank_volume"],
                start_date,
                end_date,
                TRUCKED(location),
            )

        product_data["cum_liquid_product_flowrate"] = calculate_cumulative_flows(
            product_data.product_flowrate, FREQ[CONNECTION_TYPE(location)]
        )
        product_data["cum_pumped"] = product_data.cum_liquid_product_flowrate
        product_data["cum_tank"] = calculate_cumulative_tank_volumes(
            product_data.product_tank_volume, 1
        )
        _, product_data["cum_product"] = product_calculations(product_data)

        if CONNECTION_TYPE(location) == "connection_1":
            product_data = product_data[:-1]
            location_type_b_total, _ = calculate_product_totals(location, product_data)
            location_type_b.append(location_type_b_total)
        else:
            location_type_a_total, _ = calculate_product_totals(location, product_data)
            location_type_a.append(location_type_a_total)

        if DESIGNATION(location) == "UPPER":
            product_total_upper, product_pumped_upper = calculate_product_totals(
                location, product_data
            )
            if product_total_upper > 0:
                upper_product_total.append(product_total_upper)
            else:
                upper_product_total.append(0)
            upper_pumped.append(product_pumped_upper)
            upper_locations.append(NAME(location))

        if DESIGNATION(location) == "LOWER":
            product_total_lower, product_pumped_lower = calculate_product_totals(
                location, product_data
            )
            if product_total_lower > 0:
                lower_product_total.append(product_total_lower)
            else:
                lower_product_total.append(0)
            lower_pumped.append(product_pumped_lower)
            lower_locations.append(NAME(location))

    (
        product_summary_data["summary_figure"],
        product_summary_data["summary_axes"],
    ) = product_summary_plot(
        upper_locations,
        lower_locations,
        upper_product_total,
        upper_pumped,
        lower_product_total,
        lower_pumped,
    )
    product_summary_figure = [product_summary_data["summary_figure"]]

    return product_summary_figure

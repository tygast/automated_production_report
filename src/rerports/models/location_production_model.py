# -*- coding: utf-8 -*-
import datetime as dt
import pandas as pd

from collections import defaultdict

import numexpr as ne

from reports.models.summary_production_model import (
    PRODUCT_FLOWRATE,
    PRODUCT_TANK_VOLUME,
    CONNECTION_TYPE,
    INLET_FLOWRATE,
)
from reports.templates.daily_plots import product_plot, inlet_plot
from data_tools.utilities.tags import TAGS, GetTags
from data_tools.utilities.alter_table import (
    product_calculations,
    calculate_cumulative_flows,
    calculate_cumulative_tank_volumes,
    get_location_data,
)
from data_tools.utilities.summary_table import (
    calculate_product_summary_stats,
    calculate_flow_summary_stats,
    calculate_pressure_summary_stats,
)

ne.set_num_threads(12)

NAME = GetTags().name
CONNECTION_TYPE = GetTags().connection_type
INLET_FLOWRATE = GetTags().inlet_flowrate
PIPELINE_PRESSURE = GetTags().pipeline_pressure
INLET_NAMES = GetTags().inlet_names
FUEL_FLOWRATE = GetTags().fuel_flowrate
DISCHARGE_FLOWRATE = GetTags().discharge_flowrate
PRODUCT_TANK_VOLUME = GetTags().product_tank_volume
TRUCKED = GetTags().trucked
PRODUCT_FLOWRATE = GetTags().product_flowrate


def operation():
    end_date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - dt.timedelta(days=1)

    location_product_data = defaultdict(dict)
    location_inlet_data = defaultdict(dict)
    for location, _ in TAGS:
        if CONNECTION_TYPE(location) != "connection_1":
            product_data = get_location_data(
                location,
                [
                    INLET_FLOWRATE(location),
                    PRODUCT_FLOWRATE(location),
                    PRODUCT_TANK_VOLUME(location),
                ],
                ["inlet_flowrate", "product_flowrate", "product_tank_volume"],
                start_date,
                end_date,
                TRUCKED(location),
            )
            product_data["cumulative_inlet"] = calculate_cumulative_flows(
                product_data.inlet_flowrate, 1 / 1440
            )
            (
                product_data["product_per_M"],
                product_data["cum_product"],
            ) = product_calculations(product_data)
            product_data["cum_liquid_product_flowrate"] = calculate_cumulative_flows(
                product_data.product_flowrate, 1
            )
            product_data["cum_tank"] = calculate_cumulative_tank_volumes(
                product_data.product_tank_volume, 1
            )

            inlet_avg, product_avg_gpm, product_vol = calculate_product_summary_stats(
                product_data
            )
            (
                location_product_data[location]["product_figures"],
                location_product_data[location]["product_axes"],
            ) = product_plot(
                product_data, NAME(location), inlet_avg, product_avg_gpm, product_vol
            )
        if (
            INLET_FLOWRATE(location)
            and DISCHARGE_FLOWRATE(location)
            and FUEL_FLOWRATE(location)
        ):
            tags = [
                INLET_FLOWRATE(location),
                FUEL_FLOWRATE(location),
                DISCHARGE_FLOWRATE(location),
            ]
            cols = ["inlet_flowrate", "fuel_flowrate", "discharge_flowrate"]
        elif not INLET_FLOWRATE(location):
            tags = [FUEL_FLOWRATE(location), DISCHARGE_FLOWRATE(location)]
            cols = ["fuel_flowrate", "discharge_flowrate"]
        elif not DISCHARGE_FLOWRATE(location):
            tags = [INLET_FLOWRATE(location), FUEL_FLOWRATE(location)]
            cols = ["inlet_flowrate", "fuel_flowrate"]

        flow_data = get_location_data(
            location, tags, cols, start_date, end_date, TRUCKED(location),
        )
        if PIPELINE_PRESSURE(location):
            pressure_data = get_location_data(
                location,
                [PIPELINE_PRESSURE(location)],
                [INLET_NAMES(location)],
                start_date,
                end_date,
                TRUCKED(location),
                sum_values=False,
            )
            inlet_pressure_avg = calculate_pressure_summary_stats(pressure_data)
        else:
            pressure_data = pd.DataFrame()
            inlet_pressure_avg = pd.Series()
        inlet_avg, fuel_gas_avg, discharge_avg = calculate_flow_summary_stats(flow_data)
        (
            location_inlet_data[location]["inlet_figures"],
            location_inlet_data[location]["inlet_axes"],
        ) = inlet_plot(
            flow_data,
            pressure_data,
            NAME(location),
            inlet_avg,
            fuel_gas_avg,
            discharge_avg,
            inlet_pressure_avg,
        )

    product_figures = [
        location_product_data[location]["product_figures"]
        for location in location_product_data
    ]

    inlet_figures = [
        location_inlet_data[location]["inlet_figures"]
        for location in location_inlet_data
    ]

    return product_figures, inlet_figures

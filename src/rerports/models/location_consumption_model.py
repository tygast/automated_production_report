# -*- coding: utf-8 -*-
import datetime as dt

from collections import defaultdict

import numexpr as ne

from hubTools.algorithms.fill_and_drain_inference import (
    calculate_chemical_usage,
    infer_fill_and_drain,
)
from reports.templates.daily_plots import consum_measured_analysis, consum_plot
from hubtools.utilities.tags import TAGS, GetTags
from hubtools.utilities.alter_table import (
    calculate_cumulative_flows,
    get_location_data,
)
from hubtools.utilities.build_table import convert_to_zero, extend_list

ne.set_num_threads(12)

CONNECTION_TYPE = GetTags().connection_type
DESIGNATION = GetTags().designation
INLET_FLOWRATE = GetTags().inlet_flowrate
FUEL = GetTags().fuel
FUEL_FLOWRATE = GetTags().fuel_flowrate
TRUCKED = GetTags().trucked
CHEMICAL_A = GetTags().chemical_a
CHEMICAL_A_VOLUME = GetTags().chemical_a_volume


def flowrate_based_values(location, start_date: dt, end_date: dt):
    chem_data = get_location_data(
        location,
        [INLET_FLOWRATE(location), FUEL_FLOWRATE(location)],
        ["inlet_flowrate", "fuel_vol"],
        start_date,
        end_date,
        TRUCKED(location),
    )
    chem_data["cumulative_inlet"] = calculate_cumulative_flows(
        chem_data.inlet_flowrate, 1 / 1440
    )
    chem_data["cumulative_fuel"] = calculate_cumulative_flows(chem_data.fuel_vol, 1 / 1440)
    shift_1_values = chem_data.loc[chem_data.index.strftime("%H:%M:%S") == "19:00:00"]

    shift_2_values = chem_data.loc[
        chem_data.index.strftime("%H:%M:%S") == "07:00:00"
    ]
    shift_2_values = shift_2_values.drop(shift_2_values.index[0])

    return shift_1_values, shift_2_values


def level_based_values(location, start_date: dt, end_date: dt):
    chem_data = get_location_data(
        location,
        [INLET_FLOWRATE(location), CHEMICAL_A_VOLUME(location)],
        ["inlet_flowrate", "chemical_a_vol"],
        start_date,
        end_date,
        TRUCKED(location),
    )
    chem_data["cumulative_inlet"] = calculate_cumulative_flows(
        chem_data.inlet_flowrate, 1 / 1440
    )
    shift_1_start = start_date.replace(hour=7, minute=0, second=0)
    shift_1_end = shift_1_start + dt.timedelta(hours=12)
    shift_2_end = shift_1_end + dt.timedelta(hours=12)
    one_hour = dt.timedelta(hours=1)

    shift_1_level_data_slice = slice(
        start_date, shift_1_end + one_hour
    )  
    shift_2_level_data_slice = slice(
        shift_1_end - one_hour, shift_2_end + one_hour
    )
    shift_1 = chem_data.loc[shift_1_level_data_slice]
    if shift_1.empty:
        shift_1_chemical_a, shift_1_inlet = 0, 0
    else:
        valid_fwd_values, valid_bkwd_values, shift_1_inlet = infer_fill_and_drain(
            shift_1, shift_1_start, shift_1_end
        )
        shift_1_chemical_a = calculate_chemical_usage(valid_fwd_values, valid_bkwd_values)

    shift_2 = chem_data.loc[shift_2_level_data_slice]
    if shift_2.empty:
        shift_2_chemical_a, shift_2_inlet = 0, 0
    else:
        valid_fwd_values, valid_bkwd_values, shift_2_inlet = infer_fill_and_drain(
            shift_2, shift_1_end, shift_2_end,
        )
        shift_2_chemical_a = calculate_chemical_usage(valid_fwd_values, valid_bkwd_values)

    return shift_1_chemical_a, shift_2_chemical_a, shift_1_inlet, shift_2_inlet


def per_inlet_volume(
    shift_1_values, shift_2_values, chem_usage, shift_1_inlet=None, shift_2_inlet=None, column=None
):
    if chem_usage == "level_based":
        if shift_1_inlet == 0 and shift_2_inlet == 0:
            shift_1_per_inlet_volume = 0
            shift_2_per_inlet_volume = 0
        elif shift_1_inlet == 0 and shift_2_inlet != 0:
            shift_1_per_inlet_volume = 0
            shift_2_per_inlet_volume = shift_2_values / (shift_2_inlet / 1000)
        elif shift_1_inlet != 0 and shift_2_inlet == 0:
            shift_1_per_inlet_volume = shift_1_values / (shift_1_inlet / 1000)
            shift_2_per_inlet_volume = 0
        else:
            shift_1_per_inlet_volume = shift_1_values / (shift_1_inlet / 1000)
            shift_2_per_inlet_volume = shift_2_values / (shift_2_inlet / 1000)
    else:
        if shift_1_values.empty and shift_2_values.empty:
            shift_1_per_inlet_volume = 0
            shift_2_per_inlet_volume = 0
        elif shift_1_values.empty and shift_2_values.empty == False:
            shift_1_per_inlet_volume = 0
            shift_2_per_inlet_volume = (
                (shift_2_values[column].iloc[0] - shift_1_values[column].iloc[0]) * 1000
            ) / (shift_2_values.cumulative_inlet.iloc[0] - shift_1_values.cumulative_inlet.iloc[0])
        elif shift_1_values.empty == False and shift_2_values.empty:
            shift_1_per_inlet_volume = (shift_1_values[column].iloc[0] * 1000) / shift_1_values.cumulative_inlet.iloc[
                0
            ]
            shift_2_per_inlet_volume = 0
        elif shift_2_values.cumulative_inlet.iloc[0] - shift_1_values.cumulative_inlet.iloc[0] != 0:
            shift_1_per_inlet_volume = (shift_1_values[column].iloc[0] * 1000) / shift_1_values.cumulative_inlet.iloc[
                0
            ]

            shift_2_per_inlet_volume = (
                (shift_2_values[column].iloc[0] - shift_1_values[column].iloc[0]) * 1000
            ) / (shift_2_values.cumulative_inlet.iloc[0] - shift_1_values.cumulative_inlet.iloc[0])
        else:
            shift_1_per_inlet_volume = 0
            shift_2_per_inlet_volume = 0

    return shift_1_per_inlet_volume, shift_2_per_inlet_volume


def operation():
    end_date = dt.datetime.today().replace(hour=8, minute=0, second=0, microsecond=0)
    start_date = end_date - dt.timedelta(hours=26)

    location_chemical_a_data = defaultdict(dict)
    location_fuel_data = defaultdict(dict)
    location_type_b_tank_level = defaultdict(dict)

    chemical_a_shift_1_values = []
    chemical_a_shift_2_values = []
    fuel_shift_1_values = []
    fuel_shift_2_values = []
    location_names = []

    for location, _ in TAGS:
        if location != "Location_I" and CONNECTION_TYPE(location) != "connection_1":
            shift_1_chemical_a, shift_2_chemical_a, shift_1_inlet, shift_2_inlet = level_based_values(
                location, start_date, end_date,
            )

            shift_1_chemical_a_eff, shift_2_chemical_a_eff = per_inlet_volume(
                shift_1_chemical_a, shift_2_chemical_a, "level_based", shift_1_inlet, shift_2_inlet,
            )
            chemical_a_shift_1_values.append(shift_1_chemical_a_eff)
            chemical_a_shift_2_values.append(shift_2_chemical_a_eff)

            data = get_location_data(
                location,
                [INLET_FLOWRATE(location), CHEMICAL_A_VOLUME(location)],
                ["inlet_flowrate", "chemical_a_vol"],
                start_date,
                end_date,
                TRUCKED(location),
            )
            valid_fwd_values, valid_bkwd_values, _ = infer_fill_and_drain(
                data, start_date.replace(hour=7), end_date.replace(hour=7),
            )
            vol_used = calculate_chemical_usage(valid_fwd_values, valid_bkwd_values)

            (
                location_type_b_tank_level[location]["measured_figures"],
                location_type_b_tank_level[location]["summary_figures"],
            ) = consum_measured_analysis(
                start_date.replace(hour=7),
                end_date.replace(hour=7),
                location,
                data,
                valid_fwd_values,
                valid_bkwd_values,
                vol_used,
            )
            daily_measured_figures = [
                location_type_b_tank_level[location_type_b]["measured_figures"] for location_type_b in location_type_b_tank_level
            ]

        shift_1_fuel, shift_2_fuel = flowrate_based_values(location, start_date, end_date,)
        shift_1_fuel_avg, shift_2_fuel_avg = per_inlet_volume(
            shift_1_fuel, shift_2_fuel, "flow_based", column="cumulative_fuel"
        )
        fuel_shift_1_values.append(shift_1_fuel_avg)
        fuel_shift_2_values.append(shift_2_fuel_avg)
        location_names.append(location)

    chemical_a_shift_1_values = extend_list(chemical_a_shift_1_values)
    chemical_a_shift_2_values = extend_list(chemical_a_shift_2_values)

    chemical_a_shift_1_values = convert_to_zero(chemical_a_shift_1_values)
    chemical_a_shift_2_values = convert_to_zero(chemical_a_shift_2_values)

    fuel_shift_1_values = convert_to_zero(fuel_shift_1_values)
    fuel_shift_2_values = convert_to_zero(fuel_shift_2_values)
    (
        location_chemical_a_data["consum_figures"],
        location_chemical_a_data["summary_figures"],
    ) = consum_plot(chemical_a_shift_1_values, chemical_a_shift_2_values, location_names, "chemical_a",)

    (
        location_fuel_data["consum_figures"],
        location_fuel_data["summary_figures"],
    ) = consum_plot(fuel_shift_1_values, fuel_shift_2_values, location_names, "fuel",)

    daily_consum_figures = [
        location_chemical_a_data["consum_figures"],
        location_fuel_data["consum_figures"],
    ]

    return daily_consum_figures, daily_measured_figures

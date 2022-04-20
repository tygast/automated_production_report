import datetime as dt

import numexpr as ne

from reports.algorithms.fill_and_drain_inference import (
    calculate_chemical_usage,
    infer_fill_and_drain,
)
from reports.utilities.configuration import CONFIGURATION, Configuration
from reports.utilities.data_builder import get_location_data

ne.set_num_threads(12)

CONNECTION_TYPE = Configuration().connection_type
INLET_FLOWRATE = Configuration().inlet_flowrate
TRUCKED = Configuration().trucked
CHEMICAL_A_VOLUME = Configuration().chemical_a_volume
CHEMICAL_A = Configuration().chemical_a
CHEMICAL_B_VOLUME = Configuration().chemical_b_volume
CHEMICAL_B = Configuration().chemical_b
CHEMICAL_C_VOLUME = Configuration().chemical_c_volume
CHEMICAL_C = Configuration().chemical_c
CHEMICAL_D_VOLUME = Configuration().chemical_d_volume
CHEMICAL_D = Configuration().chemical_d
CHEMICAL_E_VOLUME = Configuration().chemical_e_volume
CHEMICAL_E = Configuration().chemical_e


def get_tank_volume():
    """
    Generates csv file to be used in spotfire analysis for chemical consumption.
    """
    end_date = dt.datetime.today().replace(hour=7, minute=0, second=0, microsecond=0)
    start_date = end_date - dt.timedelta(hours=24)
    for location, _ in CONFIGURATION:
        if location != "Location_I" and CONNECTION_TYPE(location) != "connection_1":
            tags = [
                CHEMICAL_A_VOLUME,
                CHEMICAL_B_VOLUME,
                CHEMICAL_C_VOLUME,
                CHEMICAL_D_VOLUME,
                CHEMICAL_E_VOLUME,
            ]
            chems = [CHEMICAL_A, CHEMICAL_B, CHEMICAL_C, CHEMICAL_D, CHEMICAL_E]
            for tag, chem in zip(tags, chems):
                try:
                    data = get_location_data(
                        location,
                        [INLET_FLOWRATE(location), tag(location)],
                        ["inlet_flowrate", "tank_volume"],
                        start_date,
                        end_date,
                        TRUCKED(location),
                    )
                    valid_fwd_values, valid_bkwd_values, _ = infer_fill_and_drain(
                        data, start_date.replace(hour=7), end_date.replace(hour=7),
                    )
                    vol_used = calculate_chemical_usage(
                        valid_fwd_values, valid_bkwd_values
                    )
                    data["datetime"] = data.index
                    data["vol_used"] = [vol_used] * len(data)
                    data["location"] = [str(location)] * len(data)
                    data["tank"] = [f"{chem(location).upper()}"] * len(data)
                    data["peak_locs"] = [0] * len(data)
                    if (
                        valid_fwd_values[0]["row_num"] != 0
                        and valid_bkwd_values[0]["row_num"] != 0
                    ):
                        for fwd_row, bkwd_row in zip(
                            valid_fwd_values, valid_bkwd_values
                        ):
                            data.peak_locs.loc[
                                data.datetime == fwd_row["peak_min_time"]
                            ] = 1
                            data.peak_locs.loc[
                                data.datetime == bkwd_row["peak_min_time"]
                            ] = 1

                    data.to_csv(
                        f"C:\\Users\\user1\\Projects\\data_files\\chem_report_data\\{location}_{chem(location)}.csv",
                        index=False,
                    )
                except KeyError:
                    pass


if __name__ == "__main__":
    get_tank_volume()

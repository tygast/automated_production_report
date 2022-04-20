# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime as dt

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

from matplotlib.dates import DateFormatter, HourLocator, MinuteLocator
from matplotlib.offsetbox import AnchoredText
from matplotlib.ticker import MultipleLocator
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

plt.rcParams["figure.figsize"] = [15, 10]
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["figure.titlesize"] = "large"
plt.rcParams["figure.titleweight"] = "bold"
plt.rcParams["figure.max_open_warning"] = 0


def autolabel(data, axis, name=None):
    rects = axis.patches
    for idx, rect in enumerate(rects):
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2
        space = y_value + (max(data) * 0.01)
        if name == "fuel":
            label = "{:.1f}".format(y_value)
        else:
            if idx == 16 or idx == 38:
                label = ""
            else:
                label = "{:.2f}".format(y_value)

        va = "bottom"

        axis.annotate(
            label,
            (x_value, space),
            xytext=(0, 2),
            textcoords="offset points",
            ha="center",
            rotation=90,
            va=va,
        )


def set_ticks(axis, data, which):
    scale = {
        "fuel": {
            "high": {"scale": 0.14, "step": 1.0},
            "med": {"scale": 0.14, "step": 0.5},
            "low": {"scale": 0.14, "step": 0.1},
        },
        "flow": {
            "high": {"scale": 1.4, "step": 10},
            "med": {"scale": 1.4, "step": 5},
            "low": {"scale": 1.4, "step": 1},
        },
    }
    if data.max() > 40:
        try:
            scaled_axis = axis.set_yticks(
                np.arange(
                    0,
                    data.max() * scale[which]["high"]["scale"],
                    scale[which]["high"]["step"],
                )
            )
        except ValueError:
            pass
    elif data.max() < 10:
        try:
            scaled_axis = axis.set_yticks(
                np.arange(
                    0,
                    data.max() * scale[which]["low"]["scale"],
                    scale[which]["low"]["step"],
                )
            )
        except ValueError:
            pass
    else:
        try:
            scaled_axis = axis.set_yticks(
                np.arange(
                    0,
                    data.max() * scale[which]["med"]["scale"],
                    scale[which]["med"]["step"],
                )
            )
        except ValueError:
            pass
    return scaled_axis


def inlet_plot(
    df_1,
    df_2,
    location_type_b_name,
    inlet_avg,
    fuel_gas_avg,
    discharge_avg,
    inlet_pressure_avg,
):
    fig, (flow, psi) = plt.subplots(2, sharex=True)
    fig.suptitle(f"{location_type_b_name} Inlet Analysis", size=20, ha="left", x=0.1)

    flow.title.set_text("Volume")
    flow.grid(True, linestyle="--")

    if "inlet_flowrate" in df_1 and "discharge_flowrate" in df_1:
        flow.plot(df_1.index, df_1.inlet_flowrate, label="Inlet", color="tab:blue")
        flow.plot(
            df_1.index, df_1.discharge_flowrate, label="Discharge", color="tab:orange"
        )
        flow_textstr = f"Inlet Avg = {round(inlet_avg,2)} SCFD\nDischarge Avg = {round(discharge_avg,2)} SCFD\nFuel Gas Avg = {round(fuel_gas_avg,2)} SCFD"
        set_ticks(flow, df_1.inlet_flowrate, "flow")
    elif "discharge_flowrate" in df_1 and "inlet_flowrate" not in df_1:
        flow.plot(
            df_1.index, df_1.discharge_flowrate, label="Discharge", color="tab:orange"
        )
        flow_textstr = f"Inlet Avg = NA\nDischarge Avg = {round(discharge_avg,2)} SCFD\nFuel Gas Avg = {round(fuel_gas_avg,2)} SCFD"
        set_ticks(flow, df_1.discharge_flowrate, "flow")
    else:
        flow.plot(df_1.index, df_1.inlet_flowrate, label="Inlet", color="tab:blue")
        flow_textstr = f"Inlet Avg = {round(inlet_avg,2)} SCFD\nDischarge Avg = NA\nFuel Gas Avg = {round(fuel_gas_avg,2)} SCFD"
        set_ticks(flow, df_1.inlet_flowrate, "flow")

    flow.set_ylabel("SCFD (Inlet & Discharge)")
    flow.set_xticks(df_1.index)
    flow.set_xticklabels(df_1.index, rotation="vertical")
    flow.xaxis.set_major_locator(HourLocator(interval=1))
    flow.xaxis.set_minor_locator(MinuteLocator(interval=15))
    flow.xaxis.set_major_formatter(DateFormatter("%I:%M %p"))

    fuel = flow.twinx()
    fuel.plot(df_1.index, df_1.fuel_flowrate, color="#0a481e", label="Fuel Gas")
    fuel.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.1f"))

    if "inlet_flowrate" in df_1:
        set_ticks(fuel, df_1.inlet_flowrate, "fuel")
    else:
        set_ticks(fuel, df_1.discharge_flowrate, "fuel")

    fuel.set_ylabel("SCFD (Fuel Gas)")
    fuel.spines["right"].set_color("#0a481e")
    fuel.yaxis.label.set_color("#0a481e")
    fuel.tick_params(axis="y", colors="#0a481e")

    handles, labels = [], []
    for ax in fig.axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            handles.append(h)
            labels.append(l)

    plt.legend(
        handles, labels, bbox_to_anchor=(1.03, 1), loc="upper left", borderaxespad=0.0
    )

    psi.title.set_text("Pressure")
    psi.grid(True, linestyle="--")

    psi.set_ylabel("PSI")

    psi.set_xticks(df_1.index)
    psi.set_xticklabels(df_1.index, rotation="vertical")
    psi.xaxis.set_major_locator(HourLocator(interval=1))
    psi.xaxis.set_minor_locator(MinuteLocator(interval=15))
    psi.xaxis.set_major_formatter(DateFormatter("%I:%M %p"))

    if not df_2.empty:
        psi_color = {
            0: "#047495",
            1: "#789b73",
            2: "#856798",
            3: "#a83c09",
            4: "#fec615",
        }
        psi_textstr = ""
        for name, value in zip(df_2, inlet_pressure_avg):
            if name != "product_flowrate":
                psi.plot(
                    df_2.index,
                    df_2[name],
                    color=psi_color[df_2.columns.get_loc(name)],
                    label=name,
                )
                psi_textstr = psi_textstr + f"{name} Avg = {round(value, 2)} PSI\n"

        psi_textstr = psi_textstr.rstrip()
        psi_text_box = AnchoredText(psi_textstr, frameon=True, loc=3, pad=0.01)
        plt.setp(psi_text_box.patch, boxstyle="round", facecolor="wheat", alpha=0.5)
        psi.add_artist(psi_text_box)
        try:
            psi.set_yticks(np.arange(0, df_2.values.max() * 1.4, 10))
        except ValueError:
            pass
        psi.legend(bbox_to_anchor=(1.03, 1), loc="upper left", borderaxespad=0.0)
    else:
        text_kwargs = dict(
            ha="center", va="center", fontsize=28, color="C3", in_layout=True
        )
        psi.text(
            0.5,
            0.5,
            "No Data.",
            **text_kwargs,
            transform=psi.transAxes,
            label="_nolegend_",
        )

    flow_text_box = AnchoredText(flow_textstr, frameon=True, loc=3, pad=0.01)
    plt.setp(flow_text_box.patch, boxstyle="round", facecolor="wheat", alpha=0.5)
    flow.add_artist(flow_text_box)

    return fig, (flow, psi)


def product_plot(df, location_type_b_name, inlet_avg, product_avg_gpm, product_vol):
    fig, (gpm, gal) = plt.subplots(2, sharex=True)
    fig.suptitle(f"{location_type_b_name} Production Rates", size=20, ha="left", x=0.1)

    gpm.title.set_text("Recovery Rate")
    gpm.grid(True, linestyle="--")

    gpm.plot(df.index, df.product_per_M, color="#5b7c99")

    gpm.set_ylabel("gal/SCF")
    if not np.isnan(df.product_per_M.max()):
        try:

            gpm.set_yticks(
                np.arange(0, ((df.product_per_M.max() * 1.2 // 0.1) / 10) + 0.1, 0.2)
            )

        except ValueError:
            pass

    gal.title.set_text("Accumulation")
    gal.grid(True, linestyle="--")

    gal.plot(df.index, df.cum_product / 42, color="#789b73")

    gal.set_ylabel("gal")

    if location_type_b_name == "Location_I":
        try:
            gal.set_yticks(np.arange(0, ((product_vol * 1.2 // 100) * 100) + 100, 200))
        except ValueError:
            pass
    else:
        try:
            gal.set_yticks(np.arange(0, ((product_vol * 1.2 // 100) * 100) + 100, 100))
        except ValueError:
            pass

    gal.fill_between(df.index, 0, df.cum_product / 42, color="#789b73")

    gal.set_xticks(df.index)
    gal.set_xticklabels(df.index, rotation="vertical")
    gal.xaxis.set_major_locator(HourLocator(interval=1))
    gal.xaxis.set_minor_locator(MinuteLocator(interval=15))
    gal.xaxis.set_major_formatter(DateFormatter("%I:%M %p"))

    textstr = (
        "$Inlet~Avg=%.2f~SCFD$\n$Product~Avg=%.2f~gal$/$M$\n$Product~Total=%.2f~gal$"
        % (inlet_avg, product_avg_gpm, product_vol,)
    )

    text_box = AnchoredText(textstr, frameon=True, loc=2, pad=0.01)

    plt.setp(text_box.patch, boxstyle="round", facecolor="#ada587", alpha=0.5)

    gal.add_artist(text_box)

    return fig, (gpm, gal)


def consum_plot(shift_1, shift_2, location_names, chem_name):

    y_pos = np.arange(len(location_names))
    width = 0.25

    COLORS = {"chemical_a": ["#fac205", "#bf9005"], "fuel": ["#b1d1fc", "#607c8e"]}

    fig, consum = plt.subplots(1)
    consum.bar(
        y_pos - 0.175, shift_1, width, color=COLORS[chem_name][0], label="shift_1"
    )
    consum.bar(
        y_pos + 0.175, shift_2, width, color=COLORS[chem_name][1], label="shift_2",
    )

    if chem_name == "fuel":
        plt.axhline(y=35, xmin=0, linestyle=":", color="#840000", alpha=0.65)
        plt.text(21.5, 35, "Usage Goal", color="#840000", style="italic")
    else:
        plt.axhline(y=4 / 35, xmin=0, linestyle=":", color="#840000", alpha=0.65)
        plt.text(21.5, 4 / 35, "Usage Goal", color="#840000", style="italic")

    consum.title.set_text(f"Daily {chem_name.upper()} Usage Summary")

    consum.set_xticks(y_pos)
    consum.set_xticklabels(location_names, rotation="vertical")

    consum.set_ylim(0, max(max(shift_1), max(shift_2)) * 1.1)

    if chem_name == "fuel":
        consum.set_ylabel("SCF")
        try:
            consum.set_yticks(
                np.arange(
                    0, ((max(max(shift_1), max(shift_2)) * 1.4 // 0.1) / 10) + 0.1, 10,
                )
            )
            consum.yaxis.set_minor_locator(MultipleLocator(5))
        except ValueError:
            pass
    else:
        consum.set_ylabel("gal/SCF")
        try:
            consum.set_yticks(
                np.arange(
                    0, ((max(max(shift_1), max(shift_2)) * 0.14 // 0.1) / 10) + 0.1,
                ),
                0.05,
            )
            consum.yaxis.set_minor_locator(MultipleLocator(0.1))
        except ValueError:
            pass

    autolabel(shift_1, consum, chem_name)

    handles, labels = [], []
    for ax in fig.axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            handles.append(h)
            labels.append(l)

    plt.legend(
        handles, labels, loc="upper right", borderaxespad=1,
    )

    return fig, consum


def consum_measured_analysis(
    shift_start: dt.datetime,
    shift_end: dt.datetime,
    location: str,
    data: pd.DataFrame,
    fwd_values: list,
    bkwd_values: list,
    vol_used: float = None,
):
    data = data.loc[shift_start:shift_end]

    formatter = mdates.DateFormatter("%I:%M %p")
    locator = mdates.HourLocator(interval=1)
    sub_locator = mdates.MinuteLocator(interval=15)

    fig, (md, vol) = plt.subplots(2, sharex=True)
    fig.suptitle(
        f"{location} Chemical A Tank Volume Analysis", size=20, ha="left", x=0.1
    )

    md.title.set_text("Mahalanobis Distance")
    md.plot(data.fwd_mds, color="#82cafc", label="fwd_pass")
    md.plot(data.bkwd_mds, color="#cf6275", label="bkwd_pass")

    md.set_ylabel("sigma (σ)", fontsize=12)
    md.legend()
    md.grid(linewidth=0.5)

    vol.title.set_text("Tank Level")
    vol.plot(data.filtered_vol_fwd, color="#82cafc", label="fwd_pass")
    vol.plot(data.filtered_vol_bkwd, color="#cf6275", label="bkwd_pass")
    vol.plot(data.chemical_a_vol, color="#fcb001", label="measured", alpha=0.45)
    vol.text(
        0,
        1.01,
        f"Volume Used: {vol_used} gal",
        horizontalalignment="left",
        verticalalignment="bottom",
        color="#8b2e16",
        fontsize=11,
        transform=vol.transAxes,
    )

    if vol_used > 0:
        for fwd, bkwd in zip(fwd_values, bkwd_values):
            md.plot(fwd["peak_time"], fwd["peak"], "b.")
            md.plot(bkwd["peak_time"], bkwd["peak"], "r.")

            md_date_fwd = fwd["peak_min_time"].strftime("%I:%M %p")
            md_date_bkwd = bkwd["peak_min_time"].strftime("%I:%M %p")
            level_fwd = round(fwd["level"], 2)
            level_bkwd = round(bkwd["level"], 2)

            md.plot(fwd["peak_min_time"], fwd["peak_min"], "bx", markersize=7)
            vol.plot(fwd["peak_min_time"], fwd["level"], "bx", markersize=7)
            vol.annotate(
                f"({md_date_fwd}, {level_fwd})",
                xy=(fwd["peak_min_time"], fwd["level"]),
                textcoords="data",
            )
            md.plot(bkwd["peak_min_time"], bkwd["peak_min"], "rx", markersize=7)
            vol.plot(bkwd["peak_min_time"], bkwd["level"], "rx", markersize=7)
            vol.annotate(
                f"({md_date_bkwd}, {level_bkwd})",
                xy=(bkwd["peak_min_time"], bkwd["level"]),
                textcoords="data",
                horizontalalignment="right",
                verticalalignment="top",
            )

    vol.set_ylabel("gal", fontsize=12)
    vol.xaxis.set_major_formatter(formatter)
    vol.xaxis.set_major_locator(locator)
    vol.xaxis.set_minor_locator(sub_locator)
    vol.legend()
    vol.grid(linewidth=0.5)

    plt.xticks(rotation=90)

    return fig, (md, vol)


def product_summary_plot(
    upper_locations,
    lower_locations,
    upper_product_total,
    upper_pumped,
    lower_product_total,
    lower_pumped,
    days_in_week,
    weekly_location_type_a_prod,
    weekly_location_type_b_prod,
    weekly_total_prod,
):
    blank_str = [""]
    blank_num = [0.000001]
    locations = upper_locations + blank_str + lower_locations
    prod_total = upper_product_total + blank_num + lower_product_total
    pumped_total = upper_pumped + blank_num + lower_pumped

    y_pos = np.arange(len(locations))
    width = 0.3

    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(3, 1)
    weekly = fig.add_subplot(gs[:1, :])
    daily = fig.add_subplot(gs[1:, :])

    daily.bar(y_pos - 0.23, prod_total, width, label="Total Produced", color="#2b5d34")
    daily.bar(
        y_pos + 0.23,
        pumped_total,
        width,
        label="Total Pumped to Sales",
        color="#96ae8d",
    )
    daily.title.set_text(f"Daily Product Summary")
    daily.set_xticks(y_pos)
    daily.set_xticklabels(locations, rotation="vertical")
    daily.set_ylabel("gal")
    daily.set_ylim(0, max(max(prod_total), max(pumped_total)) * 1.3)

    autolabel(prod_total, daily)

    handles, labels = [], []
    for ax in fig.axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            handles.append(h)
            labels.append(l)

    daily.legend(
        handles,
        labels,
        bbox_to_anchor=(1.01, 0.98),
        loc="upper left",
        borderaxespad=0.0,
        frameon=False,
    )

    daily_textstr = (
        r"$\it{Upper:}$"
        + f"\nProduced={round(sum(upper_product_total),2)} gal,  Pumped={round(sum(upper_pumped),2)} gal\n"
        + r"$\it{Lower:}$"
        + f"\nProduced={round(sum(lower_product_total),2)} gal,  Pumped={round(sum(lower_pumped),2)} gal\n"
        + r"$\it{Total:}$"
        + f"\nProduced={round(sum(lower_product_total) + sum(upper_product_total),2)} gal,  Pumped={round(sum(lower_pumped) + sum(upper_pumped),2)} gal"
    )

    daily_text_box = AnchoredText(daily_textstr, frameon=True, loc=2, pad=0.01)
    plt.setp(daily_text_box.patch, boxstyle="round", facecolor="#5b7c99", alpha=0.25)

    daily.add_artist(daily_text_box)

    trucked_textstr = r"$\bf{Trucked~Locations:}$" + "\n--Location~F\n--Location~I"

    trucked_box = AnchoredText(
        trucked_textstr,
        frameon=True,
        bbox_to_anchor=(1.01, 0.85),
        bbox_transform=ax.transAxes,
        loc="upper left",
        pad=0.01,
    )
    plt.setp(trucked_box.patch, boxstyle="round", alpha=0.25)

    daily.add_artist(trucked_box)
    daily.text(
        0.374, 0.7, "upper", transform=ax.transAxes, fontsize=15, fontweight="bold"
    )
    daily.text(
        0.84, 0.7, "lower", transform=ax.transAxes, fontsize=15, fontweight="bold"
    )
    weekly.title.set_text("Previous 7 Day Production")
    weekly.plot(
        days_in_week, weekly_total_prod, label="Total Production", color="#1e488f"
    )
    weekly.plot(
        days_in_week,
        weekly_location_type_a_prod,
        label="Location Type A Production",
        color="#b04e0f",
    )
    weekly.plot(
        days_in_week,
        weekly_location_type_b_prod,
        label="Location Type B Production",
        color="#045producta",
    )

    weekly.set_ylabel("gal")
    try:

        weekly.set_yticks(
            np.arange(0, ((max(weekly_total_prod) * 1.3 // 1000) * 1000) + 1000, 1000)
        )
    except ValueError:
        pass
    weekly.xaxis.set_major_formatter(DateFormatter("%b %d,%Y"))

    for x, y in zip(days_in_week, weekly_total_prod):
        label = "{:.2f}".format(y)
        weekly.annotate(
            label,
            (x, y),
            textcoords="offset points",
            xytext=(0, 4),
            ha="center",
            fontweight="bold",
            color="#070d0d",
        )

    for x, y in zip(days_in_week, weekly_location_type_a_prod):
        label = "{:.2f}".format(y)
        weekly.annotate(
            label,
            (x, y),
            textcoords="offset points",
            xytext=(0, 4),
            ha="center",
            fontweight="bold",
            color="#6b7c85",
        )

    for x, y in zip(days_in_week, weekly_location_type_b_prod):
        label = "{:.2f}".format(y)
        weekly.annotate(
            label,
            (x, y),
            textcoords="offset points",
            xytext=(0, 4),
            ha="center",
            fontweight="bold",
            color="#6b7c85",
        )

    weekly_textstr = (
        r"$\bf{Average~Production:}$"
        + "\n$Total=%.2f~gpm$\n$Location~Type~A=%.2f~BPD$\n$Location~Type~B=%.2f~gpm$"
        % (
            np.average(weekly_total_prod),
            np.average(weekly_location_type_a_prod),
            np.average(weekly_location_type_b_prod),
        )
    )

    weekly_text_box = AnchoredText(
        weekly_textstr,
        bbox_to_anchor=(1.01, 1.45),
        bbox_transform=ax.transAxes,
        loc="upper left",
        frameon=True,
    )
    plt.setp(weekly_text_box.patch, boxstyle="round", alpha=0.25)
    weekly.add_artist(weekly_text_box)

    weekly.grid(True, linestyle="--")
    weekly.legend(
        bbox_to_anchor=(1.01, 0.98), loc="upper left", borderaxespad=0.0, frameon=False
    )

    gs.tight_layout(fig, pad=0)

    return fig, (daily, weekly)

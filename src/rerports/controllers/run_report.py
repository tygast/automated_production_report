# -*- coding: utf-8 -*-
# %%
import datetime as dt

from reports.config import get_logger
from reports.models import summary_production_model, location_consumption_model, location_production_model
from reports.email import email_recips, email_utils
from reports.utilities.log_helper import log_call

logger = get_logger(__name__)

@log_call(logger=logger)
def generate_master():
    end_date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - dt.timedelta(days=1)

    product_summary_figure = summary_production_model.operation()

    location_consumable_figures, location_measured_figures = location_consumption_model.operation()

    location_product_figures, location_inlet_figures = location_production_model.operation()

    logger.info("\nStarting add all figures to Master Report")
    all_figs = (
        product_summary_figure
        + location_product_figures
        + location_inlet_figures
        + location_consumable_figures
        + location_measured_figures
    )
    logger.info("Add all figures to Master Report complete\n")
    if not all_figs:
        raise Exception("All figures failed\n")

    logger.info("\nCreating email for Master Report")
    email = email_utils.EmailMsg(
        email_recips.get_recipiant_list("all"),
        f"Location & Unit Operation Report - {start_date.strftime('%B %d')}",
    )
    email.convert_plots_to_attachment(
        f"Location & Unit Summary {start_date.strftime('%m-%d-%Y')}.pdf",
        all_figs,
    )

    email.send()
    logger.info("Email for Master Report prepared to send\n")

if __name__ == "__main__":
    generate_master()

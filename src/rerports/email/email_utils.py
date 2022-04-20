# -*- coding: utf-8 -*-
from __future__ import annotations

import mimetypes
import smtplib

from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from tempfile import TemporaryDirectory

from matplotlib.backends.backend_pdf import PdfPages
from reports.config import get_logger
from reports.utilities.log_helper import log_call

logger = get_logger(__name__)

SIGNATURE = (
    '<div style="font-family: agency fb; font-size:130%;"><b>Name</b></div>\n'
    "<div>Company</div>\n"
    "<div>Address</div>\n"
    "<div>City & Zip</div>\n"
    "<div>Office: (000) 000-0000</div>\n"
    "<div>Cell: (111) 111-1111</div>\n"
    "<div>user@company.com</div>\n"
)


class EmailMsg:
    def __init__(self, recipient_list, subject, signature=SIGNATURE):
        self.sender = "user1@company.com"
        self.subject = subject
        self.recipient_list = recipient_list
        self.signature = signature
        self.attachments = []
        self.images = []
        self.text = []

    @log_call(logger=logger)
    def send(self):
        msg = self.construct_msg()
        with smtplib.SMTP("smtp.company.com") as mailer:
            server_response = smtplib.SMTP.ehlo(mailer)
            mailer.sendmail(msg["From"], self.recipient_list, msg.as_string())

    def construct_msg(self):
        msg = MIMEMultipart()
        msg["Subject"] = self.subject
        msg["From"] = self.sender
        for attachment in self.attachments:
            msg.attach(attachment)
        for display in self.images:
            msg.attach(display)
        all_text = "<br></br>".join(self.text)
        all_text += "<br></br>" + self.signature
        msg.attach(MIMEText(all_text, "html"))
        return msg

    @log_call(logger=logger)
    def convert_plots_to_attachment(self, figure_name, figures):
        if not isinstance(figures, (list, tuple)):
            figures = [figures]
        with TemporaryDirectory() as temp_dir:
            dir_path = Path(str(temp_dir))
            file = dir_path / "plots.pdf"
            with PdfPages(file) as pdf_file:
                for figure in figures:
                    pdf_file.savefig(figure, dpi=300, bbox_inches="tight")
            self.attach_file(figure_name, file, "pdf")

    def attach_file(self, attachment_name, file, file_type):
        with file.open("rb") as f:
            attachment = MIMEApplication(f.read(), _subtype=file_type)
        attachment.add_header(
            "Content-Disposition", "attachment", filename=attachment_name
        )
        self.attachments.append(attachment)

    def add_image(self, image_name, image):
        c_type, encoding = mimetypes.guess_type(image)
        main_type, sub_type = c_type.split("/", 1)
        attachment = MIMEImage(image, _subtype=sub_type)
        attachment.add_header(
            "Content-Disposition", "attachment", image_name=image_name
        )
        self.images.append(attachment)
        self.add_text(f'<p><img src="cid:{len(self.images)-1}"></p>')

    def add_text(self, text):
        self.text.append(text)

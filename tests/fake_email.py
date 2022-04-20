# -*- coding: utf-8 -*-
from __future__ import annotations


class FakeMsg:
    def __init__(self, recipient_list, subject, signature="TEST"):
        self.sender = "testing"
        self.subject = subject
        self.recipient_list = recipient_list
        self.signature = signature
        self.attachments = {}
        self.images = {}
        self.text = []

    def send(self):
        pass

    def construct_msg(self):
        pass

    def convert_plots_to_attachment(self, figure_name, figures):
        self.attach_file(figure_name, figures, "pdf")

    def attach_file(self, attachment_name, file, file_type):
        self.attachments[attachment_name] = (file, file_type)

    def add_image(self, image_name, image):
        self.images[image_name] = image

    def add_text(self, text):
        self.text.append(text)

import logging
from logging.handlers import SMTPHandler
import sys

logger = logging.getLogger("Test")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler2 = SMTPHandler(
    mailhost="smtp.company.com",
    fromaddr="user1@company.com",
    toaddrs=["user1@company.com"],
    subject="Test",
)
handler.setLevel(logging.DEBUG)
handler2.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(handler2)


logger.info("Does this work")

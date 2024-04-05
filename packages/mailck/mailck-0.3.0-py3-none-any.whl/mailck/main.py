#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  SPDX-License-Identifier: GPL-3.0-only
#  Copyright 2023 drad <sa@adercon.com>

import email
import imaplib
import json
import logging
import sys
from datetime import datetime
from enum import Enum
from optparse import OptionParser
from os import getenv


logger_base = logging.getLogger("default")
logger_base.setLevel(logging.getLevelName(getenv("LOG_LEVEL", "INFO")))
logger_base.addHandler(logging.StreamHandler(sys.stdout))
logger = logging.LoggerAdapter(logging.getLogger("default"))


class MessageFormat(str, Enum):
    short = "short"
    horizontal1 = "horizontal1"


class MCRequest:
    server: str = None
    port: int = None
    username: str = None
    password: str = None
    folder: str = None
    message_type: str = None
    messages_date_format: str = None
    messages_format: MessageFormat = None
    show_messages: bool = False
    password_cmd: str = None
    output_prefix: str = ""
    output_suffix: str = ""

    def __init__(self, dictionary):
        self.__dict__.update(dictionary)

    def validate(self):
        """
        Validate a MCRequest.

        NOTICE: validation also handles setting the password from the password-cmd if password-cmd is used.
        """

        logger.debug("Validating MCRequest...")
        if not self.server:
            raise ValueError("Server not supplied")
        if not self.port:
            raise ValueError("Server Port not supplied")
        if not self.username:
            raise ValueError("Server Username not supplied")
        if not self.password and not self.password_cmd:
            raise ValueError(
                "Server password or password-cmd not supplied! You must provide either a password or a password-cmd (we recommend password-cmd)"
            )
        elif self.password:
            # we have a password from arg, use it
            pass
        elif self.password_cmd and not self.password:
            # get the password from the password_cmd
            import subprocess  # nosec

            _pwdcmdres = subprocess.check_output(self.password_cmd.split())  # nosec
            self.password = _pwdcmdres.decode("utf-8").rstrip()

        logger.debug("MCRequest is valid!")
        return True

    def dump(self):
        """
        Dump.
        """

        logger.debug(f"{self.__dict__}")

    def to_json(self):
        """
        Dump to json.
        """

        return json.dumps(self.__dict__, indent=4)


def show_version():
    """
    Show version.
    """

    import importlib.metadata

    _meta = importlib.metadata.metadata("mailck")
    _name = _meta["Name"]
    _version = _meta["Version"]

    logger.critical(f"{_name} {_version}")


def check_mail(r: MCRequest = None):
    """
    Check mail.
    """

    logger.debug("checking mail...")
    mail = imaplib.IMAP4_SSL(host=r.server, port=r.port)
    (retcode, capabilities) = mail.login(r.username, r.password)
    mail.list()
    mail.select(r.folder, readonly=True)

    n = 0
    (retcode, messages) = mail.search(None, r.message_type)
    if retcode == "OK":
        for num in messages[0].split():
            n = n + 1
            if r.show_messages:
                resp_code, mail_data = mail.fetch(num, "(RFC822)")
                message = email.message_from_bytes(mail_data[0][1])
                _date = datetime.strptime(
                    message.get("Date"), "%a, %d %b %Y %H:%M:%S %z"
                )
                if r.messages_format == MessageFormat.short:
                    logger.critical(
                        f"{message.get('From')}, {_date.strftime(r.messages_date_format)}, {message.get('Subject')}"
                    )
                elif r.messages_format == MessageFormat.horizontal1:
                    logger.critical(f"From       : {message.get('From')}")
                    # ~ logger.critical(f"To         : {message.get('To')}")
                    # ~ logger.critical(f"Bcc        : {message.get('Bcc')}")
                    logger.critical(
                        f"Date       : {_date.strftime(r.messages_date_format)}"
                    )
                    logger.critical(f"Subject    : {message.get('Subject')}")
                    logger.critical("---------------------------------")
                else:
                    pass

    # the base/normal output which is the # of messages only.
    logger.critical(f"{r.output_prefix}{n}{r.output_suffix}")

    mail.close()
    mail.logout()


def app():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)

    parser.add_option(
        "-f",
        "--folder",
        dest="folder",
        default="inbox",
        help="folder to check mail for (e.g. inbox, inbox.Send)",
    )
    parser.add_option(
        "-m",
        "--show-messages",
        dest="show_messages",
        default=False,
        help="show messages (from, subject)",
    )
    parser.add_option(
        "-p",
        "--port",
        dest="port",
        default=993,
        help="mail server port (e.g. 143, 993)",
    )
    parser.add_option(
        "-s", "--server", dest="server", help="mail server url (e.g. mail.example.com)"
    )
    parser.add_option(
        "-t",
        "--message-type",
        dest="message_type",
        default="(UNSEEN)",
        help="message type to check for (e.g. '(UNSEEN)', '(ALL)')",
    )
    parser.add_option(
        "-u",
        "--username",
        dest="username",
        help="mail server username (e.g. myuser, myuser@example.com)",
    )
    parser.add_option(
        "--password",
        dest="password",
        help="mail server password (NOTE: we recommend using --password-cmd instead of supplying a password)",
    )
    parser.add_option(
        "--messages-format",
        dest="messages_format",
        default="short",
        help="[short|horizontal1] format to display messages in (only applicable if --show-messages=true)",
    )
    parser.add_option(
        "--messages-date-format",
        dest="messages_date_format",
        default="%Y-%m-%d %H:%M",
        help="date format to use in messages - uses python's strftime for formatting (only applicable if --show-messages=true)",
    )
    parser.add_option(
        "--password-cmd",
        dest="password_cmd",
        help="command to get the password (e.g. 'spw -g mail/my-account -u')",
    )
    parser.add_option(
        "--prefix",
        dest="output_prefix",
        default="",
        help="prefix to add to output (e.g. 'my-account: ', 'new mail: ')",
    )
    parser.add_option(
        "--suffix",
        dest="output_suffix",
        default="",
        help="suffix to add to output (e.g. ' (unread)', ' (new)')",
    )
    parser.add_option(
        "--version",
        action="store_true",
        dest="showVersion",
        help="show script version and exit",
    )

    (options, args) = parser.parse_args()
    _options = vars(options)

    if options.showVersion:
        show_version()
        sys.exit()
    else:
        # remove unneeded items.
        del _options["showVersion"]

    try:
        _req = MCRequest(vars(options))
        _req.validate()
        check_mail(_req)
        sys.exit()

    except ValueError as e:
        logger.critical(e)
        sys.exit(1)

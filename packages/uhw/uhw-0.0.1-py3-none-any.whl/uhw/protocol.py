#!/usr/bin/env python
# -*- coding: utf-8 -*-

from asyncio import Protocol
from logging import debug

from .parser import split_line


def find(commands: dict, command: str) -> dict | None:
    """
    Find the first matching command for a given string.
    """

    for value in commands.values():
        regex = value.get("regex")
        if regex.match(command):
            return value
    return None


class ProtocolFactory(Protocol):
    """Protocol factory representation."""

    def __init__(self, commands: dict) -> None:
        self.commands = commands

    def connection_made(self, transport):
        """
        Called when a connection is made.
        """

        peername = transport.get_extra_info("peername")
        debug(f"Connection from {peername}")
        self.transport = transport

    def data_received(self, data: bytes):
        """
        Called when some data is received. data is a non-empty
        bytes object containing the incoming data.
        """

        message = data.decode()
        debug(f"Data received: {message!r}")
        for name, args, query in split_line(message):
            debug(f"Lookup request: {name!r}")
            command = find(self.commands, name)
            if not command:
                continue  # i.e. does not match
            debug(f"Match: {command!r}")
            if not query:
                push = command.get("push")
                debug(f"Calling push: {push!r}")
                push(args)
                continue
            pull = command.get("pull")
            debug(f"Calling pull: {pull!r}")
            response = pull(args)
            debug(f"Send: {response!r}")
            self.transport.write(response.encode())

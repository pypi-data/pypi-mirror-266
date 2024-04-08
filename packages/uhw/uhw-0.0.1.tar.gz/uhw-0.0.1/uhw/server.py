#!/usr/bin/env python
# -*- coding: utf-8 -*-

from asyncio import AbstractEventLoop
from asyncio import get_running_loop
from asyncio import run as asyncio_run
from ssl import SSLContext
from typing import Any
from typing import Callable

from .parser import command_to_compiled_regex
from .protocol import ProtocolFactory


class UHW:
    """
    Server application.
    """

    commands: dict = {}

    def __init__(self, import_name: str) -> None:
        self.import_name = import_name

    def push(self, name: str) -> None:
        """
        Decorator method for registering push commands.
        """

        def wrapper(func: Callable) -> None:
            if not self.commands.get(name, None):
                regex = command_to_compiled_regex(name)
                self.commands[name] = dict(regex=regex)
            self.commands[name]["push"] = func

        return wrapper

    def pull(self, name: str) -> None:
        """
        Decorator method for registering pull commands.
        """

        def wrapper(func: Callable) -> None:
            if not self.commands.get(name, None):
                regex = command_to_compiled_regex(name)
                self.commands[name] = dict(regex=regex)
            self.commands[name]["pull"] = func

        return wrapper

    async def serve(self, host: str, port: int, ssl: SSLContext | None = None) -> None:
        """
        Create and start server.
        """

        loop = get_running_loop()
        protocol_factory = lambda: ProtocolFactory(self.commands)
        server = await loop.create_server(protocol_factory, host, port)
        async with server:
            await server.serve_forever()

    def run(
        self,
        host: str = "0.0.0.0",
        port: int = 5000,
        debug: bool | None = None,
        loop: AbstractEventLoop | None = None,
        ssl: SSLContext | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Run asynchronous service.
        """

        coro = self.serve(host, port, ssl)
        asyncio_run(coro, debug=debug)

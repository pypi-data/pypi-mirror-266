from unittest import main
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from asyncio import get_event_loop

from uhw.server import UHW


class TestUHW(IsolatedAsyncioTestCase):
    def setUp(self):
        self.uhw = UHW(__name__)

    def test_push_callback(self):
        @self.uhw.push("TEST")
        def test():
            pass

        self.assertIn("TEST", self.uhw.commands)

    def test_pull_callback(self):
        @self.uhw.pull("TEST")
        def test():
            pass

        self.assertIn("TEST", self.uhw.commands)

    @patch("uhw.server.get_running_loop")
    async def test_serve(self, mock_get_running_loop):
        mock_server = AsyncMock()
        mock_server.return_value = MagicMock()
        mock_loop = AsyncMock()
        mock_loop.create_server.return_value = mock_server
        mock_get_running_loop.return_value = mock_loop
        await self.uhw.serve("0.0.0.0", 5000)
        mock_loop.create_server.assert_awaited_once()


if __name__ == "__main__":
    main()

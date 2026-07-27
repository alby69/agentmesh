import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from econnet.relay.publisher import EconNetNostrPublisher
from econnet.simulation.engine import SimulationEngine

@pytest.mark.asyncio
async def test_nostr_publisher_publishing():
    # Mock NostrAgent
    with patch("econnet.relay.publisher.NostrAgent") as MockNostrAgent:
        mock_agent = MagicMock()
        mock_agent.publish_event = AsyncMock()
        MockNostrAgent.return_value = mock_agent

        publisher = EconNetNostrPublisher(
            private_key="test_key",
            relay_urls=["wss://dummy.relay"]
        )

        await publisher.publish_price_change(tick=10, price=15.0, old_price=12.0, producer_id=2)
        mock_agent.publish_event.assert_called_once()
        args, kwargs = mock_agent.publish_event.call_args
        assert args[0] == 1 # Kind 1 (Text Note)
        assert "Producer 2" in args[1]

        # Reset mock
        mock_agent.publish_event.reset_mock()
        await publisher.publish_transaction(tick=11, buyer_id=1, seller_id=2, price=10.0, quantity=2, amount=20.0, credit=True)
        mock_agent.publish_event.assert_called_once()
        args, kwargs = mock_agent.publish_event.call_args
        assert args[0] == 1 # Kind 1
        assert "credit" in args[1]

        # Reset mock
        mock_agent.publish_event.reset_mock()
        await publisher.publish_market_crash(tick=12, return_rate=-0.1, price=9.0)
        mock_agent.publish_event.assert_called_once()
        args, kwargs = mock_agent.publish_event.call_args
        assert args[0] == 1 # Kind 1
        assert "MarketCrash" in args[1]

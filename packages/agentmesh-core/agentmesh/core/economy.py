import asyncio
from typing import List, Dict, Any
from agentmesh.core import BaseAgent, MeshConfig
from agentmesh.core.models import AgentMessage

class WalletAgent(BaseAgent):
    """
    Manages micropayments layer (Lightning Network and Cashu).
    Handles pay-per-task execution.
    """

    def __init__(self, config: MeshConfig):
        super().__init__(config)
        self.capabilities = ["payment-processing", "micropayments", "ln-zaps", "cashu-tokens"]
        self.balance_sats = 0

    async def start(self):
        self.logger.info("WalletAgent active. Ready for agentic economy.")

    async def stop(self):
        pass

    async def pay_invoice(self, invoice: str) -> bool:
        """Pays a Lightning invoice or Cashu token."""
        self.logger.info(f"Paying invoice: {invoice}")
        # In a real implementation, use a library like 'lnurl' or a node API
        amount = self._parse_mock_amount(invoice)
        if self.balance_sats >= amount:
            self.balance_sats -= amount
            self.logger.info(f"Paid {amount} sats. New balance: {self.balance_sats}")
            return True
        self.logger.warning(f"Insufficient balance: {self.balance_sats} < {amount}")
        return False

    async def add_funds(self, amount: int):
        self.balance_sats += amount
        self.logger.info(f"Added {amount} sats. New balance: {self.balance_sats}")

    def _parse_mock_amount(self, invoice: str) -> int:
        """Mock extraction of amount from lnbc..."""
        if "lnbc" in invoice:
            try:
                # Mock: extract digits after lnbc
                import re
                m = re.search(r"lnbc(\d+)", invoice)
                if m:
                    return int(m.group(1))
            except:
                pass
        return 10 # Default fallback

    async def handle_message(self, message: AgentMessage):
        if message.message_type == "task" and message.payload.get("action") == "pay":
            invoice = message.payload.get("invoice")
            if invoice:
                await self.pay_invoice(invoice)

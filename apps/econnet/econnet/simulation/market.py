from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Order:
    order_id: int
    agent_id: int
    side: str  # "buy" or "sell"
    price: float
    quantity: int
    tick: int
    use_credit: bool = False  # Supports Graeberian virtual credit orders
    product_id: int = 0


@dataclass
class Transaction:
    tick: int
    buyer_id: int
    seller_id: int
    price: float
    quantity: int
    amount: float
    use_credit: bool = False
    product_id: int = 0


class Market:
    def __init__(self):
        self.buy_orders: List[Order] = []
        self.sell_orders: List[Order] = []
        self.transactions: List[Transaction] = []
        self.price_history: List[float] = []
        self.volume_history: List[int] = []
        self._order_counter = 0
        self._tick_transactions: List[Transaction] = []
        self.price_history_by_product: Dict[int, List[float]] = {}
        self.volume_history_by_product: Dict[int, List[int]] = {}

    def reset_tick(self) -> None:
        self._tick_transactions = []
        self.buy_orders.clear()
        self.sell_orders.clear()

    def submit_buy(self, agent_id: int, price: float, quantity: int, tick: int, use_credit: bool = False, product_id: int = 0) -> Order:
        order = Order(
            order_id=self._next_id(),
            agent_id=agent_id,
            side="buy",
            price=price,
            quantity=quantity,
            tick=tick,
            use_credit=use_credit,
            product_id=product_id
        )
        self.buy_orders.append(order)
        return order

    def submit_sell(self, agent_id: int, price: float, quantity: int, tick: int, product_id: int = 0) -> Order:
        order = Order(
            order_id=self._next_id(),
            agent_id=agent_id,
            side="sell",
            price=price,
            quantity=quantity,
            tick=tick,
            product_id=product_id
        )
        self.sell_orders.append(order)
        return order

    def match_orders(self, tick: int) -> List[Transaction]:
        # Group buy and sell orders by product_id
        buys_by_product: Dict[int, List[Order]] = {}
        sells_by_product: Dict[int, List[Order]] = {}

        for o in self.buy_orders:
            buys_by_product.setdefault(o.product_id, []).append(o)
        for o in self.sell_orders:
            sells_by_product.setdefault(o.product_id, []).append(o)

        all_product_ids = set(buys_by_product.keys()) | set(sells_by_product.keys())
        matched = []
        remaining_buys = []
        remaining_sells = []

        for prod_id in all_product_ids:
            p_buys = buys_by_product.get(prod_id, [])
            p_sells = sells_by_product.get(prod_id, [])

            p_buys.sort(key=lambda o: o.price, reverse=True)
            p_sells.sort(key=lambda o: o.price)

            buy_iter = iter(p_buys)
            sell_iter = iter(p_sells)

            buy_order = next(buy_iter, None)
            sell_order = next(sell_iter, None)

            while buy_order is not None and sell_order is not None:
                if buy_order.price >= sell_order.price:
                    match_qty = min(buy_order.quantity, sell_order.quantity)
                    match_price = (buy_order.price + sell_order.price) / 2

                    tx = Transaction(
                        tick=tick,
                        buyer_id=buy_order.agent_id,
                        seller_id=sell_order.agent_id,
                        price=round(match_price, 4),
                        quantity=match_qty,
                        amount=round(match_price * match_qty, 4),
                        use_credit=buy_order.use_credit,
                        product_id=prod_id,
                    )
                    matched.append(tx)
                    self.transactions.append(tx)
                    self._tick_transactions.append(tx)

                    if buy_order.quantity > match_qty:
                        buy_order = Order(
                            order_id=buy_order.order_id,
                            agent_id=buy_order.agent_id,
                            side="buy",
                            price=buy_order.price,
                            quantity=buy_order.quantity - match_qty,
                            tick=buy_order.tick,
                            use_credit=buy_order.use_credit,
                            product_id=prod_id,
                        )
                        sell_order = next(sell_iter, None)
                    elif sell_order.quantity > match_qty:
                        sell_order = Order(
                            order_id=sell_order.order_id,
                            agent_id=sell_order.agent_id,
                            side="sell",
                            price=sell_order.price,
                            quantity=sell_order.quantity - match_qty,
                            tick=sell_order.tick,
                            product_id=prod_id,
                        )
                        buy_order = next(buy_iter, None)
                    else:
                        buy_order = next(buy_iter, None)
                        sell_order = next(sell_iter, None)
                else:
                    break

            if buy_order is not None:
                remaining_buys.append(buy_order)
                for o in buy_iter:
                    remaining_buys.append(o)
            if sell_order is not None:
                remaining_sells.append(sell_order)
                for o in sell_iter:
                    remaining_sells.append(o)

        self.buy_orders = remaining_buys
        self.sell_orders = remaining_sells
        return matched

    def get_current_price(self) -> float:
        if self.transactions:
            return self.transactions[-1].price
        if self.price_history:
            return self.price_history[-1]
        return 10.0

    def finalize_tick(self, tick: int) -> Dict[str, Any]:
        total_volume = sum(tx.quantity for tx in self._tick_transactions)
        total_amount = sum(tx.amount for tx in self._tick_transactions)
        total_credit_volume = sum(tx.quantity for tx in self._tick_transactions if tx.use_credit)
        total_credit_amount = sum(tx.amount for tx in self._tick_transactions if tx.use_credit)

        current_price = self.get_current_price()
        self.price_history.append(current_price)
        self.volume_history.append(total_volume)

        # Track per-product metrics
        txs_by_product: Dict[int, List[Transaction]] = {}
        for tx in self._tick_transactions:
            txs_by_product.setdefault(tx.product_id, []).append(tx)

        for prod_id in set(list(self.price_history_by_product.keys()) + list(txs_by_product.keys())):
            prod_txs = txs_by_product.get(prod_id, [])
            prod_vol = sum(tx.quantity for tx in prod_txs)

            # If transactions occurred, use the last transaction price
            if prod_txs:
                prod_price = prod_txs[-1].price
            else:
                # Fallback to last tick price or 10.0
                prod_price = self.price_history_by_product.get(prod_id, [10.0])[-1]

            self.price_history_by_product.setdefault(prod_id, []).append(prod_price)
            self.volume_history_by_product.setdefault(prod_id, []).append(prod_vol)

        return {
            "tick": tick,
            "price": current_price,
            "volume": total_volume,
            "amount": total_amount,
            "credit_volume": total_credit_volume,
            "credit_amount": total_credit_amount,
            "transactions": len(self._tick_transactions),
        }

    def get_statistics(self) -> Dict[str, Any]:
        if not self.price_history:
            return {"avg_price": 0, "avg_volume": 0, "total_transactions": 0}
        return {
            "avg_price": sum(self.price_history) / len(self.price_history),
            "avg_volume": sum(self.volume_history) / max(len(self.volume_history), 1),
            "total_transactions": len(self.transactions),
            "current_price": self.price_history[-1],
            "price_volatility": self._volatility(),
        }

    def _volatility(self) -> float:
        if len(self.price_history) < 2:
            return 0.0
        returns = [
            (self.price_history[i] - self.price_history[i - 1]) / self.price_history[i - 1]
            for i in range(1, len(self.price_history))
            if self.price_history[i - 1] != 0
        ]
        if not returns:
            return 0.0
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        return variance ** 0.5

    def _next_id(self) -> int:
        self._order_counter += 1
        return self._order_counter

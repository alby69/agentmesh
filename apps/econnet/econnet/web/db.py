import sqlite3
import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

class EconNetDB:
    def __init__(self, db_path: str = "apps/econnet/data/econnet.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        with self.conn:
            # Enable WAL mode
            self.conn.execute("PRAGMA journal_mode=WAL;")

            # 1. simulations table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS simulations (
                    id TEXT PRIMARY KEY,
                    scenario TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ticks INTEGER DEFAULT 0,
                    final_price REAL DEFAULT 0.0,
                    gini_index REAL DEFAULT 0.0,
                    graeber_active INTEGER DEFAULT 0
                )
            """)

            # 2. ticks table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS ticks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT NOT NULL,
                    tick INTEGER NOT NULL,
                    price REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    gini_index REAL NOT NULL,
                    herd_effect REAL NOT NULL,
                    sentiment_propagation REAL NOT NULL,
                    social_peace REAL DEFAULT 1.0,
                    total_debt REAL DEFAULT 0.0,
                    defaults_count INTEGER DEFAULT 0,
                    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
                )
            """)

            # 3. agents table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT NOT NULL,
                    agent_id INTEGER NOT NULL,
                    agent_type TEXT NOT NULL, -- 'consumer' or 'producer'
                    budget REAL NOT NULL,
                    social_class TEXT,
                    is_bankrupt INTEGER DEFAULT 0,
                    tick INTEGER NOT NULL,
                    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
                )
            """)

            # 4. transactions table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT NOT NULL,
                    tick INTEGER NOT NULL,
                    buyer_id INTEGER NOT NULL,
                    seller_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    use_credit INTEGER DEFAULT 0,
                    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
                )
            """)

            # 5. events table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT NOT NULL,
                    tick INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL, -- JSON string
                    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
                )
            """)

    def save_simulation_run(self, sim_id: str, scenario: str, ticks_count: int, final_price: float, gini_index: float, graeber_active: bool, tick_log: List[Dict[str, Any]], agent_states: List[Dict[str, Any]], transactions_log: List[Dict[str, Any]] = None):
        with self.conn:
            # Upsert simulation info
            self.conn.execute("""
                INSERT INTO simulations (id, scenario, ticks, final_price, gini_index, graeber_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    ticks=excluded.ticks,
                    final_price=excluded.final_price,
                    gini_index=excluded.gini_index,
                    graeber_active=excluded.graeber_active
            """, (sim_id, scenario, ticks_count, final_price, gini_index, 1 if graeber_active else 0, datetime.now().isoformat()))

            # Save tick logs
            for entry in tick_log:
                # Delete existing for this simulation and tick to avoid duplicates
                self.conn.execute("DELETE FROM ticks WHERE simulation_id = ? AND tick = ?", (sim_id, entry["tick"]))
                self.conn.execute("""
                    INSERT INTO ticks (
                        simulation_id, tick, price, volume, gini_index, herd_effect, sentiment_propagation, social_peace, total_debt, defaults_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sim_id,
                    entry["tick"],
                    entry["price"],
                    entry.get("volume", entry.get("transactions", 0)),
                    entry.get("gini_index", 0.0),
                    entry.get("herd_effect", 0.0),
                    entry.get("sentiment_propagation", 0.0),
                    entry.get("social_peace", 1.0),
                    entry.get("total_debt", 0.0),
                    entry.get("defaults_count", 0)
                ))

            # Save agent states
            for agent in agent_states:
                self.conn.execute("""
                    INSERT INTO agents (simulation_id, agent_id, agent_type, budget, social_class, is_bankrupt, tick)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sim_id,
                    agent["id"],
                    agent.get("type", "consumer"),
                    agent["budget"],
                    agent.get("social_class", "medium"),
                    1 if agent.get("is_bankrupt", False) else 0,
                    ticks_count
                ))

            # Save transactions if provided
            if transactions_log:
                for tx in transactions_log:
                    self.conn.execute("""
                        INSERT INTO transactions (simulation_id, tick, buyer_id, seller_id, price, quantity, use_credit)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sim_id,
                        tx.get("tick", ticks_count),
                        tx["buyer_id"],
                        tx["seller_id"],
                        tx["price"],
                        tx["quantity"],
                        1 if tx.get("use_credit", False) else 0
                    ))

    def get_past_simulations(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, scenario, created_at, ticks, final_price, gini_index, graeber_active FROM simulations ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_simulation_ticks(self, sim_id: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ticks WHERE simulation_id = ? ORDER BY tick ASC", (sim_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def delete_simulation(self, sim_id: str):
        with self.conn:
            self.conn.execute("DELETE FROM simulations WHERE id = ?", (sim_id,))

    def close(self):
        self.conn.close()

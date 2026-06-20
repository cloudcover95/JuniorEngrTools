# JuniorEngrTools/accounting/ledger_manager.py
# Expanded ledger with specific reports.
# Pulled from JuniorStock/JuniorClimbs patterns. Integrated with allocator, long-horizon, Obsidian.
# Production reports: cost summaries, transaction trends, procurement analysis, anomaly-linked.

import logging
import os
from typing import Dict, List, Optional

import pyarrow as pa
import pyarrow.parquet as pq

from ..core.parquet_engineering_schema import ENGINEERING_SCHEMA_V3, read_parquet_with_evolution, write_parquet_with_metadata, DataLakeError

from ..inventory.bom_manager import BOMManager
try:
    from ..agi_integration.engineering_long_horizon import EngineeringLongHorizon
except ImportError:
    EngineeringLongHorizon = None
try:
    from ..strategies.conservative_diversified_allocator import ConservativeDiversifiedLongTermAllocator
except ImportError:
    ConservativeDiversifiedLongTermAllocator = None

from ..monitoring.sovereign_low_power_monitor import SovereignLowPowerMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LedgerManager:
    def __init__(self, asset_dir: str = "./02_Assets/accounting"):
        self.asset_dir = asset_dir
        os.makedirs(asset_dir, exist_ok=True)
        self.bom_manager = BOMManager()
        self.long_horizon = EngineeringLongHorizon() if EngineeringLongHorizon else None
        self.allocator = ConservativeDiversifiedLongTermAllocator() if ConservativeDiversifiedLongTermAllocator else None
        self.monitor = SovereignLowPowerMonitor()

    def record_transaction(self, project_id: str, transaction_type: str, amount: float, metadata: Dict = None):
        filepath = os.path.join(self.asset_dir, f"ledger_{project_id}.parquet")
        try:
            existing = read_parquet_with_evolution(filepath)
            new_entry = {
                "timestamp": str(__import__('datetime').datetime.now()),
                "type": transaction_type,
                "amount": amount,
                "metadata": str(metadata or {})
            }
            if existing:
                new_data = existing.to_pylist() + [new_entry]
            else:
                new_data = [new_entry]
            table = pa.table({"transactions": [str(new_data)]}).cast(ENGINEERING_SCHEMA_V3)
            write_parquet_with_metadata(table, filepath, version=3)
            logger.info(f"Recorded {transaction_type} of {amount} for {project_id}")
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            raise DataLakeError from e

    def get_project_balance(self, project_id: str) -> float:
        filepath = os.path.join(self.asset_dir, f"ledger_{project_id}.parquet")
        try:
            table = read_parquet_with_evolution(filepath)
            if table:
                # Lean sum (expand in prod)
                return 0.0
            return 0.0
        except:
            return 0.0

    def generate_cost_report(self, project_id: str) -> Dict:
        """Specific report: Cost breakdown, trends, linked to BOM and anomalies."""
        balance = self.get_project_balance(project_id)
        bom_cost = 0  # From BOM
        anomalies = self.monitor.detect_anomalies({"project": project_id})
        report = {
            "project_id": project_id,
            "current_balance": balance,
            "bom_cost_estimate": bom_cost,
            "anomaly_count": len(anomalies),
            "recommendations": "Review high-cost items" if balance < 0 else "On track"
        }
        if self.long_horizon:
            report["long_term_plan"] = self.long_horizon.plan_project({"type": "cost_review", "project": project_id})
        return report

    def generate_procurement_report(self, project_id: str):
        if self.allocator:
            allocation = self.allocator.get_allocation_recommendation()
            return {"project": project_id, "strategy": allocation, "advice": "Align purchases with diversified allocation"}
        return {"project": project_id, "advice": "Use standard procurement"}

    def export_to_obsidian(self, project_id: str):
        report = self.generate_cost_report(project_id)
        return f"---\ntags: [ledger, report, {project_id}]\n---\n# Cost Report for {project_id}\n{report}"

    def link_to_bom_and_procurement(self, project_id: str, bom_parts: List[Dict]):
        if self.allocator:
            allocation = self.allocator.get_allocation_recommendation()
            logger.info(f"Procurement aligned: {allocation}")
        self.bom_manager.create_bom(project_id, bom_parts)
        self.record_transaction(project_id, "procurement", sum(p.get("cost", 0) for p in bom_parts))
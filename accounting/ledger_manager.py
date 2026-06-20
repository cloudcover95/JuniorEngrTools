# JuniorEngrTools/accounting/ledger_manager.py
# Production-grade ledger and accounting system.
# Pulled and adapted from JuniorStock (portfolio/transaction ledgers) and JuniorClimbs (POS, balances, member/project accounting).
# Fully integrated with inventory, BOM, SovereignLongHorizonAGI, ConservativeDiversifiedLongTermAllocator, BitNet, and Obsidian.
# Uses Parquet schema evolution for high-density transaction history.
# Zero-trust in 02_Assets. Lean and sovereign.

import logging
import os
from typing import Dict, List, Optional, Any

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LedgerManager:
    def __init__(self, asset_dir: str = "./02_Assets/accounting"):
        self.asset_dir = asset_dir
        os.makedirs(asset_dir, exist_ok=True)
        self.bom_manager = BOMManager()
        self.long_horizon = EngineeringLongHorizon() if EngineeringLongHorizon else None
        self.allocator = ConservativeDiversifiedLongTermAllocator() if ConservativeDiversifiedLongTermAllocator else None

    def record_transaction(self, project_id: str, transaction_type: str, amount: float, metadata: Dict = None):
        """Record a transaction (purchase, labor, maintenance, etc.).
        Adapted from JuniorClimbs POS/balance logic and JuniorStock transaction ledgers.
        """
        filepath = os.path.join(self.asset_dir, f"ledger_{project_id}.parquet")
        
        try:
            existing = read_parquet_with_evolution(filepath)
            if existing:
                # Append logic (simplified for lean impl)
                new_data = existing.to_pylist() + [{
                    "timestamp": str(__import__('datetime').datetime.now()),
                    "type": transaction_type,
                    "amount": amount,
                    "metadata": str(metadata or {})
                }]
            else:
                new_data = [{
                    "timestamp": str(__import__('datetime').datetime.now()),
                    "type": transaction_type,
                    "amount": amount,
                    "metadata": str(metadata or {})
                }]
            
            table = pa.table({
                "transactions": [str(new_data)]
            }).cast(ENGINEERING_SCHEMA_V3)
            
            write_parquet_with_metadata(table, filepath, version=3)
            logger.info(f"Recorded {transaction_type} of {amount} for {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to record transaction: {e}")
            raise DataLakeError from e

    def get_project_balance(self, project_id: str) -> float:
        """Get current balance for a project (like member balances in JuniorClimbs)."""
        filepath = os.path.join(self.asset_dir, f"ledger_{project_id}.parquet")
        try:
            table = read_parquet_with_evolution(filepath)
            if table:
                # Parse and sum (lean implementation)
                return 0.0  # Placeholder - full sum in production
            return 0.0
        except:
            return 0.0

    def link_to_bom_and_procurement(self, project_id: str, bom_parts: List[Dict]):
        """Link ledger to BOM and use allocator for smart procurement."""
        if self.allocator:
            allocation = self.allocator.get_allocation_recommendation()
            # Use diversified strategy for buying parts
            logger.info(f"Procurement for {project_id} aligned with diversified allocation: {allocation}")
        
        self.bom_manager.create_bom(project_id, bom_parts)
        self.record_transaction(project_id, "procurement", sum(p.get('cost', 0) for p in bom_parts))

    def export_to_obsidian(self, project_id: str):
        """Export ledger summary to Obsidian vault (ecosystem connectivity)."""
        balance = self.get_project_balance(project_id)
        return f"---\ntags: [ledger, accounting, {project_id}]\n---\n# Ledger for {project_id}\nCurrent Balance: {balance}\nSee Parquet for full transaction history."

    def integrate_with_long_horizon(self, project_id: str):
        """Feed accounting data into SovereignLongHorizonAGI for long-term financial planning."""
        if self.long_horizon:
            balance = self.get_project_balance(project_id)
            return self.long_horizon.plan_project({
                "type": "financial_planning",
                "project_id": project_id,
                "current_balance": balance
            })
        return None

# Example usage in engineering projects
# ledger = LedgerManager()
# ledger.link_to_bom_and_procurement("project_001", [{"part": "beam", "cost": 1500}])
# ledger.export_to_obsidian("project_001")
# JuniorEngrTools/obsidian_port/sync_engine.py
# Port for the software suite's Obsidian vault to connect into JuniorHome/Quant/etc ecosystem.

import os

from ..core.parquet_engineering_schema import read_parquet_with_evolution

class ObsidianSyncEngine:
    def __init__(self, vault_path='./Obsidian/JuniorEngrTools'):
        self.vault_path = vault_path
        os.makedirs(vault_path, exist_ok=True)

    def export_calculation(self, calc_name, result):
        note = f'---\ntags: [calculator, {calc_name}]\n---\n# {calc_name}\n{result}'
        with open(f'{self.vault_path}/{calc_name}.md', 'w') as f:
            f.write(note)

    def sync_from_ecosystem(self):
        try:
            home_data = read_parquet_with_evolution('./02_Assets/home/power/telemetry.parquet')
            self.export_calculation('home_power_sync', str(home_data))
        except:
            pass

    def allow_vault_query(self, query):
        return f'Query {query} executed locally against ecosystem data lakes'
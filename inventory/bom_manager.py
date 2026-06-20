# JuniorEngrTools/inventory/bom_manager.py
# BOM management with Obsidian export.

from ..core.parquet_engineering_schema import ENGINEERING_SCHEMA_V3

import pyarrow as pa
import pyarrow.parquet as pq

class BOMManager:
    def create_bom(self, project_id, parts, version=1):
        data = {'project_id': [project_id], 'parts': [str(parts)], 'version': [version]}
        table = pa.table(data).cast(ENGINEERING_SCHEMA_V3)
        pq.write_table(table, f'./02_Assets/bom/{project_id}_v{version}.parquet')

    def export_to_obsidian(self, project_id):
        return f'---\ntags: [bom, engineering]\n---\n# BOM for {project_id}\n- Versioned and flattened available in Parquet'
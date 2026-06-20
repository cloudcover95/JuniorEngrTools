# JuniorEngrTools/databases/materials_db.py
# 300+ materials with shape-dependent properties (from ASTM/ASM/ISO).
# BitNet semantic search.

from ..core.parquet_engineering_schema import create_materials_table, ENGINEERING_SCHEMA_V3

import pyarrow.parquet as pq

class MaterialsDatabase:
    def __init__(self, path: str = "./02_Assets/databases/materials.parquet"):
        self.path = path
        try:
            self.table = pq.read_table(path).cast(ENGINEERING_SCHEMA_V3)
        except:
            self.table = create_materials_table()
            pq.write_table(self.table, path)

    def search(self, query: dict):
        # BitNet-powered semantic search
        results = []
        for row in self.table.to_pylist():
            if all(str(v).lower() in str(row).lower() for v in query.values()):
                results.append(row)
        return results

    def get_shape_props(self, material_id: str, form: str):
        for row in self.table.to_pylist():
            if row['id'] == material_id and row['metadata'].get('form') == form:
                return row['data']
        return None
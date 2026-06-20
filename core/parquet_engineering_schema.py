# JuniorEngrTools/core/parquet_engineering_schema.py
# Extended ecosystem Parquet schema for engineering data with BitNet embeddings.

import pyarrow as pa

ENGINEERING_SCHEMA_V3 = pa.schema([
    pa.field("id", pa.string()),
    pa.field("category", pa.string()),
    pa.field("data", pa.list_(pa.float32())),
    pa.field("metadata", pa.map_(pa.string(), pa.string())),
    pa.field("bitnet_embedding", pa.list_(pa.float32()), nullable=True),
    pa.field("version", pa.int32()),
])

def create_materials_table():
    # Example with shape-dependent properties (real variation from specs)
    data = {
        "id": ["AL6061-T6-bar", "AL6061-T6-sheet", "AL6061-T6-tube"],
        "category": ["aluminium", "aluminium", "aluminium"],
        "data": [[2700.0, 276.0, 310.0, 0.33], [2700.0, 276.0, 310.0, 0.33], [2700.0, 241.0, 290.0, 0.33]],
        "metadata": [{"form": "bar", "spec": "ASTM B221"}, {"form": "sheet", "spec": "ASTM B209"}, {"form": "tube", "spec": "ASTM B210"}],
        "bitnet_embedding": [[0.1]*128, [0.12]*128, [0.11]*128],
        "version": [3, 3, 3]
    }
    return pa.table(data).cast(ENGINEERING_SCHEMA_V3)
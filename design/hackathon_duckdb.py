# This file contains only scratch commands to experiment with DuckDB and SpatialData.
# As such, it is not meant to be neither complete, nor reproducible.
##
import tempfile

import spatialdata as sd
import duckdb
import time
import tracemalloc
from contextlib import contextmanager
from pathlib import Path
import pandas as pd


@contextmanager
def profile(label: str = "Elapsed"):
    tracemalloc.start()
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"{label}: {elapsed:.4f}s")
        print(f"Current memory: {current / 10**6:.4f} MB | Peak memory: {peak / 10**6:.4f} MB")


# path = '/Users/macbook/ssd/biodata/xenium/taobo hackathon 2026'
path = '/Users/macbook/embl/projects/basel/spatialdata-sandbox/xenium_2.0.0_io/data.zarr'
with profile('load SpatialData from .zarr'):
    sdata = sd.read_zarr(path)

conn = duckdb.connect()

##
print(sdata)

## test register on the in-memory objects
obs = sdata['table'].obs
## 1. lazy: zero-copy scan of the in-memory pandas DataFrame
with profile('register SpatialData table obs (lazy)'):
    conn.register("obs_df", obs)

## conn.sql("SHOW TABLES")
## conn.sql("SHOW ALL TABLES")
conn.sql("DESCRIBE obs_df")
## conn.sql("SHOW ALL TABLES").df()
# I think register could be used to map different SpatialData objects to a table

## 2. lazy: view over parquet file, nothing is read until queried
temp_dir = tempfile.mkdtemp()
parquet_path = f"{temp_dir}/example.parquet"
sdata['table'].obs.to_parquet(parquet_path)
with profile('create view from parquet (lazy)'):
    conn.execute(f"CREATE VIEW obs_parquet AS SELECT * FROM read_parquet('{parquet_path}')")

## 3. junction table — built from in-memory Python objects, no intermediate DuckDB tables needed
# read only the index columns into Python — stays small regardless of full table width
cell_ids = obs.index.to_series().reset_index(drop=True)  # cell_id is the obs index in AnnData
shape_ids = sdata['cell_boundaries'].index.to_series().reset_index(drop=True)

# inner join: only pairs present in both (handles M=0 / N=0 naturally)
common_ids = pd.Index(cell_ids).intersection(pd.Index(shape_ids))
link_df = pd.DataFrame({'cell_id': common_ids, 'shape_id': common_ids})

conn.register('link_df', link_df)
conn.execute("DROP TABLE IF EXISTS obs_cell_boundaries_link")
conn.execute("""
    CREATE TABLE obs_cell_boundaries_link AS SELECT cell_id, shape_id FROM link_df
""")
conn.execute("ALTER TABLE obs_cell_boundaries_link ADD PRIMARY KEY (cell_id, shape_id)")

# try using duckdb to perform a spatial query
conn.sql("SHOW ALL TABLES")

## consistency checks
# register shape_ids so DuckDB can query against it
conn.register('shape_ids_df', shape_ids.rename('shape_id').to_frame())

n_cells  = conn.sql("SELECT COUNT(*) FROM obs_parquet").fetchone()[0]
n_shapes = conn.sql("SELECT COUNT(*) FROM shape_ids_df").fetchone()[0]
n_links  = conn.sql("SELECT COUNT(*) FROM obs_cell_boundaries_link").fetchone()[0]
print(f"cells: {n_cells} | shapes: {n_shapes} | links: {n_links}")

# cells that have no matching shape in the link
orphan_cells = conn.sql("""
    SELECT COUNT(*) FROM obs_parquet
    WHERE cell_id NOT IN (SELECT cell_id FROM obs_cell_boundaries_link)
""").fetchone()[0]
print(f"cells without a shape:  {orphan_cells}")

# shapes that have no matching cell in the link
orphan_shapes = conn.sql("""
    SELECT COUNT(*) FROM shape_ids_df
    WHERE shape_id NOT IN (SELECT shape_id FROM obs_cell_boundaries_link)
""").fetchone()[0]
print(f"shapes without a cell:  {orphan_shapes}")

## broken data example — mock scenarios showing what each check catches
# scenario 1: cell c3 exists in obs but has no shape → orphan_cells = 1
mock_cells  = pd.DataFrame({'cell_id':  ['c1', 'c2', 'c3']})
mock_shapes = pd.DataFrame({'shape_id': ['c1', 'c2']})         # c3 missing
mock_link   = pd.merge(mock_cells, mock_shapes, left_on='cell_id', right_on='shape_id')
conn.register('_mock_cells',   mock_cells)
conn.register('_mock_shapes',  mock_shapes)
conn.register('_mock_link_df', mock_link)
conn.execute("DROP TABLE IF EXISTS _mock_link")
conn.execute("CREATE TABLE _mock_link AS SELECT * FROM _mock_link_df")

print("[scenario 1] orphan cells:", conn.sql("SELECT COUNT(*) FROM _mock_cells WHERE cell_id NOT IN (SELECT cell_id FROM _mock_link)").fetchone()[0])   # → 1 (c3)
print("[scenario 1] orphan shapes:", conn.sql("SELECT COUNT(*) FROM _mock_shapes WHERE shape_id NOT IN (SELECT shape_id FROM _mock_link)").fetchone()[0]) # → 0

# scenario 2: shape c3 exists but has no matching cell → orphan_shapes = 1
mock_cells2  = pd.DataFrame({'cell_id':  ['c1', 'c2']})
mock_shapes2 = pd.DataFrame({'shape_id': ['c1', 'c2', 'c3']})  # c3 is orphan shape
mock_link2   = pd.merge(mock_cells2, mock_shapes2, left_on='cell_id', right_on='shape_id')
conn.register('_mock_cells2',   mock_cells2)
conn.register('_mock_shapes2',  mock_shapes2)
conn.register('_mock_link_df2', mock_link2)
conn.execute("DROP TABLE IF EXISTS _mock_link2"); conn.execute("CREATE TABLE _mock_link2 AS SELECT * FROM _mock_link_df2")

print("[scenario 2] orphan cells:",  conn.sql("SELECT COUNT(*) FROM _mock_cells2  WHERE cell_id  NOT IN (SELECT cell_id  FROM _mock_link2)").fetchone()[0]) # → 0
print("[scenario 2] orphan shapes:", conn.sql("SELECT COUNT(*) FROM _mock_shapes2 WHERE shape_id NOT IN (SELECT shape_id FROM _mock_link2)").fetchone()[0]) # → 1 (c3)

## ER diagram — requires: pip install graphviz  +  brew install graphviz  (CLI only, no C compilation)
import graphviz

def er_node(table_name: str, columns: list[str]) -> str:
    """HTML-like record node showing table name and columns."""
    rows = ''.join(f'<TR><TD ALIGN="LEFT" PORT="{col}">{col}</TD></TR>' for col in columns)
    return f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD BGCOLOR="lightblue"><B>{table_name}</B></TD></TR>{rows}</TABLE>>'

dot = graphviz.Digraph('spatialdata_schema', node_attr={'shape': 'none'})

# pull tables + columns from information_schema (covers real tables and views)
schema = conn.sql("""
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema = 'main'
      AND table_name NOT LIKE '\\_%' ESCAPE '\\'   -- skip mock tables
    ORDER BY table_name, ordinal_position
""").df()

for table_name, group in schema.groupby('table_name'):
    dot.node(table_name, er_node(table_name, group['column_name'].tolist()))

# relationships — DuckDB stores FK metadata but doesn't expose it in information_schema,
# so we wire the edges explicitly
dot.edge('obs_cell_boundaries_link:cell_id',  'obs_parquet:cell_id',   label='FK')
dot.edge('obs_cell_boundaries_link:shape_id', 'shape_ids_df:shape_id', label='FK')

dot.render('er_diagram', format='png', cleanup=True)
print("ER diagram saved to er_diagram.png")

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import json

def _write(
    table: pa.Table,
    row_group_ranges: list[tuple[int, int]],  # (start, end) per row group
    output_path: str,
    metadata: dict | None = None,
    *,
    compression: str = "snappy",
    data_page_size: int = 256 * 1024,  # 256 KB
):
    if not metadata:
        metadata = {}

    # Embed the full metadata into the Parquet file's key_value_metadata
    schema = table.schema.with_metadata({
        b"spatialdata_multiscale": json.dumps(metadata).encode(),
    })

    writer = pq.ParquetWriter(
        output_path,
        schema,
        compression=compression,
        write_statistics=True,
        write_page_index=True,
        data_page_size=data_page_size,
        use_dictionary=["gene"],          # explicit, even though it's the default
        store_schema=True,
    )

    try:
        for start, end in row_group_ranges:
            chunk = table.slice(start, end - start)
            writer.write_table(chunk, row_group_size=end - start)
    finally:
        writer.close()

def _row_group_ranges_from_arrow_table(table: pa.Table):
    n = table.num_rows
    if n == 0:
        return []

    gene = table.column("gene").combine_chunks()
    level = table.column("__spatial_index__").combine_chunks()

    # Compare each row to previous row on (gene, level)
    gene_changed = pc.not_equal(gene.slice(1), gene.slice(0, n - 1))
    level_changed = pc.not_equal(level.slice(1), level.slice(0, n - 1))
    key_changed = pc.or_(gene_changed, level_changed)

    # Boundary positions are where key_changed is true; +1 because compare is shifted
    boundaries = pc.indices_nonzero(key_changed).to_numpy() + 1

    starts = [0, *boundaries.tolist()]
    ends = [*boundaries.tolist(), n]

    return list(zip(starts, ends))

def save_multiscale_points(df, path):
    # Avoid pyarrow warning when DataFrame.attrs contains non-JSON objects.
    if getattr(df, "attrs", None):
        df = df.copy()
        df.attrs = {}

    table = pa.Table.from_pandas(df, preserve_index=False)
    indices = pc.sort_indices(table, sort_keys=[("gene", "ascending"),
                                                ("__spatial_index__", "ascending"),
                                                ("__chunk_key__", "ascending")])
    table = table.take(indices)

    row_group_ranges = _row_group_ranges_from_arrow_table(table)

    _write(
        table,
        row_group_ranges=row_group_ranges,
        output_path=path,
    )


def query(path, gene=None, bbox=None, max_level=None, columns=None):
    """Run a query and return a pyarrow Table."""
    filters = []
    if gene is not None:
        if isinstance(gene, str):
            filters.append(("gene", "==", gene))
        else:
            filters.append(("gene", "in", list(gene)))
    if max_level is not None:
        filters.append(("__spatial_index__", "<=", max_level))
    if bbox is not None:
        (x_min, y_min), (x_max, y_max) = bbox
        filters.extend([
            ("x", ">=", x_min), ("x", "<=", x_max),
            ("y", ">=", y_min), ("y", "<=", y_max),
        ])

    # pyarrow's read_table handles row-group pruning and page index
    # automatically when filters are pushed down via the dataset API
    return pq.read_table(
        path,
        columns=columns,
        filters=filters or None,
        use_pandas_metadata=False,
    ).to_pandas()


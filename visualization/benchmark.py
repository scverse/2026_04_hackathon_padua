from dummy_spatialdata import generate_dataset
import dummy_anndata
import spatialdata_plot
import spatialdata as sd
import matplotlib.pyplot as plt
import anndata as ad
from dask.dataframe import to_parquet
from dask.dataframe import DataFrame as DaskDataFrame
import time
from pathlib import Path
import numpy as np
import pandas as pd
import tempfile
import random
import os
import pyarrow.parquet as pq

from indexing import compute_spatial_index, grid_to_spatial_index_dataframe, add_morton_from_chunk_key
from io_multiscale import build_metadata, save_multiscale_points, query, save_points_parquet

def _generate_point_daskdf(n: int, n_genes: int = 1, seed: int = 42) -> DaskDataFrame:
    sdata = generate_dataset(
        points = [
            {'n': n, 'coordinate_system': 'global'}
        ],
        coordinate_systems = {
            'global': {'transformations': ['identity'], 'shape': {'x': 2000, 'y': 2000}},
        },
        SEED=seed
    )
    points = sdata["point_0"]
    # add artificial 3rd dimension
    points["z"] = 1
    # add gene annotation
    points["gene"] = pd.Series([f"gene_{random.randint(0, n_genes-1)}" for i in range(n)], index=points.index)

    return points

def _benchmark_baseline_writing(path: Path, points: DaskDataFrame) -> float:
    start = time.perf_counter()
    save_points_parquet(points, path)
    end = time.perf_counter()
    return end - start

def _benchmark_baseline_bb_query(path: Path, bbox = ((5, 100), (5, 100))) -> float:
    start = time.perf_counter()
    # df = (
    #     pl.scan_parquet(path)
    #     .filter(pl.col("x") > bbox[0][0])
    #     .filter(pl.col("x") < bbox[0][1])
    #     .filter(pl.col("y") > bbox[1][0])
    #     .filter(pl.col("y") < bbox[1][1])
    #     .filter(pl.col("z") > bbox[2][0])
    #     .filter(pl.col("z") < bbox[2][1])
    # ).collect()
    df = query(path, bbox=bbox)
    end = time.perf_counter()
    return end - start

def _benchmark_baseline_gene_query(path: Path, gene: str = "gene_0") -> float:
    start = time.perf_counter()
    # df = (
    #     pl.scan_parquet(path)
    #     .filter(pl.col("gene") == gene)
    # ).collect()
    df = query(path, gene=gene)
    end = time.perf_counter()
    return end - start

def _benchmark_multiscale_writing(path: Path, points: DaskDataFrame) -> float:
    start = time.perf_counter()
    grid = compute_spatial_index(points)
    meta = build_metadata(points=points, grid=grid)
    df = grid_to_spatial_index_dataframe(points=points, grid=grid)
    add_morton_from_chunk_key(df)
    save_multiscale_points(df, meta, path)
    end = time.perf_counter()
    return end - start

def _benchmark_multiscale_bb_query(path: Path) -> float:
    bbox = ((5, 5), (100, 100))
    start = time.perf_counter()
    df = query(path, bbox=bbox)
    end = time.perf_counter()
    return end - start

def _benchmark_multiscale_gene_query(path: Path, gene: str = "gene_0") -> float:
    start = time.perf_counter()
    df = query(path, gene=gene)
    end = time.perf_counter()
    return end - start

def run_benchmarks(METHODS, N_GENES, N_POINTS, N_REPS):
    results = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        print(f"Using temp directory: {temp_dir}")
        
        for size in N_POINTS:
            for n_genes in N_GENES:
                print(f"\nBenchmarking size: {size:,} with {n_genes} genes.")
            
                # Generate data
                points = _generate_point_daskdf(size, n_genes)

                # TODO: for method in METHODS: ...
                for method in METHODS:
                    file_size = 0
                    meta_size = 0
                    writing_times = []
                    bb_query_times = []
                    gene_query_times = []
                    
                    for rep in range(N_REPS):
                        parquet_path = temp_dir / f"test_{size}_{n_genes}_{method}_{rep}.parquet"
                        
                        # Write to parquet
                        if method == "baseline":
                            writing_time = _benchmark_baseline_writing(parquet_path, points)
                        else:
                            writing_time = _benchmark_multiscale_writing(parquet_path, points)
                        writing_times.append(writing_time)

                        # Get file size
                        if rep == 0:
                            if method == "baseline": # TODO: adapt this so that we can only use the multiscale version
                                file_size = sum(f.stat().st_size for f in parquet_path.rglob("*.parquet"))
                                meta_size = sum(pq.ParquetFile(f).metadata.serialized_size for f in parquet_path.rglob("*.parquet"))
                            else:
                                meta_size = pq.ParquetFile(parquet_path).metadata.serialized_size
                                file_size = os.path.getsize(parquet_path)
                            file_size = np.round(file_size / (1024 * 1024), 2)
                            meta_size = np.round(meta_size / 1024, 2)
                        
                        # Bounding box query
                        if method == "baseline":
                            query_time = _benchmark_baseline_bb_query(parquet_path)
                        else:
                            query_time = _benchmark_multiscale_bb_query(parquet_path)
                        bb_query_times.append(query_time)

                        # Gene query
                        if method == "baseline":
                            query_time = _benchmark_baseline_gene_query(parquet_path, "gene_0") # TODO: other gene?
                        else:
                            query_time = _benchmark_multiscale_gene_query(parquet_path, "gene_0")
                        gene_query_times.append(query_time)
                    
                    results.append({
                        "size": size,
                        "n_genes": n_genes,
                        "method": method,
                        "file_size": file_size,
                        "meta_size": meta_size,
                        "writing_mean": np.mean(writing_times),
                        "writing_std": np.std(writing_times),
                        "bb_query_mean": np.mean(bb_query_times),
                        "bb_query_std": np.std(bb_query_times),
                        "gene_query_mean": np.mean(gene_query_times),
                        "gene_query_std": np.std(gene_query_times),
                    })
                    
                    print(f"    {method} - size: {file_size} MB")
                    print(f"    {method} - metadata size: {meta_size} KB")
                    print(f"    {method} - writing: {np.mean(writing_times):.4f}s")
                    print(f"    {method} - gene query: {np.mean(gene_query_times):.4f}s")
                    print(f"    {method} - bounding box query: {np.mean(bb_query_times):.4f}s")
        
    print("\nCleaned up temp directory")
    
    return pd.DataFrame(results)

def plot_benchmark_results(results: pd.DataFrame, METHODS, N_GENES):
    """Plot benchmark results with error bars."""
    fig, axes = plt.subplots(3, 2, figsize=(14, 15))
    
    # Colors and markers for different combinations
    styles = {
        ("baseline", 0): {'color': 'blue', 'marker': 'o', 'linestyle': '-'},
        ("baseline", 1): {'color': 'blue', 'marker': 's', 'linestyle': '--'},
        ("baseline", 2): {'color': 'blue', 'marker': '^', 'linestyle': '-.'},
        ("multiscale", 0): {'color': 'red', 'marker': 'o', 'linestyle': '-'},
        ("multiscale", 1): {'color': 'red', 'marker': 's', 'linestyle': '--'},
        ("multiscale", 2): {'color': 'red', 'marker': '^', 'linestyle': '-.'},
    }

    # Plot file sizes
    ax = axes[0][0]
    for method in METHODS:
        for i in range(len(N_GENES)):
            n_genes = N_GENES[i]
            data = results[(results["method"] == method) & (results["n_genes"] == n_genes)]
            style = styles[(method, i if i < 3 else 2)]
            ax.plot(
                data["size"], 
                data["file_size"],
                label=f"{method} - {n_genes} genes",
                **style,
                markersize=8
            )
    
    ax.set_xlabel('Number of points')
    ax.set_ylabel('Size (MB)')
    ax.set_title('parquet file - sizes')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot metadata sizes
    ax = axes[0][1]
    for method in METHODS:
        for i in range(len(N_GENES)):
            n_genes = N_GENES[i]
            data = results[(results["method"] == method) & (results["n_genes"] == n_genes)]
            style = styles[(method, i if i < 3 else 2)]
            ax.plot(
                data["size"], 
                data["meta_size"],
                label=f"{method} - {n_genes} genes",
                **style,
                markersize=8
            )
    
    ax.set_xlabel('Number of points')
    ax.set_ylabel('Size (KB)')
    ax.set_title('parquet metadata - sizes')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot gene query times
    ax = axes[1][0]
    for method in METHODS:
        for i in range(len(N_GENES)):
            n_genes = N_GENES[i]
            data = results[(results["method"] == method) & (results["n_genes"] == n_genes)]
            style = styles[(method, i if i < 3 else 2)]
            ax.errorbar(
                data["size"], 
                data["gene_query_mean"],
                yerr=data["gene_query_std"],
                label=f"{method} - {n_genes} genes",
                **style,
                capsize=3,
                markersize=8
            )
    
    ax.set_xlabel('Number of points')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('gene query - times')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot bounding box query times
    ax = axes[1][1]
    for method in METHODS:
        for i in range(len(N_GENES)):
            n_genes = N_GENES[i]
            data = results[(results["method"] == method) & (results["n_genes"] == n_genes)]
            style = styles[(method, i if i < 3 else 2)]
            ax.errorbar(
                data["size"], 
                data["bb_query_mean"],
                yerr=data["bb_query_std"],
                label=f"{method} - {n_genes} genes",
                **style,
                capsize=3,
                markersize=8
            )
    
    ax.set_xlabel('Number of points')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('bounding box query - times')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot bounding writing times
    ax = axes[2][0]
    for method in METHODS:
        for i in range(len(N_GENES)):
            n_genes = N_GENES[i]
            data = results[(results["method"] == method) & (results["n_genes"] == n_genes)]
            style = styles[(method, i if i < 3 else 2)]
            ax.errorbar(
                data["size"], 
                data["writing_mean"],
                yerr=data["writing_std"],
                label=f"{method} - {n_genes} genes",
                **style,
                capsize=3,
                markersize=8
            )
    
    ax.set_xlabel('Number of points')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('writing - times')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    fig.delaxes(axes[2][1])
    plt.tight_layout()
    return fig
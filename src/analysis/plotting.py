import sys
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import pandas as pd
except ImportError:
    print("Error: This script requires 'matplotlib' and 'pandas'.")
    print("Please install them using: pip install matplotlib pandas")
    sys.exit(1)


def load_results(csv_path: Path) -> pd.DataFrame:
    """Load experiment results from CSV."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Results file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    return df


def plot_success_rate(df: pd.DataFrame, output_dir: Path):
    """Plot success rate by algorithm."""
    success_rates = df.groupby("algorithm")["success"].mean() * 100
    
    plt.figure(figsize=(10, 6))
    success_rates.plot(kind="bar", color="skyblue")
    plt.title("Success Rate by Algorithm")
    plt.ylabel("Success Rate (%)")
    plt.xlabel("Algorithm")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "success_rate.png")
    plt.close()


def plot_runtime(df: pd.DataFrame, output_dir: Path):
    """Plot runtime distribution by algorithm."""
    plt.figure(figsize=(10, 6))
    
    df.boxplot(column="runtime", by="algorithm", rot=45, figsize=(12, 8))
    plt.title("Runtime Distribution by Algorithm")
    plt.ylabel("Runtime (s)")
    plt.xlabel("Algorithm")
    plt.suptitle("")
    plt.tight_layout()
    plt.savefig(output_dir / "runtime_boxplot.png")
    plt.close()


def plot_nodes_expanded(df: pd.DataFrame, output_dir: Path):
    """Plot nodes expanded distribution by algorithm."""
    plt.figure(figsize=(10, 6))
    
    df.boxplot(column="nodes_expanded", by="algorithm", rot=45, figsize=(12, 8))
    plt.title("Nodes Expanded Distribution by Algorithm")
    plt.ylabel("Nodes Expanded")
    plt.xlabel("Algorithm")
    plt.yscale("log")
    plt.suptitle("")
    plt.tight_layout()
    plt.savefig(output_dir / "nodes_expanded_boxplot.png")
    plt.close()


def plot_solution_cost(df: pd.DataFrame, output_dir: Path):
    success_df = df[df["success"] == 1]
    
    if success_df.empty:
        print("No successful runs to plot solution cost.")
        return

    plt.figure(figsize=(10, 6))
    success_df.boxplot(column="solution_cost", by="algorithm", rot=45, figsize=(12, 8))
    plt.title("Solution Cost Distribution (Successful Runs)")
    plt.ylabel("Path Cost")
    plt.xlabel("Algorithm")
    plt.suptitle("")
    plt.tight_layout()
    plt.savefig(output_dir / "solution_cost_boxplot.png")
    plt.close()


def main():
    results_files = [
        Path("results") / "puzzle_experiments_size3_depth20.csv",
        Path("results") / "puzzle_experiments_size4_depth40.csv"
    ]
    
    if len(sys.argv) > 1:
        results_files = [Path(sys.argv[1])]
        
    for results_file in results_files:
        print(f"Loading results from {results_file}...")
        try:
            df = load_results(results_file)
        except FileNotFoundError:
            print(f"File {results_file} not found. Skipping.")
            continue

        output_dir = results_file.parent / "plots" / results_file.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Generating plots in {output_dir}...")
        
        plot_success_rate(df, output_dir)
        plot_runtime(df, output_dir)
        plot_nodes_expanded(df, output_dir)
        plot_solution_cost(df, output_dir)
    
    print("Done.")


if __name__ == "__main__":
    main()

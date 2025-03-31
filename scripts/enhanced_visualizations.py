import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Import configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RESULTS_DIR, GRAPHS_DIR

# Ensure the graphs directory exists
os.makedirs(GRAPHS_DIR, exist_ok=True)

# Define a color palette for algorithms
ALGORITHM_COLORS = {
    'Programação Dinâmica': '#1f77b4',  # blue
    'Backtracking': '#ff7f0e',          # orange
    'Branch and Bound': '#2ca02c'       # green
}

# Algorithm name mapping
ALGORITHM_NAMES = {
    'run_dynamic_programming': 'Programação Dinâmica',
    'run_backtracking': 'Backtracking',
    'run_branch_and_bound': 'Branch and Bound',
    'dynamic_programming': 'Programação Dinâmica',
    'backtracking': 'Backtracking',
    'branch_and_bound': 'Branch and Bound'
}

def load_and_process_data():
    """Load and process data from results files."""
    # Load data
    n_file = os.path.join(RESULTS_DIR, 'resultados_variando_n.csv')
    w_file = os.path.join(RESULTS_DIR, 'resultados_variando_W.csv')
    
    df_n = pd.read_csv(n_file) if os.path.exists(n_file) else pd.DataFrame()
    df_w = pd.read_csv(w_file) if os.path.exists(w_file) else pd.DataFrame()
    
    # Combine data
    df_combined = pd.concat([df_n, df_w], ignore_index=True)
    
    # Clean data
    for col in ['n', 'W', 'tempo', 'valor']:
        if col in df_combined.columns:
            df_combined[col] = pd.to_numeric(df_combined[col], errors='coerce')
    
    # Map algorithm names
    if 'algoritmo' in df_combined.columns:
        df_combined['algoritmo_display'] = df_combined['algoritmo'].map(
            lambda x: ALGORITHM_NAMES.get(x, x)
        )
    
    return df_combined, df_n, df_w

def generate_combined_performance_chart(df):
    """Generate a combined performance chart for all algorithms."""
    if df.empty or 'algoritmo' not in df.columns:
        return
    
    plt.figure(figsize=(12, 8))
    
    # Group by algorithm and calculate statistics
    summary = df.groupby(['algoritmo_display']).agg({
        'tempo': ['mean', 'std', 'min', 'max', 'count']
    }).reset_index()
    
    summary.columns = ['algoritmo', 'tempo_medio', 'tempo_std', 'tempo_min', 'tempo_max', 'count']
    summary = summary.sort_values('tempo_medio')
    
    # Calculate confidence intervals (95%)
    summary['erro'] = summary['tempo_std'] / np.sqrt(summary['count']) * 1.96
    
    # Create the plot
    bars = plt.bar(
        summary['algoritmo'],
        summary['tempo_medio'],
        yerr=summary['erro'],
        capsize=10,
        color=[ALGORITHM_COLORS.get(alg, '#333333') for alg in summary['algoritmo']]
    )
    
    # Add data labels
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2.,
            height + 0.001,
            f'{height:.5f}s',
            ha='center', 
            va='bottom',
            fontweight='bold'
        )
    
    plt.title('Performance Comparison of Knapsack Algorithms', fontsize=16)
    plt.ylabel('Execution Time (seconds)', fontsize=14)
    plt.yscale('log')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, 'algoritmos_performance_combined.png'), dpi=300)
    plt.close()

def generate_efficiency_metric_chart(df):
    """Generate a visualization showing efficiency (value/time) metrics."""
    if df.empty or 'valor' not in df.columns or 'tempo' not in df.columns:
        return
    
    # Calculate efficiency metric
    df['eficiencia'] = df['valor'] / df['tempo']
    
    plt.figure(figsize=(12, 8))
    
    # Create boxplot
    sns.boxplot(
        x='algoritmo_display',
        y='eficiencia',
        data=df,
        palette=ALGORITHM_COLORS
    )
    
    # Add statistical annotations
    stats = df.groupby('algoritmo_display')['eficiencia'].agg(['mean', 'median'])
    for i, alg in enumerate(stats.index):
        plt.text(
            i,
            stats.loc[alg, 'mean'] * 1.1,
            f"Mean: {stats.loc[alg, 'mean']:.1f}\nMedian: {stats.loc[alg, 'median']:.1f}",
            ha='center',
            fontsize=10,
            bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5')
        )
    
    plt.title('Algorithm Efficiency (Value/Time)', fontsize=16)
    plt.xlabel('Algorithm')
    plt.ylabel('Efficiency (value/second)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, 'efficiency_metrics.png'), dpi=300)
    plt.close()

def generate_time_complexity_comparison(df_n):
    """Generate a visualization comparing theoretical vs. empirical time complexity."""
    if df_n.empty or 'n' not in df_n.columns:
        return
    
    plt.figure(figsize=(14, 9))
    
    # Group by n and algorithm, calculate mean time
    grouped = df_n.groupby(['n', 'algoritmo_display'])['tempo'].mean().reset_index()
    
    # Plot for each algorithm
    for alg in grouped['algoritmo_display'].unique():
        alg_data = grouped[grouped['algoritmo_display'] == alg]
        
        # Sort by n value
        alg_data = alg_data.sort_values('n')
        
        # Plot empirical data
        plt.plot(
            alg_data['n'],
            alg_data['tempo'],
            'o-',
            linewidth=2.5,
            markersize=8,
            label=f"{alg} (Empirical)",
            color=ALGORITHM_COLORS.get(alg, None)
        )
        
        # If we have enough points, we could add trend lines
        if len(alg_data) >= 3:
            # For future implementation: add trend lines here
            pass
    
    plt.title('Time Complexity Analysis', fontsize=16)
    plt.xlabel('Number of Items (n)')
    plt.ylabel('Time (seconds)')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend()
    
    # Use log scales if we have multiple data points
    if len(grouped['n'].unique()) > 1:
        plt.xscale('log', base=2)
        plt.yscale('log')
    
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, 'time_complexity_comparison.png'), dpi=300)
    plt.close()

def generate_heatmap_visualization(df):
    """Generate a heatmap visualization showing time by n and W combinations."""
    if df.empty or 'n' not in df.columns or 'W' not in df.columns:
        return
    
    # Pivot table for the heatmap
    for alg in df['algoritmo_display'].unique():
        df_alg = df[df['algoritmo_display'] == alg]
        
        # Pivot the data
        pivot = df_alg.pivot_table(
            index='n',
            columns='W',
            values='tempo',
            aggfunc='mean'
        )
        
        if pivot.empty or pivot.size < 4:
            continue
        
        plt.figure(figsize=(12, 8))
        
        # Create heatmap
        sns.heatmap(
            pivot,
            annot=True,
            fmt='.5f',
            cmap='YlGnBu',
            linewidths=0.5,
            cbar_kws={'label': 'Time (seconds)'}
        )
        
        plt.title(f'Execution Time Heatmap - {alg}')
        plt.xlabel('Knapsack Capacity (W)')
        plt.ylabel('Number of Items (n)')
        
        plt.tight_layout()
        filename = f'heatmap_{alg.replace(" ", "_").lower()}.png'
        plt.savefig(os.path.join(GRAPHS_DIR, filename), dpi=300)
        plt.close()

def main():
    print("Generating enhanced visualizations for knapsack algorithms...")
    
    # Load and process data
    df_combined, df_n, df_w = load_and_process_data()
    
    if df_combined.empty:
        print("No data available for visualization!")
        return
    
    print(f"Loaded {len(df_combined)} data points")
    
    # Generate visualizations
    print("Generating combined performance chart...")
    generate_combined_performance_chart(df_combined)
    
    print("Generating efficiency metrics chart...")
    generate_efficiency_metric_chart(df_combined)
    
    print("Generating time complexity comparison...")
    generate_time_complexity_comparison(df_n)
    
    print("Generating heatmap visualization...")
    generate_heatmap_visualization(df_combined)
    
    print(f"Enhanced visualizations saved to {GRAPHS_DIR}")

if __name__ == "__main__":
    main()
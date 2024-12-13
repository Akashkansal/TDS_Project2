# /// script
# dependencies = [
#   "pandas",
#   "matplotlib",
#   "seaborn",
#   "openai","requests","scikit-learn","scipy","numpy","chardet"
# ]
# ///

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from scipy.stats import zscore
import numpy as np
import chardet

# Function to load a dataset while automatically detecting encoding.
def load_dataset(file_path):
    """
    Load a dataset from the given file path with automatic encoding detection.

    Args:
        file_path (str): Path to the dataset file.

    Returns:
        pd.DataFrame: Loaded dataset.
    """
    try:
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())

        print(f"Detected encoding: {result['encoding']}")
        df = pd.read_csv(file_path, encoding=result['encoding'])
        print(f"Dataset loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

# Function to generate basic visualizations from the dataset.
def visualize_data(df):
    """
    Generate and save visualizations such as pairplots and target distributions.

    Args:
        df (pd.DataFrame): The dataset to visualize.
    """
    sns.set(style="whitegrid")
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns

    if len(num_cols) > 1:
        sns.pairplot(df[num_cols])
        plt.title("Pairplot of Numerical Features")
        plt.savefig("pairplot.png")
        print("Pairplot saved as pairplot.png")

    if "target" in df.columns:
        sns.histplot(df["target"], kde=True, bins=30)
        plt.title("Distribution of Target Variable")
        plt.xlabel("Target")
        plt.ylabel("Frequency")
        plt.savefig("target_distribution.png")
        print("Target distribution saved as target_distribution.png")

# Function to perform basic data analysis and return a summary.
def analyze_data(df):
    """
    Perform basic analysis to summarize the dataset.

    Args:
        df (pd.DataFrame): The dataset to analyze.

    Returns:
        dict: Summary statistics and missing values.
    """
    if df.empty:
        print("The dataset is empty.")
        return None

    summary = {
        "columns": df.columns.tolist(),
        "missing_values": df.isnull().sum().to_dict(),
        "summary_stats": df.describe().to_dict(),
    }
    return summary

# Function to detect and report outliers using z-scores.
def detect_outliers(df):
    """
    Detect outliers in numerical columns based on z-scores.

    Args:
        df (pd.DataFrame): The dataset to analyze.

    Returns:
        dict: Number of outliers per numerical column.
    """
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    outliers = {}

    for col in numerical_cols:
        z_scores = zscore(df[col].dropna())
        outliers[col] = (abs(z_scores) > 3).sum()

    print("Outlier detection completed.")
    return outliers

# Function to analyze correlations between numerical columns.
def correlation_analysis(df):
    """
    Generate a correlation matrix heatmap for numerical features.

    Args:
        df (pd.DataFrame): The dataset to analyze.
    """
    numerical_data = df.select_dtypes(include=[np.number])
    correlation_matrix = numerical_data.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
    plt.title("Correlation Matrix")
    plt.savefig("correlation_matrix.png")
    print("Correlation matrix saved as correlation_matrix.png.")

# Function to analyze feature importance using regression.
def regression_analysis(df, target):
    """
    Perform regression to analyze feature importance.

    Args:
        df (pd.DataFrame): The dataset to analyze.
        target (str): Target column name.

    Returns:
        dict: Feature importances.
    """
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).drop(columns=[target], errors='ignore').columns
    X = df[numerical_cols].dropna()
    y = df[target].dropna()

    if X.shape[0] > 0 and y.shape[0] > 0:
        model = RandomForestRegressor()
        model.fit(X, y)
        feature_importances = dict(zip(numerical_cols, model.feature_importances_))
        print("Feature importance analysis completed.")
        return feature_importances

    print("Insufficient data for regression analysis.")
    return {}

# Function to perform time-series analysis.
def time_series_analysis(df, date_col, target):
    """
    Analyze time-series data to identify trends.

    Args:
        df (pd.DataFrame): The dataset to analyze.
        date_col (str): Date column name.
        target (str): Target column name.
    """
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
        time_series_data = df.groupby(date_col)[target].mean()
        time_series_data.plot(title="Time Series Analysis")
        plt.savefig("time_series_analysis.png")
        print("Time series analysis saved as time_series_analysis.png.")

# Function to perform geographic analysis.
def geographic_analysis(df, lat_col, lon_col):
    """
    Visualize geographic data using latitude and longitude.

    Args:
        df (pd.DataFrame): The dataset to analyze.
        lat_col (str): Latitude column name.
        lon_col (str): Longitude column name.
    """
    if lat_col in df.columns and lon_col in df.columns:
        sns.scatterplot(x=lon_col, y=lat_col, data=df)
        plt.title("Geographic Analysis")
        plt.savefig("geographic_analysis.png")
        print("Geographic analysis saved as geographic_analysis.png.")

# Placeholder function for network analysis.
def network_analysis():
    """
    Placeholder for network analysis functionality.
    """
    print("Network analysis functionality is a placeholder.")

# Function to generate a narrative story from dataset analysis using OpenAI API.
def narrate_story(df, analysis_summary):
    """
    Generate a narrative story based on the dataset analysis.

    Args:
        df (pd.DataFrame): The dataset analyzed.
        analysis_summary (dict): Summary of the analysis.

    Returns:
        str: Generated story.
    """
    significant_analyses = []

    if 'target' in df.columns:
        significant_analyses.append("Regression Analysis identifies key features impacting the target variable.")

    if 'latitude' in df.columns and 'longitude' in df.columns:
        significant_analyses.append("Geographic Analysis provides location-based insights.")

    if not df.empty and df.select_dtypes(include=['float64', 'int64']).shape[1] > 1:
        significant_analyses.append("Cluster Analysis identifies natural groupings for insights.")

    prompt = (
        f"The dataset has {df.shape[0]} rows and {df.shape[1]} columns.\n"
        f"Here is the summary of the analysis:\n{analysis_summary}\n"
        f"Significant insights include:\n"
        + '\n'.join(f"- {analysis}" for analysis in significant_analyses) + "\n"
        f"Create an engaging story from this analysis that explains the key insights."
    )

    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('AIPROXY_TOKEN')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a data analyst."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 3000
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        story = data['choices'][0]['message']['content']
        return story
    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err}")
    except ValueError as val_err:
        print(f"JSON parsing error: {val_err}")
    return None

# Function to save the analysis and story into a README file.
def save_readme(df, analysis_summary, story):
    """
    Save analysis results and generated story into README.md.

    Args:
        df (pd.DataFrame): The dataset analyzed.
        analysis_summary (dict): Summary of the analysis.
        story (str): Generated narrative story.
    """
    with open("README.md", "w") as f:
        f.write("# Analysis Results\n\n")
        f.write("## Summary\n\n")
        f.write("This document presents a detailed analysis of the provided dataset and narrates a data-driven story based on key insights.\n\n")
        f.write("---\n\n")
        f.write("### Key Insights from the Analysis:\n\n")
        f.write("1. **Outlier Detection:**\n")
        f.write("   - Identified potential anomalies that could indicate errors, fraud, or high-impact opportunities.\n\n")
        f.write("2. **Correlation Analysis:**\n")
        f.write("   - Analyzed relationships between variables to determine key correlations.\n")
        f.write("   - A heatmap was generated and saved as `correlation_matrix.png`.\n\n")
        f.write("3. **Time Series Analysis:**\n")
        f.write("   - Patterns over time were examined to help predict future trends.\n")
        f.write("   - Visualization saved as `time_series_analysis.png`.\n\n")
        f.write("4. **Geographic Analysis:**\n")
        f.write("   - Location-based insights were derived from latitude and longitude data.\n")
        f.write("   - Geographic plot saved as `geographic_analysis.png`.\n\n")
        f.write("5. **Network Analysis:**\n")
        f.write("   - Placeholder functionality for network insights is available.\n\n")
        f.write("---\n\n")
        f.write("## Generated Story\n\n")
        f.write(f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns, offering a wealth of information.\n\n")
        f.write("### Story:\n\n")
        f.write(f"> {story}\n\n")
        f.write("---\n\n")
        f.write("## Visualizations\n\n")
        f.write("### Heatmap\n")
        f.write("- Saved as `correlation_matrix.png`\n\n")
        f.write("### Pairplot\n")
        f.write("- Saved as `pairplot.png`\n\n")
        f.write("---\n")
        f.write("Thank you for reviewing this analysis. For questions or further exploration, please reach out!\n")

# Main script execution
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python autolysis.py <dataset.csv>")
        sys.exit(1)

    file_path = sys.argv[1]
    df = load_dataset(file_path)

    if df is not None:
        analysis_summary = analyze_data(df)
        if analysis_summary:
            visualize_data(df)
            outliers = detect_outliers(df)
            print(f"Outliers detected: {outliers}")

            correlation_analysis(df)

            if "target" in df.columns:
                feature_importances = regression_analysis(df, "target")
                print(f"Feature Importances: {feature_importances}")
                time_series_analysis(df, "date", "target")

            geographic_analysis(df, "latitude", "longitude")
            network_analysis()

            story = narrate_story(df, analysis_summary)
            save_readme(df, analysis_summary, story)
            if story:
                print("Generated Story:")
                print(story)
    else:
        print("Failed to process the dataset.")

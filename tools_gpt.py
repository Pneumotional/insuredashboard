import json
from typing import Optional
import numpy as np
import pandas as pd
from tabulate import tabulate
from phi.tools.sql import SQLTools


class SQLStatsTools(SQLTools):
    def calculate_column_stats(self, table_name: str, column_name: str) -> str:
        """
        Calculate basic statistics for a numeric column in a table.
        Use this function when you need to find standard deviation or other basic statistics.
        
        Args:
            table_name (str): Name of the table to analyze
            column_name (str): Name of the numeric column to analyze
            
        Returns:
            str: JSON string containing statistics including mean, std_dev, min, max, and median
            
        Example:
            To get statistics for the 'salary' column in 'employees' table:
            calculate_column_stats('employees', 'salary')
        """
        try:
            # Query to get the column data
            query = f"""
                SELECT 
                    AVG({column_name}) as mean,
                    STDDEV({column_name}) as std_dev,
                    MIN({column_name}) as min_val,
                    MAX({column_name}) as max_val,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {column_name}) as median,
                    COUNT(*) as count,
                    COUNT(CASE WHEN {column_name} IS NULL THEN 1 END) as null_count
                FROM {table_name}
                WHERE {column_name} IS NOT NULL
            """
            
            results = self.run_sql(query)
            
            if not results:
                return json.dumps({"error": "No results found or column is empty"})
                
            # Format the results
            stats = results[0]
            formatted_stats = {
                "column": column_name,
                "table": table_name,
                "statistics": {
                    "mean": round(float(stats['mean']), 2) if stats['mean'] is not None else None,
                    "standard_deviation": round(float(stats['std_dev']), 2) if stats['std_dev'] is not None else None,
                    "minimum": float(stats['min_val']) if stats['min_val'] is not None else None,
                    "maximum": float(stats['max_val']) if stats['max_val'] is not None else None,
                    "median": float(stats['median']) if stats['median'] is not None else None,
                    "total_rows": int(stats['count']),
                    "null_count": int(stats['null_count'])
                }
            }
            
            return json.dumps(formatted_stats, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Error calculating statistics: {str(e)}"})

    def show_numeric_distribution(self, table_name: str, column_name: str, bins: int = 10) -> str:
        """
        Show the distribution of values in a numeric column using basic ASCII visualization.
        Use this when you need to understand the distribution of numeric values.
        
        Args:
            table_name (str): Name of the table
            column_name (str): Name of the numeric column
            bins (int): Number of bins for the distribution (default: 10)
            
        Returns:
            str: Text representation of the value distribution
            
        Example:
            To see the distribution of 'salary' in 'employees' table:
            show_numeric_distribution('employees', 'salary', bins=5)
        """
        try:
            # Get the raw data
            query = f"SELECT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL"
            results = self.run_sql(query)
            
            if not results:
                return "No data found"
                
            # Convert to pandas series
            data = pd.Series([float(r[column_name]) for r in results])
            
            # Calculate histogram
            hist, bin_edges = np.histogram(data, bins=bins)
            max_bar_length = 50  # Maximum length of ASCII bar
            
            # Create ASCII visualization
            output = f"\nDistribution of {column_name} in {table_name}:\n"
            output += "-" * 60 + "\n"
            
            max_count = max(hist)
            for count, edge in zip(hist, bin_edges[:-1]):
                bar_length = int((count / max_count) * max_bar_length)
                output += f"{edge:8.2f} | {'#' * bar_length} ({count})\n"
                
            output += f"{bin_edges[-1]:8.2f} |\n"
            
            return output
            
        except Exception as e:
            return f"Error creating distribution: {str(e)}"

    def quick_column_profile(self, table_name: str, column_name: str) -> str:
        """
        Get a quick profile of any column (numeric or categorical) with basic statistics and patterns.
        Use this for a quick overview of any column's characteristics.
        
        Args:
            table_name (str): Name of the table
            column_name (str): Name of the column to analyze
            
        Returns:
            str: JSON string containing column profile information
            
        Example:
            To profile the 'department' column in 'employees' table:
            quick_column_profile('employees', 'department')
        """
        try:
            # Query for basic column information
            query = f"""
                SELECT 
                    COUNT(*) as total_count,
                    COUNT(DISTINCT {column_name}) as unique_count,
                    COUNT(CASE WHEN {column_name} IS NULL THEN 1 END) as null_count
                FROM {table_name}
            """
            
            basic_stats = self.run_sql(query)[0]
            
            # Query for top 5 most common values
            value_query = f"""
                SELECT {column_name} as value, COUNT(*) as frequency
                FROM {table_name}
                WHERE {column_name} IS NOT NULL
                GROUP BY {column_name}
                ORDER BY COUNT(*) DESC
                LIMIT 5
            """
            
            top_values = self.run_sql(value_query)
            
            # Format the results
            profile = {
                "column_name": column_name,
                "table_name": table_name,
                "basic_stats": {
                    "total_rows": int(basic_stats['total_count']),
                    "unique_values": int(basic_stats['unique_count']),
                    "null_count": int(basic_stats['null_count']),
                    "uniqueness_ratio": round(int(basic_stats['unique_count']) / int(basic_stats['total_count']) * 100, 2)
                },
                "top_values": [
                    {"value": str(v['value']), "frequency": int(v['frequency'])}
                    for v in top_values
                ]
            }
            
            return json.dumps(profile, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Error creating profile: {str(e)}"})
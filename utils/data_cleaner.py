import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
import logging
from datetime import datetime
import warnings

class DataCleaner:
    """
    Enhanced data cleaner with performance optimizations and advanced features.
    """
    
    def __init__(self, 
                chunk_size: int = 10000,
                log_level: str = "INFO",
                optimize_memory: bool = True):
        
        self.chunk_size = chunk_size
        self.optimize_memory = optimize_memory
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def clean_data(self, 
                    df: pd.DataFrame,
                    clean_columns: bool = True,
                    handle_duplicates: bool = True,
                    handle_missing: bool = True,
                    optimize_types: bool = True,
                    remove_outliers: bool = False,
                    outlier_method: str = 'iqr',
                    outlier_threshold: float = 1.5) -> pd.DataFrame:
        if df.empty:
            raise ValueError("DataFrame is empty. No data to clean.")
            
        self.logger.info(f"Starting data cleaning for DataFrame with shape: {df.shape}")
        
        # Create a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Track memory usage if optimization is enabled
        if self.optimize_memory:
            initial_memory = cleaned_df.memory_usage(deep=True).sum() / 1024**2
            self.logger.info(f"Initial memory usage: {initial_memory:.2f} MB")
        
        # Cleaning steps
        if clean_columns:
            cleaned_df = self._clean_column_names(cleaned_df)
            
        if handle_duplicates:
            cleaned_df = self._handle_duplicates(cleaned_df)
            
        if handle_missing:
            cleaned_df = self._handle_missing_values(cleaned_df)
            
        if optimize_types:
            cleaned_df = self._optimize_data_types(cleaned_df)
            
        if remove_outliers:
            cleaned_df = self._handle_outliers(
                cleaned_df, method=outlier_method, threshold=outlier_threshold
            )
        
        # Final optimization
        if self.optimize_memory:
            final_memory = cleaned_df.memory_usage(deep=True).sum() / 1024**2
            memory_saved = initial_memory - final_memory
            self.logger.info(f"Final memory usage: {final_memory:.2f} MB")
            self.logger.info(f"Memory saved: {memory_saved:.2f} MB ({(memory_saved/initial_memory)*100:.1f}%)")
        
        self.logger.info(f"Data cleaning completed. Final shape: {cleaned_df.shape}")
        return cleaned_df
    
    # Clean and standardize column names
    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') 
                    for col in df.columns]
        return df

    # Remove duplicate rows efficiently    
    def _handle_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        initial_rows = len(df)
        df = df.drop_duplicates()
        removed = initial_rows - len(df)
        if removed > 0:
            self.logger.info(f"Removed {removed} duplicate rows")
        return df
    
    # Handle missing values with optimized strategies
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Get missing value counts
        missing_counts = df.isnull().sum()
        missing_cols = missing_counts[missing_counts > 0]
        
        if len(missing_cols) > 0:
            self.logger.info(f"Handling missing values in {len(missing_cols)} columns")
            
            for col in missing_cols.index:
                missing_pct = missing_counts[col] / len(df) * 100
                
                if missing_pct > 50:
                    self.logger.warning(f"Column '{col}' has {missing_pct:.1f}% missing values")
                
                # Use appropriate strategy based on data type
                if df[col].dtype in ['int64', 'float64']:
                    # Numeric: use median
                    df[col] = df[col].fillna(df[col].median())
                elif df[col].dtype == 'object':
                    # Categorical: use mode or 'Unknown'
                    mode_val = df[col].mode()
                    if len(mode_val) > 0:
                        df[col] = df[col].fillna(mode_val[0])
                    else:
                        df[col] = df[col].fillna('Unknown')
                else:
                    # Other types: forward fill
                    df[col] = df[col].fillna(method='ffill')
        
        return df
    
    def _optimize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data types for memory efficiency."""
        df = df.copy()
        
        # Optimize numeric types
        for col in df.select_dtypes(include=['int64', 'float64']).columns:
            col_type = df[col].dtype
            
            if col_type == 'int64':
                # Downcast integers
                c_min = df[col].min()
                c_max = df[col].max()
                
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                    
            elif col_type == 'float64':
                # Downcast floats
                c_min = df[col].min()
                c_max = df[col].max()
                
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
        
        # Optimize object types
        for col in df.select_dtypes(include=['object']).columns:
            num_unique_values = len(df[col].unique())
            num_total_values = len(df[col])
            
            # Convert to category if beneficial
            if num_unique_values / num_total_values < 0.5:
                df[col] = df[col].astype('category')
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame, method: str = 'iqr', 
                        threshold: float = 1.5) -> pd.DataFrame:
        """Detect and handle outliers in numeric columns."""
        df = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        outliers_removed = 0
        
        for col in numeric_cols:
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                outliers_count = mask.sum()
                
                if outliers_count > 0:
                    df = df[~mask]
                    outliers_removed += outliers_count
                    self.logger.info(f"Removed {outliers_count} outliers from '{col}'")
                    
            elif method == 'zscore':
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                mask = z_scores > threshold
                
                outliers_count = mask.sum()
                if outliers_count > 0:
                    df = df[~mask]
                    outliers_removed += outliers_count
                    self.logger.info(f"Removed {outliers_count} outliers from '{col}'")
        
        if outliers_removed > 0:
            self.logger.info(f"Total outliers removed: {outliers_removed}")
        
        return df
    
    def profile_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data quality profile."""
        profile = {
            'shape': df.shape,
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated().sum(),
            'numeric_summary': df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
            'categorical_summary': {
                col: {
                    'unique': df[col].nunique(),
                    'top': df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None,
                    'freq': df[col].value_counts().iloc[0] if len(df[col].value_counts()) > 0 else 0
                }
                for col in df.select_dtypes(include=['object', 'category']).columns
            }
        }
        
        return profile
    
    def clean_in_chunks(self, file_path: str, **kwargs) -> pd.DataFrame:
        chunks = []
        
        for chunk in pd.read_csv(file_path, chunksize=self.chunk_size):
            cleaned_chunk = self.clean_data(chunk, **kwargs)
            chunks.append(cleaned_chunk)
        
        return pd.concat(chunks, ignore_index=True)


# Backward compatibility function
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaner = DataCleaner()
    return cleaner.clean_data(df, clean_columns=True, handle_duplicates=True, 
                            handle_missing=True, optimize_types=True)

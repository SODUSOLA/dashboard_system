import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio
from typing import List, Dict, Optional
import io
import base64
import random
from datetime import datetime


def clean_select(value: str) -> Optional[str]:
    return None if value == "None" else value


@st.cache_data
def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=['number']).columns.tolist()


@st.cache_data
def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=['object', 'category']).columns.tolist()


def calculate_kpi_metrics(df: pd.DataFrame, kpi_col: str) -> Dict[str, float]:
    series = df[kpi_col]
    return {
        'mean': float(series.mean()),
        'median': float(series.median()),
        'std': float(series.std()),
        'min': float(series.min()),
        'max': float(series.max()),
        'sum': float(series.sum()),
        'count': int(series.count()),
        'q25': float(series.quantile(0.25)),
        'q75': float(series.quantile(0.75)),
        'skewness': float(series.skew()),
        'kurtosis': float(series.kurtosis())
    }


class KPIEngine:
    CHART_TYPES = {
        'Bar': px.bar,
        'Line': px.line,
        'Area': px.area,
        'Scatter': px.scatter,
        'Pie': px.pie,
        'Histogram': px.histogram,
        'Box': px.box,
        'Violin': px.violin,
        'Heatmap': 'heatmap',
        'Bubble': 'bubble'
    }

    def __init__(self, df: pd.DataFrame, color_mode: str = "randomized", plain_color: str = "#1f77b4"):
        self.df = df
        self.numeric_cols = get_numeric_columns(df)
        self.categorical_cols = get_categorical_columns(df)

        self.color_mode = color_mode
        self.plain_color = plain_color

    def get_kpi_summary(self) -> pd.DataFrame:
        if not self.numeric_cols:
            return pd.DataFrame()
        summary_data = []
        for col in self.numeric_cols:
            metrics = calculate_kpi_metrics(self.df, col)
            metrics['KPI'] = col
            summary_data.append(metrics)
        return pd.DataFrame(summary_data).set_index('KPI')

    def _random_color(self) -> str:
        """Generate a random hex color."""
        return f"#{random.randint(0, 0xFFFFFF):06x}"

    def _apply_color_mode(self, fig: go.Figure) -> go.Figure:
        if self.color_mode == "plain":
            for trace in fig.data:
                if hasattr(trace, "marker") and hasattr(trace.marker, "colors"):
                    trace.marker.colors = [self.plain_color] * len(trace.marker.colors) if hasattr(trace.marker, "colors") and trace.marker.colors else [self.plain_color]
                elif hasattr(trace, "marker") and hasattr(trace.marker, "color"):
                    trace.marker.color = self.plain_color
                if hasattr(trace, "line") and hasattr(trace.line, "color"):
                    trace.line.color = self.plain_color
        elif self.color_mode == "randomized":
            for trace in fig.data:
                if hasattr(trace, "marker") and hasattr(trace.marker, "colors"):
                    if not trace.marker.colors:
                        # Generate random colors for pie chart
                        trace.marker.colors = [self._random_color() for _ in range(len(trace.labels) if hasattr(trace, 'labels') else 10)]
                elif hasattr(trace, "marker") and hasattr(trace.marker, "color") and not trace.marker.color:
                    trace.marker.color = self._random_color()
                if hasattr(trace, "line") and hasattr(trace.line, "color") and not trace.line.color:
                    trace.line.color = self._random_color()
        return fig

    def create_chart(self,
                    kpi: str,
                    chart_type: str,
                    group_by: Optional[str] = None,
                    secondary_kpi: Optional[str] = None,
                    color_by: Optional[str] = None,
                    label: Optional[str] = None,
                    **kwargs) -> go.Figure:

        title = label if label else f"{chart_type} of {kpi}"

        if chart_type == "Heatmap":
            fig = self._create_heatmap()

        elif chart_type == "Bubble":
            fig = self._create_bubble_chart(kpi, secondary_kpi, color_by)

        elif chart_type == "Pie":
            fig = self._create_pie_chart(kpi, group_by)

        elif chart_type == "Histogram":
            fig = px.histogram(self.df, x=kpi, nbins=20, title=title)

        elif chart_type == "Box":
            fig = px.box(self.df, y=kpi, x=color_by, title=title)

        elif chart_type == "Violin":
            fig = px.violin(self.df, y=kpi, x=color_by, title=title)

        else:
            fig = self._create_standard_chart(
                kpi=kpi,
                chart_type=chart_type,
                group_by=group_by,
                color_by=color_by,
                secondary_kpi=secondary_kpi,
                label=label  
            )

        return self._apply_color_mode(fig)

    def _create_standard_chart(self, kpi: str, chart_type: str,
                            group_by: Optional[str], color_by: Optional[str],
                            secondary_kpi: Optional[str] = None,
                            label: Optional[str] = None) -> go.Figure:
        fig_func = self.CHART_TYPES[chart_type]
        group_by = clean_select(group_by)
        color_by = clean_select(color_by)
        title = label if label else f"{chart_type} of {kpi}"

        if group_by:
            df_copy = self.df.copy()
            if df_copy[kpi].dtype == 'float16':
                if df_copy[kpi].max() > 3.4e38 or df_copy[kpi].min() < -3.4e38:
                    df_copy[kpi] = df_copy[kpi].astype('float64')
                else:
                    df_copy[kpi] = df_copy[kpi].astype('float32')

            if df_copy[group_by].dtype == 'float16':
                if df_copy[group_by].max() > 3.4e38 or df_copy[group_by].min() < -3.4e38:
                    df_copy[group_by] = df_copy[group_by].astype('float64')
                else:
                    df_copy[group_by] = df_copy[group_by].astype('float32')

            df_grouped = (
                df_copy.groupby(group_by, as_index=False, observed=False)[kpi]
                .agg(sum_val='sum', mean_val='mean', count_val='count')
            )
            df_grouped.columns = [group_by, f'{kpi}_sum', f'{kpi}_mean', f'{kpi}_count']
            x_col = group_by
            y_col = f'{kpi}_mean'
        else:
            df_grouped = self.df.copy()
            df_grouped.reset_index(inplace=True)
            x_col = df_grouped.columns[0]
            y_col = kpi

        if chart_type in ['Bar', 'Line', 'Area']:
            return fig_func(df_grouped, x=x_col, y=y_col,
                            color=color_by,
                            title=f"{kpi} by {group_by}" if group_by else f"{kpi} Overview")
        else:
            return fig_func(self.df, x=kpi,
                            y=secondary_kpi if secondary_kpi else kpi,
                            color=color_by,
                            title=f"{kpi} vs {secondary_kpi}" if secondary_kpi else f"{kpi} Scatter")

    def _create_heatmap(self) -> go.Figure:
        if len(self.numeric_cols) < 2:
            fig = go.Figure()
            fig.add_annotation(text="Need at least 2 numeric columns for heatmap")
            return fig
        corr_matrix = self.df[self.numeric_cols].corr()
        fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                        title="KPI Correlation Heatmap")
        return fig

    def _create_bubble_chart(self, kpi: str, secondary_kpi: Optional[str], color_by: Optional[str]) -> go.Figure:
        if not secondary_kpi:
            secondary_kpi = kpi
        if secondary_kpi not in self.numeric_cols:
            return px.scatter(self.df, x=kpi, y=kpi, color=color_by, size_max=15, title=f"{kpi} Bubble")
        size_values = self.df[secondary_kpi]
        fig = px.scatter(self.df, x=kpi, y=secondary_kpi, size=size_values,
                        color=color_by, title=f"{kpi} vs {secondary_kpi}")
        return fig

    def _create_pie_chart(self, kpi: str, group_by: Optional[str]) -> go.Figure:
        group_by = clean_select(group_by)
        if not group_by:
            fig = go.Figure()
            fig.add_annotation(text="Pie chart requires a group-by column", showarrow=False)
            fig.update_layout(showlegend=False)
            return fig

        df_copy = self.df.copy()
        if df_copy[kpi].dtype == 'float16':
            if df_copy[kpi].max() > 3.4e38 or df_copy[kpi].min() < -3.4e38:
                df_copy[kpi] = df_copy[kpi].astype('float64')
            else:
                df_copy[kpi] = df_copy[kpi].astype('float32')

        df_grouped = df_copy.groupby(group_by, as_index=False, observed=False)[kpi].sum()
        return px.pie(df_grouped, values=kpi, names=group_by, title=f"{kpi} Distribution")




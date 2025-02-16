import sys
from pathlib import Path
import pytz
from datetime import datetime, timedelta
import pandas as pd

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import requests
import logging
import dash
import dash_bootstrap_components as dbc

from src.data.data_loader import EntsoeClient
from src.config import Config

# Setup logging
logging.basicConfig(
    filename='dashboard.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    update_title=None,  # This removes the "Updating..." browser title
    suppress_callback_exceptions=True
)
server = app.server

try:
    # Initialize data client
    client = EntsoeClient(
        api_key=Config.ENTSOE_API_KEY,
        country_code=Config.COUNTRY_CODE
    )
    logger.info("Successfully initialized EntsoeClient")
except Exception as e:
    logger.error(f"Failed to initialize EntsoeClient: {str(e)}")
    raise

# Add logging configuration
logging.basicConfig(
    filename='dashboard.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define the layout
app.layout = html.Div([
    #html.H1("German Energy Load Dashboard"),
    
    dcc.Interval(
        id='interval-component',
        interval=Config.UPDATE_INTERVAL * 60 * 1000,  # Convert minutes to milliseconds
        n_intervals=0
    ),
    
    html.Div([
        html.Div(id='last-update-time', className='update-time'),
        dcc.Loading(
            id="loading-1",
            type="default",
            children=dcc.Graph(id='load-chart')
        ),
        
        # html.Div([
        #     html.Div([
        #         html.H3("Current Load", style={'fontSize': '36px'}),
        #         html.P(id='current-load', children="Loading...")
        #     ], className='stat-card'),
        #     html.Div([
        #         html.H3("Forecast Load", style={'fontSize': '36px'}),
        #         html.P(id='forecast-load', children="Loading...")
        #     ], className='stat-card')

        # ], className='stats-panel'),
        html.Div(id='error-message', className='error-message'),
    ], className='dashboard-grid')
])

@app.callback(
    [Output('load-chart', 'figure'),
     #Output('current-load', 'children'),
     #Output('forecast-load', 'children'),
     Output('last-update-time', 'children'),
     Output('error-message', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_dashboard(n):
    try:
        logger.info("Fetching new data...")
        actual_load, forecast_load = client.get_load_data(
            hours_back=48,
            forecast_hours=24
        )
        
        # Create figure
        fig = go.Figure()
        
        # Get current time using datetime
        now = datetime.now(pytz.timezone("Europe/Berlin"))
        now_ts = pd.Timestamp(now)
        
        # Add actual load trace
        if not actual_load.empty:
            fig.add_trace(go.Scatter(
                x=actual_load.index,
                y=actual_load.values,
                name='Actual Load',
                line=dict(color='#00bbec', width=2)
            ))
        
        # Add forecast load trace (only future values)
        if not forecast_load.empty:
            #future_forecast = forecast_load[forecast_load.index >= now_ts]
            #if not forecast_load.empty:
            fig.add_trace(go.Scatter(
                x=forecast_load.index,
                y=forecast_load.values,
                name='Forecast Load',
                line=dict(color='#ff9f1c', width=2, dash='dash')
            ))
        
        # Calculate x-axis range using timedelta
        x_min = actual_load.index.min() if not actual_load.empty else pd.Timestamp(now - timedelta(hours=48))
        x_max = forecast_load.index.max() if not forecast_load.empty else pd.Timestamp(now + timedelta(hours=24))
        
        # Update layout
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#1a1a1a',
            plot_bgcolor='#1a1a1a',
            height=450,
            margin=dict(l=30, r=30, t=20, b=50),
            xaxis=dict(
                title="Time",
                title_font=dict(size=16),
                tickfont=dict(size=12),
                gridcolor='#2f3338',
                range=[x_min, x_max]

            ),
            yaxis=dict(
                title="Load [MW]",
                title_font=dict(size=16),
                tickfont=dict(size=12),
                gridcolor='#2f3338'
            ),
            hovermode='x unified',

            showlegend=True,
            legend=dict(
                font=dict(size=16),
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor='rgba(26,26,26,0.8)'
            )
        )
        
        # # Format values with proper timezone handling
        # current_load = html.Div([
        #     #html.Span(style={'fontSize': '48px'}),s
        #     html.Br(),
        #     html.Span(f"{float(actual_load.iloc[-1]):,.0f} MW" if not actual_load.empty else "N/A", 
        #              style={'fontSize': '18', 'fontWeight': 'bold'})
        # ])
        
        # forecast_load = html.Div([
        #     #html.Span(style={'fontSize': '48px'}),
        #     html.Br(),
        #     html.Span(f"{float(forecast_load.iloc[0]):,.0f} MW" if not forecast_load.empty else "N/A", 
        #              style={'fontSize': '18px', 'fontWeight': 'bold'})
        # ])
        
        last_update = html.Div(
            f"Last updated: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            style={'fontSize': '18px'}
        )
        
        return fig, last_update, "" , #current_load, forecast_load, 
        
    except Exception as e:
        logger.error(f"Error updating dashboard: {str(e)}")
        return (
            go.Figure(),
            "Data unavailable",
            "Data unavailable",
            f"Last update failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Error: {str(e)}"
        )

if __name__ == '__main__':
    logger.info(f"Starting dashboard on {Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}")
    app.run_server(
        host=Config.DASHBOARD_HOST,
        port=Config.DASHBOARD_PORT,
        debug=False,
        dev_tools_ui=False,       # Disable the debug UI
        dev_tools_props_check=False,  # Disable props validation
        dev_tools_hot_reload=False,   # Disable hot-reloading
        dev_tools_silence=True    # Silence dev tools messages
    ) 
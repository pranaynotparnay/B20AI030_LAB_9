# alpha - MU4CSJR96HC2DD42

import pandas as pd
import requests
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from alpha_vantage.timeseries import TimeSeries
import plotly.graph_objs as go
import plotly.express as px
import datetime as dt


api_key = "<MU4CSJR96HC2DD42>"
ts = TimeSeries(key=api_key, output_format="pandas")

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Stock Price Dashboard"),
        html.Div(
            [
                html.Label("Enter Ticker Symbol"),
                dcc.Input(id="symbol-input", type="text", value="AAPL"),
                html.Label("Select Time Series"),
                dcc.Dropdown(
                    id="time-series-dropdown",
                    options=[
                        {"label": "Daily", "value": "daily"},
                        {"label": "Weekly", "value": "weekly"},
                        {"label": "Monthly", "value": "monthly"},
                    ],
                    value="daily",
                ),
            ],
            className="input-container",
        ),
        dcc.Graph(id="stock-graph"),
        dcc.Graph(id="volume-graph"),
        dcc.Graph(id="open-close-graph"),
        html.Div(id="output"),
    ]
)


@app.callback(
    [
        dash.dependencies.Output("stock-graph", "figure"),
        dash.dependencies.Output("volume-graph", "figure"),
        dash.dependencies.Output("open-close-graph", "figure"),
    ],
    [
        dash.dependencies.Input("symbol-input", "value"),
        dash.dependencies.Input("time-series-dropdown", "value"),
    ],
)
def update_stock_graph(symbol, time_series):
    data, metadata = ts.get_daily_adjusted(symbol=symbol)
    data = data.reset_index()
    data = data.rename(
        columns={
            "date": "Date",
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. adjusted close": "Adjusted Close",
            "6. volume": "Volume",
            "7. dividend amount": "Dividend Amount",
            "8. split coefficient": "Split Coefficient",
        }
    )
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date")
    if time_series == "weekly":
        data = data.resample("W").last()
    elif time_series == "monthly":
        data = data.resample("M").last()

    stock_fig = {
        "data": [{"x": data.index, "y": data["Adjusted Close"], "type": "line"}],
        "layout": {"title": symbol + " Adjusted Close Price"},
    }
    volume_fig = {
        "data": [{"x": data.index, "y": data["Volume"], "type": "bar"}],
        "layout": {"title": symbol + " Volume"},
    }
    open_close_fig = {
        "data": [
            {"x": data.index, "y": data["Open"], "name": "Open", "type": "line"},
            {"x": data.index, "y": data["Close"], "name": "Close", "type": "line"},
        ],
        "layout": {"title": symbol + " Open and Close Price"},
    }
    return stock_fig, volume_fig, open_close_fig


if __name__ == "__main__":
    app.run_server(debug=True)

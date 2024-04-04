"""
File contains different classes for time series forecasting

Classes:
BaseProphetForecasterModel - Class that uses prophet library to forecast 

"""


import math
import ruptures as rpt
from collections import defaultdict
import matplotlib.pyplot as plt
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot

__all__ = ['BaseProphetForecasterModel']


class BaseProphetForecasterModel(object):
    """
    Base class for time series forecasting
    """

    def __init__(self, df, *args, **kwargs):
        """
        defaults
        """
        self.data = df

        self.growth =  'linear'
        self.horizon = 3
        self.periods = self.horizon * 2
        self.seasonality_mode = 'multiplicative'

        super().__init__(*args, **kwargs)

    
    def _init_model(self, growth, seasonality_mode):

        model = Prophet(growth=growth,
                        changepoint_prior_scale=0.5,
                        seasonality_mode=seasonality_mode)
        self.model = model



    def run_forecasting(self, params):
        # setup and run

        df = self.data

        holidays = params.get('holidays', [])
        regressors = params.get('regressors', [])
        growth = params.get('growth', self.growth)
        periods = params.get('periods', self.periods)
        seasonality_mode = params.get('seasonality_mode', self.seasonality_mode)

        self._init_model(growth, seasonality_mode)
        model = self.model

        # add country holidays
        for country in holidays:
            model.add_country_holidays(country_name=country)
        
        # add any additional regressors
        for r in regressors:
            model.add_regressor(r)
        
        # set the cap for the dataframe
        # needed for logitstic model 
        cap = df['y'].max()
        if growth == 'logistic':
            df['cap'] = cap
        
        # fit the model 
        model.fit(df)
        
        # create a future timeseries set for N periods
        future = model.make_future_dataframe(periods=periods)
        # set the cap
        if growth == 'logistic':
            future['cap'] = cap

        # add any additional regressors to the future timeseries
        for r in regressors:
            future[r] = df[r].tail(1).values[0]

        # make predictions using the fitted model
        forecast = model.predict(future)
        
        return forecast


    def visualize_forecasting(self, forecast, chart_params):
        """
        visualize the changepoints
        """
        model = self.model

        xlabel = chart_params.get('xlabel', 'Date')
        ylabel = chart_params.get('ylabel', 'Value')
        title = chart_params.get('title', 'Forecast')
        show_changepoints = chart_params.get('show_changepoints', False)

        fig = model.plot(forecast)

        fig.gca().set_xlabel(xlabel)
        fig.gca().set_ylabel(ylabel)
        fig.gca().set_title(title)

        if show_changepoints:
             add_changepoints_to_plot(fig.gca(), model, forecast)

        return fig

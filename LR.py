import numpy as np
import pandas as pd
import yfinance as yf
from typing import Dict, Tuple
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

class LogisticRegressionPortfolioOptimizer:
    """
    A portfolio optimization class using logistic regression to predict the direction of stock price movement.
    
    Attributes:
        tickers (List[str]): List of ticker symbols to be included in the portfolio.
        start_date (str): The start date for historical data retrieval.
        end_date (str): The end date for historical data retrieval.
        data (pd.DataFrame): DataFrame containing the historical data.
        models (Dict[str, Tuple[LogisticRegression, StandardScaler]]): Dictionary mapping ticker symbols to tuples of trained logistic regression models and their associated scalers.
        allocations (Dict[str, List[int]]): Dictionary mapping ticker symbols to lists of daily allocation decisions (1 for predicted up, 0 for predicted down).
    """

    def __init__(self, tickers: list[str], start_date: str, end_date: str) -> None:
        """
        Initializes the LogisticRegressionPortfolioOptimizer with given tickers and date range.

        Args:
            tickers (List[str]): List of ticker symbols.
            start_date (str): Start date in 'YYYY-MM-DD' format.
            end_date (str): End date in 'YYYY-MM-DD' format.
        """
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.models: Dict[str, Tuple[LogisticRegression, StandardScaler]] = {}
        self.allocations: Dict[str, List[int]] = {ticker: [] for ticker in tickers}

    def load_data(self) -> None:
        """Loads financial data from Yahoo Finance for the specified tickers and date range."""
        self.data = yf.download(self.tickers, start=self.start_date, end=self.end_date)

    def preprocess_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prepares the data for logistic regression by calculating daily returns and creating binary outcomes.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing the features (previous day's returns) and outcomes (binary indicators of price movement direction).
        """
        # Calculate daily returns
        daily_returns = self.data['Close'].pct_change()

        # Calculate binary outcomes: 1 for positive return, 0 for negative
        outcomes = (daily_returns > 0).astype(int)

        # Use previous day's returns as features
        features = daily_returns.shift(1).fillna(0)

        return features, outcomes

    def train_models(self) -> None:
        """
        Trains logistic regression models for each ticker symbol based on historical data.
        """
        features, outcomes = self.preprocess_data()
        
        for ticker in self.tickers:
            X = features[ticker].values.reshape(-1, 1)  # Features matrix
            y = outcomes[ticker].values  # Target vector
            
            # Split data into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Standardize features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Initialize and train the logistic regression model
            model = LogisticRegression()
            model.fit(X_train_scaled, y_train)
            
            # Evaluate the model
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            print(f'{ticker} Model Accuracy: {accuracy:.2f}')
            
            self.models[ticker] = (model, scaler)

    def predict_daily_allocations(self, start_date: str, end_date: str) -> Dict[str, List[int]]:
        """
        Predicts daily allocations for each asset within the specified date range.

        Args:
            start_date (str): The start date for the prediction period in 'YYYY-MM-DD' format.
            end_date (str): The end date for the prediction period in 'YYYY-MM-DD' format.

        Returns:
            Dict[str, List[int]]: A dictionary mapping ticker symbols to lists of daily allocation decisions.
        """
        # Filter the data for the specified date range
        date_mask = (self.data.index >= start_date) & (self.data.index <= end_date)
        filtered_data = self.data.loc[date_mask]

        # Iterate over each day in the filtered data
        for current_date in filtered_data.index[:-1]:  # Exclude the last day since we can't predict the next day's movement
            last_day_returns = self.data['Close'].pct_change().loc[current_date]
            
            for ticker, (model, scaler) in self.models.items():
                # Standardize the feature for the current day
                feature = scaler.transform([[last_day_returns[ticker]]])
                
                # Predict the direction for the next day (1 for up, 0 for down)
                prediction = model.predict(feature)[0]
                
                # Append the prediction to the allocations list for the ticker
                self.allocations[ticker].append(prediction)

        return self.allocations
    
if __name__ == '__main__':
    tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN']
    start_date = '2010-01-01'
    end_date = '2022-12-31'

    optimizer = LogisticRegressionPortfolioOptimizer(tickers, start_date, end_date)
    optimizer.load_data()
    optimizer.train_models()
    
    # Predict allocations for a specified period
    prediction_start_date = '2022-01-01'
    prediction_end_date = '2022-12-31'
    daily_allocations = optimizer.predict_daily_allocations(prediction_start_date, prediction_end_date)
    
    print('Daily Predicted Allocations:', daily_allocations)


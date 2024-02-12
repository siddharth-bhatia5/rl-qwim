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

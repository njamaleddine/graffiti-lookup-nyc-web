"""
Graffiti Prediction Model

Handles training and prediction for graffiti recurrence, cleaning likelihood,
and time-to-next-update using machine learning models.
"""

import datetime

import numpy as np
import pandas
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from graffiti_data_pipeline.config import GRAFFITI_CLEANED_STATUS
from graffiti_data_pipeline.logger import get_logger

logger = get_logger(__name__)

MIN_TRAIN_SIZE = 10


class GraffitiPredictionModel:
    def __init__(self, min_train_size: int = MIN_TRAIN_SIZE):
        self.min_train_size = min_train_size
        self.recurrence_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.cleaning_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.time_regressor = RandomForestRegressor(n_estimators=50, random_state=42)
        self.recurrence_window_regressor = RandomForestRegressor(
            n_estimators=50, random_state=42
        )
        self.resolution_time_regressor = RandomForestRegressor(
            n_estimators=50, random_state=42
        )

    @staticmethod
    def estimate_next_tag_date(last_updated: str, likelihood_percent: float) -> str:
        """
        Estimate the next expected tag date based on last updated and likelihood.
        Higher likelihood means sooner next tag, with a minimum of 1 day and a maximum of 365 days.
        Args:
            last_updated (str): Last updated date as YYYY-MM-DD.
            likelihood_percent (float): Likelihood percentage (0-100).
        Returns:
            str: Estimated next tag date as YYYY-MM-DD or 'Unknown'.
        """
        if not last_updated or likelihood_percent <= 0:
            return "Unknown"
        try:
            last_date = datetime.datetime.strptime(last_updated, "%Y-%m-%d")
            # Clamp likelihood_percent to [0.01, 100] to avoid division by zero
            likelihood = max(min(likelihood_percent, 100), 0.01)
            # Inverse mapping: higher likelihood = fewer days, min 1 day, max 365 days
            days_until_next_tag = int(365 * (1 - (likelihood / 100))) + 1
            next_tag_date = last_date + datetime.timedelta(days=days_until_next_tag)
            return next_tag_date.strftime("%Y-%m-%d")
        except Exception:
            return "Unknown"

    def train_recurrence_classifier(
        self, features: pandas.DataFrame, targets: pandas.Series
    ):
        if features.empty or targets.empty:
            raise ValueError("Features and targets must not be empty.")
        if len(features) > self.min_train_size:
            features_train, features_test, targets_train, targets_test = (
                train_test_split(features, targets, test_size=0.2, random_state=42)
            )
            self.recurrence_model.fit(features_train, targets_train)
            predictions = self.recurrence_model.predict(features_test)
            accuracy = accuracy_score(targets_test, predictions)
            logger.info(f"Recurrence model accuracy: {accuracy:.3f}")
        else:
            self.recurrence_model.fit(features, targets)

    def train_cleaning_classifier(
        self, features: pandas.DataFrame, targets: pandas.Series
    ):
        if features.empty or targets.empty:
            raise ValueError("Features and targets must not be empty.")
        if len(features) > self.min_train_size:
            features_train, features_test, targets_train, targets_test = (
                train_test_split(features, targets, test_size=0.2, random_state=42)
            )
            self.cleaning_model.fit(features_train, targets_train)
            predictions = self.cleaning_model.predict(features_test)
            accuracy = accuracy_score(targets_test, predictions)
            logger.info(f"Cleaning model accuracy: {accuracy:.3f}")
        else:
            self.cleaning_model.fit(features, targets)

    def train_time_regressor(self, features: pandas.DataFrame, targets: pandas.Series):
        if features.empty or targets.empty:
            raise ValueError("Features and targets must not be empty.")
        valid_mask = targets.notnull()
        if valid_mask.sum() > self.min_train_size:
            self.time_regressor.fit(features[valid_mask], targets[valid_mask])
        else:
            logger.warning("Not enough data to train time regressor")

    def train_recurrence_window_regressor(
        self, features: pandas.DataFrame, targets: pandas.Series
    ):
        """Train regressor that predicts days until next report at address."""
        if features.empty or targets.empty:
            raise ValueError("Features and targets must not be empty.")
        valid_mask = targets.notnull()
        if valid_mask.sum() > self.min_train_size:
            self.recurrence_window_regressor.fit(
                features[valid_mask], targets[valid_mask]
            )
        else:
            logger.warning("Not enough data to train recurrence window regressor")

    def train_resolution_time_regressor(
        self, features: pandas.DataFrame, targets: pandas.Series
    ):
        """Train regressor that predicts days from report to resolution."""
        if features.empty or targets.empty:
            raise ValueError("Features and targets must not be empty.")
        valid_mask = targets.notnull()
        if valid_mask.sum() > self.min_train_size:
            self.resolution_time_regressor.fit(
                features[valid_mask], targets[valid_mask]
            )
        else:
            logger.warning("Not enough data to train resolution time regressor")

    def predict(self, features: pandas.DataFrame):
        recurrence_probabilities = self._get_class_probabilities(
            self.recurrence_model, features
        )
        cleaning_probabilities = self._get_class_probabilities(
            self.cleaning_model, features
        )
        time_predictions = self._get_time_predictions(features)
        recurrence_window_predictions = self._get_regressor_predictions(
            self.recurrence_window_regressor, features
        )
        resolution_time_predictions = self._get_regressor_predictions(
            self.resolution_time_regressor, features
        )
        return (
            recurrence_probabilities,
            cleaning_probabilities,
            time_predictions,
            recurrence_window_predictions,
            resolution_time_predictions,
        )

    def _get_class_probabilities(self, model, features):
        proba = model.predict_proba(features)
        if proba.shape[1] == 1:
            single_class = model.classes_[0]
            if single_class == 1:
                return np.ones(len(features))
            else:
                return np.zeros(len(features))
        else:
            return proba[:, 1]

    def _get_time_predictions(self, features):
        try:
            return self.time_regressor.predict(features)
        except Exception:
            return [None] * len(features)

    @staticmethod
    def _get_regressor_predictions(regressor, features):
        """Safely predict from a regressor, returning None on failure."""
        try:
            return regressor.predict(features)
        except Exception:
            return [None] * len(features)

    def predict_cleaning_date(
        self, last_updated: str, cleaning_prob: float, predicted_days=None
    ) -> str:
        """Predict the cleaning date using probability and time prediction.

        Returns a date string when cleaning is likely (>50%) and the time
        regressor produced a valid prediction, otherwise 'Unknown'.
        """
        if cleaning_prob <= 0.5:
            return "Unknown"
        if not _is_valid_day_count(predicted_days):
            return "Unknown"
        try:
            last_date = datetime.datetime.strptime(last_updated, "%Y-%m-%d")
            cleaning_date = last_date + datetime.timedelta(days=int(predicted_days))
            return cleaning_date.strftime("%Y-%m-%d")
        except (ValueError, OverflowError):
            return "Unknown"

    def enrich_requests(
        self,
        requests,
        recurrence_probabilities,
        cleaning_probabilities,
        time_predictions,
        recurrence_window_predictions=None,
        resolution_time_predictions=None,
        times_reported=None,
        times_cleaned=None,
    ):
        """Enrich each request record with prediction fields."""
        prediction_count = len(requests)
        if (
            len(recurrence_probabilities) != prediction_count
            or len(cleaning_probabilities) != prediction_count
            or len(time_predictions) != prediction_count
        ):
            raise ValueError(
                f"Length mismatch: {prediction_count} requests, "
                f"{len(recurrence_probabilities)} recurrence, "
                f"{len(cleaning_probabilities)} cleaning, "
                f"{len(time_predictions)} time predictions"
            )

        if recurrence_window_predictions is None:
            recurrence_window_predictions = [None] * prediction_count
        if resolution_time_predictions is None:
            resolution_time_predictions = [None] * prediction_count
        if times_reported is None:
            times_reported = [0] * prediction_count
        if times_cleaned is None:
            times_cleaned = [0] * prediction_count

        for idx, request in enumerate(requests):
            rec_prob = float(recurrence_probabilities[idx])
            clean_prob = float(cleaning_probabilities[idx])
            predicted_days = time_predictions[idx]

            request.record["graffiti_likelihood"] = self.compute_graffiti_likelihood(
                rec_prob
            )
            request.record["estimated_next_tag"] = self.compute_estimated_next_tag(
                request.last_updated, rec_prob
            )
            request.record["predicted_time_to_next_update"] = (
                self.compute_predicted_time_to_next_update(
                    request.last_updated, predicted_days
                )
            )

            # New continuous predictions
            recurrence_window = recurrence_window_predictions[idx]
            request.record["predicted_recurrence_days"] = (
                round(float(recurrence_window))
                if _is_valid_day_count(recurrence_window)
                else None
            )

            resolution_days = resolution_time_predictions[idx]
            request.record["predicted_resolution_days"] = (
                round(float(resolution_days))
                if _is_valid_day_count(resolution_days)
                else None
            )

            request.record["times_reported"] = int(times_reported[idx])
            request.record["times_cleaned"] = int(times_cleaned[idx])

            # Ground truth replaces predictions when the outcome is known.
            if request.status == GRAFFITI_CLEANED_STATUS:
                request.record["cleaning_likelihood"] = 100.0
                request.record["predicted_cleaning_date"] = request.last_updated
            else:
                request.record["cleaning_likelihood"] = (
                    self.compute_cleaning_likelihood(clean_prob)
                )
                request.record["predicted_cleaning_date"] = self.predict_cleaning_date(
                    request.last_updated, clean_prob, predicted_days
                )
        return [request.record for request in requests]

    def compute_graffiti_likelihood(self, recurrence_probability: float) -> float:
        return float(recurrence_probability) * 100

    def compute_estimated_next_tag(
        self, last_updated: str, recurrence_probability: float
    ) -> str:
        return self.estimate_next_tag_date(
            last_updated, float(recurrence_probability) * 100
        )

    def compute_cleaning_likelihood(self, cleaning_probability: float) -> float:
        return float(cleaning_probability) * 100

    def compute_predicted_time_to_next_update(
        self, last_updated: str, predicted_days
    ) -> str:
        """Convert a day-count prediction into a date string."""
        if not _is_valid_day_count(predicted_days):
            return "Unknown"
        try:
            last_date = datetime.datetime.strptime(last_updated, "%Y-%m-%d")
            predicted_date = last_date + datetime.timedelta(days=int(predicted_days))
            return predicted_date.strftime("%Y-%m-%d")
        except (ValueError, OverflowError):
            return "Unknown"


def _is_valid_day_count(value) -> bool:
    """Return True if *value* is a positive, finite number."""
    if value is None:
        return False
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False

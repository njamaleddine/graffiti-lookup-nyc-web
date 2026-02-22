import pytest
import pandas

from graffiti_data_pipeline.prediction.model import GraffitiPredictionModel


class DummyRequest:
    def __init__(self, last_updated="2026-02-01"):
        self.record = {"last_updated": last_updated}
        self.last_updated = last_updated


class TestGraffitiPredictionModel:
    def test_estimate_next_tag_date_valid(self):
        date = GraffitiPredictionModel.estimate_next_tag_date("2026-02-01", 50)
        assert isinstance(date, str) and date != "Unknown"

    def test_estimate_next_tag_date_invalid(self):
        date = GraffitiPredictionModel.estimate_next_tag_date("", 0)
        assert date == "Unknown"

    def test_estimate_next_tag_date_extreme_likelihood(self):
        date = GraffitiPredictionModel.estimate_next_tag_date("2026-02-01", 100)
        date_min = GraffitiPredictionModel.estimate_next_tag_date("2026-02-01", 0.01)
        assert isinstance(date, str) and date != "Unknown"
        assert isinstance(date_min, str) and date_min != "Unknown"

    def test_train_and_predict(self):
        model = GraffitiPredictionModel(min_train_size=1)
        features = pandas.DataFrame(
            {
                "days_since_last_tag": [1, 2],
                "borough": [0, 1],
                "total_tags": [1, 2],
                "response_time": [1, 2],
                "latitude": [40.7, 40.6],
                "longitude": [-74.0, -73.9],
                "status_code": [0, 1],
            }
        )
        recurrence_targets = pandas.Series([0, 1])
        cleaning_targets = pandas.Series([1, 0])
        time_targets = pandas.Series([5, 10])
        model.train_recurrence_classifier(features, recurrence_targets)
        model.train_cleaning_classifier(features, cleaning_targets)
        model.train_time_regressor(features, time_targets)
        recurrence_probabilities, cleaning_probabilities, time_predictions = (
            model.predict(features)
        )
        assert all(
            len(lst) == 2
            for lst in [
                recurrence_probabilities,
                cleaning_probabilities,
                time_predictions,
            ]
        )

    def test_train_with_empty_features(self):
        model = GraffitiPredictionModel(min_train_size=1)
        features = pandas.DataFrame()
        targets = pandas.Series(dtype=int)
        # Should raise ValueError for empty features
        with pytest.raises(ValueError):
            model.train_recurrence_classifier(features, targets)
        with pytest.raises(ValueError):
            model.train_cleaning_classifier(features, targets)
        with pytest.raises(ValueError):
            model.train_time_regressor(features, targets)

    def test_predict_with_invalid_features(self):
        model = GraffitiPredictionModel(min_train_size=1)
        with pytest.raises(Exception):
            model.predict(None)

    def test_predict_with_empty_features(self):
        model = GraffitiPredictionModel(min_train_size=1)
        features = pandas.DataFrame()
        with pytest.raises(Exception):
            model.predict(features)

    def test_enrich_requests(self):
        model = GraffitiPredictionModel(min_train_size=1)
        requests = [DummyRequest(), DummyRequest()]
        recurrence_probabilities = [0.5, 0.7]
        cleaning_probabilities = [0.8, 0.2]
        time_predictions = [5, 10]
        enriched = model.enrich_requests(
            requests, recurrence_probabilities, cleaning_probabilities, time_predictions
        )
        assert isinstance(enriched, list)
        for record in enriched:
            assert all(
                key in record
                for key in [
                    "graffiti_likelihood",
                    "estimated_next_tag",
                    "cleaning_likelihood",
                    "predicted_cleaning_date",
                    "predicted_time_to_next_update",
                ]
            )

    def test_enrich_requests_with_empty(self):
        model = GraffitiPredictionModel(min_train_size=1)
        enriched = model.enrich_requests([], [], [], [])
        assert isinstance(enriched, list) and len(enriched) == 0

    def test_enrich_requests_mismatched_lengths(self):
        model = GraffitiPredictionModel(min_train_size=1)
        requests = [DummyRequest()]
        recurrence_probabilities = [0.5, 0.7]
        cleaning_probabilities = [0.8]
        time_predictions = [5]
        try:
            model.enrich_requests(
                requests,
                recurrence_probabilities,
                cleaning_probabilities,
                time_predictions,
            )
            assert False, "Expected an exception due to mismatched lengths"
        except Exception:
            assert True

    def test_predict_cleaning_date_edge_cases(self):
        model = GraffitiPredictionModel(min_train_size=1)
        # cleaning_prob > 0.5
        date = model.predict_cleaning_date("2026-02-01", 0.6)
        assert isinstance(date, str) and date != "Unknown"
        # cleaning_prob <= 0.5
        date = model.predict_cleaning_date("2026-02-01", 0.4)
        assert date == "Unknown"
        # invalid date
        date = model.predict_cleaning_date("invalid-date", 0.6)
        assert date == "Unknown"

    def test_compute_predicted_time_to_next_update_edge_cases(self):
        model = GraffitiPredictionModel(min_train_size=1)
        # valid predicted_days
        date = model.compute_predicted_time_to_next_update("2026-02-01", 5)
        assert isinstance(date, str) and date != "Unknown"
        # predicted_days is None
        date = model.compute_predicted_time_to_next_update("2026-02-01", None)
        assert date == "Unknown"
        # predicted_days is NaN
        import numpy as np

        date = model.compute_predicted_time_to_next_update("2026-02-01", np.nan)
        assert date == "Unknown"
        # predicted_days is negative
        date = model.compute_predicted_time_to_next_update("2026-02-01", -5)
        assert date == "Unknown"
        # invalid date
        date = model.compute_predicted_time_to_next_update("invalid-date", 5)
        assert date == "Unknown"

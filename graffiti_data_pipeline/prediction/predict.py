"""
Graffiti Prediction CLI Entry Point

This module orchestrates loading data, feature engineering, model training,
and enrichment for graffiti recurrence prediction.
"""

from graffiti_data_pipeline.storages import JsonFile
from graffiti_data_pipeline.logger import get_logger
from graffiti_data_pipeline.config import GRAFFITI_CLEANED_STATUS, GRAFFITI_LOOKUPS_FILE
from graffiti_data_pipeline.prediction.request import GraffitiServiceRequest
from graffiti_data_pipeline.prediction.features import extract_features
from graffiti_data_pipeline.prediction.model import GraffitiPredictionModel

logger = get_logger(__name__)


def main():
    """
    Main entry point for graffiti recurrence prediction.
    Loads data, engineers features, trains model, enriches and saves results.
    """
    logger.info("Loading graffiti lookup data...")
    graffiti_records = JsonFile(GRAFFITI_LOOKUPS_FILE).load()
    graffiti_requests = [GraffitiServiceRequest(record) for record in graffiti_records]

    logger.info("Engineering features...")
    features = extract_features(graffiti_requests, [GRAFFITI_CLEANED_STATUS])
    feature_matrix = features[
        [
            "days_since_last_tag",
            "borough",
            "total_tags",
            "response_time",
            "created_day_of_week",
            "created_month",
            "times_reported",
            "times_cleaned",
            "resolution_velocity",
            "latitude",
            "longitude",
            "status_code",
        ]
    ]
    recurrence_targets = features["tagged_again"]
    cleaning_targets = features["cleaned"]
    time_to_next_update_targets = features["time_to_next_update"]
    recurrence_window_targets = features["recurrence_window"]
    resolution_time_targets = features["resolution_time"]

    predictor = GraffitiPredictionModel()
    predictor.train_recurrence_classifier(feature_matrix, recurrence_targets)
    predictor.train_cleaning_classifier(feature_matrix, cleaning_targets)
    predictor.train_time_regressor(feature_matrix, time_to_next_update_targets)
    predictor.train_recurrence_window_regressor(
        feature_matrix, recurrence_window_targets
    )
    predictor.train_resolution_time_regressor(
        feature_matrix, resolution_time_targets
    )

    logger.info("Making predictions and enriching data...")
    (
        recurrence_probabilities,
        cleaning_probabilities,
        time_predictions,
        recurrence_window_predictions,
        resolution_time_predictions,
    ) = predictor.predict(feature_matrix)
    enriched_data = predictor.enrich_requests(
        graffiti_requests,
        recurrence_probabilities,
        cleaning_probabilities,
        time_predictions,
        recurrence_window_predictions,
        resolution_time_predictions,
        times_reported=features["times_reported"],
        times_cleaned=features["times_cleaned"],
    )
    JsonFile(GRAFFITI_LOOKUPS_FILE).save(enriched_data)
    logger.info("Prediction enrichment complete.")


if __name__ == "__main__":
    main()

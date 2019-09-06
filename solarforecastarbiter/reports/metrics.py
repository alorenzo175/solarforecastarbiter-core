"""
To be deleted and replaced by
https://github.com/SolarArbiter/solarforecastarbiter-core/pull/102
"""
from collections import defaultdict


import numpy as np
import pandas as pd


from solarforecastarbiter import datamodel
from solarforecastarbiter.validation.quality_mapping import \
    convert_mask_into_dataframe


def validate_resample_align(report, metadata, data):
    data_validated = apply_validation(report, data)
    processed_fxobs = resample_realign(report, metadata, data_validated)
    return processed_fxobs


def apply_validation(report, data):
    data_validated = {}
    # datamodel doesn't restrict number of filters of given type
    qc_filters = [f.quality_flags for f in report.filters if
                  isinstance(f, datamodel.QualityFlagFilter)]
    for fx_or_ob, values in data.items():
        if isinstance(fx_or_ob, datamodel.Observation):
            _data_validated = values['value']
            for flags in qc_filters:
                validation_df = convert_mask_into_dataframe(
                    values['quality_flag'])
                _data_validated = (_data_validated.where(
                    ~validation_df[list(flags)].any(axis=1)))
            data_validated[fx_or_ob] = _data_validated
        else:
            # assume it's a forecast
            data_validated[fx_or_ob] = values

    return data_validated


def resample_realign(report, metadata, data):
    """Probably apply validation and other filters before this"""
    processed = []
    data_resampled = {}
    for fxobs in report.forecast_observations:
        # for now just resample to forecast
        interval_label = fxobs.forecast.interval_label
        interval_value_type = fxobs.forecast.interval_value_type
        interval_length = fxobs.forecast.interval_length
        # if this obs has not already been resampled, do it
        if fxobs.observation not in data_resampled:
            label = datamodel.CLOSED_MAPPING[interval_label]
            resampled = data[fxobs.observation].resample(
                interval_length, label=label).mean()
            data_resampled[fxobs.observation] = resampled
        # no resampling allowed for forecasts for now
        # convert tzs (GH 164)
        tz = metadata.timezone
        forecast_values = data[fxobs.forecast].tz_convert(tz)
        observation_values = data_resampled[fxobs.observation].tz_convert(tz)
        processed_fxobs = datamodel.ProcessedForecastObservation(
            original=fxobs, interval_value_type=interval_value_type,
            interval_length=interval_length, interval_label=interval_label,
            forecast_values=forecast_values,
            observation_values=observation_values)
        processed.append(processed_fxobs)
    return processed


def loop_forecasts_calculate_metrics(report, processed_fxobs):
    metrics = []
    for fxobs_ in processed_fxobs:
        metrics_ = calculate_metrics(fxobs_.original, fxobs_.forecast_values,
                                     fxobs_.observation_values)
        metrics.append(metrics_)
    return metrics


def calculate_metrics(forecast_observation, fx_values, obs_values):
    metrics = defaultdict(dict)
    metrics['name'] = forecast_observation.forecast.name
    if fx_values.empty:
        diff = pd.Series(index=obs_values.index)
    elif obs_values.empty:
        diff = pd.Series(index=fx_values.index)
    else:
        diff = fx_values - obs_values
    metrics['total']['mae'] = diff.abs().mean()
    _rmse = diff.aggregate(rmse)
    metrics['total']['rmse'] = _rmse
    metrics['total']['mbe'] = diff.mean()
    metrics['day']['mae'] = diff.abs().groupby(lambda x: x.date).mean()
    _rmse = diff.groupby(lambda x: x.date).aggregate(rmse)
    metrics['day']['rmse'] = _rmse
    metrics['day']['mbe'] = diff.groupby(lambda x: x.date).mean()
    metrics['month']['mae'] = diff.abs().groupby(lambda x: x.month).mean()
    _rmse = diff.groupby(lambda x: x.month).aggregate(rmse)
    metrics['month']['rmse'] = _rmse
    metrics['month']['mbe'] = diff.groupby(lambda x: x.month).mean()
    metrics['hour']['mae'] = diff.abs().groupby(lambda x: x.hour).mean()
    _rmse = diff.groupby(lambda x: x.hour).aggregate(rmse)
    metrics['hour']['rmse'] = _rmse
    metrics['hour']['mbe'] = diff.groupby(lambda x: x.hour).mean()
    return metrics


def rmse(diff):
    return np.sqrt((diff * diff).mean())
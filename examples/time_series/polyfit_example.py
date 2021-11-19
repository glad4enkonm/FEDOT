import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error

from fedot.core.data.data import InputData
from fedot.core.data.data_split import train_test_data_setup
from fedot.core.pipelines.node import PrimaryNode, SecondaryNode
from fedot.core.pipelines.pipeline import Pipeline
from fedot.core.repository.dataset_types import DataTypesEnum
from fedot.core.repository.tasks import Task, TaskTypesEnum, TsForecastingParams


def polyfit_pipeline(degree):
    node_polyfit = PrimaryNode('polyfit')
    node_polyfit.custom_params = {"degree": degree}
    return Pipeline(node_polyfit)


def polyfit_ridge_pipeline(degree):
    node_polyfit = PrimaryNode('polyfit')
    node_polyfit.custom_params = {"degree": degree}
    node_lagged = PrimaryNode('lagged')
    node_ridge = SecondaryNode('ridge', nodes_from=[node_lagged])
    node_ridge1 = SecondaryNode('ridge', nodes_from=[node_ridge, node_polyfit])

    return Pipeline(node_ridge1)


def run_experiment_with_polyfit(time_series, len_forecast=250,
                                degree=2):
    """ Function with example how time series trend could be approximated by a polynomial function
    for next extrapolation. Try different degree params to see a difference.

    :param time_series: time series for prediction
    :param len_forecast: forecast length
    :param degree: degree of polynomial function
    """

    # Let's divide our data on train and test samples
    task = Task(TaskTypesEnum.ts_forecasting,
                TsForecastingParams(forecast_length=len_forecast))

    train_input = InputData(idx=np.arange(0, len(time_series)),
                            features=time_series,
                            target=time_series,
                            task=task,
                            data_type=DataTypesEnum.ts)
    train_data, test_data = train_test_data_setup(train_input)

    pipeline = polyfit_pipeline(degree)
    pipeline.fit(train_data)

    predict = np.ravel(np.array(pipeline.predict(test_data).predict))
    test_target = np.ravel(test_data.target)

    rmse_before = mean_squared_error(test_target, predict, squared=False)
    mae_before = mean_absolute_error(test_target, predict)
    print(f'RMSE before tuning - {rmse_before:.4f}')
    print(f'MAE before tuning - {mae_before:.4f}\n')

    pipeline.print_structure()
    plt.plot(range(0, len(time_series)), time_series, label='Actual time series')
    plt.plot(range(len(test_data.features), len(time_series)), predict, label='Forecast with polyfit')
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == '__main__':
    df = pd.read_csv('../data/beer.csv')
    time_series = np.array(df.iloc[:, -1])
    run_experiment_with_polyfit(time_series,
                                len_forecast=50,
                                degree=2)
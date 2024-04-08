import polars as pl
import numpy as np
from sklearn.metrics import classification_report


class ExtractTime:
    @staticmethod
    def month_day(df: pl.DataFrame, col: str = 'grass_date') -> pl.DataFrame:
        return df.with_columns(
            pl.col(col).dt.year().alias('year').cast(pl.Int16),
            pl.col(col).dt.month().alias('month').cast(pl.Int8),
            pl.col(col).dt.day().alias('day').cast(pl.Int8),
        )

    @staticmethod
    def cycle_time(df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            pl.col('month').map(lambda x: np.sin(2 * np.pi * x / 12)).alias('month_sin'),
            pl.col('month').map(lambda x: np.cos(2 * np.pi * x / 12)).alias('month_cos'),
            pl.col('day').map(lambda x: np.sin(2 * np.pi * x / 31)).alias('day_sin'),
            pl.col('day').map(lambda x: np.cos(2 * np.pi * x / 31)).alias('day_cos'),
            (pl.col('month') - pl.col('day')).alias('days_dif_spike'),
        )

    @staticmethod
    def trend(df: pl.DataFrame, col: list, window: int = 7) -> pl.DataFrame:
        return df.with_columns(
            pl.col(i).rolling_mean(window).alias(f'trend_{window}d_{i}') for i in col
        )

    @staticmethod
    def season(df: pl.DataFrame, col: list, window: int = 7) -> pl.DataFrame:
        return df.with_columns(
            (pl.col(i) - pl.col(f'trend_{window}d_{i}')).alias(f'season_{window}d_{i}') for i in col
        )

    @staticmethod
    def lag(df: pl.DataFrame, col: list, window: int = 7) -> pl.DataFrame:
        return df.with_columns(
            pl.col(i).shift(window).alias(f'shift_{window}d_{i}') for i in col
        )


class Pipeline:
    def __init__(self, x_train, y_train, x_test, y_test):
        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test
        self.y_test = y_test

    @staticmethod
    def feature_importance(model_input, all_features: list, polars: bool = True) -> pl.DataFrame:
        zip_ = zip(all_features, model_input.feature_importances_)
        data = (
            pl.DataFrame(zip_, schema=['feature', '# times the feature is used'])
            .sort('# times the feature is used', descending=True)
        )
        if polars:
            return data
        else:
            return data.to_pandas()

    def lgbm(
            self,
            report: bool = True,
            params: dict = None,
    ):
        from lightgbm import LGBMClassifier, log_evaluation, early_stopping

        # params
        if not params:
            params = {
                'metric': 'auc',
                'random_state': 42,
            }
        # train
        self.lgb_model = LGBMClassifier(**params)
        self.lgb_model.fit(
            self.x_train, self.y_train,
            eval_set=[(self.x_test, self.y_test)],
            callbacks=[log_evaluation(0), early_stopping(50)]
        )
        # predict
        pred = self.lgb_model.predict(self.x_test, num_iteration=self.lgb_model.best_iteration_)
        # report
        if report:
            print(classification_report(self.y_test, pred))
        return self.lgb_model

    def xgb(
            self,
            report: bool = True,
            params: dict = None,
    ):
        from xgboost import XGBClassifier

        # params
        if not params:
            params = {
                'metric': 'auc',
                'random_state': 42,
            }
        # train
        self.xgb_model = XGBClassifier(**params)
        self.xgb_model.fit(
            self.x_train, self.y_train,
            eval_set=[(self.x_test, self.y_test)],
        )
        # predict
        pred = self.xgb_model.predict(self.x_test, num_iteration=self.xgb_model.best_iteration_)
        # report
        if report:
            print(classification_report(self.y_test, pred))
        return self.xgb_model

    def rf(self, report: bool = True, params: dict = None):
        from sklearn.ensemble import RandomForestClassifier

        # train
        self.rf_model = RandomForestClassifier()
        self.rf_model.fit(self.x_train, self.y_train)
        # predict
        pred = self.rf_model.predict(self.x_test)
        # report
        if report:
            print(classification_report(self.y_test, pred))
        return self.rf_model

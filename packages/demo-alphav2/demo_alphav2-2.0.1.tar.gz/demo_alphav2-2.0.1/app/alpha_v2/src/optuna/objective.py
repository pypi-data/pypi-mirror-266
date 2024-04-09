import xgboost as xgb
import numpy as np

from ..evaluate.evaluate import sharpe_for_vn30f

def objective_feature_vn30f(trial, X_train, X_valid, y_train, y_valid):
    """
    Return values of metrics of each trial object to find set of features for training XGBoost model.
    
    This function will create a search space that contain binary bits for each feature in input dataset. 
    The 1 bit representing for selecting that feature, otherwise it's bit 0. 
    Then the XGBoost model is trained by using selected features and evaluated by two metrics:
    - sharpe_oos: Sharpe ratio calculated on the out-of-sample (validation) dataset.
    - generalization_score: Absolute ratio of out-of-samples sharpe ratio to in-sample sharpe ratio)    
    
    Parameters
    ----------
    trial : Trial
        Optuna `Trial` object used for hyperparameter optimization.
    X_train : pd.DataFrame
        Pandas DataFrame containing features of the training dataset.
    X_valid : pd.DataFrame
        Pandas DataFrame containing features of the validation dataset.
    y_train : pd.DataFrame
        Pandas DataFrame containing target variables of the training dataset.
    y_valid : pd.DataFrame
        Pandas DataFrame containing target variables of the validation dataset.
    
    Returns
    -------
    sharpe_oos : numpy.float64
        Sharpe ratio calculated on the out-of-sample (validation) dataset.
    generalization_score : numpy.float64
        Absolute ratio of out-of-sample Sharpe ratio to in-sample Sharpe ratio.
    """
    selected_features = []
    for col in X_train.columns:
        if trial.suggest_categorical(col, [0, 1]):
            selected_features.append(col)

    X_train_selected = X_train[selected_features]
    X_valid_selected = X_valid[selected_features]

    model = xgb.XGBRegressor()
    model.fit(X_train_selected, y_train)

    y_pred_train = model.predict(X_train_selected)
    y_pred_valid = model.predict(X_valid_selected)

    _, _, _, sharpe_is = sharpe_for_vn30f(y_pred_train, y_train)
    _, _, _, sharpe_oos = sharpe_for_vn30f(y_pred_valid, y_valid)
    
    generalization_ratio = abs(sharpe_oos / sharpe_is)

    return sharpe_oos, generalization_ratio

def objective_model_vn30f(trial, X_train, X_valid, y_train, y_valid):
    """
    Return values of metrics of each trial object to find the optimized set of hyperparameters for XGBoost model.
    
    This function will create a search space for each hyperparameters in XGBoost model. 
    The 1 bit representing for selecting that feature, otherwise it's bit 0. 
    Then the XGBoost model is trained by using optimized hyperparameters and evaluated by metric:
    - sharpe_oos: Sharpe ratio calculated on the out-of-sample (validation) dataset.
    
    Parameters
    ----------
    trial : Trial
        Optuna `Trial` object used for hyperparameter optimization.
    X_train : pd.DataFrame
        Pandas DataFrame containing features of the training dataset.
    X_valid : pd.DataFrame
        Pandas DataFrame containing features of the validation dataset.
    y_train : pd.DataFrame
        Pandas DataFrame containing target variables of the training dataset.
    y_valid : pd.DataFrame
        Pandas DataFrame containing target variables of the validation dataset.
    
    Returns
    -------
    sharpe_oos : numpy.float64
        Sharpe ratio calculated on the out-of-sample (validation) dataset.
    generalization_score : numpy.float64
        Absolute ratio of out-of-sample Sharpe ratio to in-sample Sharpe ratio.
    """
    params = {
        'max_depth': trial.suggest_int('max_depth', 1, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 1.0),
        'n_estimators': 200,
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'gamma': trial.suggest_float('gamma', 0.01, 1.0),
        'subsample': trial.suggest_float('subsample', 0.01, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.01, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.01, 1.0),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.01, 1.0),
        'random_state': trial.suggest_int('random_state', 1, 1000)
    }

    model = xgb.XGBRegressor(**params)
    model.fit(X_train, y_train)
    
    y_pred_train = model.predict(X_train)
    y_pred_valid = model.predict(X_valid)
    
    _, _, _, sharpe_is = sharpe_for_vn30f(y_pred_train, y_train)
    _, _, _, sharpe_oos = sharpe_for_vn30f(y_pred_valid, y_valid)

    generalization_ratio = abs(sharpe_oos / sharpe_is)

    return sharpe_oos, generalization_ratio
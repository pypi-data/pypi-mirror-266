from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
import pandas as pd
import lightgbm as lgb
from lightgbm import early_stopping
import operator

def _prepare_xy(df, target_col, target_val, op='=='):
    ops = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne
    }
    if op not in ops:
        raise ValueError(f"Invalid comparison operator '{op}'")

    y = (ops[op](df[target_col], target_val)).astype(int)
    bool_cols = df.select_dtypes(include=['bool'])
    for col in bool_cols:
        df[col] = df[col].astype('str')
    str_cols = [col for col in df.select_dtypes(['object', 'string']).columns if col != target_col]
    for col in str_cols:
        df[col] = pd.Categorical(df[col])
    cat_cols = [col for col in df.select_dtypes('category').columns if col != target_col]
    num_cols = [col for col in df.select_dtypes('number').columns if col != target_col]
    for col in num_cols:
        df[col] = df[col].astype('float')
    X = df[cat_cols + num_cols]
    return X, y

def train_model(df, target_col, target_val, op='=='):
    X, y= _prepare_xy(df, target_col, target_val, op)

    cat_cols = list(X.select_dtypes('category').columns)
    X_trn, X_val, y_trn, y_val = train_test_split(X, y, test_size=0.2, random_state=1)
    ds_trn = lgb.Dataset(X_trn, label=y_trn, categorical_feature=cat_cols, free_raw_data=False)
    ds_val = lgb.Dataset(X_val, label=y_val, categorical_feature=cat_cols, free_raw_data=False)
    model = lgb.train(
        params={
            'verbose': -1,
            'metric': 'auc',
            'objective': 'binary'
        },
        train_set=ds_trn,
        valid_sets=[ds_val],
        callbacks=[early_stopping(5)],
    )
    return model

def evaluate_model(model, hol, target_col, target_val, op='=='):
    X_hol, y_hol = _prepare_xy(hol, target_col, target_val, op)
    probs = model.predict(X_hol)
    preds = (probs >= 0.5).astype(int)
    auc = roc_auc_score(y_hol, probs)
    acc = accuracy_score(y_hol, preds)
    out = pd.DataFrame({
          'auc': [auc],
          'acc': [acc],
        })
    return out
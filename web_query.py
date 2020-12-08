from flask import render_template, Blueprint, request
import json
import pandas as pd
import numpy as np
import joblib
import time
import gc
import warnings

warnings.filterwarnings("ignore")

app_query = Blueprint('app_query', __name__, template_folder='templates')

df = pd.read_csv('./data/model_data.csv')


@app_query.route('/query_page')
def query_page():
    return render_template('query_page.html')


@app_query.route('/get_query_info', methods=['POST'])
def get_query_info():
    guids = list(df['guid'].unique()[:5])
    return json.dumps(guids)


@app_query.route('/query', methods=['POST'])
def query():
    user = request.form['user']
    data = df[df['guid'] == user]
    predict_data = preprocessing(data)
    clf = joblib.load('./data/load_model.pkl')
    data['target'] = clf.predict_proba(predict_data)[:, 1]
    data = data.sort_values('target', ascending=False).iloc[:20, :]
    res = pd.DataFrame({
        'newsid': data['newsid'],
        'pos': data['pos'],
        'ts': data['ts'],
        'target': data['target']
    })
    return res.to_json(orient='records')


def preprocessing(df):
    df['date'] = pd.to_datetime(
        df['ts'].apply(lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x / 1000)))
    )
    df['day'] = df['date'].dt.day
    df.loc[df['day'] == 10, 'day'] = 11
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    slice_df = pd.DataFrame(df['guid'].value_counts())
    slice_df = slice_df.rename(columns={'guid': 'guid_count'})
    slice_df['id'] = np.arange(len(slice_df))
    slice_df['guid'] = slice_df.index
    slice_df.set_index('id', inplace=True)
    df = pd.merge(df, slice_df, how='left', on='guid')
    df = df.sort_values('guid_count', ascending=False).dropna(axis=0, how='any')
    df['lng_lat'] = df['lng'].astype('str') + '_' + df['lat'].astype('str')

    cate_cols = [
        'deviceid', 'newsid1', 'pos1', 'app_version', 'device_vendor',
        'netmodel', 'osversion', 'device_version', 'lng', 'lat', 'lng_lat'
    ]
    df['newsid1'] = df['newsid']
    df['pos1'] = df['pos']
    for f in cate_cols:
        map_dict = dict(zip(df[f].unique(), range(df[f].nunique())))
        df[f] = df[f].map(map_dict).fillna(-1).astype('int32')
        df[f + '_count'] = df[f].map(df[f].value_counts())
    cols = [col for col in df.columns if col not in ['guid', 'date', 'day', 'newsid', 'pos']]
    return df[cols]


def reduce_mem(df):
    start_mem = df.memory_usage().sum() / 1024 ** 2
    for col in df.columns:
        col_type = df[col].dtypes
        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
    end_mem = df.memory_usage().sum() / 1024 ** 2
    print('{:.2f} Mb, {:.2f} Mb ({:.2f} %)'.format(start_mem, end_mem, 100 * (start_mem - end_mem) / start_mem))
    gc.collect()
    return df

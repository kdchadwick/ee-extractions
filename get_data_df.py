def get_data_df(d, dateformat, collection_short_name):
    import pandas as pd
    df = pd.json_normalize(d['features'])
    df = df[df.columns[df.columns.str.contains('id')].append(df.columns[df.columns.str.contains('properties')])]
    df['id'] = pd.to_datetime(df['id'].values, format=dateformat)
    df = df.set_index('id')
    oldnames = df.columns[df.columns.str.contains('properties')]
    df.columns = list(map(lambda x: x.replace('properties.', collection_short_name),oldnames))
    return df

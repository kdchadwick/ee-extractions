import pandas as pd

def get_data_df(d, dateformat, collection_short_name, watershed):
    if watershed == True:
        df = pd.json_normalize(d['features'])
        df['id'] = df['properties.system:index']
        df['id'] = pd.to_datetime(df['id'], format= dateformat)
        df = df.set_index('id')
        df = df.drop(df.filter(regex='index').columns, axis=1)
        oldnames = df.columns[df.columns.str.contains('properties')]
        df = df[df.columns[df.columns.str.contains('properties')]]
        df.columns = list(map(lambda x: x.replace('properties.', collection_short_name),oldnames))

    else:
        df = pd.json_normalize(d['features'])
        df = df[df.columns[df.columns.str.contains('id')].append(df.columns[df.columns.str.contains('properties')])]
        df['id'] = pd.to_datetime(df['id'].values, format=dateformat)
        df = df.set_index('id')
        oldnames = df.columns[df.columns.str.contains('properties')]
        df.columns = list(map(lambda x: x.replace('properties.', collection_short_name),oldnames))

    return df
import pandas as pd
import json

def render(data):
    print(render_raw(data))


def render_raw(data):
    if isinstance(data, pd.DataFrame):
        return json.dumps(convert_dataframe_to_render_format(data))
    else:
        return


def convert_dataframe_to_render_format(df: pd.DataFrame):
    data = json.loads(df.to_json(orient="records"))
    headers = list(df.columns)
    return {"records": data, "headers": headers}
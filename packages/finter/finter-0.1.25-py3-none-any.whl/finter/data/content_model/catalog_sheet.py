import pandas as pd
import requests

from finter.ai.gpt.config import URL_NAME


def get_data():
    url = f"http://{URL_NAME}:8282/cm-catalog"
    response = requests.get(url)
    data = response.json()["data"]
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

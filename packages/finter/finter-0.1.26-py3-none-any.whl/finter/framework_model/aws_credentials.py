from finter.settings import get_api_client
from finter.rest import ApiException
import finter

import pandas as pd
import s3fs


def get_aws_credentials():
    api_instance = finter.AWSCredentialsApi(get_api_client())

    try:
        api_response = api_instance.aws_credentials_retrieve()
        return api_response
    except ApiException as e:
        print("Exception when calling AWSCredentialsApi->aws_credentials_retrieve: %s\n" % e)


def get_parquet_df(cm):

    # Currently only 3 CMs are supported
    if cm not in [
        "content.spglobal.compustat.price_volume.us-all-price_close.1d",
        "content.fnguide.ftp.price_volume.price_close.1d",
        "content.fnguide.ftp.economy.currency.1d",
    ]:
        raise ValueError("Not supported CM")

    credentials = get_aws_credentials()
    fs = s3fs.S3FileSystem(
        key=credentials.aws_access_key_id,
        secret=credentials.aws_secret_access_key,
        token=credentials.aws_session_token,
    )

    s3_bucket_name = "cm-parquet"
    file_name = f"{cm}.parquet"
    s3_uri = f"s3://{s3_bucket_name}/{file_name}"

    with fs.open(s3_uri, "rb") as f:
        df = pd.read_parquet(f, engine="pyarrow")

    return df

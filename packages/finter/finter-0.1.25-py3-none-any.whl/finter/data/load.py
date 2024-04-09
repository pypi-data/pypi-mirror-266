from finter.api.alpha_api import AlphaApi
from finter.api.content_api import ContentApi
from finter.api.flexible_fund_api import FlexibleFundApi
from finter.api.fund_api import FundApi
from finter.api.metafund_api import MetafundApi
from finter.api.portfolio_api import PortfolioApi
from finter.settings import get_api_client, logger
from finter.utils.convert import to_dataframe


class ModelData:
    @classmethod
    def load(cls, identity_name: str):
        model_type = identity_name.split(".")[0]
        if model_type == "content":
            df = cls.get_cm_df(identity_name)
        elif model_type == "alpha":
            df = cls.get_am_df(identity_name)
        elif model_type == "portfolio":
            df = cls.get_pm_df(identity_name)
        elif model_type == "fund":
            df = cls.get_fm_df(identity_name)
        elif model_type == "flexible_fund":
            df = cls.get_ffm_df(identity_name)
        elif model_type == "metafund":
            logger.error(f"Metafund model is not supported yet.")
            raise NotImplementedError
        else:
            logger.error(f"Unknown identity_name: {identity_name}")
            raise ValueError

        logger.info(f"Loading {model_type} model: {identity_name}")
        logger.info(
            "Column types not supported well yet. It will be supported soon. Please contact the developer."
        )

        return df

    @staticmethod
    def get_cm_df(identity_name):
        api_response = (
            ContentApi(get_api_client())
            .content_model_retrieve(identity_name=identity_name)
            .to_dict()
        )
        return to_dataframe(api_response["cm"], api_response["column_types"])

    @staticmethod
    def get_am_df(identity_name):
        api_response = (
            AlphaApi(get_api_client())
            .alpha_model_retrieve(identity_name=identity_name)
            .to_dict()
        )
        return to_dataframe(
            api_response["am"],  # api_response["column_types"]
        )

    @staticmethod
    def get_pm_df(identity_name):
        api_response = (
            PortfolioApi(get_api_client())
            .portfolio_model_retrieve(identity_name=identity_name)
            .to_dict()
        )
        return to_dataframe(
            api_response["pm"],  # api_response["column_types"]
        )

    @staticmethod
    def get_fm_df(identity_name):
        api_response = (
            FundApi(get_api_client())
            .fund_model_retrieve(identity_name=identity_name)
            .to_dict()
        )
        return to_dataframe(
            api_response["fm"],  # api_response["column_types"]
        )

    @staticmethod
    def get_ffm_df(identity_name):
        api_response = (
            FlexibleFundApi(get_api_client())
            .flexiblefund_model_retrieve(identity_name=identity_name)
            .to_dict()
        )
        return to_dataframe(
            api_response["ffm"],  # api_response["column_types"]
        )

    # @staticmethod
    # def get_mfm_df(identity_name):
    #     api_response = (
    #         MetafundApi(get_api_client())
    #         .metafund_model_retrieve(metafund_name=identity_name)
    #         .to_dict()
    #     )
    #     return to_dataframe(
    #         api_response["mfm"],  # api_response["column_types"]
    #     )


if __name__ == "__main__":
    # ModelData.load(identity_name="content.fnguide.ftp.economy.currency.1d")
    # df = ModelData.load(identity_name="alpha.krx.krx.stock.ldh0127.div_2")
    # df = ModelData.load(identity_name="portfolio.krx.krx.stock.ldh0127.div_1")
    # df = ModelData.load(identity_name="flexible_fund.krx.krx.stock.ldh0127.ipo_event")
    df = ModelData.load(identity_name="fund.krx.krx.stock.soobeom33.cs_fund_2")

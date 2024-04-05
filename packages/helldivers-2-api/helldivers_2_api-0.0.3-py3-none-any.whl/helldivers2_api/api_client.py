import logging
from typing import Optional

from helldivers2_api.api_version import API_VERSION
from helldivers2_api.endpoint_map import ENDPOINT_MAP
from helldivers2_api.news import News
from helldivers2_api.war_status import WarStatus
from helldivers2_api.mapping_strategy import get_mapping_strategy_for_api_version


class ApiError(Exception):
    """ Catch-all exception if something went wrong, to be refined later """

    def __init__(self, original_error: Exception) -> None:
        logging.exception("Something went wrong: ", exc_info=original_error)


class ApiClient:
    def __init__(self, used_api: API_VERSION = API_VERSION.OFFICIAL) -> None:
        self._used_api = used_api
        self._base_endpoint = str(used_api.value)
        self._mapping_strategy = get_mapping_strategy_for_api_version(used_api)

    @property
    def active_api_version(self) -> API_VERSION:
        return self._used_api

    def get_war_status(self, war_id: Optional[int] = None) -> WarStatus:
        """
        Retrieves the current war status
        :param war_id: Optionally define which war to get the status from. If None, the latest war is used.
        :return: A WarStatus object.
        """
        try:
            war_status_data = self._mapping_strategy.make_and_parse_request(
                self._base_endpoint,
                ENDPOINT_MAP[self._used_api]["war_status"],
                [str(self.get_current_war_id())] if not war_id else [str(war_id)]
            )
        except Exception as err:
            raise ApiError(err)

        return self._mapping_strategy.get_war_status(war_status_data)

    def get_current_war_id(self) -> int:
        try:
            war_id_data = self._mapping_strategy.make_and_parse_request(
                self._base_endpoint,
                ENDPOINT_MAP[self._used_api]["current_war_id"],
                []
            )
        except Exception as err:
            raise ApiError(err)

        return self._mapping_strategy.get_current_war_id(war_id_data)

    def get_news(self) -> list[News]:
        try:
            news_feed_data = self._mapping_strategy.make_and_parse_request(
                self._base_endpoint,
                ENDPOINT_MAP[self._used_api]["news_feed"],
                [] if self._used_api == API_VERSION.HELLDIVERS_TRAINING_MANUAL_V1 else [str(self.get_current_war_id())]
            )
        except Exception as err:
            raise ApiError(err)

        return self._mapping_strategy.get_news(news_feed_data)

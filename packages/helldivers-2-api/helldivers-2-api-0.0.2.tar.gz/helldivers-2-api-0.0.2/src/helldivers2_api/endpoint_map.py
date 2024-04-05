from helldivers2_api.api_version import API_VERSION

ENDPOINT_MAP = {
    API_VERSION.HELLDIVERS_TRAINING_MANUAL_V1: {
        "war_status": "/war/status",
        "current_war_id": "/war/info",
        "news_feed": "/war/news"

    },
    API_VERSION.OFFICIAL: {
        "war_status": "/WarSeason/PARAM1/Status",
        "current_war_id": "/WarSeason/current/WarID",
        "news_feed": "/NewsFeed/PARAM1"
    }
}

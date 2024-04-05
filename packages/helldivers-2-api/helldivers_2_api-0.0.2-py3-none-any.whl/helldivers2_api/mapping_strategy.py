import json
import logging
from abc import ABC, abstractmethod
from typing import Union

import requests

from helldivers2_api.joint_operation import JointOperation
from helldivers2_api.news import News
from helldivers2_api.planet_event import PlanetEvent, PlanetEventType
from helldivers2_api.planet_info_table import get_planet_by_id
from helldivers2_api.api_version import API_VERSION
from helldivers2_api.campaign import Campaign
from helldivers2_api.faction import Faction
from helldivers2_api.global_event import GlobalEvent
from helldivers2_api.planet_attack import PlanetAttack
from helldivers2_api.planet_status import PlanetStatus
from helldivers2_api.war_status import WarStatus


class Strategy(ABC):
    """
    The base strategy interface for all mapping strategies
    """

    @abstractmethod
    def get_war_status(self, data: dict) -> WarStatus:
        pass

    @abstractmethod
    def get_current_war_id(self, data: dict) -> int:
        pass

    @abstractmethod
    def get_news(self, data: dict) -> list[News]:
        pass

    @abstractmethod
    def make_and_parse_request(self, base: str, endpoint: str, params: list[str]) -> dict:
        pass


class HDTMStrategy(Strategy):
    def get_war_status(self, data: dict) -> WarStatus:
        campaigns = [Campaign(
            count=campaign["count"],
            campaign_id=campaign["id"],
            planet_index=campaign["planetIndex"],
            campaign_type=campaign["type"]
        ) for campaign in data["campaigns"]]

        global_events = [GlobalEvent(
            assignment_id=global_event["assignmentId32"],
            effect_ids=global_event["effectIds"],
            event_id=global_event["eventId"],
            flag=global_event["flag"],
            id32=global_event["id32"],
            message=global_event["message"],
            message_id=global_event["messageId32"],
            affected_planets=global_event["planetIndices"],
            portrait_id=global_event["portraitId32"],
            race=Faction(global_event["race"]),
            title=global_event["title"],
            title_id=global_event["titleId32"]
        ) for global_event in data["globalEvents"]]

        planet_attacks = [PlanetAttack(
            source_planet_id=planet_attack["source"],
            target_planet_id=planet_attack["target"]
        ) for planet_attack in data["planetAttacks"]]

        planet_status = [PlanetStatus(
            planet_id=planet_status["index"],
            planet_info=get_planet_by_id(planet_status["index"]),
            health=planet_status["health"],
            owner=Faction(planet_status["owner"]),
            players=planet_status["players"],
            regen_per_second=planet_status["regenPerSecond"]
        ) for planet_status in data["planetStatus"]]

        return WarStatus(
            active_election_policy_effects=data["activeElectionPolicyEffects"],
            campaigns=campaigns,
            community_targets=data["communityTargets"],
            global_events=global_events,
            impact_multiplier=data["impactMultiplier"],
            joint_operations=[JointOperation(
                hq_node_index=joint_operation["hqNodeIndex"],
                joint_operation_id=joint_operation["id"],
                planet_index=joint_operation["planetIndex"]
            ) for joint_operation in data["jointOperations"]],
            planet_active_effects=data["planetActiveEffects"],
            planet_attacks=planet_attacks,
            planet_events=[PlanetEvent(
                campaign_id=planet_event["campaignId"],
                event_type=PlanetEventType(planet_event["eventType"]),
                expire_time=planet_event["expireTime"],
                health=planet_event["health"],
                event_id=planet_event["id"],
                joint_operation_ids=planet_event["jointOperationIds"],
                max_health=planet_event["maxHealth"],
                planet_index=planet_event["planetIndex"],
                faction=Faction(planet_event["race"]),
                start_time=planet_event["startTime"],
            ) for planet_event in data["planetEvents"]],
            planet_status=planet_status,
            story_beat_id=data["storyBeatId32"],
            super_earth_war_results=data["superEarthWarResults"],
            time=data["time"],
            war_id=data["warId"]
        )

    def get_current_war_id(self, data: dict) -> int:
        return data["warId"]

    def get_news(self, data: dict) -> list[News]:
        return [
            News(
                news_id=raw_news["id"],
                published=raw_news["published"],
                type=raw_news["type"],
                tagIds=raw_news["tagIds"],
                message=raw_news["message"]
            ) for raw_news in data
        ]

    def make_and_parse_request(self, base: str, endpoint: str, params: list[str]) -> dict:
        r = requests.get(f"{base}{endpoint}")
        if r.status_code != 200:
            logging.error(f"Request to endpoint '{endpoint}' resulted in status code {r.status_code}")
            raise ConnectionError
        return json.loads(r.content)


class OfficialStrategy(Strategy):
    REQUEST_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "Accept-Encoding": "gzip",
        "Accept-Language": "en-US,en;q=0.5"
    }

    def get_war_status(self, data: dict) -> WarStatus:
        campaigns = [Campaign(
            count=campaign["count"],
            campaign_id=campaign["id"],
            planet_index=campaign["planetIndex"],
            campaign_type=campaign["type"]
        ) for campaign in data["campaigns"]]

        global_events = [GlobalEvent(
            assignment_id=global_event["assignmentId32"],
            effect_ids=global_event["effectIds"],
            event_id=global_event["eventId"],
            flag=global_event["flag"],
            id32=global_event["id32"],
            message=global_event["message"],
            message_id=global_event["messageId32"],
            affected_planets=global_event["planetIndices"],
            portrait_id=global_event["portraitId32"],
            race=Faction(global_event["race"]),
            title=global_event["title"],
            title_id=global_event["titleId32"]
        ) for global_event in data["globalEvents"]]

        planet_attacks = [PlanetAttack(
            source_planet_id=planet_attack["source"],
            target_planet_id=planet_attack["target"]
        ) for planet_attack in data["planetAttacks"]]

        planet_status = [PlanetStatus(
            planet_id=planet_status["index"],
            planet_info=get_planet_by_id(planet_status["index"]),
            health=planet_status["health"],
            owner=Faction(planet_status["owner"]),
            players=planet_status["players"],
            regen_per_second=planet_status["regenPerSecond"]
        ) for planet_status in data["planetStatus"]]

        return WarStatus(
            active_election_policy_effects=data["activeElectionPolicyEffects"],
            campaigns=campaigns,
            community_targets=data["communityTargets"],
            global_events=global_events,
            impact_multiplier=data["impactMultiplier"],
            joint_operations=[JointOperation(
                hq_node_index=joint_operation["hqNodeIndex"],
                joint_operation_id=joint_operation["id"],
                planet_index=joint_operation["planetIndex"]
            ) for joint_operation in data["jointOperations"]],
            planet_active_effects=data["planetActiveEffects"],
            planet_attacks=planet_attacks,
            planet_events=[PlanetEvent(
                campaign_id=planet_event["campaignId"],
                event_type=PlanetEventType(planet_event["eventType"]),
                expire_time=planet_event["expireTime"],
                health=planet_event["health"],
                event_id=planet_event["id"],
                joint_operation_ids=planet_event["jointOperationIds"],
                max_health=planet_event["maxHealth"],
                planet_index=planet_event["planetIndex"],
                faction=Faction(planet_event["race"]),
                start_time=planet_event["startTime"],
            ) for planet_event in data["planetEvents"]],
            planet_status=planet_status,
            story_beat_id=data["storyBeatId32"],
            super_earth_war_results=data["superEarthWarResults"],
            time=data["time"],
            war_id=data["warId"]
        )

    def get_current_war_id(self, data: dict) -> int:
        return data["id"]

    def get_news(self, data: dict) -> list[News]:
        return [
            News(
                news_id=raw_news["id"],
                published=raw_news["published"],
                type=raw_news["type"],
                tagIds=raw_news["tagIds"],
                message=raw_news["message"]
            ) for raw_news in data
        ]

    def make_and_parse_request(self, base: str, endpoint: str, params: list[str]) -> dict:
        url = f"{base}{endpoint}"
        for idx, param in enumerate(params):
            url = url.replace(f"PARAM{idx+1}", param.strip())

        r = requests.get(url, headers=self.REQUEST_HEADERS)
        if r.status_code != 200:
            logging.error(f"Request to endpoint '{endpoint}' resulted in status code {r.status_code}")
            raise ConnectionError
        return json.loads(r.content)


def get_mapping_strategy_for_api_version(api_version: API_VERSION) -> Union[HDTMStrategy, OfficialStrategy]:
    if api_version == API_VERSION.HELLDIVERS_TRAINING_MANUAL_V1:
        return HDTMStrategy()
    elif api_version == API_VERSION.OFFICIAL:
        return OfficialStrategy()

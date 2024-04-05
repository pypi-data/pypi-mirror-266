from typing import Union

from helldivers2_api.planet import Planet
from helldivers2_api.sector import Sector

PLANET_INFO_TABLE: dict = {
    "0": {
        "name": "Super Earth",
        "sector": "Sol",
        "biome": None,
        "environmentals": []
    },
    "1": {
        "name": "Klen Dahth II",
        "sector": "Altus",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "2": {
        "name": "Pathfinder V",
        "sector": "Altus",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "3": {
        "name": "Widow's Harbor",
        "sector": "Altus",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "4": {
        "name": "New Haven",
        "sector": "Altus",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "5": {
        "name": "Pilen V",
        "sector": "Altus",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "6": {
        "name": "Hydrofall Prime",
        "sector": "Barnard",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "7": {
        "name": "Zea Rugosia",
        "sector": "Ferris",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "8": {
        "name": "Darrowsport",
        "sector": "Barnard",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "9": {
        "name": "Fornskogur II",
        "sector": "Barnard",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "10": {
        "name": "Midasburg",
        "sector": "Barnard",
        "biome": None,
        "environmentals": []
    },
    "11": {
        "name": "Cerberus IIIc",
        "sector": "Cancri",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "12": {
        "name": "Prosperity Falls",
        "sector": "Cancri",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "13": {
        "name": "Okul VI",
        "sector": "Gothmar",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "14": {
        "name": "Martyr's Bay",
        "sector": "Cantolus",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "15": {
        "name": "Freedom Peak",
        "sector": "Cantolus",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "16": {
        "name": "Fort Union",
        "sector": "Orion",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "17": {
        "name": "Kelvinor",
        "sector": "Cantolus",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "18": {
        "name": "Wraith",
        "sector": "Idun",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "19": {
        "name": "Igla",
        "sector": "Kelvin",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "20": {
        "name": "New Kiruna",
        "sector": "Kelvin",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "21": {
        "name": "Fort Justice",
        "sector": "Kelvin",
        "biome": None,
        "environmentals": []
    },
    "22": {
        "name": "Zegema Paradise",
        "sector": "Kelvin",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "23": {
        "name": "Providence",
        "sector": "Iptus",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "24": {
        "name": "Primordia",
        "sector": "Iptus",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "25": {
        "name": "Sulfura",
        "sector": "Celeste",
        "biome": {
            "slug": "ethereal",
            "description": "This world teems with ethereal, boundless, and peculiar plant life that spreads silent "
                           "and uninterrupted across its entire surface."
        },
        "environmentals": []
    },
    "26": {
        "name": "Nublaria I",
        "sector": "Celeste",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "27": {
        "name": "Krakatwo",
        "sector": "Celeste",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "28": {
        "name": "Volterra",
        "sector": "Korpus",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "29": {
        "name": "Crucible",
        "sector": "Korpus",
        "biome": None,
        "environmentals": []
    },
    "30": {
        "name": "Veil",
        "sector": "Barnard",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "31": {
        "name": "Marre IV",
        "sector": "Barnard",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "32": {
        "name": "Fort Sanctuary",
        "sector": "Cancri",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "33": {
        "name": "Seyshel Beach",
        "sector": "Cancri",
        "biome": {
            "slug": "ethereal",
            "description": "This world teems with ethereal, boundless, and peculiar plant life that spreads silent "
                           "and uninterrupted across its entire surface."
        },
        "environmentals": []
    },
    "34": {
        "name": "Hellmire",
        "sector": "Mirin",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "35": {
        "name": "Effluvia",
        "sector": "Cancri",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "36": {
        "name": "Solghast",
        "sector": "Gothmar",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "37": {
        "name": "Diluvia",
        "sector": "Gothmar",
        "biome": None,
        "environmentals": []
    },
    "38": {
        "name": "Viridia Prime",
        "sector": "Cantolus",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "39": {
        "name": "Obari",
        "sector": "Cantolus",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "40": {
        "name": "Myradesh",
        "sector": "Idun",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "41": {
        "name": "Atrama",
        "sector": "Idun",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "42": {
        "name": "Emeria",
        "sector": "Kelvin",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "43": {
        "name": "Barabos",
        "sector": "Marspira",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "44": {
        "name": "Fenmire",
        "sector": "Marspira",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "45": {
        "name": "Mastia",
        "sector": "Marspira",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "46": {
        "name": "Shallus",
        "sector": "Talus",
        "biome": {
            "slug": "ethereal",
            "description": "This world teems with ethereal, boundless, and peculiar plant life that spreads silent "
                           "and uninterrupted across its entire surface."
        },
        "environmentals": []
    },
    "47": {
        "name": "Krakabos",
        "sector": "Iptus",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "48": {
        "name": "Iridica",
        "sector": "Iptus",
        "biome": {
            "slug": "ethereal",
            "description": "This world teems with ethereal, boundless, and peculiar plant life that spreads silent"
                           "and uninterrupted across its entire surface."
        },
        "environmentals": []
    },
    "49": {
        "name": "Azterra",
        "sector": "Orion",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally"
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "50": {
        "name": "Azur Secundus",
        "sector": "Sten",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "51": {
        "name": "Ivis",
        "sector": "Celeste",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its"
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "52": {
        "name": "Slif",
        "sector": "Celeste",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "53": {
        "name": "Caramoor",
        "sector": "Korpus",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "54": {
        "name": "Kharst",
        "sector": "Gallux",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "55": {
        "name": "Eukoria",
        "sector": "Morgon",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "56": {
        "name": "Myrium",
        "sector": "Morgon",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "57": {
        "name": "Kerth Secundus",
        "sector": "Rictus",
        "biome": None,
        "environmentals": []
    },
    "58": {
        "name": "Parsh",
        "sector": "Rictus",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "59": {
        "name": "Reaf",
        "sector": "Saleria",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "60": {
        "name": "Irulta",
        "sector": "Saleria",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "61": {
        "name": "Emorath",
        "sector": "Meridian",
        "biome": None,
        "environmentals": []
    },
    "62": {
        "name": "Ilduna Prime",
        "sector": "Meridian",
        "biome": None,
        "environmentals": []
    },
    "63": {
        "name": "Maw",
        "sector": "Idun",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            }
        ]
    },
    "64": {
        "name": "Meridia",
        "sector": "Umlaut",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "65": {
        "name": "Borea",
        "sector": "Sagan",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "66": {
        "name": "Curia",
        "sector": "Marspira",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "67": {
        "name": "Tarsh",
        "sector": "Marspira",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "68": {
        "name": "Shelt",
        "sector": "Talus",
        "biome": None,
        "environmentals": []
    },
    "69": {
        "name": "Imber",
        "sector": "Talus",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "70": {
        "name": "Blistica",
        "sector": "Gellert",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "71": {
        "name": "Ratch",
        "sector": "Iptus",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "72": {
        "name": "Julheim",
        "sector": "Nanos",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "73": {
        "name": "Valgaard",
        "sector": "Iptus",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "74": {
        "name": "Arkturus",
        "sector": "Arturion",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "75": {
        "name": "Esker",
        "sector": "Falstaff",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "76": {
        "name": "Terrek",
        "sector": "Orion",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "77": {
        "name": "Cirrus",
        "sector": "Orion",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "78": {
        "name": "Crimsica",
        "sector": "Draco",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "79": {
        "name": "Heeth",
        "sector": "Orion",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "80": {
        "name": "Veld",
        "sector": "Orion",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "81": {
        "name": "Alta V",
        "sector": "Korpus",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall"
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "82": {
        "name": "Ursica XI",
        "sector": "Borgus",
        "biome": None,
        "environmentals": []
    },
    "83": {
        "name": "Inari",
        "sector": "Korpus",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "84": {
        "name": "Skaash",
        "sector": "Ursa",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "85": {
        "name": "Moradesh",
        "sector": "Celeste",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "86": {
        "name": "Rasp",
        "sector": "Gallux",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "87": {
        "name": "Bashyr",
        "sector": "Gallux",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "88": {
        "name": "Regnus",
        "sector": "Morgon",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "89": {
        "name": "Mog",
        "sector": "Morgon",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "90": {
        "name": "Valmox",
        "sector": "Rictus",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "91": {
        "name": "Iro",
        "sector": "Rictus",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "92": {
        "name": "Grafmere",
        "sector": "Rictus",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "93": {
        "name": "New Stockholm",
        "sector": "Hanzo",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "94": {
        "name": "Oasis",
        "sector": "Rictus",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "95": {
        "name": "Genesis Prime",
        "sector": "Rictus",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "96": {
        "name": "Outpost 32",
        "sector": "Saleria",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "97": {
        "name": "Calypso",
        "sector": "Saleria",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "98": {
        "name": "Elysian Meadows",
        "sector": "Guang",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "99": {
        "name": "Alderidge Cove",
        "sector": "Guang",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "100": {
        "name": "Trandor",
        "sector": "Sten",
        "biome": {
            "slug": "tundra",
            "description": "A perenially chilly climate has allowed short, colourful shrubs to flourish across this "
                           "planet's surface."
        },
        "environmentals": []
    },
    "101": {
        "name": "East Iridium Trading Bay",
        "sector": "Tarragon",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "102": {
        "name": "Liberty Ridge",
        "sector": "Meridian",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "103": {
        "name": "Baldrick Prime",
        "sector": "Meridian",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "104": {
        "name": "The Weir",
        "sector": "Theseus",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "105": {
        "name": "Kuper",
        "sector": "Theseus",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "106": {
        "name": "Oslo Station",
        "sector": "Sagan",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "107": {
        "name": "P\u00f6pli IX",
        "sector": "Xzar",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "108": {
        "name": "Gunvald",
        "sector": "Sagan",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "109": {
        "name": "Dolph",
        "sector": "Nanos",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "110": {
        "name": "Bekvam III",
        "sector": "Nanos",
        "biome": None,
        "environmentals": []
    },
    "111": {
        "name": "Duma Tyr",
        "sector": "Nanos",
        "biome": None,
        "environmentals": []
    },
    "112": {
        "name": "Vernen Wells",
        "sector": "Hydra",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "113": {
        "name": "Aesir Pass",
        "sector": "Hydra",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "114": {
        "name": "Aurora Bay",
        "sector": "Valdis",
        "biome": {
            "slug": "tundra",
            "description": "A perenially chilly climate has allowed short, colourful shrubs to flourish across this "
                           "planet's surface."
        },
        "environmentals": []
    },
    "115": {
        "name": "Penta",
        "sector": "Lacaille",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "116": {
        "name": "Gaellivare",
        "sector": "Talus",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "117": {
        "name": "Vog-sojoth",
        "sector": "Tanis",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "118": {
        "name": "Kirrik",
        "sector": "Arturion",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "119": {
        "name": "Mortax Prime",
        "sector": "Arturion",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "120": {
        "name": "Wilford Station",
        "sector": "Arturion",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "121": {
        "name": "Pioneer II",
        "sector": "Arturion",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "122": {
        "name": "Erson Sands",
        "sector": "Falstaff",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "123": {
        "name": "Socorro III",
        "sector": "Falstaff",
        "biome": None,
        "environmentals": []
    },
    "124": {
        "name": "Bore Rock",
        "sector": "Falstaff",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "125": {
        "name": "Fenrir III",
        "sector": "Umlaut",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "126": {
        "name": "Turing",
        "sector": "Umlaut",
        "biome": {
            "slug": "ethereal",
            "description": "This world teems with ethereal, boundless, and peculiar plant life that spreads silent "
                           "and uninterrupted across its entire surface."
        },
        "environmentals": []
    },
    "127": {
        "name": "Angel's Venture",
        "sector": "Orion",
        "biome": {
            "slug": "tundra",
            "description": "A perenially chilly climate has allowed short, colourful shrubs to flourish across this "
                           "planet's surface."
        },
        "environmentals": []
    },
    "128": {
        "name": "Darius II",
        "sector": "Borgus",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "129": {
        "name": "Acamar IV",
        "sector": "Jin Xi",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "130": {
        "name": "Achernar Secundus",
        "sector": "Borgus",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "131": {
        "name": "Achird III",
        "sector": "Borgus",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "132": {
        "name": "Acrab XI",
        "sector": "Ursa",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "133": {
        "name": "Acrux IX",
        "sector": "Ursa",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "134": {
        "name": "Acubens Prime",
        "sector": "Gallux",
        "biome": None,
        "environmentals": []
    },
    "135": {
        "name": "Adhara",
        "sector": "Gallux",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "136": {
        "name": "Afoyay Bay",
        "sector": "Gallux",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland"
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "137": {
        "name": "Ain-5",
        "sector": "Hanzo",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from"
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "138": {
        "name": "Alairt III",
        "sector": "Hanzo",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "139": {
        "name": "Alamak VII",
        "sector": "Hanzo",
        "biome": None,
        "environmentals": []
    },
    "140": {
        "name": "Alaraph",
        "sector": "Akira",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "141": {
        "name": "Alathfar XI",
        "sector": "Akira",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "142": {
        "name": "Andar",
        "sector": "Akira",
        "biome": None,
        "environmentals": []
    },
    "143": {
        "name": "Asperoth Prime",
        "sector": "Akira",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of"
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "144": {
        "name": "Bellatrix",
        "sector": "Guang",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "145": {
        "name": "Botein",
        "sector": "Guang",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "146": {
        "name": "Osupsam",
        "sector": "Tarragon",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "147": {
        "name": "Brink-2",
        "sector": "Tarragon",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "148": {
        "name": "Bunda Secundus",
        "sector": "Tarragon",
        "biome": None,
        "environmentals": []
    },
    "149": {
        "name": "Canopus",
        "sector": "Tarragon",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "150": {
        "name": "Caph",
        "sector": "Theseus",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "151": {
        "name": "Castor",
        "sector": "Theseus",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "152": {
        "name": "Durgen",
        "sector": "Severin",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "153": {
        "name": "Draupnir",
        "sector": "Xzar",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "154": {
        "name": "Mort",
        "sector": "Xzar",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "155": {
        "name": "Ingmar",
        "sector": "Xzar",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "156": {
        "name": "Charbal-VII",
        "sector": "Andromeda",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "157": {
        "name": "Charon Prime",
        "sector": "Andromeda",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            }
        ]
    },
    "158": {
        "name": "Choepessa IV",
        "sector": "Trigon",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "159": {
        "name": "Choohe",
        "sector": "Lacaille",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "160": {
        "name": "Chort Bay",
        "sector": "Lacaille",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "161": {
        "name": "Claorell",
        "sector": "Tanis",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "162": {
        "name": "Clasa",
        "sector": "Tanis",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "163": {
        "name": "Demiurg",
        "sector": "Tanis",
        "biome": {
            "slug": "tundra",
            "description": "A perenially chilly climate has allowed short, colourful shrubs to flourish across this "
                           "planet's surface."
        },
        "environmentals": []
    },
    "164": {
        "name": "Deneb Secundus",
        "sector": "Arturion",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "165": {
        "name": "Electra Bay",
        "sector": "Arturion",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "166": {
        "name": "Enuliale",
        "sector": "L'estrade",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "167": {
        "name": "Epsilon Phoencis VI",
        "sector": "L'estrade",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "168": {
        "name": "Erata Prime",
        "sector": "Umlaut",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "169": {
        "name": "Estanu",
        "sector": "Draco",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "170": {
        "name": "Fori Prime",
        "sector": "Draco",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "171": {
        "name": "Gacrux",
        "sector": "Jin Xi",
        "biome": None,
        "environmentals": []
    },
    "172": {
        "name": "Gar Haren",
        "sector": "Jin Xi",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "173": {
        "name": "Gatria",
        "sector": "Jin Xi",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "174": {
        "name": "Gemma",
        "sector": "Ursa",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "175": {
        "name": "Grand Errant",
        "sector": "Farsight",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "176": {
        "name": "Hadar",
        "sector": "Ferris",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "177": {
        "name": "Haka",
        "sector": "Leo",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "178": {
        "name": "Haldus",
        "sector": "Ferris",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "179": {
        "name": "Halies Port",
        "sector": "Leo",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "180": {
        "name": "Herthon Secundus",
        "sector": "Ferris",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "181": {
        "name": "Hesoe Prime",
        "sector": "Rigel",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "182": {
        "name": "Heze Bay",
        "sector": "Hanzo",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "183": {
        "name": "Hort",
        "sector": "Rigel",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "184": {
        "name": "Hydrobius",
        "sector": "Omega",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "185": {
        "name": "Karlia",
        "sector": "Omega",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "186": {
        "name": "Keid",
        "sector": "Akira",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "187": {
        "name": "Khandark",
        "sector": "Guang",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "188": {
        "name": "Klaka 5",
        "sector": "Alstrad",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "189": {
        "name": "Kneth Port",
        "sector": "Alstrad",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "190": {
        "name": "Kraz",
        "sector": "Alstrad",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "191": {
        "name": "Kuma",
        "sector": "Hawking",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "192": {
        "name": "Lastofe",
        "sector": "Theseus",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "193": {
        "name": "Leng Secundus",
        "sector": "Quintus",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "194": {
        "name": "Lesath",
        "sector": "Lacaille",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "195": {
        "name": "Maia",
        "sector": "Severin",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "196": {
        "name": "Malevelon Creek",
        "sector": "Severin",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "197": {
        "name": "Mantes",
        "sector": "Xzar",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "198": {
        "name": "Marfark",
        "sector": "Andromeda",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "199": {
        "name": "Martale",
        "sector": "Andromeda",
        "biome": None,
        "environmentals": []
    },
    "200": {
        "name": "Matar Bay",
        "sector": "Andromeda",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "201": {
        "name": "Meissa",
        "sector": "Ymir",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "202": {
        "name": "Mekbuda",
        "sector": "Valdis",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "203": {
        "name": "Menkent",
        "sector": "Hydra",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "204": {
        "name": "Merak",
        "sector": "Valdis",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "205": {
        "name": "Merga IV",
        "sector": "Valdis",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "206": {
        "name": "Minchir",
        "sector": "Gellert",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "207": {
        "name": "Mintoria",
        "sector": "Gellert",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "208": {
        "name": "Mordia 9",
        "sector": "Hawking",
        "biome": {
            "slug": "ethereal",
            "description": "This world teems with ethereal, boundless, and peculiar plant life that spreads silent "
                           "and uninterrupted across its entire surface."
        },
        "environmentals": []
    },
    "209": {
        "name": "Nabatea Secundus",
        "sector": "L'estrade",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "210": {
        "name": "Navi VII",
        "sector": "L'estrade",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "211": {
        "name": "Nivel 43",
        "sector": "Mirin",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "212": {
        "name": "Oshaune",
        "sector": "Mirin",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "213": {
        "name": "Overgoe Prime",
        "sector": "Sten",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "214": {
        "name": "Pandion-XXIV",
        "sector": "Jin Xi",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "215": {
        "name": "Partion",
        "sector": "Sten",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "216": {
        "name": "Peacock",
        "sector": "Sten",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "217": {
        "name": "Phact Bay",
        "sector": "Jin Xi",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "218": {
        "name": "Pherkad Secundus",
        "sector": "Farsight",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "219": {
        "name": "Polaris Prime",
        "sector": "Farsight",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "220": {
        "name": "Pollux 31",
        "sector": "Farsight",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "221": {
        "name": "Prasa",
        "sector": "Farsight",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "222": {
        "name": "Propus",
        "sector": "Leo",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "223": {
        "name": "Ras Algethi",
        "sector": "Leo",
        "biome": None,
        "environmentals": []
    },
    "224": {
        "name": "RD-4",
        "sector": "Rigel",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "225": {
        "name": "Rogue 5",
        "sector": "Rigel",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "226": {
        "name": "Rirga Bay",
        "sector": "Rigel",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "227": {
        "name": "Seasse",
        "sector": "Omega",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "228": {
        "name": "Senge 23",
        "sector": "Omega",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "229": {
        "name": "Setia",
        "sector": "Omega",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "230": {
        "name": "Shete",
        "sector": "Xi Tauri",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "231": {
        "name": "Siemnot",
        "sector": "Xi Tauri",
        "biome": {
            "slug": "rainforest",
            "description": "The strange subversion of photosynthesis that sustains the oddly-hued flora that "
                           "flourishes on this planet remains an intriguing mystery to Super Earth's greatest "
                           "exo-biologists."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "232": {
        "name": "Sirius",
        "sector": "Xi Tauri",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "233": {
        "name": "Skat Bay",
        "sector": "Xi Tauri",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "234": {
        "name": "Spherion",
        "sector": "Quintus",
        "biome": {
            "slug": "jungle",
            "description": "Abundant with life, this wet planet is covered in deep oceans, thick forests, and tall "
                           "grasses."
        },
        "environmentals": [
            {
                "name": "Volcanic Activity",
                "description": "Volcanoes throw burning rocks around this planet"
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "235": {
        "name": "Stor Tha Prime",
        "sector": "Quintus",
        "biome": {
            "slug": "icemoss",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            }
        ]
    },
    "236": {
        "name": "Stout",
        "sector": "Quintus",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "237": {
        "name": "Termadon",
        "sector": "Quintus",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "238": {
        "name": "Tibit",
        "sector": "Severin",
        "biome": {
            "slug": "ethereal",
            "description": "This world teems with ethereal, boundless, and peculiar plant life that spreads silent "
                           "and uninterrupted across its entire surface."
        },
        "environmentals": []
    },
    "239": {
        "name": "Tien Kwan",
        "sector": "Theseus",
        "biome": {
            "slug": "icemoss-special",
            "description": "Ice and moss-covered rock can be found across most of the surface of this planet."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "240": {
        "name": "Troost",
        "sector": "Trigon",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "241": {
        "name": "Ubanea",
        "sector": "Severin",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "242": {
        "name": "Ustotu",
        "sector": "Trigon",
        "biome": {
            "slug": "desert",
            "description": "A desert planet prone to unpredictable and dangerous,sand twisters."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    },
    "243": {
        "name": "Vandalon IV",
        "sector": "Trigon",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "244": {
        "name": "Varylia 5",
        "sector": "Trigon",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "245": {
        "name": "Wasat",
        "sector": "Ymir",
        "biome": None,
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Acid Storms",
                "description": "Violent acid storms reduce visibility"
            }
        ]
    },
    "246": {
        "name": "Vega Bay",
        "sector": "Ymir",
        "biome": {
            "slug": "winter",
            "description": "Submerged in eternal winter, this world's frosty peaks glimmer in the light of its "
                           "too-distant star."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Blizzards",
                "description": ""
            }
        ]
    },
    "247": {
        "name": "Wezen",
        "sector": "Ymir",
        "biome": {
            "slug": "desolate",
            "description": "Scorching temperatures, high winds, and low precipitation cause a near-constant cycle of "
                           "fires to sweep this planet, punctuated by short bursts of lush rebirth between infernos."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Fire Tornadoes",
                "description": "Planet is ravaged by deadly fire tornadoes"
            }
        ]
    },
    "248": {
        "name": "Vindemitarix Prime",
        "sector": "Valdis",
        "biome": {
            "slug": "ethereal",
            "description": "This world teems with ethereal, boundless, and peculiar plant life that spreads silent "
                           "and uninterrupted across its entire surface."
        },
        "environmentals": []
    },
    "249": {
        "name": "X-45",
        "sector": "Ymir",
        "biome": {
            "slug": "swamp",
            "description": "The lifeless grey of this planet is interrupted only by the violet flowers that grow from "
                           "strange, parasitic outcroppings."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            }
        ]
    },
    "250": {
        "name": "Yed Prior",
        "sector": "Tanis",
        "biome": {
            "slug": "crimsonmoor",
            "description": "A crimson algae has propagated wildly across this entire planet, coating its rocky hills "
                           "with a constant red that masks the spilt blood of the heroes who defend it from tyranny."
        },
        "environmentals": [
            {
                "name": "Ion Storms",
                "description": "Ion storms intermittently disable Stratagems"
            }
        ]
    },
    "251": {
        "name": "Zefia",
        "sector": "Tanis",
        "biome": {
            "slug": "ethereal",
            "description": "This world teems with ethereal, boundless, and peculiar plant life that spreads silent "
                           "and uninterrupted across its entire surface."
        },
        "environmentals": []
    },
    "252": {
        "name": "Zosma",
        "sector": "Gellert",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "253": {
        "name": "Zzaniah Prime",
        "sector": "Gellert",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "254": {
        "name": "Skitter",
        "sector": "Hawking",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "255": {
        "name": "Euphoria III",
        "sector": "Hawking",
        "biome": {
            "slug": "moon",
            "description": "A rocky, lonely moon with extremely valuable mineral deposits underneath the surface."
        },
        "environmentals": [
            {
                "name": "Extreme Cold",
                "description": "Icy temperatures reduce rate of fire and delay heat buildup in weapons."
            },
            {
                "name": "Meteor Storms",
                "description": "Meteors impact the surface causing massive damage"
            }
        ]
    },
    "256": {
        "name": "Diaspora X",
        "sector": "L'estrade",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "257": {
        "name": "Gemstone Bluffs",
        "sector": "L'estrade",
        "biome": {
            "slug": "highlands",
            "description": "Rocky outcroppings punctuate fields of tall grass in a planet dominated by misty highland "
                           "terrain."
        },
        "environmentals": [
            {
                "name": "Thick Fog",
                "description": ""
            },
            {
                "name": "Rainstorms",
                "description": "Torrential rainstorms reduce visibility"
            }
        ]
    },
    "258": {
        "name": "Zagon Prime",
        "sector": "Mirin",
        "biome": {
            "slug": "mesa",
            "description": "A blazing-hot desert planet, it's rocky mesas are the sole interruptions to the endless "
                           "sea of dunes."
        },
        "environmentals": [
            {
                "name": "Intense Heat",
                "description": "High temperatures increase stamina drain and speed up heat buildup in weapons"
            },
            {
                "name": "Sandstorms",
                "description": ""
            }
        ]
    },
    "259": {
        "name": "Omicron",
        "sector": "L'estrade",
        "biome": {
            "slug": "tundra",
            "description": "A perenially chilly climate has allowed short, colourful shrubs to flourish across this"
                           "planet's surface."
        },
        "environmentals": []
    },
    "260": {
        "name": "Cyberstan",
        "sector": "Valdis",
        "biome": {
            "slug": "canyon",
            "description": "This arid, rocky biome covering this world has driven the evolution of exceptionally "
                           "efficient water usage in its various organisms."
        },
        "environmentals": [
            {
                "name": "Tremors",
                "description": "Frequent earthquakes stun players and enemies alike."
            }
        ]
    }
}


def get_planet_by_id(planet_id: Union[str, int]) -> Planet:
    """
    Retrieves a planet from the database by its ID
    :param planet_id: Planet ID or planet index
    :return: The found planet
    :raises: KeyError if the planet could not been found
    """
    if isinstance(planet_id, int):
        planet_id = str(planet_id)

    try:
        planet_info = PLANET_INFO_TABLE[planet_id]
    except KeyError:
        raise KeyError(f"Planet with ID '{planet_id}' is not on the database.")
    return Planet(
        planet_id=int(planet_id),
        name=planet_info["name"],
        sector=Sector(planet_info["sector"])
    )

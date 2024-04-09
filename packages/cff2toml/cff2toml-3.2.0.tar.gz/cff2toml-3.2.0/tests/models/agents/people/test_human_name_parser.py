
from cff2toml.models.agents.people.human_name import HumanName, HumanNameParser


def test_parse_with_different_human_names():

    human_names_to_parts = {
        'Bob Smith Jr': ('Bob', '', '', 'Smith', 'Jr'),
        'Bob Smith Jr.': ('Bob', '', '', 'Smith', 'Jr.'),
        'Bob Dave Smith Jr.': ('Bob', 'Dave', '', 'Smith', 'Jr.'),
        'Sally Lou May': ('Sally', 'Lou', '', 'May', ''),
        'Sally Elizabeth Lou May': ('Sally', 'Elizabeth Lou', '', 'May', ''),
        'Sally Lou van May': ('Sally', 'Lou', 'van', 'May', ''),
        'Alicia de Francisco': ('Alicia', '', 'de', 'Francisco', ''),
        'Adam van het Francisco IV': ('Adam', '', 'van het', 'Francisco', 'IV'),
        'Tony': ('Tony', '', '', '', ''),
        'Tony Li': ('Tony', '', '', 'Li', ''),
        'Tony X': ('Tony', '', '', 'X', ''),
    }

    for human_name_to_parse, (expected_first_name, expected_middle_name, expected_particle, expected_last_name, expected_suffix) in human_names_to_parts.items():
        human_name: HumanName = HumanNameParser.parse(
            text=human_name_to_parse)
        assert human_name.first_name == expected_first_name
        assert human_name.middle_name == expected_middle_name
        assert human_name.particle == expected_particle
        assert human_name.last_name == expected_last_name
        assert human_name.suffix == expected_suffix

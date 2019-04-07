#!/usr/bin/env python

from srd_index_builder import SRDIndexBuilder
import logging
import argparse

build_config = {
    'class_spell_lists': {
        'build': True,
        'index_path': './docs/spellcasting/spell_lists/'
    },
    'indexes': {
        'spells': {
            'source_directory': './docs/spellcasting/spells',
            'link_prefix': '/spellcasting/spells',
            'index_path': './docs/spellcasting/spell_indexes/',
            'indexes_to_generate': {
                'school': {
                    'page_title': 'Spells by School',
                    'output_file_name': 'spells_by_school.md'
                },
                'name_category': {
                    'page_title': 'Spells by Name',
                    'output_file_name': 'spells_by_name.md'
                },
                'level': {
                    'page_title': 'Spells by Level',
                    'output_file_name': 'spells_by_level.md'
                }
            }
        },
        'magic_items': {
            'source_directory': './docs/gamemaster_rules/magic_items',
            'link_prefix': '/gamemaster_rules/magic_items',
            'index_path': './docs/gamemaster_rules/magic_item_indexes/',
            'indexes_to_generate': {
                'name_category': {
                    'page_title': 'Magic Items by Name',
                    'output_file_name': 'items_by_name.md'
                },
                'type': {
                    'page_title': 'Magic Items by Type',
                    'output_file_name': 'items_by_type.md'
                }
            }

        },
        'monsters': {
            'source_directory': './docs/gamemaster_rules/monsters',
            'link_prefix': '/gamemaster_rules/monsters',
            'index_path': './docs/gamemaster_rules/monster_indexes/',
            'indexes_to_generate': {
                'name_category': {
                    'page_title': 'Monsters by Name',
                    'output_file_name': 'monsters_by_name.md'
                },
                'cr': {
                    'page_title': 'Monsters by CR',
                    'output_file_name': 'monsters_by_cr.md'
                },
                'type': {
                    'page_title': 'Monsters by Type',
                    'output_file_name': 'monsters_by_type.md'
                }
            }
        }
    }
}

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true', default=False,
                        help='Generate links in offline mode')
    args = parser.parse_args()

    # First, build metadata driven indexes using the SRDIndexBuilder
    SRDIndexBuilder(args.offline).build_indexes_from_config(build_config)

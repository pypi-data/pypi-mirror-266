#
# Function definition
#

EXTRACT_DATE_TIME = {
    'required': ['query'],
    'parameters': {
        'query': {
            'name': 'query',
            'equivalence': {
                'tester': 'get_equivalence_tester',
                'category': 'date, time, time range, date range',
            },
            'consistency': {
                'tester': 'get_category_consistency_tester',
                'instruction': 'latest',
                'category': 'date, time, time range, date range',
            },
            'grammar': {
                'tester': 'get_grammar_tester',
            },
        }
    }
}

EXTRACT_COORDINATES = {
    'required': ['query'],
    'parameters': {
        'query': {
            'name': 'query',
            'equivalence': {
                'tester': 'get_equivalence_tester',
                'category': 'date, time, time range, date range',
            },
            'consistency': {
                'tester': 'get_category_consistency_tester',
                'instruction': 'latest',
                'category': 'place, land mark, district, building',
            },
            'grammar': {
                'tester': 'get_grammar_tester',
            },
        }
    }
}

GET_MOVIE_THEATERS = {
    'required': ['latitude', 'longitude'],
    'parameters': {
        'latitude': {
            'name': 'latitude',
            'equivalence': {
                'tester': 'get_equivalence_tester',
                'category': 'coordinate',
            },
            'consistency': {
                'tester': 'get_number_consistency_tester',
                'instruction': 'latest',
                'range': [-90, 90],
            },
        },
        'longitude': {
            'name': 'longitude',
            'equivalence': {
                'tester': 'get_equivalence_tester',
                'category': 'coordinate',
            },
            'consistency': {
                'tester': 'get_number_consistency_tester',
                'instruction': 'latest',
                'range': [-180, 180],
            },
        },
    },
}

GET_MOVIE_TITLES = {
    'required' : [],
    'parameters': {
        'start_time': {
            'name': 'start_time',
            'equivalence': {
                'tester': 'get_equivalence_tester',
                'category': 'datetime, YYYY-mm-dd HH:MM:SS',
            },
            'consistency': {
                'tester': 'get_category_consistency_tester',
                'category': 'datetime, YYYY-mm-dd HH:MM:SS',
                'comment': 'If the start time is not provided explicitly, it should be inferred from the compound of the current time and user request.',
                'instruction': 'all',
            },
        },
        'end_time': {
            'name': 'end_time',
            'equivalence': {
                'tester': 'get_equivalence_tester',
                'category': 'datetime, YYYY-mm-dd HH:MM:SS',
            },
            'consistency': {
                'tester': 'get_category_consistency_tester',
                'category': 'datetime, YYYY-mm-dd HH:MM:SS',
                'comment': 'If the end time is not provided explicitly, it should be inferred from the compound of the current time and user request.',
                'instruction': 'all',
            },
        },
        'movie_theater': {
            'name': 'movie_theater',
            'equivalence': {
                'tester': 'get_equivalence_tester',
                'category': 'theater name',
            },
            'consistency': {
                'tester': 'get_category_consistency_tester',
                'category': 'theater name',
                'instruction': 'all',
            },
        },
        'query': {
            'name': 'query',
            'equivalence': {
                'tester': 'get_equivalence_tester',
                'category': 'movie title',
            },
            'consistency': {
                'tester': 'get_category_consistency_tester',
                'category': 'movie title',
                'instruction': 'latest',
            },
            'grammar': {
                'tester': 'get_grammar_tester',
            },
        },
    },
}

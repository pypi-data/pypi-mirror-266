from logging import Logger
from typing import Any, Optional

from equivalent_llm import testers

RESERVATION_BOARD = {
    'answer': {
        'name': 'answer',
        'equivalence': {
            'tester': 'get_equivalence_tester',
            'category': 'answer for a question or a request of user, suggestion of related to movie reservation, or confirmation of reservation',
        },
        'consistency': {
            'tester': 'get_category_consistency_tester',
            'instruction': 'all',
            'category': 'answer for a question or a request of user, suggestion of related to movie reservation, or confirmation of reservation',
        },
        'grammar': {
            'tester': 'get_grammar_tester',
        },
        'elegance': {
            'tester': 'get_elegance_tester',
        },
    },
    'selected_title': {
        'name': 'selected_title',
        'equivalence': {
            'tester': 'get_equivalence_tester',
            'category': 'movie title',
        },
        'consistency': {
            'tester': 'get_category_consistency_tester',
            'instruction': 'all',
            'category': 'movie title',
        },
    },
    'selected_theater': {
        'name': 'selected_theater',
        'equivalence': {
            'tester': 'get_equivalence_tester',
            'category': 'theater name',
        },
        'consistency': {
            'tester': 'get_category_consistency_tester',
            'instruction': 'all',
            'category': 'theater name',
        },
    },
    'selected_schedule': {
        'name': 'selected_schedule',
        'equivalence': {
            'tester': 'get_equivalence_tester',
            'category': 'schedule',
        },
        'consistency': {
            'tester': 'get_category_consistency_tester',
            'instruction': 'all',
            'category': 'schedule',
        },
    },
    'selected_time': {
        'name': 'selected_time',
        'equivalence': {
            'tester': 'get_equivalence_tester',
            'category': 'time',
        },
        'consistency': {
            'tester': 'get_category_consistency_tester',
            'instruction': 'all',
            'category': 'time',
        },
    },
    'reference_number': {
        'name': 'reference_number',
        'equivalence': {
            'tester': 'get_equivalence_tester',
            'category': 'ref:DDD, ref:DDDD',
        },
    },
    'template': {
        'name': 'template',
        'equivalence': {
            'tester': 'get_equivalence_tester',
            'category': 'template of theater or movies, none',
        },
    },
}

def equivalence_test(
    generated: Any,
    reference: Any,
    instructions: Optional[list],
    definition: dict,
    prompt_engine: Any,
    logger: Logger,
) -> dict:
    if generated != reference:
        get_tester = getattr(testers, definition['tester'])
        tester = get_tester(definition, prompt_engine)
        return tester(generated, reference, instructions, logger)
    return {'passed': True, 'evidence': "exactly matched"}

def consistency_test(
    generated: Any,
    instructions: Optional[list],
    definition: dict,
    prompt_engine: Any,
    logger: Logger,
) -> dict:
    get_tester = getattr(testers, definition['tester'])
    tester = get_tester(definition, prompt_engine)
    return tester(generated, None, instructions, logger)

def grammar_test(
    generated: Any,
    definition: dict,
    prompt_engine: Any,
    logger: Logger,
) -> dict:
    get_tester = getattr(testers, definition['tester'])
    tester = get_tester(definition, prompt_engine)
    return tester(generated, None, None, logger)

def elegance_test(
    generated: Any,
    reference: Any,
    instructions: Optional[list],
    definition: dict,
    prompt_engine: Any,
    logger: Logger,
) -> dict:
    get_tester = getattr(testers, definition['tester'])
    tester = get_tester(definition, prompt_engine)
    return tester(generated, reference, instructions, logger)

def validate(
    generated: dict,
    reference: dict,
    instructions: Optional[list],
    configurations: dict,
    prompt_engine: Any,
    api_version: str,
    logger: Logger,
) -> dict:
    reports = {
        'target': 'reservation_board',
        'tests': {
            'equivalence': [],
            'consistency': [],
            'grammar': [],
            'elegance': [],
        },
    }

    elements = [
        'answer',
        'selected_title',
        'selected_theater',
        'selected_schedule',
        'selected_time',
        'reference_number',
        'template',
    ]

    if generated['type'] is not reference['type']:
        return {'passed': False, 'count': {'total': {'passed': 0, 'total': 1}}, 'tests': {}, 'reason': 'reservation is not generated ', 'level': 'fatal'}

    equivalence_counter = testers.TestCounter()
    consistency_counter = testers.TestCounter()
    grammar_counter = testers.TestCounter()
    elegance_counter = testers.TestCounter()

    for element in elements:
        if (
            RESERVATION_BOARD.get(element) and
            (
                (
                    generated['reservation'].get(element) is not None and
                    generated['reservation'][element] != ''
                ) or (
                    reference['reservation'].get(element) is not None and
                    reference['reservation'][element] != ''
                )
            )
        ) :
            # equivalence test
            equivalence_result = equivalence_test(
                generated['reservation'].get(element),
                reference['reservation'].get(element),
                instructions,
                RESERVATION_BOARD[element]['equivalence'],
                prompt_engine,
                logger,
            )
            reports['tests']['equivalence'].append({'element': element, **equivalence_result})
            equivalence_counter.count(equivalence_result)

            # consistency test
            if RESERVATION_BOARD[element].get('consistency'):
                consistency_result = consistency_test(
                    generated['reservation'].get(element),
                    instructions,
                    RESERVATION_BOARD[element]['consistency'],
                    prompt_engine,
                    logger,
                )
                reports['tests']['consistency'].append({'element': element, **consistency_result})
                consistency_counter.count(consistency_result)

            # grammar test
            if RESERVATION_BOARD[element].get('grammar'):
                grammar_result = grammar_test(
                    generated['reservation'].get(element),
                    RESERVATION_BOARD[element]['grammar'],
                    prompt_engine,
                    logger,
                )
                reports['tests']['grammar'].append({'element': element, **grammar_result})
                grammar_counter.count(grammar_result)

            # elegance test
            if RESERVATION_BOARD[element].get('elegance'):
                elegance_result = elegance_test(
                    generated['reservation'].get(element),
                    reference['reservation'].get(element),
                    instructions,
                    RESERVATION_BOARD[element]['elegance'],
                    prompt_engine,
                    logger,
                )
                reports['tests']['elegance'].append({'element': element, **elegance_result})
                elegance_counter.count(elegance_result)

    total_counter = equivalence_counter + consistency_counter + grammar_counter + elegance_counter

    reports['passed'] = total_counter.fully_passed()
    reports['count'] = {
        'total': total_counter.settlement(),
        'equivalence': equivalence_counter.settlement(),
        'consistency': consistency_counter.settlement(),
        'grammar': grammar_counter.settlement(),
        'elegance': elegance_counter.settlement(),
    }
    return reports

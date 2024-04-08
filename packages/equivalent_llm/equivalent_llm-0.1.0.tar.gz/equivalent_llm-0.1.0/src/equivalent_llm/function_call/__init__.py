from logging import Logger
from typing import Any

from equivalent_llm import testers
from equivalent_llm.function_call import v1
from equivalent_llm.function_call import v2

def check_function_call(generated: str, reference: str) -> dict:
    if generated != reference:
        return {
            'passed': False,
            'reason': 'Wrong function call',
            'level': 'fatal',
            'evidance': {
                'type': 'function_call',
                'reference': reference,
                'generated': generated,
            }
        }
    else:
        return {'passed': True}

def check_required_parameters(arguments: dict, required: list) -> dict:
    # check if all required parameters are present
    argument_names = arguments.keys()
    for p in required:
        if p not in argument_names:
            return {
                'passed': False,
                'level': 'critical',
                'evidance': {
                    'not_in_required': p,
                },
            }
    return {'passed': True}

def check_paired_arguments(generated_keys: dict, reference_keys: dict) -> dict:
    if generated_keys != reference_keys:
        not_in_reference = list(filter(lambda v: v not in generated_keys, reference_keys))
        not_in_generated = list(filter(lambda v: v not in reference_keys, generated_keys))
        return {
            'passed': False,
            'level': 'severe',
            'evidance': {
                'not_in_reference': not_in_reference,
                'not_in_generated': not_in_generated,
            }
        }
    return {'passed': True}

def equivalence_test(
    generated: Any,
    reference: Any,
    instructions: list,
    definition: dict,
    prompt_engine: Any,
    logger: Logger,
) -> dict:
    result = {}
    # value equality
    if generated != reference:
        get_tester = getattr(testers, definition['tester'])
        tester = get_tester(definition, prompt_engine)
        return tester(generated, reference, instructions, logger)
    return {'passed': True, 'evidence': "exactly mactched"}

def consistency_test(
    generated: Any,
    instructions: list,
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
    instructions: list,
    definition: dict,
    prompt_engine: Any,
    logger: Logger,
) -> dict:
    get_tester = getattr(testers, definition['tester'])
    tester = get_tester(definition, prompt_engine)
    return tester(generated, reference, instructions, logger)

### function call

def validate(
    function_name: str,
    generated: dict,
    reference: dict,
    instructions: list,
    configurations: dict,
    prompt_engine: Any,
    api_version: str,
    logger: Logger,
) -> dict:
    try:
        match(api_version):
            case 'v1':
                DEFINITION = getattr(v1, function_name.upper())
            case _:
                DEFINITION = getattr(v2, function_name.upper())
    except AttributeError:
        logger.error(f'Function {function_name} not found in equivalent_llm')
        return {'passed': False, 'count': {'total': {'passed': 0, 'total': 1}}, 'tests': {}, 'reason': 'Function not found', 'level': 'fatal'}

    reports = {
        'target': function_name,
        'tests': {
            'equivalence': [],
            'consistency': [],
            'grammar': [],
            'elegance': [],
        },
    }

    if generated['type'] is not reference['type']:
        return {'passed': False, 'count': {'total': {'passed': 0, 'total': 1}}, 'tests': {}, 'reason': 'function call is not generated', 'level': 'fatal'}

    # counters

    equivalence_counter = testers.TestCounter()
    consistency_counter = testers.TestCounter()
    grammar_counter = testers.TestCounter()
    elegance_counter = testers.TestCounter()
    etc_counter = testers.TestCounter()

    ### mandatory tests

    # function name
    function_call_result = check_function_call(generated['name'], reference['name'])
    reports['tests']['function_name'] = function_call_result
    etc_counter.count(function_call_result)

    # required parameters
    required_result = check_required_parameters(generated['arguments'], DEFINITION['required'])
    reports['tests']['required'] = required_result
    etc_counter.count(required_result)

    # argument paried to reference
    paired_arguments_result = check_paired_arguments(generated['arguments'].keys(), reference['arguments'].keys())
    reports['tests']['paired_arguments'] = paired_arguments_result
    etc_counter.count(paired_arguments_result)

    # value type
    for name in generated['arguments']:
        definition = DEFINITION['parameters'].get(name)

        # equivalence tests
        equivalence_result = equivalence_test(
            generated['arguments'].get(name),
            reference['arguments'].get(name),
            instructions,
            definition['equivalence'],
            prompt_engine,
            logger,
        )
        reports['tests']['equivalence'].append({'argument': name, **equivalence_result})
        equivalence_counter.count(equivalence_result)

        ### supplementary tests

        # consistency tests
        if definition.get('consistency'):
            consistency_result = consistency_test(
                generated['arguments'].get(name),
                instructions,
                definition['consistency'],
                prompt_engine,
                logger,
            )
            reports['tests']['consistency'].append({'argument': name, **consistency_result})
            consistency_counter.count(consistency_result)

        # grammar tests
        if definition.get('grammar'):
            grammar_result = grammar_test(
                generated['arguments'].get(name),
                definition['grammar'],
                prompt_engine,
                logger,
            )
            reports['tests']['grammar'].append({'argument': name, **grammar_result})
            grammar_counter.count(grammar_result)

        # grammar tests
        if definition.get('elegance'):
            elegance_result = elegance_test(
                generated['arguments'].get(name),
                reference['arguments'].get(name),
                instructions,
                definition['elegance'],
                prompt_engine,
                logger,
            )
            reports['tests']['elegance'].append({'argument': name, **elegance_result})
            elegance_counter.count(elegance_result)

    total_counter = equivalence_counter + consistency_counter + grammar_counter + elegance_counter

    reports['passed'] = total_counter.fully_passed()
    reports['count'] = {
        'total': total_counter.settlement(),
        'equivalence': equivalence_counter.settlement(),
        'consistency': consistency_counter.settlement(),
        'grammar': grammar_counter.settlement(),
        'elegance': elegance_counter.settlement(),
        'etc': etc_counter.settlement(),
    }
    return reports

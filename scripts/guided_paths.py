"""Selected worked steps for the middle route through each lesson.

Keep the order as a coherent decision story; the full technical route retains
every original stop in its original order.
"""

GUIDED = {
    1: ['decision-first', 'keys', 'comparison', 'join', 'handoff'],
    2: ['distribution', 'centers', 'fair-groups', 'budget-decision', 'distribution-handoff'],
    3: ['paired-data', 'paired-spread', 'paired-test', 'paired-meaning', 'inference-handoff'],
    4: ['juniper-question', 'juniper-bins', 'juniper-residual-pattern', 'juniper-candidate-scores', 'juniper-handoff'],
    5: ['cedar-data-contract', 'cedar-conditional-comparison', 'cedar-fixed-rows', 'cedar-interacting-fixture', 'cedar-inference-handoff'],
    6: ['mica-prediction-contract', 'mica-loss-target', 'mica-feature-availability', 'mica-final-evaluation', 'mica-transport-stress', 'mica-decision-handoff'],
    7: ['causal-question', 'define-intervention', 'observed-gap', 'decomposition', 'random-rule', 'decision', 'brief'],
    8: ['conditional', 'strata-calculation', 'graph-language', 'collider', 'balance-not-proof', 'brief'],
    9: ['target-trial', 'descriptive', 'standardization', 'overlap', 'hidden-confounding', 'bounded-brief'],
    10: ['decision', 'two-by-two', 'second-difference', 'parallel', 'drift', 'brief'],
}

def selected(number, sections):
    by_id = {section['id']: section for section in sections}
    ids = GUIDED[number]
    if len(by_id) != len(sections) or len(set(ids)) != len(ids):
        raise ValueError(f'Lesson {number} has duplicate step IDs')
    missing = [id for id in ids if id not in by_id]
    if missing:
        raise ValueError(f'Lesson {number} is missing guided steps: {missing}')
    return [by_id[id] for id in ids]

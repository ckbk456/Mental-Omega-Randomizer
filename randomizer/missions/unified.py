"""Installed content identity and selection for standalone mixed runs.

Pool identity describes the authored content, never a player's chosen house.
ARPA2 operations have their own pool row but retain the solo campaign launch contract.
"""

from collections.abc import Mapping

from randomizer.challenges.presentation import challenge_color_group
from randomizer.missions.catalogue import normalize_faction


POOL_ROWS = (
    ('mo_campaign', 'MO campaign'),
    ('mo_coop', 'MO co-op'),
    ('challenges', 'Challenges'),
    ('apra2_campaign', 'ARPA2 campaign'),
    ('apra2_special_ops', 'ARPA2 special ops'),
)
POOL_FACTIONS = ('Allies', 'Soviets', 'Epsilon', 'Foehn', 'Mixed')
POOL_CELLS = tuple(f'{row}:{faction}' for row, _ in POOL_ROWS for faction in POOL_FACTIONS)
SUPPORTED_CELLS = frozenset(
    [f'mo_campaign:{faction}' for faction in POOL_FACTIONS[:4]]
    + [f'mo_coop:{faction}' for faction in POOL_FACTIONS[:3]]
    + [f'challenges:{faction}' for faction in POOL_FACTIONS]
    + [f'apra2_campaign:{faction}' for faction in POOL_FACTIONS[:2]]
    + [f'apra2_special_ops:{faction}' for faction in POOL_FACTIONS[:2]]
)
POOL_SELECTION_VERSION = 2
APRA2_OPERATION_CODES = frozenset(
    f'{side}CO{number}' for side in ('A', 'S') for number in range(1, 4)
)
APRA2_MISSION_CODES = frozenset(
    [f'{side}{number:02}' for side in ('A', 'S') for number in range(1, 21)]
) | APRA2_OPERATION_CODES


def mission_kind(mission):
    """Return the native launch contract: campaign, challenge, or co-op."""
    if mission.get('mission_category') == 'challenge' or mission.get('challenge_name'):
        return 'challenge'
    return 'coop' if mission.get('coop_name') else 'campaign'


def mission_pool_cell(mission):
    kind = mission_kind(mission)
    if kind == 'challenge':
        return f'challenges:{challenge_color_group(mission) or "Mixed"}'
    code = str(mission.get('code', '')).upper()
    source = 'apra2' if code in APRA2_MISSION_CODES else 'mo'
    faction = normalize_faction(mission.get('side', '')) or 'Mixed'
    if code in APRA2_OPERATION_CODES:
        return f'apra2_special_ops:{faction}'
    return f'{source}_{kind}:{faction}'


def pool_cell_counts(missions):
    counts = dict.fromkeys(POOL_CELLS, 0)
    seen = set()
    for mission in missions:
        if mission.get('skirmish'):
            continue
        code = str(mission.get('code', '')).upper()
        if not code or code in seen:
            continue
        seen.add(code)
        cell = mission_pool_cell(mission)
        counts[cell] = counts.get(cell, 0) + 1
    return counts


def pool_cell_status(row, faction, counts):
    """Describe an empty cell without pretending unshipped maps are missing."""
    cell = f'{row}:{faction}'
    if counts.get(cell, 0):
        return ''
    if cell not in SUPPORTED_CELLS:
        return 'No authored missions in this category'
    return 'Pack not installed' if row.startswith('apra2_') else 'No installed missions'


def normalize_pool_selection(selection):
    """Validate and copy a portable pool selection; never mutate a saved run."""
    if not isinstance(selection, Mapping):
        raise ValueError('Mission pool selection must be an object.')
    version = selection.get('version', 1)
    if type(version) is not int or version not in (1, POOL_SELECTION_VERSION):
        raise ValueError('Unsupported mission pool selection version. Update the launcher.')
    cells = selection.get('cells', [])
    if not isinstance(cells, (list, tuple, set, frozenset)):
        raise ValueError('Mission pool cells must be a list.')
    legacy_coop_cells = {f'apra2_coop:{faction}' for faction in POOL_FACTIONS}
    valid_cells = set(POOL_CELLS) | (legacy_coop_cells if version == 1 else set())
    if any(not isinstance(cell, str) or cell not in valid_cells for cell in cells):
        raise ValueError('Mission pool contains an unknown category or faction.')
    cells = set(cells)
    if version == 1:
        # The old campaign row included all 30 solo maps. Preserve that choice
        # when interpreting old settings, without altering any frozen run data.
        cells.update(f'apra2_special_ops:{faction}' for faction in POOL_FACTIONS
                     if f'apra2_campaign:{faction}' in cells)
        cells.difference_update(legacy_coop_cells)
    policy = selection.get('cooperative_policy', 'flexible')
    if policy not in ('flexible', 'required'):
        raise ValueError('Co-op policy must be flexible or required.')
    return {'version': POOL_SELECTION_VERSION,
            'cells': [cell for cell in POOL_CELLS if cell in cells],
            'cooperative_policy': policy}


def pool_selection_from_settings(selection, *, include_operations=True):
    """Migrate next-run preferences, including the old global operation filter.

    Frozen run data uses normalize_pool_selection directly: its stored mission
    order already decides which operations belong to that run.
    """
    normalized = normalize_pool_selection(selection)
    if selection.get('version', 1) == 1 and not include_operations:
        original = set(selection.get('cells', ()))
        normalized['cells'] = [
            cell for cell in normalized['cells']
            if not cell.startswith('apra2_special_ops:') or cell in original
        ]
    return normalized


def legacy_pool_selection(category='campaign', campaign='All Campaigns',
                          include_challenges=False):
    """Translate settings for the next run without rewriting a legacy seed."""
    rows = ({'challenges'} if category == 'challenge' else {'mo_coop'}
            if category == 'coop' else {'mo_campaign', 'apra2_campaign', 'apra2_special_ops'})
    cells = [cell for cell in POOL_CELLS
             if cell in SUPPORTED_CELLS and cell.split(':')[0] in rows
             and (category == 'challenge' or campaign == 'All Campaigns'
                  or cell.split(':')[1] == campaign)]
    if include_challenges and category != 'challenge':
        cells.extend(f'challenges:{faction}' for faction in POOL_FACTIONS)
    return normalize_pool_selection({
        'version': POOL_SELECTION_VERSION,
        'cells': cells,
        'cooperative_policy': 'required' if category == 'coop' else 'flexible',
    })


def validate_mixed_generation(selection, progression_mode):
    selection = normalize_pool_selection(selection)
    if progression_mode not in ('Mission List', 'Grid Mode'):
        raise ValueError(
            'The unified mission pool supports standalone Mission List and Grid Mode. '
            'Choose one of those modes, or resume a legacy run for Classic, Shop '
            'or Archipelago. Final Fortress uses its own mission pool.'
        )
    if not selection['cells']:
        raise ValueError('Select at least one category and faction in Mission Pool.')
    return selection

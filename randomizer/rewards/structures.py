"""Reviewed, portable campaign and capturable-technology reward data."""

from randomizer.config.static import load_static_config


STRUCTURE_PACKS = tuple(load_static_config(path) for path in (
    'rewards/campaign_structures.json',
    'rewards/tech_structures.json',
))
BUILDING_REWARD_DEFINITIONS = tuple(
    dict(building, universal_access=True)
    for pack in STRUCTURE_PACKS for building in pack['buildings']
)
PORTABLE_STRUCTURE_IDS = frozenset(
    str(unit_id).upper()
    for pack in STRUCTURE_PACKS for unit_id in pack['unit_base_stats']
)


def structure_data(field):
    """Combine the two independently authored packs without mutating either."""
    result = {}
    for pack in STRUCTURE_PACKS:
        for key, value in pack.get(field, {}).items():
            if key in result:
                raise ValueError(f'Duplicate portable structure {field}: {key}')
            result[key] = value
    return result


STRUCTURE_ART_TEMPLATES = {
    str(key).upper(): dict(value)
    for key, value in structure_data('art_templates').items()
}

"""Portable structure prerequisites and exact player-clone references.

The native objective/capturable structures remain untouched. These rules apply
only to registered reward copies after their final (possibly compact) IDs exist.
"""

from randomizer.core.collections import comma_items, unique_in_order
from randomizer.maps.base import resolved_academy_clone_rules
from randomizer.maps.ini import all_section_value_maps_preserve
from randomizer.missions.access import _alternative_prerequisite_rules
from randomizer.rewards.structures import PORTABLE_STRUCTURE_IDS


LAB_ID = 'CASLAB'
LAB_UNIT_ID = 'REJU'
LAB_FACTORIES = ('GAWEAP', 'NAWEAP', 'YAWEAP', 'FAWEAP')
HOSPITAL_IDS = ('CATHOSP', 'CAFHOSP')
_BUILDING_REFERENCE_FIELDS = frozenset({
    'auxbuilding', 'sw.auxbuildings', 'sw.negbuildings', 'sw.designators',
    'empulse.cannons', 'prismforwarding.targets',
})


def secret_lab_unit_access_rules():
    """Prepare the dependent production clone without granting a saved reward.

    The final physical lab prerequisite is attached once its clone ID is known.
    Exact War Factory alternatives avoid the secret-lab engine's capture-only
    activation and make construction/loss of the owned lab work immediately.
    """
    return {
        'TechLevel': '1', 'BuildLimit': None,
        **_alternative_prerequisite_rules(LAB_FACTORIES),
    }


def _inherited_paradrop_rules(sections, powers):
    """Carry native country drop recipes onto campaign/player child countries.

    Ares' SW-specific ParaDrop.Country fields match the actual CountryType;
    ParentCountry alone does not supply that entry in a private power's INI.
    """
    parents = {
        str(section).upper(): str(value).strip()
        for section, values in sections.items()
        for key, value in values.items()
        if str(key).lower() == 'parentcountry' and str(value).strip()
    }
    country_names = {str(section).upper(): str(section) for section in sections}
    updates = {}
    for section, values in powers.items():
        by_lower = {str(key).lower(): value for key, value in values.items()}
        if str(by_lower.get('type', '')).lower() not in {'paradrop', 'amerparadrop'}:
            continue
        for country, parent in parents.items():
            current = parent.upper()
            visited = {country}
            while current and current not in visited:
                visited.add(current)
                prefix = f'paradrop.{current.lower()}.'
                inherited = {
                    str(key)[len(prefix):]: value
                    for key, value in values.items()
                    if str(key).lower().startswith(prefix)
                }
                if inherited:
                    for suffix, value in inherited.items():
                        field = f'ParaDrop.{country_names[country]}.{suffix}'
                        if field.lower() not in by_lower:
                            updates.setdefault(section, {})[field] = value
                    break
                current = parents.get(current, '').upper()
    return updates


def portable_structure_reference_rules(
    sections, clone_handled, owned_clone_ids, *,
    secret_lab_access=False, direct_rejuvenator_access=False,
    unlimited_buildings=False,
):
    """Resolve owned academy lists, provider links and conditional access."""
    names = {str(name).upper(): name for name in sections}
    clones = {
        str(source).upper(): str(details.get('clone_id') or '')
        for source, details in clone_handled.items()
        if details.get('clone_id')
    }
    replacements = {}
    for source, clone in clones.items():
        replacements[source] = clone
        replacements[f'MORP{source}'] = clone
        preferred = owned_clone_ids.get(source)
        if preferred:
            replacements[str(preferred).upper()] = clone
    owned_sections = {
        names[clone.upper()]: sections[names[clone.upper()]]
        for source, clone in clones.items()
        if source in PORTABLE_STRUCTURE_IDS and clone.upper() in names
    }
    updates = resolved_academy_clone_rules(
        owned_sections, clone_handled, owned_clone_ids,
    )

    # Only the owned structures and their private provider powers participate.
    # A source TechnoType's inherited links must never broaden native AI powers.
    private_sections = dict(owned_sections)
    from randomizer.rewards.definitions import STANDALONE_UNIT_RULE_TEMPLATES
    authored_power_ids = {
        str(power).upper()
        for source in PORTABLE_STRUCTURE_IDS
        for registry, definitions in STANDALONE_UNIT_RULE_TEMPLATES.get(source, {}).items()
        if str(registry).lower() == 'superweapontypes'
        for power in definitions
    }
    pending = list(owned_sections)
    for section in pending:
        for field, raw in sections.get(section, {}).items():
            if str(field).lower() not in {
                'superweapon', 'superweapon2', 'superweapons',
                'sw.postdependent', 'sw.next',
            }:
                continue
            for token in comma_items(raw):
                name = names.get(token.upper())
                # Reviewed private providers and multiplayer namespace copies
                # are safe; native powers accidentally retained by an editable
                # roster are not rewritten globally.
                private = token.upper() in authored_power_ids or token.upper().startswith('MOR')
                if name and private and name not in private_sections:
                    private_sections[name] = sections[name]
                    pending.append(name)
    for section, values in private_sections.items():
        for field, raw in values.items():
            if str(field).lower() not in _BUILDING_REFERENCE_FIELDS:
                continue
            resolved = ','.join(unique_in_order(
                replacements.get(item.upper(), item) for item in comma_items(raw)
            ))
            if resolved != str(raw):
                updates.setdefault(section, {})[field] = resolved
    for section, values in _inherited_paradrop_rules(sections, private_sections).items():
        updates.setdefault(section, {}).update(values)

    if secret_lab_access:
        lab = clones.get(LAB_ID)
        unit = clones.get(LAB_UNIT_ID)
        if not lab or not unit:
            raise ValueError('Secret Lab access is missing its lab or Rejuvenator clone.')
        unit_rules = secret_lab_unit_access_rules()
        if not direct_rejuvenator_access:
            unit_rules.update(_alternative_prerequisite_rules(
                f'{factory},{lab}' for factory in LAB_FACTORIES
            ))
        # Replace all old alternative paths, including capture/stolen-tech
        # escape hatches. Existing units and separately owned direct access
        # are unaffected when the lab is sold or destroyed.
        for field in sections.get(names.get(unit.upper(), unit), {}):
            if str(field).lower().startswith('prerequisite'):
                updates.setdefault(unit, {})[field] = None
        updates.setdefault(unit, {}).update(unit_rules)
        updates.setdefault(lab, {}).update({
            'SecretLab': 'no', 'SecretLab.GenerateOnCapture': 'no',
            'SecretLab.PossibleBoons': 'none',
        })

    # These visual alternatives are one hospital reward and share its cap.
    # Preserve other safety gates; only remove the paired-hospital gate when
    # the existing unlimited-buildings option is enabled.
    for source in HOSPITAL_IDS:
        clone = clones.get(source)
        if not clone:
            continue
        sibling_source = next(item for item in HOSPITAL_IDS if item != source)
        sibling = clones.get(sibling_source)
        if not sibling:
            continue
        values = sections.get(names.get(clone.upper(), clone), {})
        field = next((key for key in values
                      if str(key).lower() == 'prerequisite.negative'), 'Prerequisite.Negative')
        exclusions = [item for item in comma_items(values.get(field, ''))
                      if item.upper() not in {
                          sibling.upper(), sibling_source, f'MORP{sibling_source}',
                          'NONE', '<NONE>',
                      }]
        if not unlimited_buildings:
            exclusions.append(sibling)
        updates.setdefault(clone, {})[field] = ','.join(unique_in_order(exclusions)) or None
    return updates


def portable_structure_map_rules(lines, clone_handled, owned_clone_ids, **options):
    """Map adapter shared by campaign and standalone generation."""
    return portable_structure_reference_rules(
        all_section_value_maps_preserve(lines), clone_handled, owned_clone_ids,
        **options,
    )

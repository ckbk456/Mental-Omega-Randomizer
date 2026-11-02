"""Shared campaign/co-op pool selection with optional native challenges."""

from collections.abc import MutableSet

from randomizer.missions.catalogue import normalize_faction
from randomizer.missions.unified import mission_pool_cell, normalize_pool_selection


class MissionExclusions(MutableSet):
    """A writable view of base-map and shared challenge exclusions."""

    def __init__(self, base, challenges, *, coop=None):
        self.base, self.challenges = base, challenges
        self.coop = coop if coop is not None else base

    def __contains__(self, code):
        return code in self.base or code in self.challenges or code in self.coop

    def __iter__(self):
        return iter(set(self.base) | set(self.challenges) | set(self.coop))

    def __len__(self):
        return len(set(self.base) | set(self.challenges) | set(self.coop))

    @classmethod
    def _from_iterable(cls, values):
        return set(values)

    def add(self, code):
        target = (self.challenges if code.upper().startswith('C_') else
                  self.coop if code.upper().startswith('COOP_') else self.base)
        target.add(code)

    def discard(self, code):
        self.base.discard(code)
        self.challenges.discard(code)
        self.coop.discard(code)

    def update(self, values):
        for code in values:
            self.add(code)

    def difference_update(self, values):
        for code in values:
            self.discard(code)


def is_challenge(mission):
    return bool(mission and (mission.get('mission_category') == 'challenge'
                             or mission.get('challenge_name')))


def select_mission_pool(missions, *, category, campaign='All Campaigns',
                        include_challenges=False, excluded_codes=(),
                        excluded_challenge_codes=(), selection=None):
    """Challenges supplement the base pool and ignore its campaign faction.

    Keep the legacy challenge-only category readable for existing saved runs.
    Per-map house and color choices are validated at launch, not at generation.
    """
    selected_cells = (set(normalize_pool_selection(selection)['cells'])
                      if selection is not None else None)
    if category == 'mixed' and selected_cells is None:
        raise ValueError('Mixed runs require a mission pool selection.')
    excluded = {str(code).upper() for code in excluded_codes}
    challenge_excluded = {str(code).upper() for code in excluded_challenge_codes}
    result = []
    seen = set()
    for mission in missions:
        code = mission['code'].upper()
        if code in excluded or code in seen:
            continue
        seen.add(code)
        if selected_cells is not None:
            if mission.get('skirmish'):
                continue
            if (mission_pool_cell(mission) in selected_cells
                    and (not is_challenge(mission) or code not in challenge_excluded)):
                result.append(mission)
            continue
        if is_challenge(mission):
            if ((category == 'challenge' or include_challenges)
                    and mission['code'].upper() not in challenge_excluded):
                result.append(mission)
        elif category != 'challenge':
            cooperative = bool(mission.get('coop_name'))
            if cooperative != (category == 'coop'):
                continue
            if campaign == 'All Campaigns' or normalize_faction(mission.get('side', '')) == campaign:
                result.append(mission)
    return result

"""Export real installed maps with an opt-in structure tryout loadout.

Reads an existing run, adds the selected access rewards in memory, and writes
playable map/manifest copies plus an integrity report to a separate directory.
It never saves over a run, installs a map, launches the game or operates the UI.
"""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from randomizer.core.paths import GAME_ROOT
from randomizer.challenges.catalogue import (
    discover_challenge_missions, map_config, allowed_colors,
)
from randomizer.coop.prototype import build_manifest, rebuild_from_manifest
from randomizer.maps.assets import deploy_generated_unit_art
from randomizer.maps.ini import all_section_value_maps_preserve
from randomizer.rewards.definitions import REWARD_POOL
from randomizer.rewards.structures import PORTABLE_STRUCTURE_IDS, STRUCTURE_ART_TEMPLATES
from randomizer.rewards.roster import randomizer_unit_roster
from randomizer.maps.structure_buildup import shp_frame_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--maps', nargs='+')
    parser.add_argument('--lab-route', action='store_true',
                        help='Export a lab-only tryout with ordinary building caps.')
    args = parser.parse_args()
    original = args.run.read_bytes()
    state = json.loads(original)
    rewards = [reward for reward in REWARD_POOL
               if reward.get('access_unit') in PORTABLE_STRUCTURE_IDS]
    state = deepcopy(state)
    existing = {entry.get('name') for entry in state.get('starting_rewards', [])}
    state.setdefault('starting_rewards', []).extend(
        reward for reward in rewards if reward['name'] not in existing
    )
    if args.lab_route:
        state['starting_rewards'] = [r for r in state['starting_rewards']
                                     if r.get('name') != 'Rejuvenator Access']
        state.setdefault('reward_settings', {})['unlimited_buildings'] = False
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'tryout-loadout.json').write_text(
        json.dumps({'source_run_sha256': hashlib.sha256(original).hexdigest(),
                    'added_access_rewards': [r['name'] for r in rewards]}, indent=2),
        encoding='utf-8',
    )
    names = args.maps or [Path(m['scenario']).stem for m in discover_challenge_missions(GAME_ROOT)]
    templates = randomizer_unit_roster()[2]
    report = {'source_run_unchanged': None, 'exports': [], 'failures': []}
    for name in names:
        try:
            options = {'mission_category': 'coop', 'player_count': 2}
            if name.startswith('c_'):
                _source, _key, metadata, country, _family = map_config(GAME_ROOT, name)
                options = {'mission_category': 'challenge', 'player_count': 1,
                           'country': country, 'player_colors': [allowed_colors(metadata)[0]]}
            manifest, data = build_manifest(GAME_ROOT, state, name, **options)
            replay = rebuild_from_manifest(GAME_ROOT, manifest)
            if isinstance(replay, tuple):
                replay = replay[-1]
            destination = args.output / name
            destination.mkdir(exist_ok=True)
            map_path = destination / manifest['map_file']
            map_path.write_bytes(data)
            (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
            parsed = all_section_value_maps_preserve(data.decode('latin-1').splitlines())
            by_image = {}
            for key, fields in parsed.items():
                lowered = {k.lower(): v for k, v in fields.items()}
                image = lowered.get('image', '').upper()
                if image:
                    by_image.setdefault(image, []).append((key, lowered))
            missing = []
            locks = []
            unsellable = []
            for source in sorted(PORTABLE_STRUCTURE_IDS):
                image = str(templates[source].get('Image', '')).upper()
                copies = by_image.get(image, [])
                if not copies:
                    missing.append(source)
                for key, fields in copies:
                    if fields.get('buildlimit') == '0' or int(fields.get('techlevel', '1')) < 0:
                        locks.append(key)
                    if fields.get('unsellable', 'no').lower() not in {'no', 'false', '0'}:
                        unsellable.append(key)
            art_path, aliases = deploy_generated_unit_art(
                map_path, target_path=destination / 'artmo.ini',
            )
            buildup_frames = {}
            for art_id, values in aliases.items():
                fields = {str(k).lower(): v for k, v in values.items()}
                if (art_id not in STRUCTURE_ART_TEMPLATES or 'foundation' not in fields
                        or fields.get('tooverlay')):
                    continue
                buildup = fields.get('buildup', '')
                if not buildup:
                    raise ValueError(f'{art_id} has no build/sell artwork.')
                buildup_frames[art_id] = shp_frame_count(
                    (destination / (buildup.lower() + '.shp')).read_bytes()
                )
            entry = {'map': name, 'sha256': hashlib.sha256(data).hexdigest(),
                     'replay_matches': replay == data, 'missing_structures': missing,
                     'locked_structures': locks, 'art_aliases': len(aliases),
                     'unsellable_structures': unsellable, 'buildup_frames': buildup_frames,
                     'sprite_files': len(list(destination.glob('*.shp')))}
            report['exports'].append(entry)
            if missing or locks or unsellable or replay != data:
                report['failures'].append(entry)
            print(f'{name}: {len(PORTABLE_STRUCTURE_IDS)-len(missing)} structures, '
                  f'replay={replay == data}, locks={len(locks)}', flush=True)
        except Exception as exc:
            report['failures'].append({'map': name, 'error': f'{type(exc).__name__}: {exc}'})
            print(f'{name}: {type(exc).__name__}: {exc}', flush=True)
    report['source_run_unchanged'] = args.run.read_bytes() == original
    (args.output / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return int(bool(report['failures']) or not report['source_run_unchanged'])


if __name__ == '__main__':
    raise SystemExit(main())

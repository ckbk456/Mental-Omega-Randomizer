"""Atomic, independent run saves with non-destructive legacy imports."""

from datetime import datetime, timezone
from pathlib import Path
import uuid

from randomizer.core.storage import atomic_write_json, read_json_object


LEGACY_RUNS = (
    ('randomizer_state.json', 'Campaign'),
    ('randomizer_coop_state.json', 'Co-op'),
    ('challenge_solo_state.json', 'Solo challenges'),
    ('challenge_coop_state.json', 'Co-op challenges'),
)


class RunLibrary:
    def __init__(self, app_dir):
        self.app_dir = Path(app_dir)
        self.directory = self.app_dir / 'runs'
        self.index_path = self.directory / 'library.json'

    def index(self):
        if self.index_path.exists():
            data = read_json_object(self.index_path)
            if data.get('version') != 1 or not isinstance(data.get('runs'), dict):
                raise ValueError('Unsupported run library. Existing saves were left untouched.')
            return data
        return {'version': 1, 'active_run_id': '', 'runs': {}, 'legacy_imports': {}}

    def path(self, run_id):
        # Saved/network data never controls a filesystem path.
        return self.directory / (str(uuid.UUID(str(run_id))) + '.json')

    def load(self, run_id):
        state = read_json_object(self.path(run_id))
        if state.get('run_id') != run_id:
            raise ValueError('Run save identity does not match its library entry.')
        return state

    def save(self, state, *, activate=True, label=None):
        if not state or not state.get('mission_order'):
            return
        run_id = state.setdefault('run_id', str(uuid.uuid4()))
        index = self.index()
        previous = index['runs'].get(run_id, {})
        atomic_write_json(self.path(run_id), state, indent=None)
        index['runs'][run_id] = {
            'label': label or previous.get('label') or str(state.get('seed', 'Run')),
            'seed': state.get('seed', ''),
            'category': state.get('mission_category', 'campaign'),
            'progression_mode': state.get('progression_mode', 'Mission List'),
            'created_at': state.get('created_at', ''),
            'updated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'completed': len(state.get('completed_missions', ())),
            'missions': len(state.get('mission_order', ())),
            'legacy_source': previous.get('legacy_source', ''),
        }
        if activate:
            index['active_run_id'] = run_id
        atomic_write_json(self.index_path, index)

    def import_legacy(self, preferred_filename='randomizer_state.json'):
        """Copy each old run once; leave source documents byte-for-byte intact."""
        errors = []
        for filename, label in LEGACY_RUNS:
            index = self.index()
            path = self.app_dir / filename
            if filename in index['legacy_imports'] or not path.exists():
                continue
            try:
                state = read_json_object(path)
                if not state.get('mission_order'):
                    continue
                # A legacy file might already contain an identity from another
                # profile. Imports are independent, including identical seeds.
                state['run_id'] = str(uuid.uuid4())
                self.save(state, activate=False, label=f'{label} · {state.get("seed", "Imported run")}')
                index = self.index()
                index['legacy_imports'][filename] = state['run_id']
                index['runs'][state['run_id']]['legacy_source'] = filename
                atomic_write_json(self.index_path, index)
            except (OSError, ValueError) as exc:
                errors.append(f'{filename}: {exc}')
        index = self.index()
        if not index['active_run_id']:
            index['active_run_id'] = index['legacy_imports'].get(preferred_filename, '')
            atomic_write_json(self.index_path, index)
        return errors

    def activate(self, run_id):
        state = self.load(run_id)
        index = self.index()
        if run_id not in index['runs']:
            raise ValueError('This run is not in the library.')
        index['active_run_id'] = run_id
        atomic_write_json(self.index_path, index)
        return state

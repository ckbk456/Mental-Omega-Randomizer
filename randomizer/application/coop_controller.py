"""Co-op settings, shared Grid lobby, suggestions, and direct game launch."""

import copy
import json
import os
import queue
import re
import secrets
import threading
import traceback
from tkinter import messagebox

from .coop_connection_controller import CoopConnectionController
from .challenge_lobby import ChallengeLobbyController
from .coop_shop_controller import CoopShopController, CoopShopSetupRequired
from randomizer.config.player import save_config
from randomizer.coop import feature
from randomizer.coop.direct import host_session, join_session
from randomizer.coop.lobby import LOBBY_PORT, Lobby, decode_state, encode_state
from randomizer.coop.archipelago import shared_run_state, shared_shop_inventory
from randomizer.coop.prototype import build_manifest, shop_unit_loadout
from randomizer.coop.shop_stage import recovery_result_message, stage_snapshot
from randomizer.coop.victory import victory_marker_name
from randomizer.core.diagnostics import event as log_event
from randomizer.core.game_shutdown import GameShutdownWatch
from randomizer.core.paths import DEBUG_LOG, GAME_ROOT
from randomizer.rewards.arsenal import ARSENAL_MODE
from randomizer.shop.model import RunStatus
from randomizer.missions.pool import MissionExclusions
from randomizer.missions.unified import normalize_pool_selection
from randomizer.ui.config import GAME_SPEEDS


def normalize_network_mode(value):
    """Migrate all previously offered connection modes to ZeroTier."""
    return 'zerotier'


class CoopController(CoopShopController, ChallengeLobbyController, CoopConnectionController):
    def party_connection_available(self):
        if self.final_fortress_mode_selected():
            return False
        if self.shop_mode_selected():
            return bool(feature.COOP_FEATURE_ENABLED and self.coop_mode_var.get())
        return bool(feature.COOP_FEATURE_ENABLED and (
            self.coop_mode_var.get() or self.state.get('coop_mode') or self.adaptive_challenge_run_active()
            or self.progression_mode_var.get() in ('Grid Mode', 'Mission List')))

    def party_run_shareable(self):
        if self.shop_mode_selected() or self.final_fortress_mode_selected():
            return False
        return bool(self.state.get('seed') and (
            self.state.get('coop_mode') or self.adaptive_challenge_run_active()))

    def refresh_party_summary(self):
        variable = getattr(self, 'party_launch_summary_var', None)
        if variable is None:
            return
        mission = self.selected_mission()
        lobby = getattr(self, '_coop_lobby', None)
        connected = bool(lobby and lobby.connected)
        if self.shop_mode_selected():
            text = ('Shop run · Two humans play the selected co-op mission offer.'
                    if self.coop_mode_var.get() else
                    'Shop run · Play the selected campaign mission offer solo.')
            if connected:
                text += f'\nParty: {lobby.peer} connected. The host selects each mission.'
            variable.set(text)
            return
        if not mission:
            text = 'Select a mission to see its player setup.'
        elif self.challenge_mission():
            partner = (self.selected_challenge_partner() if self.adaptive_challenge_run_active() else
                       'Friend' if self.state.get('coop_mode') else
                       'AI teammate' if (self.challenge_ai_selected()
                                        or self.automatic_challenge_helper(mission)) else 'Solo')
            text = ('Challenge · ' + ('Host chooses participants' if self.coop_guest_connected() else partner)
                    + '. Choose houses and different colors before launch.')
            if mission.get('requires_teammate'):
                text += '\nThis challenge needs an AI teammate or a friend.'
        elif mission.get('coop_name'):
            text = 'Co-op mission · Two human players required. The map fixes both player houses.'
        else:
            text = 'Campaign mission · Solo, with the scripted player house.'
            if connected:
                text += '\nYour friend stays connected and waits for the next team mission.'
        if mission and mission.get('unavailable_locally'):
            text += '\nThis mission is not installed here. Other installed team missions remain playable.'
        if self.coop_guest_connected() and getattr(self, '_coop_host_phase', '') == 'solo':
            text += '\nHost is playing solo. Waiting for the next team mission.'
        text += '\n' + (f'Party: {lobby.peer} connected. Host controls game speed.' if connected
                          else 'Party: playing locally. Invite a friend between missions.')
        variable.set(text)

    def refresh_coop_controls(self):
        if not hasattr(self, 'coop_connection_button'):
            return
        available = feature.COOP_FEATURE_ENABLED
        shop = self.shop_mode_selected() and not self.final_fortress_mode_selected()
        self.coop_controls_frame.grid_remove() if shop else self.coop_controls_frame.grid()
        self.shop_coop_row.grid() if shop else self.shop_coop_row.grid_remove()
        category = self.selected_mission_category()
        challenge = self.challenge_mission()
        mission = self.selected_mission()
        team_mission = bool(mission and mission.get('coop_name'))
        enabled = self.party_connection_available()
        guest = self.coop_guest_connected()
        self.rewards_per_check_label.configure(text='Rewards per check')
        for button in (self.coop_connection_button, self.shop_coop_connection_button):
            button.configure(state='normal' if available else 'disabled')
            button.grid() if enabled else button.grid_remove()
        process = getattr(self, 'active_game_process', None)
        active_game = process is not None and process.poll() is None
        run = getattr(self, 'shop_run', None)
        active_shop = bool(self.shop_mode_selected() and run is not None
                           and run.status is RunStatus.ACTIVE)
        locked = (bool(getattr(self, '_coop_lobby', None))
                  or bool(getattr(self, '_coop_busy', False))
                  or active_game or self.shop_launch_active()
                  or self.gameplay_settings_locked())
        for name in ('progression_mode_combo', 'shop_progression_mode_combo'):
            widget = getattr(self, name, None)
            if widget is not None:
                widget.configure(state='disabled' if locked else 'readonly')
        self.coop_mode_check.configure(state='disabled')
        self.coop_mode_check.grid_remove()
        # Shop's category switch belongs to its pool setup, not the Party
        # panel. Its container decides visibility; do not re-grid it here.
        self.shop_coop_mode_check.configure(state='disabled' if locked or not available else 'normal')
        for widget in (self.coop_player_count_combo, self.shop_coop_player_count_combo):
            widget.configure(state='disabled' if locked or active_shop else 'readonly')
        for prefix in ('', 'shop_'):
            for widget in getattr(self, prefix + 'challenge_fields', ()):
                widget.grid_remove()
            country = getattr(self, prefix + 'challenge_country_combo', None)
            if country is not None:
                country.configure(state='disabled' if locked else 'readonly')
        self._refresh_coop_connection_fields()
        for button in (self.launch_selected_button, self.compact_launch_button):
            button.configure(text='Suggest Mission' if guest else 'Launch Selected Mission')
        for button in (self.debug_complete_button, self.compact_complete_button):
            button.configure(text=(
                'Record Challenge Victory' if challenge else
                'Record Co-op Victory' if team_mission else 'Mark Mission Complete'
            ))
        self.sync_debug_completion_controls()
        self.refresh_challenge_support_controls()
        self.refresh_game_speed_controls()
        self.refresh_challenge_player_controls()
        self.refresh_party_summary()
        if challenge:
            self.difficulty_combo.configure(state='disabled' if guest or active_game
                                            or getattr(self, '_coop_busy', False) else 'readonly')
        refresh = getattr(self, 'refresh_setup_flow', None)
        if callable(refresh):
            refresh()

    def active_mission_exclusions(self):
        category = getattr(self, 'selected_setup_category', self.selected_mission_category)()
        if category == 'mixed':
            return MissionExclusions(
                self.excluded_mission_codes, self.excluded_challenge_mission_codes,
                coop=self.excluded_coop_mission_codes,
            )
        if category == 'challenge':
            return self.excluded_challenge_mission_codes
        base = (self.excluded_coop_mission_codes if category == 'coop'
                else self.excluded_mission_codes)
        return MissionExclusions(base, self.excluded_challenge_mission_codes)

    def coop_guest_connected(self):
        lobby = getattr(self, '_coop_lobby', None)
        return bool(lobby and lobby.role == 'guest')

    def on_coop_mode_changed(self):
        if self.coop_mode_var.get() and not feature.COOP_FEATURE_ENABLED:
            self.coop_mode_var.set(False)
            return
        process = getattr(self, 'active_game_process', None)
        if (self.gameplay_settings_locked() or self.shop_launch_active()
                or getattr(self, '_coop_busy', False)
                or getattr(self, '_coop_lobby', None)
                or (process is not None and process.poll() is None)):
            self.coop_mode_var.set(bool(self.config.get('coop_mode', False)))
            self.restore_mission_setup_from_config()
            return
        self.initialize_challenge_defaults()
        enabled = bool(self.coop_mode_var.get())
        self.select_shop_repository()
        self.config['coop_mode'] = enabled
        self.config['mission_category'] = self.selected_mission_category()
        self.config['challenge_player_count'] = self.selected_challenge_player_count()
        self.config['challenge_country'] = self.challenge_country_var.get()
        if (self.selected_mission_category() == 'challenge'
                and self.progression_mode_var.get() == 'Shop Mode'):
            self.progression_mode_var.set('Grid Mode')
        self.config['progression_mode'] = self.progression_mode_var.get()
        self.refresh_coop_controls()
        self.config['campaign_filter'] = self.campaign_var.get()
        save_config(self.config)
        self.state = self.load_state()
        if (self.selected_mission_category() == 'challenge' and self.state
                and self.state.get('challenge_player_count', 1)
                != self.selected_challenge_player_count()):
            # Keep the saved run on disk; a different setup needs a new seed.
            self.state = {}
        self.migrate_state()
        if self.state and not self.shop_mode_selected():
            self.progression_mode_var.set(self.state.get('progression_mode', 'Grid Mode'))
            self.reward_mode_var.set(self.state.get('reward_mode', self.reward_mode_var.get()))
            self.campaign_var.set(self.state.get('campaign_filter', self.campaign_var.get()))
            self.mission_goal_var.set(self.state.get('mission_goal', self.mission_goal_var.get()))
            self.rewards_per_check_var.set(self.state.get(
                'rewards_per_check', self.rewards_per_check_var.get()
            ))
        self.apply_missions(self.load_missions())
        if self.shop_mode_selected():
            self.sync_shop_workspace()
            self.refresh_shop_mode()
        self.grid_render_signature = None
        self.redraw_progression_views()
        self.update_header_summary()
        self.refresh_progress_view()
        self.refresh_setting_states()
        self._record_coop_log(
            'Challenge map pool selected.' if self.selected_mission_category() == 'challenge'
            else 'Co-op map pool selected.' if enabled else 'Campaign map pool selected.'
        )

    def _connect_coop(self, role, name, address, *, pairing_code=''):
        if not feature.COOP_FEATURE_ENABLED:
            return
        if getattr(self, '_fortress_lobbies', None):
            messagebox.showwarning('Co-op', 'Disconnect the Fortress lobby before connecting another mode.')
            return
        if getattr(self, '_coop_lobby', None):
            return
        if getattr(self, '_coop_busy', False):
            messagebox.showwarning('Co-op', 'Wait for the current game preparation to finish.')
            return
        session = getattr(self, '_archipelago_session', None)
        if role == 'guest' and session is not None and session.running:
            messagebox.showwarning(
                'Co-op Archipelago',
                'Host owns the shared AP slot. Disconnect this guest AP session before joining.',
            )
            return
        if self.active_game_process is not None and self.active_game_process.poll() is None:
            messagebox.showwarning('Co-op', 'Close current game first.')
            return
        if self.shop_mode_selected():
            run = self.shop_repository.load_run()
            if run is not None and run.status is RunStatus.ACTIVE:
                try:
                    stage_snapshot(run)
                except ValueError as exc:
                    messagebox.showwarning('Co-op Shop', str(exc))
                    return
            if run is None and role == 'host':
                messagebox.showwarning('Co-op', 'Start a Shop run first.')
                return
            if run is not None and run.status is not RunStatus.ACTIVE and role == 'host':
                try:
                    recoverable = recovery_result_message(run) is not None
                except ValueError as exc:
                    messagebox.showwarning('Co-op', str(exc))
                    return
                if not recoverable:
                    messagebox.showwarning(
                        'Co-op', 'This Shop run has ended. Start a new co-op Shop run before hosting.'
                    )
                    return
            if run is not None and (not run.eligible_mission_codes or any(
                    not str(code).startswith('COOP_')
                    for code in run.eligible_mission_codes)):
                messagebox.showwarning('Co-op', 'Start a Shop run from the co-op map pool.')
                return
        elif role == 'host' and not self.party_run_shareable():
            messagebox.showwarning('Party', 'Generate or load a mixed, challenge, or co-op run before hosting.')
            return
        try:
            pairing_code = pairing_code.strip()
            port = LOBBY_PORT
            if not 16 <= len(pairing_code) <= 128:
                raise ValueError('Enter the host pairing code (16–128 characters).')
            lobby = Lobby(GAME_ROOT, role, name.strip(), address=address.strip(),
                          port=port, pairing_code=pairing_code)
        except (ValueError, OSError) as exc:
            self._record_coop_log('Co-op connection failed: ' + str(exc), error=True)
            messagebox.showerror('Co-op', self._coop_safe_message(exc))
            return
        self.config['coop_network_mode'] = normalize_network_mode(
            self.config.get('coop_network_mode')
        )
        self.config['coop_role'] = 'Host' if role == 'host' else 'Join'
        self.config['player_name'] = lobby.name
        if role == 'guest':
            self._coop_local_pool_selection = copy.deepcopy(getattr(self, 'mission_pool_selection', None))
            self._coop_local_config_snapshot = copy.deepcopy(self.config)
            status = getattr(self, 'archipelago_status_var', None)
            if status is not None:
                self._coop_local_ap_status = status.get()
            self._coop_local_ap_views = {
                key: copy.deepcopy(getattr(self, key, {}))
                for key in ('_archipelago_slot_data', '_archipelago_location_groups',
                            '_archipelago_local_victories', '_archipelago_allowed_locations')
            }
            self.config['coop_last_host'] = address.strip()
            names = ('campaign_var', 'reward_mode_var', 'seed_var', 'difficulty_var',
                     'progression_mode_var', 'mission_goal_var', 'rewards_per_check_var',
                     'selected_index', 'mission_category_var', 'challenge_player_count_var',
                     'challenge_country_var', 'coop_mode_var', 'game_speed_var',
                     'include_challenge_missions_var', 'challenge_partner_var', 'setup_category_var')
            self._coop_local_snapshot = (copy.deepcopy(self.state), {
                key: getattr(self, key).get() for key in names if hasattr(self, key)
            })
        save_config(self.config)
        self._coop_lobby = lobby
        self._coop_progression_mode = self.progression_mode_var.get()
        self._coop_peer_options = None
        self.ensure_challenge_player_options()
        self._coop_connection_error = False
        self._coop_shop_ready = False
        self._coop_shop_stage_digest = ''
        self._refresh_coop_connection_fields()
        self._set_coop_status('Waiting for guest…' if role == 'host' else 'Connecting…')
        self._record_coop_log(f'Co-op starting as {role}; lobby TCP {port}.')
        self.refresh_coop_controls()
        lobby.start()
        self.after(100, self._poll_coop_lobby)

    def disconnect_coop(self):
        process = getattr(self, 'active_game_process', None)
        if process is not None and process.poll() is None:
            self._record_coop_log('Close the active game before disconnecting.', error=True)
            return
        lobby = getattr(self, '_coop_lobby', None)
        if not lobby:
            return
        if (getattr(self, '_coop_busy', False) and lobby.connected
                and not getattr(self, '_coop_connection_error', False)):
            self._record_coop_log('Wait for mission preparation to finish before leaving the party.', error=True)
            return
        was_guest = lobby.role == 'guest'
        lobby.close()
        self._coop_lobby = None
        if getattr(self, '_coop_pending_launch', None):
            self._coop_busy = False
        self.__dict__.pop('_coop_progression_mode', None)
        self._coop_peer_options = None
        self.__dict__.pop('_coop_pending_launch', None)
        self.__dict__.pop('_coop_party_activity', None)
        self.__dict__.pop('_coop_host_phase', None)
        self._coop_shop_ready = False
        self._coop_shop_stage_digest = ''
        if was_guest:
            selection = self.__dict__.pop('_coop_local_pool_selection', None)
            if selection is not None:
                self.mission_pool_selection = selection
            restored = self.__dict__.pop('_coop_local_config_snapshot', None)
            if restored is not None:
                # These preferences belong to the person, not the host's run.
                for key in ('coop_challenge_country', 'coop_challenge_color',
                            'coop_network_mode', 'coop_role', 'player_name', 'coop_last_host',
                            'dark_mode', 'hide_reward_details', 'hide_locked_grid_missions'):
                    if key in self.config:
                        restored[key] = copy.deepcopy(self.config[key])
                self.config = restored
                save_config(self.config)
            status = getattr(self, 'archipelago_status_var', None)
            if status is not None:
                status.set(self.__dict__.pop('_coop_local_ap_status', 'Disconnected'))
            for key, value in self.__dict__.pop('_coop_local_ap_views', {}).items():
                setattr(self, key, value)
            snapshot = self.__dict__.pop('_coop_local_snapshot', None)
            if snapshot:
                self.state, settings = snapshot
                for key, value in settings.items():
                    getattr(self, key).set(value)
                self.apply_missions(self.load_missions())
            else:
                self.state = self.load_state()
                self.migrate_state()
            self._refresh_coop_state_views()
            self.refresh_unified_pool()
            refresh_library = getattr(self, 'refresh_run_library', None)
            if callable(refresh_library):
                refresh_library()
        self._refresh_coop_connection_fields()
        if not getattr(self, '_coop_connection_error', False):
            self._set_coop_status('Disconnected.')
        self._record_coop_log('Co-op lobby disconnected.')
        self.refresh_coop_controls()
        if self.shop_mode_selected():
            self.refresh_shop_mode()

    def _refresh_coop_state_views(self):
        for key in ('_active_reward_settings_cache', '_canonical_earned_rewards_cache',
                    '_unlock_dashboard_sources_cache', '_configured_reward_pool_cache'):
            self.__dict__.pop(key, None)
        self._enemy_buffs_view_dirty = True
        self.grid_render_signature = None
        self._coop_applying_selection = True
        try:
            self.sync_shop_workspace()
            self.redraw_mission_tree()
            self.redraw_progression_views()
            self.refresh_progress_view()
            self.update_header_summary()
            self.refresh_setting_states()
            self.refresh_coop_controls()
        finally:
            self._coop_applying_selection = False

    def _poll_coop_lobby(self):
        lobby = getattr(self, '_coop_lobby', None)
        if not lobby:
            return
        try:
            while True:
                event = lobby.events.get_nowait()
                if event[0] == 'status':
                    self._record_coop_log('Co-op: ' + event[1])
                    self._set_coop_status(event[1])
                elif event[0] == 'diagnostic':
                    label, details = event[1]
                    log_event(label, **details)
                    self._record_coop_log(label + ': ' + json.dumps(details, sort_keys=True))
                elif event[0] == 'listening':
                    self._record_coop_log(f'Co-op lobby listening on TCP {event[1]}.')
                elif event[0] == 'connected':
                    self._record_coop_log(f'Co-op lobby connected to {event[1]}.')
                    self.refresh_coop_controls()
                    self._set_coop_status(f'Connected to {event[1]}. Host selects and launches.')
                    if lobby.role == 'host':
                        self.coop_publish_state()
                    self.publish_challenge_player_options()
                elif event[0] == 'message':
                    self._handle_coop_message(lobby, event[1])
                elif event[0] == 'error':
                    self._record_coop_log('Co-op lobby: ' + event[1], error=True)
                    self._coop_connection_error = True
                    self._set_coop_status('Disconnected: ' + event[1])
                elif event[0] == 'disconnected':
                    self.disconnect_coop()
                    return
        except queue.Empty:
            pass
        except CoopShopSetupRequired as exc:
            self._record_coop_log('Co-op Shop setup required: ' + str(exc), error=True)
            self._coop_connection_error = True
            self.disconnect_coop()
            # Disconnect restores the guest's previous settings first. Show the
            # local Shop setup afterward, without replacing an existing run.
            self.progression_mode_var.set('Shop Mode')
            run = self.shop_repository.load_run()
            if run is None or run.status is not RunStatus.ACTIVE:
                self.seed_var.set(exc.seed)
            self.sync_shop_workspace()
            self.workspace_tabs.select(self.settings_tab)
            self.refresh_setting_states()
            self._set_coop_status('Shop setup required. Start a matching run, then reconnect.')
            messagebox.showwarning('Co-op Shop Setup', str(exc), parent=self)
            return
        except Exception as exc:
            self._record_coop_log('Co-op lobby message failed: ' + str(exc), error=True)
            self._coop_connection_error = True
            self._set_coop_status('Disconnected: ' + str(exc))
            self.disconnect_coop()
            return
        self._publish_party_activity()
        self.after(100, self._poll_coop_lobby)

    def _publish_party_activity(self):
        lobby = getattr(self, '_coop_lobby', None)
        if not (self.adaptive_challenge_run_active() and lobby and lobby.connected and lobby.role == 'host'):
            return
        process = getattr(self, 'active_game_process', None)
        solo = bool(not getattr(self, '_coop_busy', False) and (
            getattr(self, '_challenge_preparing', False)
            or (process is not None and process.poll() is None)))
        phase = 'solo' if solo else 'ready'
        identity = (self.state.get('run_id'), phase)
        if identity == getattr(self, '_coop_party_activity', None):
            return
        try:
            lobby.send({'type': 'party_status', 'run_id': self.state.get('run_id'), 'phase': phase})
            self._coop_party_activity = identity
        except OSError as exc:
            self._record_coop_log('Party status sync failed: ' + str(exc), error=True)

    def _shared_mission_summaries(self):
        """Display metadata only; it never authorizes launching a missing map."""
        return {code: {key: mission[key] for key in ('title', 'side') if key in mission}
                for code in self.state.get('mission_order', ())
                if (mission := self.mission_lookup().get(code))}

    def _append_unavailable_host_missions(self, state, codes):
        summaries = state.get('party_mission_summaries')
        if not isinstance(summaries, dict):
            raise ValueError('Host omitted the shared run mission catalogue.')
        for code in codes:
            if code in self._mission_by_code:
                continue
            summary = summaries.get(code)
            if not isinstance(summary, dict):
                raise ValueError('Host omitted mission metadata for ' + code + '.')
            title = summary.get('title', code)
            side = summary.get('side', '')
            if not isinstance(title, str) or len(title) > 512 or side not in (
                    '', 'Allies', 'Soviets', 'Epsilon', 'Foehn', 'Mixed'):
                raise ValueError('Host sent invalid mission display metadata.')
            mission = {
                'index': len(self.missions) + 1, 'code': code, 'scenario': '',
                'title': title, 'side': side, 'briefing': 'Not installed on this computer.',
                'objectives': [], 'objective_count': 1, 'build_classification': 'base_build',
                'no_build': False, 'true_no_build': False, 'no_build_production': False,
                'operation': False, 'reward_class': 'act_1', 'reward_multiplier': 1,
                'unavailable_locally': True,
            }
            if code.startswith('COOP_'):
                mission['coop_name'] = code.lower()
            elif code.startswith('C_'):
                mission.update(mission_category='challenge', challenge_name=code.lower(),
                               coop_name=code.lower())
            self.missions.append(mission)
            self._mission_by_code[code] = mission

    def coop_publish_state(self):
        lobby = getattr(self, '_coop_lobby', None)
        if not (lobby and lobby.connected and lobby.role == 'host'):
            return
        if self.shop_mode_selected() and self.coop_mode_var.get():
            try:
                run = self.shop_repository.load_run()
                ap = self.state.get('archipelago')
                # A standalone Shop run leaves the previous Grid save loaded.
                # Only its own AP inventory may precede Shop stage sync: a Grid
                # snapshot would switch the guest out of Shop Mode.
                if (run is not None and self.state.get('coop_mode')
                        and self.state.get('progression_mode') == 'Shop Mode'
                        and self.state.get('seed') == run.seed
                        and isinstance(ap, dict) and ap.get('enabled')):
                    lobby.send({'type': 'archipelago_state',
                                'data': encode_state(shared_run_state(
                                    self.state, getattr(self, '_archipelago_slot_data', None)))})
                result = recovery_result_message(run)
                if result:
                    lobby.send(result)
                if run is not None and run.status is RunStatus.ACTIVE:
                    self.coop_publish_shop_stage()
            except (OSError, ValueError) as exc:
                self._record_coop_log('Co-op Shop recovery sync failed: ' + str(exc), error=True)
            return
        if not self.party_run_shareable():
            return
        try:
            shared = shared_run_state(self.state, getattr(self, '_archipelago_slot_data', None))
            if self.adaptive_challenge_run_active():
                shared['party_mission_summaries'] = self._shared_mission_summaries()
            lobby.send({'type': 'state', 'data': encode_state(shared)})
            self.coop_broadcast_selection()
            self.publish_challenge_player_options()
        except (OSError, ValueError) as exc:
            self._record_coop_log('Co-op state sync failed: ' + str(exc), error=True)

    def coop_broadcast_selection(self):
        lobby = getattr(self, '_coop_lobby', None)
        mission = self.selected_mission()
        if lobby and lobby.connected and lobby.role == 'host' and mission:
            try:
                lobby.send({'type': 'select', 'code': mission['code']})
                self.refresh_challenge_player_controls()
            except OSError as exc:
                self._record_coop_log('Co-op selection sync failed: ' + str(exc), error=True)

    def coop_selection_changed(self):
        if getattr(self, '_coop_applying_selection', False):
            return
        lobby = getattr(self, '_coop_lobby', None)
        mission = self.selected_mission()
        self.refresh_party_summary()
        if not (lobby and lobby.connected and mission and self.party_run_shareable()):
            return
        if lobby.role == 'host':
            self.coop_broadcast_selection()
        else:
            try:
                lobby.send({'type': 'suggest', 'code': mission['code']})
                self._record_coop_log(f'Suggested {mission["title"]} to host.')
            except OSError as exc:
                self._record_coop_log('Co-op suggestion failed: ' + str(exc), error=True)

    def _handle_coop_message(self, lobby, message):
        kind = message['type']
        if kind in {'prepare_request', 'prepare_ready'}:
            self._handle_party_prepare(lobby, message)
            return
        if self.receive_coop_shop_message(lobby, message):
            return
        if kind == 'player_options':
            self.receive_challenge_player_options(lobby, message)
            return
        if lobby.role == 'guest':
            if kind == 'party_status':
                if (not self.adaptive_challenge_run_active() or message.get('run_id') != self.state.get('run_id')
                        or message.get('phase') not in {'solo', 'ready'}):
                    raise ValueError('Party activity belongs to a different run.')
                self._set_coop_status(
                    'Host is playing solo. Waiting for the next team mission.'
                    if message['phase'] == 'solo' else 'Party ready. Host selects the next mission.'
                )
                self._coop_host_phase = message['phase']
                self.refresh_party_summary()
                return
            if kind in {'state', 'archipelago_state'}:
                state = decode_state(message.get('data', ''))
                if (kind == 'archipelago_state'
                        and state.get('progression_mode') != 'Shop Mode'):
                    raise ValueError('Host sent Grid state as Shop inventory. Update the host launcher.')
                category = state.get('mission_category') or 'coop'
                if category not in {'coop', 'challenge', 'mixed'}:
                    raise ValueError('Host sent an invalid multiplayer mission category.')
                if category == 'mixed' and (
                        state.get('progression_mode') not in {'Grid Mode', 'Mission List'}
                        or not isinstance(state.get('run_id'), str)
                        or not state['run_id'] or len(state['run_id']) > 128
                        or (state.get('archipelago') or {}).get('enabled')):
                    raise ValueError('Host sent unsupported mixed run settings.')
                if category == 'challenge' and (
                        type(state.get('challenge_player_count')) is not int
                        or state.get('challenge_player_count') not in (1, 2)
                        or state.get('progression_mode') == 'Shop Mode'
                        or (state.get('archipelago') or {}).get('enabled')):
                    raise ValueError('Host sent unsupported challenge run settings.')
                self.include_challenge_missions_var.set(bool(
                    (state.get('mission_pool_settings') or {}).get('include_challenge_missions', False)
                ))
                self.mission_category_var.set(category)
                self.challenge_player_count_var.set(str(state.get('challenge_player_count', 1)))
                self.sync_mission_transport_mode(category=category)
                # Host owns the mission pool; each player's lobby house is local.
                self.missions = self.load_missions()
                self._mission_by_code = {mission['code']: mission for mission in self.missions}
                codes = state.get('mission_order', [])
                available = {mission['code'] for mission in self.missions}
                if (not isinstance(codes, list) or not codes or len(codes) > 4096
                        or not all(isinstance(code, str) and re.fullmatch(r'[A-Z0-9_]{1,96}', code)
                                   for code in codes) or len(set(codes)) != len(codes)):
                    raise ValueError('Host sent an invalid mission order.')
                if category in {'mixed', 'challenge'}:
                    self._append_unavailable_host_missions(state, codes)
                    if category == 'mixed':
                        self.mission_pool_selection = normalize_pool_selection(state.get('mission_pool_selection'))
                elif not all(code in available for code in codes):
                    raise ValueError('Host co-op maps differ from installed catalogue.')
                self.state = state
                setup_category = getattr(self, 'setup_category_var', None)
                if setup_category is not None and category != 'mixed':
                    setup_category.set({'coop': 'Co-op', 'challenge': 'Challenges'}.get(category, 'Campaign'))
                ap = state.get('archipelago') or {}
                self._archipelago_slot_data = copy.deepcopy(ap.get('slot_data') or {})
                self._archipelago_location_groups = {}
                self._archipelago_local_victories = {}
                self._archipelago_allowed_locations = frozenset()
                cache = getattr(self, '_cache_archipelago_location_mappings', None)
                if callable(cache):
                    cache(self._archipelago_slot_data)
                for key, variable in (
                    ('seed', self.seed_var), ('campaign_filter', self.campaign_var),
                    ('reward_mode', self.reward_mode_var),
                    ('progression_mode', self.progression_mode_var),
                    ('mission_goal', self.mission_goal_var),
                    ('rewards_per_check', self.rewards_per_check_var),
                ):
                    if key in state:
                        variable.set(state[key])
                self._coop_progression_mode = self.progression_mode_var.get()
                if hasattr(self, 'archipelago_status_var'):
                    self.archipelago_status_var.set(
                        'Shared AP slot — host connected' if ap.get('enabled')
                        else 'Disconnected',
                    )
                if self.shop_mode_selected():
                    run = self.shop_repository.load_run()
                    updated = shared_shop_inventory(run, state)
                    if updated != run:
                        self.shop_repository.save_run(updated)
                    self.refresh_shop_mode()
                self._refresh_coop_state_views()
                self.refresh_unified_pool()
                self._record_coop_log(f'Host run synced: {len(codes)} maps, seed {state["seed"]}.')
                self.publish_challenge_player_options()
            elif kind == 'select':
                code = message.get('code')
                index = next((i for i, mission in enumerate(self.missions)
                              if mission['code'] == code), None)
                if index is not None:
                    self._coop_applying_selection = True
                    try:
                        if self.active_progression_mode() == 'Grid Mode':
                            self.select_grid_mission(index)
                        else:
                            self.selected_index.set(index)
                            self.refresh_progress_view(refresh_unlocks=False)
                    finally:
                        self._coop_applying_selection = False
                    self.refresh_challenge_player_controls()
                    self.refresh_party_summary()
                    if not self.challenge_mission(code) and not self.mission_lookup()[code].get('coop_name'):
                        self._set_coop_status('Host selected a solo campaign. Waiting for the next team mission.')
            elif kind == 'launch':
                code = message.get('code')
                mission = self.mission_lookup().get(code)
                if not mission or mission.get('unavailable_locally') or not mission.get('coop_name'):
                    raise ValueError('The selected team mission is not installed locally.')
                if self.adaptive_challenge_run_active() and message.get('run_id') != self.state.get('run_id'):
                    raise ValueError('Host launch belongs to a different run.')
                if self.shop_mode_selected() and self.coop_mode_var.get():
                    run = self.shop_repository.load_run()
                    if (run is None or run.status is not RunStatus.ACTIVE
                            or not run.mission_committed
                            or run.selected_mission_code != code):
                        raise ValueError('Host Shop launch differs from guest committed mission.')
                    self._shop_launch_run = run
                    self._shop_launch_victory_key = None
                    self._shop_launch_mission_pool = tuple(self._shop_run_mission_pool(run))
                elif code not in self.state.get('mission_order', []):
                    raise ValueError('Host selected map outside shared run.')
                session_token = message.get('session_token')
                if not isinstance(session_token, str) or len(session_token) < 24:
                    raise ValueError('Host sent invalid co-op game token.')
                if self.challenge_mission(code):
                    choices = message.get('player_options')
                    if (not isinstance(choices, dict)
                            or choices.get('guest') != self.own_challenge_player_options()):
                        raise ValueError('Your house or color changed while host launched. Reconnect and retry.')
                self._start_coop_game('guest', code, session_token=session_token)
        elif kind == 'challenge_victory':
            code = message.get('code')
            if (not self.challenge_mission(code)
                    or code != getattr(self, '_coop_active_game_code', None)
                    or message.get('session_token') != getattr(self, '_coop_active_game_token', None)
                    or type(message.get('game_id')) is not int
                    or message['game_id'] != getattr(self, '_coop_active_game_id', None)
                    or not self.challenge_run_identity_matches(
                        getattr(self, '_coop_challenge_launch_snapshot', None))):
                raise ValueError('Guest challenge result differs from the launched game.')
            if not self.is_mission_complete(code):
                self._record_coop_log(f'Guest verified native challenge team victory for {code}.')
                self._record_shared_victory(code, 'Co-op guest verified team victory')
        elif kind == 'suggest':
            code = message.get('code')
            mission = self.mission_lookup().get(code)
            if mission and code in self.state.get('mission_order', []):
                self._record_coop_log(f'{lobby.peer} suggests {mission["title"]} ({code}).')
                self._set_coop_status(f'{lobby.peer} suggests {mission["title"]}. Select it in Grid to play.')

    def _handle_party_prepare(self, lobby, message):
        """Check this one mission before either process begins preparing game files."""
        if not self.adaptive_challenge_run_active():
            raise ValueError('Party launch readiness requires a mixed or challenge run.')
        if message['type'] == 'prepare_request':
            if lobby.role != 'guest':
                raise ValueError('Only the host can request a team launch.')
            token, code = message.get('token'), message.get('code')
            if not isinstance(token, str) or not 24 <= len(token) <= 128:
                raise ValueError('Invalid party launch request.')
            mission = self.mission_lookup().get(code)
            reason = ''
            process = getattr(self, 'active_game_process', None)
            if message.get('run_id') != self.state.get('run_id'):
                reason = 'The shared run changed. Wait for it to synchronize.'
            elif not mission or mission.get('unavailable_locally') or not mission.get('coop_name'):
                reason = 'This team mission is not installed on the guest computer.'
            elif code not in self.state.get('mission_order', ()):
                reason = 'This mission is outside the shared run.'
            elif getattr(self, '_coop_busy', False) or (process is not None and process.poll() is None):
                reason = 'The guest is still finishing the previous mission.'
            elif self.challenge_mission(code):
                try:
                    expected = self.challenge_pair_options(mission)
                    if message.get('player_options') != expected:
                        reason = 'A player changed house or color. Wait for the choices to sync and retry.'
                except (OSError, ValueError) as exc:
                    reason = str(exc)
            lobby.send({'type': 'prepare_ready', 'token': token, 'run_id': self.state.get('run_id'),
                        'ready': not reason, 'reason': reason[:1200]})
            self._set_coop_status(reason or 'Ready for the host to launch this team mission.')
            return
        if lobby.role != 'host':
            raise ValueError('Only the guest can acknowledge a team launch.')
        pending = getattr(self, '_coop_pending_launch', None)
        if not pending or message.get('token') != pending['token']:
            return
        self._coop_pending_launch = None
        self._coop_busy = False
        self.refresh_coop_controls()
        if (message.get('run_id') != self.state.get('run_id')
                or pending['run_id'] != self.state.get('run_id')):
            self._set_coop_status('Run changed before launch. Select the mission again.')
            return
        if message.get('ready') is not True:
            reason = str(message.get('reason') or 'The guest is not ready.')[:1200]
            self._set_coop_status(reason)
            messagebox.showwarning('Party Not Ready', reason)
            return
        self._start_coop_game('host', pending['code'])

    def _expire_party_prepare(self, token):
        pending = getattr(self, '_coop_pending_launch', None)
        if not pending or pending['token'] != token:
            return
        self._coop_pending_launch = None
        self._coop_busy = False
        self.refresh_coop_controls()
        self._set_coop_status('Guest readiness timed out. Reconnect or try again.')

    def _record_shared_victory(self, code, source):
        if self.coop_guest_connected() or self.is_mission_complete(code):
            return False
        snapshot = getattr(self, '_coop_challenge_launch_snapshot', None)
        if snapshot and not self.challenge_run_identity_matches(snapshot):
            self._record_coop_log('Result belongs to a different run; no victory awarded.', error=True)
            return False
        token = getattr(self, '_coop_active_game_token', '')
        if self.adaptive_challenge_run_active():
            if not token or code != getattr(self, '_coop_active_game_code', None):
                return False
            identity = f'{self.state.get("run_id")}:{code}:victory:{token}'
            ledger = self.state.setdefault('party_completed_attempts', [])
            if identity in ledger:
                return False
            ledger.append(identity)
            del ledger[:-256]
        return self.unlock_mission_check(code, 'victory', source)

    def request_coop_launch(self):
        if not feature.COOP_FEATURE_ENABLED:
            messagebox.showwarning('Co-op', 'Co-op is disabled in this build.')
            return
        lobby = getattr(self, '_coop_lobby', None)
        mission = self.selected_mission()
        if self.challenge_mission() and not self.challenge_run_ready():
            return
        if not self.party_run_shareable() or mission is None or not mission.get('coop_name'):
            messagebox.showwarning('Party', 'Select a co-op mission or challenge in the active run.')
            return
        if getattr(self, '_coop_busy', False):
            return
        if mission['code'] not in set(self.unlocked_mission_codes()) | set(
                self.state.get('completed_missions', [])):
            messagebox.showwarning('Co-op', 'Selected co-op map is locked.')
            return
        if not lobby or not lobby.connected:
            messagebox.showwarning('Co-op', 'Connect both launchers first.')
            return
        if self.challenge_mission() and any(
                name.casefold() == 'computer' for name in (lobby.name, lobby.peer)):
            messagebox.showwarning('Challenges', 'Use human player names other than Computer.')
            return
        if lobby.role == 'guest':
            self.coop_selection_changed()
        elif self.adaptive_challenge_run_active():
            try:
                choices = self.challenge_pair_options(mission) if self.challenge_mission() else None
                pending = {'type': 'prepare_request', 'token': secrets.token_urlsafe(24),
                           'run_id': self.state.get('run_id'), 'code': mission['code'],
                           'player_options': choices}
                lobby.send(pending)
                self._coop_pending_launch = pending
                self._coop_busy = True
                self.refresh_coop_controls()
                self._set_coop_status('Checking the selected mission with your friend…')
                self.after(12000, lambda: self._expire_party_prepare(pending['token']))
            except (OSError, ValueError) as exc:
                messagebox.showwarning('Party Not Ready', str(exc))
        else:
            self._start_coop_game('host', mission['code'])

    def _start_coop_game(self, role, code, *, session_token=''):
        if not feature.COOP_FEATURE_ENABLED:
            return
        lobby = getattr(self, '_coop_lobby', None)
        if getattr(self, '_coop_busy', False) or not lobby or not lobby.connected:
            return
        if self.active_game_process is not None and self.active_game_process.poll() is None:
            messagebox.showwarning('Co-op', 'Close current game first.')
            return
        challenge = self.challenge_mission(code)
        player_options = None
        pair_options = None
        if challenge:
            try:
                player_options = self.own_challenge_player_options()
                pair_options = self.challenge_pair_options(self.mission_lookup()[code])
            except (ValueError, KeyError) as exc:
                messagebox.showwarning('Challenge Player Choices', str(exc))
                return
        self._coop_busy = True
        self._coop_preparing_lobby = lobby
        self.refresh_coop_controls()
        if role == 'host':
            session_token = secrets.token_urlsafe(24)
        self._coop_queue = queue.Queue()
        self._coop_active_game_code = code
        self._coop_active_game_role = role
        self._coop_active_game_token = session_token
        self._coop_challenge_launch_snapshot = (
            self.capture_challenge_run_identity()
            if challenge or self.mixed_run_active() else None
        )
        mission = self.mission_lookup().get(code)
        begin = getattr(self, '_begin_archipelago_mission_preparation', None)
        if callable(begin):
            begin(mission)
        state_snapshot = copy.deepcopy(self.state)
        game_speed = self.get_selected_game_speed_value()
        shop_run = (self.shop_repository.load_run()
                    if self.shop_mode_selected() and self.coop_mode_var.get()
                    else None)
        shop_profile = self.shop_profile if shop_run is not None else None
        difficulty = {'Casual': 'easy', 'Normal': 'normal',
                      'Mental': 'hard'}.get(self.difficulty_var.get(), 'normal')
        if shop_run is not None:
            level = self.shop_mission_difficulty_value(shop_run, code)
            if shop_run.assisted_mission_code == code:
                level = max(0, level - 1)
            difficulty = ('easy', 'normal', 'hard')[min(2, max(0, level))]
        self._record_coop_log(f'Preparing co-op map {code} as {role}.')
        self._set_coop_status('Preparing map and connecting game…')

        def worker():
            try:
                shop_loadout = (shop_unit_loadout(
                    shop_run, shop_profile, state=state_snapshot, mission=mission,
                ) if shop_run is not None else None)
                self.begin_direct_game_preparation()
                if role == 'host':
                    if not mission:
                        raise ValueError('Selected co-op map is missing.')
                    if shop_run is not None:
                        if (shop_run.status is not RunStatus.ACTIVE
                                or not shop_run.mission_committed
                                or shop_run.selected_mission_code != code):
                            raise ValueError('Host Shop mission is not committed.')
                        manifest = None
                        shop_setup = {
                            'seed': shop_run.seed, 'stage': shop_run.stage,
                            'coop_name': mission['coop_name'],
                            'loadout': shop_loadout,
                        }
                    else:
                        source_mission = code if state_snapshot.get('reward_mode') == ARSENAL_MODE else ''
                        manifest, _ = build_manifest(
                            GAME_ROOT, state_snapshot, mission['coop_name'],
                            source_mission=source_mission,
                            game_speed=game_speed,
                            difficulty={'easy': 0, 'normal': 1, 'hard': 2}[difficulty],
                            **({'country': pair_options['host']['country'],
                                'guest_country': pair_options['guest']['country'],
                                'player_colors': (pair_options['host']['color'], pair_options['guest']['color']),
                                'player_count': 2}
                               if challenge else {}),
                        )
                        shop_setup = None
                    lobby.send({'type': 'launch', 'code': code,
                                'session_token': session_token,
                                'run_id': state_snapshot.get('run_id'),
                                **({'player_options': pair_options} if challenge else {})})
                    result = host_session(
                        GAME_ROOT, manifest, name=lobby.name,
                        control_port=lobby.port + 1,
                        difficulty=difficulty,
                        session_token=session_token,
                        prepare_assets=self.prepare_direct_game_art,
                        shop_setup=shop_setup,
                        **({'player_options': player_options} if challenge else {}),
                    )
                else:
                    same_machine = lobby.address.lower() in ('127.0.0.1', 'localhost')
                    shop_setup = ({
                        'seed': shop_run.seed, 'stage': shop_run.stage,
                        'loadout': shop_loadout,
                    } if shop_run is not None else None)
                    result = join_session(
                        GAME_ROOT, lobby.address, name=lobby.name,
                        control_port=lobby.port + 1,
                        game_port=1235 if same_machine else 1234,
                        session_token=session_token,
                        prepare_assets=self.prepare_direct_game_art,
                        shop_setup=shop_setup,
                        **({'player_options': player_options} if challenge else {}),
                    )
                self._coop_queue.put(('ready', result))
            except Exception as exc:
                self.disable_generated_rules_for_client()
                self._coop_queue.put(('error', str(exc), traceback.format_exc()))

        threading.Thread(target=worker, name='CoopGame', daemon=True).start()
        self.after(100, self._poll_coop_session)

    def _poll_coop_session(self):
        try:
            event = self._coop_queue.get_nowait()
        except queue.Empty:
            if getattr(self, '_coop_busy', False):
                self.after(100, self._poll_coop_session)
            return
        if event[0] != 'error' and (
                getattr(self, '_coop_lobby', None) is not self._coop_preparing_lobby
                or not self._coop_preparing_lobby.connected):
            self.disable_generated_rules_for_client()
            event = ('error', 'Co-op lobby disconnected during game preparation.', '')
        if event[0] == 'error':
            finish = getattr(self, '_finish_archipelago_mission_preparation', None)
            if callable(finish):
                finish(self.mission_lookup().get(self._coop_active_game_code))
            self._coop_busy = False
            self.refresh_coop_controls()
            if self.shop_mode_selected():
                self.finish_progression_launch_context()
            self._record_coop_log('Co-op game failed: ' + event[1], error=True)
            self._record_coop_log(event[2], error=True)
            self._set_coop_status('Game connection failed: ' + event[1])
            if getattr(self, '_close_after_game', False):
                self.close_launcher()
                return
            messagebox.showerror('Co-op', self._coop_safe_message(event[1]))
            return
        result = event[1]
        self._coop_active_game_id = result['game_id']
        if result.get('player_options'):
            self._record_coop_log('Your challenge player: ' + str(result['player_options'])
                                  + '; peer: ' + str(result.get('peer_options')) + '.')
        if 'game_speed' in result:
            speed_label = next((label for label, value in GAME_SPEEDS
                                if value == result['game_speed']), str(result['game_speed']))
            self._record_coop_log(f'Host selected game speed: {speed_label}.')
        finish = getattr(self, '_finish_archipelago_mission_preparation', None)
        if callable(finish):
            finish(self.mission_lookup().get(self._coop_active_game_code))
        self._record_coop_log(f'Co-op paired with {result["peer"]}; game ID {result["game_id"]}; '
                        f'map {result["map_sha256"]}.')
        challenge_watch = None
        if self.challenge_mission(self._coop_active_game_code):
            lobby = getattr(self, '_coop_lobby', None)
            challenge_watch = self.create_challenge_result_watch(
                self.mission_lookup()[self._coop_active_game_code],
                lobby.name, peer=result.get('peer', ''),
            )
        try:
            shutdown_watch = GameShutdownWatch(DEBUG_LOG)
            process, _ = self.spawn_game_process(self.build_command())
            shutdown_watch.bind(process)
        except Exception as exc:
            self._coop_busy = False
            self.refresh_coop_controls()
            if self.shop_mode_selected():
                self.finish_progression_launch_context()
            self._record_coop_log('Co-op game launch failed: ' + str(exc), error=True)
            self.disable_generated_rules_for_client()
            if getattr(self, '_close_after_game', False):
                self.close_launcher()
                return
            messagebox.showerror('Co-op', self._coop_safe_message(exc))
            return
        self.active_game_process = process
        self._coop_shutdown_watch = shutdown_watch
        if challenge_watch is not None:
            self._coop_victory_watch = {
                'code': self._coop_active_game_code, 'native': challenge_watch,
                'run_snapshot': self._coop_challenge_launch_snapshot,
                'detected': False,
            }
        elif result['role'] == 'host':
            try:
                with DEBUG_LOG.open('rb') as handle:
                    log_stat = os.fstat(handle.fileno())
                    handle.seek(max(0, log_stat.st_size - 64))
                    log_anchor = handle.read(64)
            except OSError:
                log_stat = None
                log_anchor = b''
            self._coop_victory_watch = {
                'code': self._coop_active_game_code,
                'marker': victory_marker_name(self._coop_active_game_code.lower()),
                'offset': log_stat.st_size if log_stat else 0,
                'file_id': (log_stat.st_dev, log_stat.st_ino) if log_stat else None,
                'anchor': log_anchor,
                'detected': False,
            }
        else:
            self._coop_victory_watch = None
        self._record_coop_log(f'Co-op game started as {result["role"]}.')
        self.refresh_coop_controls()
        self._set_coop_status('Game running. Lobby stays connected.')
        self.after(1000, self._poll_coop_game)

    def _poll_coop_game(self):
        self._scan_coop_victory()
        process = self.active_game_process
        shutdown_watch = getattr(self, '_coop_shutdown_watch', None)
        if shutdown_watch is not None:
            for message, is_error in shutdown_watch.poll(process):
                self._record_coop_log(message, error=is_error)
        if process is not None and process.poll() is None:
            self.after(1000, self._poll_coop_game)
            return
        if shutdown_watch is not None and shutdown_watch.recovery_pending:
            self.after(100, self._poll_coop_game)
            return
        self.active_game_process = None
        self.disable_generated_rules_for_client()
        if shutdown_watch is not None:
            shutdown_watch.close()
        self._coop_shutdown_watch = None
        self._coop_busy = False
        self.refresh_coop_controls()
        self._record_coop_log('Co-op game process exited.')
        watch = getattr(self, '_coop_victory_watch', None)
        if watch and not watch['detected'] and not self.is_mission_complete(watch['code']):
            if 'native' in watch:
                outcome = watch['native'].result
                self._record_coop_log(
                    'Challenge defeat detected; no victory awarded.' if outcome == 'defeat'
                    else 'Challenge ended without a verified result; no victory awarded.'
                )
            elif (self.shop_mode_selected() and self.coop_mode_var.get()
                    and getattr(self, '_coop_active_game_role', '') == 'host'
                    and DEBUG_LOG.exists() and not watch.get('log_error')):
                if self.record_failed_mission_attempt(
                        watch['code'], 'Co-op game closed without victory'):
                    self._record_coop_log('Co-op Shop attempt recorded as failed for both players.')
            else:
                self._record_coop_log('No co-op victory marker detected. Host can record a won mission manually.')
        self._coop_victory_watch = None
        if self.shop_mode_selected() and self.coop_mode_var.get():
            self.finish_progression_launch_context()
        lobby = getattr(self, '_coop_lobby', None)
        self._set_coop_status(
            'Game ended. Host may select another map.' if lobby and lobby.connected else
            'Game ended. Lobby disconnected; click Disconnect before reconnecting.'
        )
        if getattr(self, '_close_after_game', False):
            self.disconnect_coop()
            self.shutdown_archipelago()
            self.destroy()

    def _scan_coop_victory(self):
        watch = getattr(self, '_coop_victory_watch', None)
        if watch and 'native' in watch:
            if watch['detected']:
                return
            result = watch['native'].poll() or watch['native'].result
            if result == 'victory':
                if not self.challenge_run_identity_matches(watch.get('run_snapshot')):
                    watch['detected'] = True
                    self._record_coop_log('Challenge result belongs to a different run; no victory awarded.', error=True)
                    return
                code = watch['code']
                lobby = getattr(self, '_coop_lobby', None)
                if getattr(self, '_coop_active_game_role', '') == 'guest':
                    if lobby and lobby.connected:
                        try:
                            lobby.send({'type': 'challenge_victory', 'code': code,
                                        'game_id': self._coop_active_game_id,
                                        'session_token': self._coop_active_game_token})
                        except OSError as exc:
                            self._record_coop_log('Team victory sync failed: ' + str(exc), error=True)
                            return
                        watch['detected'] = True
                        self._record_coop_log(f'Native team victory sent to host for {code}.')
                    return
                watch['detected'] = True
                if not self.is_mission_complete(code):
                    self._record_coop_log(f'Challenge native victory verified for {code}.')
                    self._record_shared_victory(code, 'Challenge in-game victory')
            return
        if not watch or watch['detected'] or not DEBUG_LOG.exists():
            return
        try:
            with DEBUG_LOG.open('rb') as handle:
                log_stat = os.fstat(handle.fileno())
                file_id = (log_stat.st_dev, log_stat.st_ino)
                offset = watch['offset']
                if log_stat.st_size < offset or watch.get('file_id') != file_id:
                    offset = 0
                elif offset and watch.get('anchor') is not None:
                    anchor_start = max(0, offset - 64)
                    handle.seek(anchor_start)
                    if handle.read(offset - anchor_start) != watch['anchor']:
                        offset = 0
                handle.seek(offset)
                data = handle.read()
                watch['offset'] = handle.tell()
                anchor_start = max(0, watch['offset'] - 64)
                handle.seek(anchor_start)
                watch['anchor'] = handle.read(watch['offset'] - anchor_start)
                watch['file_id'] = file_id
        except OSError as exc:
            watch['log_error'] = True
            self._record_coop_log('Co-op victory log read failed: ' + str(exc), error=True)
            return
        if not any(watch['marker'] in line for line in data.decode(
                'utf-8', errors='ignore').splitlines()):
            return
        watch['detected'] = True
        code = watch['code']
        if self.is_mission_complete(code):
            return
        self._record_coop_log(f'Co-op victory marker detected for {code}.')
        self._record_shared_victory(code, 'Co-op in-game victory')

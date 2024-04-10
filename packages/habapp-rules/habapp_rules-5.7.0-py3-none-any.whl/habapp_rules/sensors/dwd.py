"""DWD rules."""
import dataclasses
import datetime
import logging
import re

import HABApp

import habapp_rules.actors.state_observer
import habapp_rules.core.logger
import habapp_rules.core.state_machine_rule

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class DwdItems:
	"""Dataclass for DWD items needed by DwdWindAlarm."""

	description: HABApp.openhab.items.StringItem
	warn_type: HABApp.openhab.items.StringItem
	severity: HABApp.openhab.items.StringItem
	start_time: HABApp.openhab.items.DatetimeItem
	end_time: HABApp.openhab.items.DatetimeItem

	SEVERITY_MAPPING = {
		"NULL": 0,
		"Minor": 1,
		"Moderate": 2,
		"Severe": 3,
		"Extreme": 4
	}

	@classmethod
	def from_prefix(cls, prefix: str) -> "DwdItems":
		"""Init DwdItems from prefix

		:param prefix: common prefix of all DWD items
		:return: Dataclass with all needed DWD items
		"""
		description = HABApp.openhab.items.StringItem.get_item(f"{prefix}_description")
		warn_type = HABApp.openhab.items.StringItem.get_item(f"{prefix}_type")
		severity = HABApp.openhab.items.StringItem.get_item(f"{prefix}_severity")
		start_time = HABApp.openhab.items.DatetimeItem.get_item(f"{prefix}_start_time")
		end_time = HABApp.openhab.items.DatetimeItem.get_item(f"{prefix}_end_time")

		return cls(description, warn_type, severity, start_time, end_time)

	@property
	def severity_as_int(self) -> int:
		"""Get severity as integer.

		:return: severity as integer value
		"""
		return self.SEVERITY_MAPPING.get(self.severity.value, 0)


# pylint: disable=no-member
class DwdWindAlarm(habapp_rules.core.state_machine_rule.StateMachineRule):
	"""Rule for setting wind alarm by DWD warnings.

	# Items:
	Switch      I26_99_wind_alarm               "Wind alarm"
	Switch      I26_99_wind_alarm_manual        "Wind alarm manual"

	String      I26_99_warning_1_severity       "Severity"              {channel="dwdunwetter:dwdwarnings:ingolstadt:severity1"}
	String      I26_99_warning_1_description    "Description [%s]"      {channel="dwdunwetter:dwdwarnings:ingolstadt:description1"}
	DateTime    I26_99_warning_1_start_time     "valid from [%s]"       {channel="dwdunwetter:dwdwarnings:ingolstadt:onset1"}
	DateTime    I26_99_warning_1_end_time       "valid till [%s]"       {channel="dwdunwetter:dwdwarnings:ingolstadt:expires1"}
	String      I26_99_warning_1_type           "Type [%s]"             {channel="dwdunwetter:dwdwarnings:ingolstadt:event1"}

	String      I26_99_warning_2_severity       "Severity"              {channel="dwdunwetter:dwdwarnings:ingolstadt:severity2"}
	String      I26_99_warning_2_description    "Description [%s]"      {channel="dwdunwetter:dwdwarnings:ingolstadt:description2"}
	DateTime    I26_99_warning_2_start_time     "valid from [%s]"       {channel="dwdunwetter:dwdwarnings:ingolstadt:onset2"}
	DateTime    I26_99_warning_2_end_time       "valid till [%s]"       {channel="dwdunwetter:dwdwarnings:ingolstadt:expires2"}
	String      I26_99_warning_2_type           "Type [%s]"             {channel="dwdunwetter:dwdwarnings:ingolstadt:event2"}

	# Rule init:
	habapp_rules.sensors.dwd.DwdWindAlarm(
			"I26_99_wind_alarm",
			"I26_99_wind_alarm_manual",
			12 * 3600,
			number_dwd_objects=2
	)
	"""

	states = [
		{"name": "Manual"},
		{"name": "Hand", "timeout": 20 * 3600, "on_timeout": "_auto_hand_timeout"},
		{"name": "Auto", "initial": "Init", "children": [
			{"name": "Init"},
			{"name": "On"},
			{"name": "Off"}
		]}
	]

	trans = [
		{"trigger": "manual_on", "source": ["Auto", "Hand"], "dest": "Manual"},
		{"trigger": "manual_off", "source": "Manual", "dest": "Auto"},
		{"trigger": "hand", "source": "Auto", "dest": "Hand"},

		{"trigger": "wind_alarm_start", "source": "Auto_Off", "dest": "Auto_On"},
		{"trigger": "wind_alarm_end", "source": "Auto_On", "dest": "Auto_Off"},
	]

	def __init__(self,
	             name_wind_alarm: str,
	             manual_name: str,
	             hand_timeout: str | int,
	             dwd_item_prefix: str = "I26_99_warning_",
	             number_dwd_objects: int = 3,
	             threshold_wind_speed: int = 70,
	             threshold_severity: int = 2,
	             name_state: str | None = None,
	             state_label: str | None = None) -> None:
		"""Init of DWD wind alarm object.

		:param name_wind_alarm: name of OpenHAB wind alarm item (SwitchItem)
		:param manual_name: name of OpenHAB switch item to disable all automatic functions (SwitchItem)
		:param hand_timeout: name of OpenHAB number item or fixed value as integer to set timeout of manual change
		:param dwd_item_prefix: [optional] prefix of dwd warning names
		:param number_dwd_objects: [optional] number of dwd objects
		:param threshold_wind_speed: [optional] threshold for wind speed -> wind alarm will only be active if greater or equal
		:param threshold_severity: [optional] threshold for severity -> wind alarm will only be active if greater or equal
		:param name_state: [optional] name of OpenHAB item for storing the current state (StringItem)
		:param state_label: [optional] label of OpenHAB item for storing the current state (StringItem)
		:raises TypeError: if type of hand_timeout is not supported
		"""
		if not name_state:
			name_state = f"H_{name_wind_alarm}_state"
		habapp_rules.core.state_machine_rule.StateMachineRule.__init__(self, name_state, state_label)
		self._instance_logger = habapp_rules.core.logger.InstanceLogger(LOGGER, name_wind_alarm)

		self._threshold_wind_speed = threshold_wind_speed
		self._threshold_severity = threshold_severity

		# init items
		self._item_manual = HABApp.openhab.items.switch_item.SwitchItem.get_item(manual_name)
		if isinstance(hand_timeout, str):
			self._item_hand_timeout = HABApp.openhab.items.number_item.NumberItem.get_item(hand_timeout)
			self._hand_timeout = None
		elif isinstance(hand_timeout, int):
			self._item_hand_timeout = None
			self._hand_timeout = hand_timeout
		else:
			raise TypeError(f"hand_timeout must be of type string or integer! Given value: {hand_timeout} | type = {type(hand_timeout)}")
		self._items_dwd = [DwdItems.from_prefix(f"{dwd_item_prefix}{idx + 1}") for idx in range(number_dwd_objects)]

		# init state machine
		self._previous_state = None
		self.state_machine = habapp_rules.core.state_machine_rule.HierarchicalStateMachineWithTimeout(
			model=self,
			states=self.states,
			transitions=self.trans,
			ignore_invalid_triggers=True,
			after_state_change="_update_openhab_state")  # this function is missing!

		self._wind_alarm_observer = habapp_rules.actors.state_observer.StateObserverSwitch(name_wind_alarm, self._cb_hand, self._cb_hand)

		self._set_timeouts()
		self._set_initial_state()

		# callbacks
		self._item_manual.listen_event(self._cb_manual, HABApp.openhab.events.ItemStateChangedEventFilter())
		if self._item_hand_timeout is not None:
			self._item_hand_timeout.listen_event(self._cb_hand_timeout, HABApp.openhab.events.ItemStateChangedEventFilter())

		self.run.every(None, 300, self._cb_cyclic_check)

	def _get_initial_state(self, default_value: str = "") -> str:
		"""Get initial state of state machine.

		:param default_value: default / initial state
		:return: if OpenHAB item has a state it will return it, otherwise return the given default value
		"""
		if self._item_manual.is_on():
			return "Manual"
		if self._wind_alarm_active():
			return "Auto_On"
		return "Auto_Off"

	def _get_hand_timeout(self) -> int:
		"""Get value of hand timeout.

		:return: hand timeout in seconds
		"""
		if self._item_hand_timeout is not None:
			itm_value = self._item_hand_timeout.value
			return itm_value if itm_value is not None else 24 * 3600
		return self._hand_timeout

	def _set_timeouts(self) -> None:
		"""Set timeouts."""
		self.state_machine.get_state("Hand").timeout = self._get_hand_timeout()

	def _update_openhab_state(self) -> None:
		"""Update OpenHAB state item and other states.

		This should method should be set to "after_state_change" of the state machine.
		"""
		if self.state != self._previous_state:
			super()._update_openhab_state()
			self._instance_logger.debug(f"State change: {self._previous_state} -> {self.state}")

			if self.state == "Auto_On" and self._wind_alarm_observer.value is not True:
				self._wind_alarm_observer.send_command("ON")
			elif self.state == "Auto_Off" and self._wind_alarm_observer.value is not False:
				self._wind_alarm_observer.send_command("OFF")

			self._previous_state = self.state

	def on_enter_Auto_Init(self) -> None:  # pylint: disable=invalid-name
		"""Is called on entering of init state"""
		self._set_initial_state()

	def _cb_hand(self, event: HABApp.openhab.events.ItemStateUpdatedEvent | HABApp.openhab.events.ItemCommandEvent) -> None:
		"""Callback, which is triggered by the state observer if a manual change was detected.

		:param event: original trigger event
		"""
		self.hand()

	def _cb_manual(self, event: HABApp.openhab.events.ItemStateChangedEvent) -> None:
		"""Callback, which is triggered if the manual switch has a state change event.

		:param event: trigger event
		"""
		if event.value == "ON":
			self.manual_on()
		else:
			self.manual_off()

	def _cb_hand_timeout(self, _) -> None:
		"""Callback which is triggered if the timeout item changed."""
		self._set_timeouts()

	def _wind_alarm_active(self) -> bool:
		"""Check if wind alarm is active

		:return: True if active, False if not
		"""
		for dwd_items in self._items_dwd:
			if dwd_items.warn_type.value in {"BÖEN", "WIND", "STURM", "GEWITTER"}:
				speed_values = [int(value) for value in re.findall(r"\b(\d+)\s*km/h\b", dwd_items.description.value)]
				if not speed_values:
					continue

				if max(speed_values) >= self._threshold_wind_speed and dwd_items.severity_as_int >= self._threshold_severity:
					if dwd_items.start_time.value < datetime.datetime.now() < dwd_items.end_time.value:
						return True
		return False

	def _cb_cyclic_check(self) -> None:
		"""Callback to check if wind alarm is active. This should be called cyclic every few minutes."""
		if not self.state in {"Auto_On", "Auto_Off"}:
			return

		if self._wind_alarm_active() and self.state != "Auto_On":
			self.wind_alarm_start()

		elif not self._wind_alarm_active() and self.state != "Auto_Off":
			self.wind_alarm_end()

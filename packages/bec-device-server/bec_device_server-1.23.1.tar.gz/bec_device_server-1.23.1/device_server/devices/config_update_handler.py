from __future__ import annotations

import copy
import traceback
from typing import TYPE_CHECKING

from bec_lib import DeviceConfigError, MessageEndpoints, bec_logger, messages

if TYPE_CHECKING:
    from devicemanager import DeviceManagerDS

logger = bec_logger.logger


class ConfigUpdateHandler:
    def __init__(self, device_manager: DeviceManagerDS) -> None:
        self.device_manager = device_manager
        self.connector = self.device_manager.connector
        self.connector.register(
            MessageEndpoints.device_server_config_request(),
            cb=self._device_config_callback,
            parent=self,
        )

    @staticmethod
    def _device_config_callback(msg, *, parent, **_kwargs) -> None:
        logger.info(f"Received request: {msg}")
        parent.parse_config_request(msg.value)

    def parse_config_request(self, msg: messages.DeviceConfigMessage) -> None:
        """Processes a config request. If successful, it emits a config reply

        Args:
            msg (BECMessage.DeviceConfigMessage): Config request

        """
        error_msg = ""
        accepted = True
        try:
            self.device_manager.check_request_validity(msg)
            if msg.content["action"] == "update":
                self._update_config(msg)
            if msg.content["action"] == "add":
                raise NotImplementedError
            if msg.content["action"] == "reload":
                self._reload_config()
                if self.device_manager.failed_devices:
                    msg.metadata["failed_devices"] = self.device_manager.failed_devices

        except DeviceConfigError:
            error_msg = traceback.format_exc()
            accepted = False
        finally:
            self.send_config_request_reply(
                accepted=accepted, error_msg=error_msg, metadata=msg.metadata
            )

    def send_config_request_reply(self, accepted: bool, error_msg: str, metadata: dict) -> None:
        """
        Sends a config request reply

        Args:
            accepted (bool): Whether the request was accepted
            error_msg (str): Error message
            metadata (dict): Metadata of the request
        """
        msg = messages.RequestResponseMessage(
            accepted=accepted, message=error_msg, metadata=metadata
        )
        RID = metadata.get("RID")
        self.device_manager.connector.set(
            MessageEndpoints.device_config_request_response(RID), msg, expire=60
        )

    def _update_config(self, msg: messages.DeviceConfigMessage) -> None:
        for dev, dev_config in msg.content["config"].items():
            device = self.device_manager.devices[dev]
            if "deviceConfig" in dev_config:
                # store old config
                old_config = device._config["deviceConfig"].copy()

                # apply config
                try:
                    self.device_manager.update_config(device.obj, dev_config["deviceConfig"])
                except Exception as exc:
                    self.device_manager.update_config(device.obj, old_config)
                    raise DeviceConfigError(f"Error during object update. {exc}")

                if "limits" in dev_config["deviceConfig"]:
                    limits = {
                        "low": device.obj.low_limit_travel.get(),
                        "high": device.obj.high_limit_travel.get(),
                    }
                    self.device_manager.connector.set_and_publish(
                        MessageEndpoints.device_limits(device.name),
                        messages.DeviceMessage(signals=limits),
                    )

            if "enabled" in dev_config:
                device._config["enabled"] = dev_config["enabled"]
                if dev_config["enabled"]:
                    # pylint:disable=protected-access
                    if device.obj._destroyed:
                        self.device_manager.initialize_device(device._config)
                    else:
                        self.device_manager.initialize_enabled_device(device)
                else:
                    self.device_manager.disconnect_device(device.obj)
                    self.device_manager.reset_device(device)

    def _reload_config(self) -> None:
        for _, obj in self.device_manager.devices.items():
            try:
                obj.obj.destroy()
            except Exception:
                logger.warning(f"Failed to destroy {obj.obj.name}")
                raise RuntimeError
        self.device_manager.devices.flush()
        self.device_manager._get_config()
        if self.device_manager.failed_devices:
            self.handle_failed_device_inits()
        return

    def handle_failed_device_inits(self):
        if self.device_manager.failed_devices:
            msg = messages.DeviceConfigMessage(
                action="update",
                config={name: {"enabled": False} for name in self.device_manager.failed_devices},
            )
            self._update_config(msg)
            self.force_update_config_in_redis()
        return

    def force_update_config_in_redis(self):
        config = []
        for name, device in self.device_manager.devices.items():
            device_config = copy.deepcopy(device._config)
            device_config["name"] = name
            config.append(device_config)
        msg = messages.AvailableResourceMessage(resource=config)
        self.device_manager.producer.set(MessageEndpoints.device_config(), msg)

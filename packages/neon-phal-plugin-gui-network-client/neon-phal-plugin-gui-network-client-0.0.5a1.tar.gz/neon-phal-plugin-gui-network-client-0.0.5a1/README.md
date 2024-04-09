*Note*: This plugin is [planned to be deprecated](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-gui-network-client/issues/2).

# PHAL plugin - GUI Network Client

GUI Network client is a graphical user frontend to network manager and allows configuring, modifying and deleting networks. This plugin is also utilizes Plasma Network Manager for additional model support.

# Requirements

This plugin requires the following:
- Network Manager PHAL Plugin: https://github.com/OpenVoiceOS/ovos-PHAL-plugin-network-manager
- Plasma Network Manager: https://invent.kde.org/plasma/plasma-nm

# Install

`pip install ovos-PHAL-plugin-gui-network-client`

# Event Details:

##### Plugin Registeration and Activation

The GUI network client registers itself as a networking plugin for the wifi client, The following events are used for managing registeration, deregisteration and activation status of the plugin.

```python
     # WIFI Plugin Registeration and Activation Specific Events        
        self.bus.on("ovos.phal.wifi.plugin.stop.setup.event", self.handle_stop_setup)
        self.bus.on("ovos.phal.wifi.plugin.client.registered", self.handle_registered)
        self.bus.on("ovos.phal.wifi.plugin.client.deregistered", self.handle_deregistered)
        self.bus.on("ovos.phal.wifi.plugin.client.registration.failure", self.handle_registration_failure)
        self.bus.on("ovos.phal.wifi.plugin.alive", self.register_client)
```

##### Plugin Network Manager Interaction

The GUI network client utilizes the Network Manager for providing functionality such as activation of connections and deactivation of connections, the Plugin listens for the following events to display a success and failure passed from the network manager to display the status of connection activation and deactivation.

```python
        # OVOS PHAL NM EVENTS
        self.bus.on("ovos.phal.nm.connection.successful", self.display_success)
        self.bus.on("ovos.phal.nm.connection.failure", self.display_failure)
```
##### Plugin GUI Events

The GUI network client utilizes the following button events that are emitted between the QML GUI and the python side of the plugin, they handle information flow and events flow between onscreen events and logicical operations of the plugin.

```python
        # INTERNAL GUI EVENTS
        self.bus.on("ovos.phal.gui.network.client.back",
                    self.display_path_exit)
        self.bus.on("ovos.phal.gui.display.connected.network.settings",
                    self.display_connected_network_settings)
        self.bus.on("ovos.phal.gui.display.disconnected.network.settings",
                    self.display_disconnected_network_settings)
        self.bus.on("ovos.phal.gui.network.client.internal.back",
                    self.display_internal_back)
        
        # Also listen for certain events that can forcefully deactivate the client
        self.bus.on("system.display.homescreen", self.clean_shutdown)
        self.bus.on("mycroft.device.settings", self.clean_shutdown)
```

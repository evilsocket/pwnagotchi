__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'bt-tether'
__license__ = 'GPL3'
__description__ = 'This makes the display reachable over bluetooth'

import os
import time
import re
import logging
import subprocess
import dbus
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.utils import StatusFile

READY = False
INTERVAL = StatusFile('/root/.bt-tether')
OPTIONS = dict()


class BTError(Exception):
    """
    Custom bluetooth exception
    """
    pass

class BTNap:
    """
    This class creates a bluetooth connection to the specified bt-mac

    see https://github.com/bablokb/pi-btnap/blob/master/files/usr/local/sbin/btnap.service.py
    """

    IFACE_BASE = 'org.bluez'
    IFACE_DEV = 'org.bluez.Device1'
    IFACE_ADAPTER = 'org.bluez.Adapter1'
    IFACE_PROPS = 'org.freedesktop.DBus.Properties'

    def __init__(self, mac):
        self._mac = mac


    @staticmethod
    def get_bus():
        """
        Get systembus obj
        """
        bus = getattr(BTNap.get_bus, 'cached_obj', None)
        if not bus:
            bus = BTNap.get_bus.cached_obj = dbus.SystemBus()
        return bus

    @staticmethod
    def get_manager():
        """
        Get manager obj
        """
        manager = getattr(BTNap.get_manager, 'cached_obj', None)
        if not manager:
                manager = BTNap.get_manager.cached_obj = dbus.Interface(
                        BTNap.get_bus().get_object(BTNap.IFACE_BASE, '/'),
                        'org.freedesktop.DBus.ObjectManager' )
        return manager

    @staticmethod
    def prop_get(obj, k, iface=None):
        """
        Get a property of the obj
        """
        if iface is None:
            iface = obj.dbus_interface
        return obj.Get(iface, k, dbus_interface=BTNap.IFACE_PROPS)

    @staticmethod
    def prop_set(obj, k, v, iface=None):
        """
        Set a property of the obj
        """
        if iface is None:
            iface = obj.dbus_interface
        return obj.Set(iface, k, v, dbus_interface=BTNap.IFACE_PROPS)


    @staticmethod
    def find_adapter(pattern=None):
        """
        Find the bt adapter
        """

        return BTNap.find_adapter_in_objects(BTNap.get_manager().GetManagedObjects(), pattern)

    @staticmethod
    def find_adapter_in_objects(objects, pattern=None):
        """
        Finds the obj with a pattern
        """
        bus, obj = BTNap.get_bus(), None
        for path, ifaces in objects.items():
                adapter = ifaces.get(BTNap.IFACE_ADAPTER)
                if adapter is None:
                    continue
                if not pattern or pattern == adapter['Address'] or path.endswith(pattern):
                        obj = bus.get_object(BTNap.IFACE_BASE, path)
                        yield dbus.Interface(obj, BTNap.IFACE_ADAPTER)
        if obj is None:
                raise BTError('Bluetooth adapter not found')

    @staticmethod
    def find_device(device_address, adapter_pattern=None):
        """
        Finds the device
        """
        return BTNap.find_device_in_objects(BTNap.get_manager().GetManagedObjects(),
                                            device_address, adapter_pattern)

    @staticmethod
    def find_device_in_objects(objects, device_address, adapter_pattern=None):
        """
        Finds the device in objects
        """
        bus = BTNap.get_bus()
        path_prefix = ''
        if adapter_pattern:
            if not isinstance(adapter_pattern, str):
                adapter = adapter_pattern
            else:
                adapter = BTNap.find_adapter_in_objects(objects, adapter_pattern)
            path_prefix = adapter.object_path
        for path, ifaces in objects.items():
            device = ifaces.get(BTNap.IFACE_DEV)
            if device is None:
                continue
            if device['Address'] == device_address and path.startswith(path_prefix):
                obj = bus.get_object(BTNap.IFACE_BASE, path)
                return dbus.Interface(obj, BTNap.IFACE_DEV)
        raise BTError('Bluetooth device not found')

    def power(self, on=True):
        """
        Set power of devices to on/off
        """

        devs = list(BTNap.find_adapter())
        devs = dict((BTNap.prop_get(dev, 'Address'), dev) for dev in devs)

        for dev_addr, dev in devs.items():
            BTNap.prop_set(dev, 'Powered', on)
            logging.debug('Set power of %s (addr %s) to %s', dev.object_path, dev_addr, str(on))

        if devs:
            return list(devs.values())[0]

        return None

    def is_connected(self):
        """
        Check if already connected
        """
        bt_dev = self.power(True)

        if not bt_dev:
            return False

        try:
            dev_remote = BTNap.find_device(self._mac, bt_dev)
            return bool(BTNap.prop_get(dev_remote, 'Connected'))
        except BTError:
            pass
        return False


    def is_paired(self):
        """
        Check if already connected
        """
        bt_dev = self.power(True)

        if not bt_dev:
            return False

        try:
            dev_remote = BTNap.find_device(self._mac, bt_dev)
            return bool(BTNap.prop_get(dev_remote, 'Paired'))
        except BTError:
            pass
        return False

    def wait_for_device(self, timeout=15):
        """
        Wait for device

        returns device if found None if not
        """
        bt_dev = self.power(True)

        if not bt_dev:
            return None

        try:
            bt_dev.StartDiscovery()
        except Exception:
            # can fail with org.bluez.Error.NotReady / org.bluez.Error.Failed
            # TODO: add loop?
            pass

        dev_remote = None

        # could be set to 0, so check if > -1
        while timeout > -1:
            try:
                dev_remote = BTNap.find_device(self._mac, bt_dev)
                logging.debug('Using remote device (addr: %s): %s',
                    BTNap.prop_get(dev_remote, 'Address'), dev_remote.object_path )
                break
            except BTError:
                pass

            time.sleep(1)
            timeout -= 1

        try:
            bt_dev.StopDiscovery()
        except Exception:
            # can fail with org.bluez.Error.NotReady / org.bluez.Error.Failed / org.bluez.Error.NotAuthorized
            pass

        return dev_remote


    def connect(self, reconnect=False):
        """
        Connect to device

        return True if connected; False if failed
        """

        # check if device is close
        dev_remote = self.wait_for_device()

        if not dev_remote:
            return False

        try:
            dev_remote.Pair()
            logging.info('BT-TETHER: Successful paired with device ;)')
        except Exception:
            # can fail because of AlreadyExists etc.
            pass

        try:
            dev_remote.ConnectProfile('nap')
        except Exception:
            pass

        net = dbus.Interface(dev_remote, 'org.bluez.Network1')

        try:
            net.Connect('nap')
        except dbus.exceptions.DBusException as err:
            if err.get_dbus_name() != 'org.bluez.Error.Failed':
                raise

            connected = BTNap.prop_get(net, 'Connected')

            if not connected:
                return False

            if reconnect:
                net.Disconnect()
                return self.connect(reconnect=False)

            return True


#################################################
#################################################
#################################################

class SystemdUnitWrapper:
    """
    systemd wrapper
    """

    def __init__(self, unit):
        self.unit = unit

    @staticmethod
    def _action_on_unit(action, unit):
        process = subprocess.Popen(f"systemctl {action} {unit}", shell=True, stdin=None,
                                  stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
        if process.returncode > 0:
            return False
        return True

    @staticmethod
    def daemon_reload():
        """
        Calls systemctl daemon-reload
        """
        process = subprocess.Popen("systemctl daemon-reload", shell=True, stdin=None,
                                  stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
        if process.returncode > 0:
            return False
        return True

    def is_active(self):
        """
        Checks if unit is active
        """
        return SystemdUnitWrapper._action_on_unit('is-active', self.unit)

    def is_enabled(self):
        """
        Checks if unit is enabled
        """
        return SystemdUnitWrapper._action_on_unit('is-enabled', self.unit)

    def is_failed(self):
        """
        Checks if unit is failed
        """
        return SystemdUnitWrapper._action_on_unit('is-failed', self.unit)

    def enable(self):
        """
        Enables the unit
        """
        return SystemdUnitWrapper._action_on_unit('enable', self.unit)

    def disable(self):
        """
        Disables the unit
        """
        return SystemdUnitWrapper._action_on_unit('disable', self.unit)

    def start(self):
        """
        Starts the unit
        """
        return SystemdUnitWrapper._action_on_unit('start', self.unit)

    def stop(self):
        """
        Stops the unit
        """
        return SystemdUnitWrapper._action_on_unit('stop', self.unit)

    def restart(self):
        """
        Restarts the unit
        """
        return SystemdUnitWrapper._action_on_unit('restart', self.unit)


class IfaceWrapper:
    """
    Small wrapper to check and manage ifaces

    see: https://github.com/rlisagor/pynetlinux/blob/master/pynetlinux/ifconfig.py
    """

    def __init__(self, iface):
        self.iface = iface
        self.path = f"/sys/class/net/{iface}"

    def exists(self):
        """
        Checks if iface exists
        """
        return os.path.exists(self.path)

    def is_up(self):
        """
        Checks if iface is ip
        """
        return open(f"{self.path}/operstate", 'r').read().rsplit('\n') == 'up'


    def set_addr(self, addr):
        """
        Set the netmask
        """
        process = subprocess.Popen(f"ip addr add {addr} dev {self.iface}", shell=True, stdin=None,
                                  stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()

        if process.returncode == 2 or process.returncode == 0: # 2 = already set
            return True

        return False

    @staticmethod
    def set_route(addr):
        process = subprocess.Popen(f"ip route replace default via {addr}", shell=True, stdin=None,
                                  stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()

        if process.returncode > 0:
            return False

        return True



def on_loaded():
    """
    Gets called when the plugin gets loaded
    """
    global READY
    global INTERVAL

    for opt in ['share_internet', 'mac', 'ip', 'netmask', 'interval']:
        if opt not in OPTIONS or (opt in OPTIONS and OPTIONS[opt] is None):
            logging.error("BT-TET: Pleace specify the %s in your config.yml.", opt)
            return

    # ensure bluetooth is running
    bt_unit = SystemdUnitWrapper('bluetooth.service')
    if not bt_unit.is_active():
        if not bt_unit.start():
            logging.error("BT-TET: Can't start bluetooth.service")
            return

    INTERVAL.update()
    READY = True


def on_ui_update(ui):
    """
    Try to connect to device
    """

    if READY:
        global INTERVAL
        if INTERVAL.newer_then_minutes(OPTIONS['interval']):
            return

        INTERVAL.update()

        bt = BTNap(OPTIONS['mac'])

        logging.debug('BT-TETHER: Check if already connected and paired')
        if bt.is_connected() and bt.is_paired():
            logging.debug('BT-TETHER: Already connected and paired')
            ui.set('bluetooth', 'CON')
            return

        logging.debug('BT-TETHER: Try to connect to mac')
        if bt.connect():
            logging.debug('BT-TETHER: Successfuly connected')
            btnap_iface = IfaceWrapper('bnep0')

            logging.debug('BT-TETHER: Check interface')
            if btnap_iface.exists():
                logging.debug('BT-TETHER: Interface found')
                # check ip
                addr = f"{OPTIONS['ip']}/{OPTIONS['netmask']}"

                logging.debug('BT-TETHER: Try to set ADDR to interface')
                if not btnap_iface.set_addr(addr):
                    ui.set('bluetooth', 'ERR1')
                    logging.error("Could not set ip of bnep0 to %s", addr)
                    return
                else:
                    logging.debug('BT-TETHER: Set ADDR to interface')

                # change route if sharking
                if OPTIONS['share_internet']:
                    logging.debug('BT-TETHER: Set routing and change resolv.conf')
                    IfaceWrapper.set_route(".".join(OPTIONS['ip'].split('.')[:-1] + ['1'])) # im not proud about that
                    # fix resolv.conf; dns over https ftw!
                    with open('/etc/resolv.conf', 'r+') as resolv:
                        nameserver = resolv.read()
                        if 'nameserver 9.9.9.9' not in nameserver:
                            resolv.seek(0)
                            resolv.write(nameserver + 'nameserver 9.9.9.9\n')

                ui.set('bluetooth', 'CON')
            else:
                ui.set('bluetooth', 'ERR2')
        else:
            ui.set('bluetooth', 'NF')


def on_ui_setup(ui):
    ui.add_element('bluetooth', LabeledValue(color=BLACK, label='BT', value='-', position=(ui.width() / 2 - 30, 0),
                                       label_font=fonts.Bold, text_font=fonts.Medium))

"""Settings Panel - UI for device configuration."""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from typing import Callable
from threading import Thread

from ..msr605x.commands import MSR605XCommands
from ..msr605x.constants import Coercivity, TrackNumber, BPI, BPC


class SettingsPanel(Gtk.Box):
    """Panel for device settings and configuration."""

    def __init__(
        self,
        commands: MSR605XCommands,
        show_toast: Callable[[str, bool], None]
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        self.commands = commands
        self.show_toast = show_toast

        self.set_margin_top(24)
        self.set_margin_bottom(24)
        self.set_margin_start(24)
        self.set_margin_end(24)

        self._build_ui()

    def _build_ui(self):
        """Build the panel UI."""
        # Title
        title = Gtk.Label(label="Settings")
        title.add_css_class("panel-title")
        title.set_xalign(0)
        self.append(title)

        # Scrolled window for settings
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)

        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        scroll.set_child(settings_box)

        # Coercivity section
        settings_box.append(self._create_coercivity_section())

        # BPI section
        settings_box.append(self._create_bpi_section())

        # BPC section
        settings_box.append(self._create_bpc_section())

        # Leading zeros section
        settings_box.append(self._create_leading_zeros_section())

        # Device tests section
        settings_box.append(self._create_tests_section())

        self.append(scroll)

        # Status
        self.status_label = Gtk.Label(label="")
        self.status_label.set_xalign(0)
        self.status_label.set_margin_top(8)
        self.append(self.status_label)

    def _create_coercivity_section(self) -> Gtk.Frame:
        """Create coercivity settings section."""
        frame = Gtk.Frame()
        frame.set_label("Coercivity")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # Description
        desc = Gtk.Label(
            label="Set the magnetic field strength for writing cards. "
            "Use Hi-Co for more durable encoding, Lo-Co for standard cards."
        )
        desc.set_xalign(0)
        desc.set_wrap(True)
        desc.add_css_class("dim-label")
        box.append(desc)

        # Radio buttons
        radio_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        radio_box.set_margin_top(8)

        self.hico_radio = Gtk.CheckButton(label="Hi-Co (2750-4000 Oe)")
        self.hico_radio.set_active(True)
        radio_box.append(self.hico_radio)

        self.loco_radio = Gtk.CheckButton(label="Lo-Co (300 Oe)")
        self.loco_radio.set_group(self.hico_radio)
        radio_box.append(self.loco_radio)

        box.append(radio_box)

        # Apply button
        apply_btn = Gtk.Button(label="Apply Coercivity")
        apply_btn.connect("clicked", self._on_apply_coercivity)
        apply_btn.set_halign(Gtk.Align.START)
        box.append(apply_btn)

        frame.set_child(box)
        return frame

    def _create_bpi_section(self) -> Gtk.Frame:
        """Create BPI settings section."""
        frame = Gtk.Frame()
        frame.set_label("Bits Per Inch (BPI)")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        desc = Gtk.Label(
            label="Configure the recording density for each track. "
            "Standard values: Track 1 & 3 = 210 BPI, Track 2 = 75 BPI."
        )
        desc.set_xalign(0)
        desc.set_wrap(True)
        desc.add_css_class("dim-label")
        box.append(desc)

        # Track BPI settings
        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(8)
        grid.set_margin_top(8)

        self.bpi_combos = {}

        for i, track in enumerate([1, 2, 3]):
            label = Gtk.Label(label=f"Track {track}:")
            label.set_xalign(0)
            grid.attach(label, 0, i, 1, 1)

            combo = Gtk.ComboBoxText()
            combo.append("75", "75 BPI")
            combo.append("210", "210 BPI")
            # Default values
            combo.set_active_id("210" if track != 2 else "75")
            grid.attach(combo, 1, i, 1, 1)

            self.bpi_combos[track] = combo

        box.append(grid)

        apply_btn = Gtk.Button(label="Apply BPI Settings")
        apply_btn.connect("clicked", self._on_apply_bpi)
        apply_btn.set_halign(Gtk.Align.START)
        box.append(apply_btn)

        frame.set_child(box)
        return frame

    def _create_bpc_section(self) -> Gtk.Frame:
        """Create BPC settings section."""
        frame = Gtk.Frame()
        frame.set_label("Bits Per Character (BPC)")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        desc = Gtk.Label(
            label="Configure the character encoding for each track. "
            "Standard values: Track 1 = 7 BPC, Track 2 & 3 = 5 BPC."
        )
        desc.set_xalign(0)
        desc.set_wrap(True)
        desc.add_css_class("dim-label")
        box.append(desc)

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(8)
        grid.set_margin_top(8)

        self.bpc_combos = {}

        for i, track in enumerate([1, 2, 3]):
            label = Gtk.Label(label=f"Track {track}:")
            label.set_xalign(0)
            grid.attach(label, 0, i, 1, 1)

            combo = Gtk.ComboBoxText()
            combo.append("5", "5 BPC")
            combo.append("7", "7 BPC")
            combo.append("8", "8 BPC")
            # Default values
            combo.set_active_id("7" if track == 1 else "5")
            grid.attach(combo, 1, i, 1, 1)

            self.bpc_combos[track] = combo

        box.append(grid)

        apply_btn = Gtk.Button(label="Apply BPC Settings")
        apply_btn.connect("clicked", self._on_apply_bpc)
        apply_btn.set_halign(Gtk.Align.START)
        box.append(apply_btn)

        frame.set_child(box)
        return frame

    def _create_leading_zeros_section(self) -> Gtk.Frame:
        """Create leading zeros settings section."""
        frame = Gtk.Frame()
        frame.set_label("Leading Zeros")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        desc = Gtk.Label(
            label="Configure the number of leading zeros before data on each track."
        )
        desc.set_xalign(0)
        desc.set_wrap(True)
        desc.add_css_class("dim-label")
        box.append(desc)

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(8)
        grid.set_margin_top(8)

        self.lz_spins = {}

        for i, track in enumerate([1, 2, 3]):
            label = Gtk.Label(label=f"Track {track}:")
            label.set_xalign(0)
            grid.attach(label, 0, i, 1, 1)

            adjustment = Gtk.Adjustment(value=0, lower=0, upper=255, step_increment=1)
            spin = Gtk.SpinButton(adjustment=adjustment, digits=0)
            grid.attach(spin, 1, i, 1, 1)

            self.lz_spins[track] = spin

        box.append(grid)

        apply_btn = Gtk.Button(label="Apply Leading Zeros")
        apply_btn.connect("clicked", self._on_apply_leading_zeros)
        apply_btn.set_halign(Gtk.Align.START)
        box.append(apply_btn)

        frame.set_child(box)
        return frame

    def _create_tests_section(self) -> Gtk.Frame:
        """Create device tests section."""
        frame = Gtk.Frame()
        frame.set_label("Device Tests")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        desc = Gtk.Label(
            label="Run diagnostic tests on the MSR605X device."
        )
        desc.set_xalign(0)
        desc.set_wrap(True)
        desc.add_css_class("dim-label")
        box.append(desc)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_margin_top(8)

        tests = [
            ("Test Communication", self._on_test_comm),
            ("Test RAM", self._on_test_ram),
            ("Test Sensor", self._on_test_sensor),
            ("Get Firmware", self._on_get_firmware),
            ("Reset Device", self._on_reset_device),
        ]

        for label, callback in tests:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", callback)
            button_box.append(btn)

        box.append(button_box)

        # LED control
        led_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        led_box.set_margin_top(12)

        led_label = Gtk.Label(label="LED Control:")
        led_box.append(led_label)

        for color in ["Green", "Yellow", "Red", "All", "Off"]:
            btn = Gtk.Button(label=color)
            btn.connect("clicked", self._on_led_clicked, color.lower())
            led_box.append(btn)

        box.append(led_box)

        frame.set_child(box)
        return frame

    def _on_apply_coercivity(self, button):
        """Apply coercivity setting."""
        coercivity = Coercivity.HIGH if self.hico_radio.get_active() else Coercivity.LOW

        def do_apply():
            result = self.commands.set_coercivity(coercivity)
            GLib.idle_add(self._show_result, result.message, result.success)

        Thread(target=do_apply, daemon=True).start()

    def _on_apply_bpi(self, button):
        """Apply BPI settings."""
        def do_apply():
            for track_num, combo in self.bpi_combos.items():
                bpi_value = int(combo.get_active_id())
                bpi = BPI.BPI_210 if bpi_value == 210 else BPI.BPI_75
                result = self.commands.set_bpi(TrackNumber(track_num), bpi)
                if not result.success:
                    GLib.idle_add(self._show_result, result.message, False)
                    return

            GLib.idle_add(self._show_result, "BPI settings applied", True)

        Thread(target=do_apply, daemon=True).start()

    def _on_apply_bpc(self, button):
        """Apply BPC settings."""
        def do_apply():
            for track_num, combo in self.bpc_combos.items():
                bpc_value = int(combo.get_active_id())
                bpc = BPC(bpc_value)
                result = self.commands.set_bpc(TrackNumber(track_num), bpc)
                if not result.success:
                    GLib.idle_add(self._show_result, result.message, False)
                    return

            GLib.idle_add(self._show_result, "BPC settings applied", True)

        Thread(target=do_apply, daemon=True).start()

    def _on_apply_leading_zeros(self, button):
        """Apply leading zeros settings."""
        def do_apply():
            for track_num, spin in self.lz_spins.items():
                zeros = int(spin.get_value())
                result = self.commands.set_leading_zero(TrackNumber(track_num), zeros)
                if not result.success:
                    GLib.idle_add(self._show_result, result.message, False)
                    return

            GLib.idle_add(self._show_result, "Leading zeros applied", True)

        Thread(target=do_apply, daemon=True).start()

    def _on_test_comm(self, button):
        """Test communication."""
        def do_test():
            result = self.commands.test_communication()
            GLib.idle_add(self._show_result, result.message, result.success)

        Thread(target=do_test, daemon=True).start()

    def _on_test_ram(self, button):
        """Test RAM."""
        def do_test():
            result = self.commands.test_ram()
            GLib.idle_add(self._show_result, result.message, result.success)

        Thread(target=do_test, daemon=True).start()

    def _on_test_sensor(self, button):
        """Test sensor."""
        def do_test():
            result = self.commands.test_sensor()
            GLib.idle_add(self._show_result, result.message, result.success)

        Thread(target=do_test, daemon=True).start()

    def _on_get_firmware(self, button):
        """Get firmware version."""
        def do_get():
            result = self.commands.get_firmware_version()
            GLib.idle_add(self._show_result, result.message, result.success)

        Thread(target=do_get, daemon=True).start()

    def _on_reset_device(self, button):
        """Reset device."""
        def do_reset():
            result = self.commands.reset()
            GLib.idle_add(self._show_result, result.message, result.success)

        Thread(target=do_reset, daemon=True).start()

    def _on_led_clicked(self, button, color: str):
        """Control LED."""
        def do_led():
            if color == "off":
                result = self.commands.led_off()
            else:
                result = self.commands.led_on(color)
            GLib.idle_add(self._show_result, result.message, result.success)

        Thread(target=do_led, daemon=True).start()

    def _show_result(self, message: str, success: bool):
        """Show result message."""
        self.status_label.set_text(message)
        self.show_toast(message, not success)

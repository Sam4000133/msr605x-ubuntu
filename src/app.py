"""MSR605X GTK4 Application."""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib

from .window import MSR605XWindow


class MSR605XApplication(Adw.Application):
    """Main GTK4 Application class."""

    def __init__(self):
        super().__init__(
            application_id="com.github.msr605x",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )

        self.window = None

        # Setup actions
        self._setup_actions()

    def _setup_actions(self):
        """Setup application actions."""
        # Quit action
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self._on_quit)
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<primary>q"])

        # About action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

        # Preferences action
        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self._on_preferences)
        self.add_action(preferences_action)
        self.set_accels_for_action("app.preferences", ["<primary>comma"])

    def do_activate(self):
        """Handle application activation."""
        if not self.window:
            self.window = MSR605XWindow(application=self)
        self.window.present()

    def do_startup(self):
        """Handle application startup."""
        Adw.Application.do_startup(self)

        # Load CSS
        self._load_css()

    def _load_css(self):
        """Load custom CSS styles."""
        css_provider = Gtk.CssProvider()

        # Try to load from data directory
        css_path = GLib.build_filenamev([
            GLib.get_user_data_dir(),
            "msr605x",
            "style.css"
        ])

        try:
            css_provider.load_from_path(css_path)
        except GLib.Error:
            # Use embedded CSS
            css_provider.load_from_data(self._get_default_css().encode())

        Gtk.StyleContext.add_provider_for_display(
            self.window.get_display() if self.window else Gtk.Window().get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _get_default_css(self) -> str:
        """Get default CSS styles."""
        return """
        .track-entry {
            font-family: monospace;
            font-size: 14px;
        }

        .track-label {
            font-weight: bold;
            font-size: 12px;
        }

        .status-connected {
            color: @success_color;
        }

        .status-disconnected {
            color: @error_color;
        }

        .led-indicator {
            min-width: 16px;
            min-height: 16px;
            border-radius: 8px;
        }

        .led-green {
            background-color: #4CAF50;
        }

        .led-yellow {
            background-color: #FFC107;
        }

        .led-red {
            background-color: #F44336;
        }

        .led-off {
            background-color: #666666;
        }

        .log-view {
            font-family: monospace;
            font-size: 12px;
        }

        .panel-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 12px;
        }

        .action-button {
            min-height: 48px;
            font-size: 14px;
        }
        """

    def _on_quit(self, action, param):
        """Handle quit action."""
        if self.window:
            self.window.close()
        self.quit()

    def _on_about(self, action, param):
        """Show about dialog."""
        about = Adw.AboutWindow(
            transient_for=self.window,
            application_name="MSR605X Utility",
            application_icon="com.github.msr605x",
            developer_name="Samuele Quaranta",
            version="1.0.0",
            developers=["Samuele Quaranta"],
            copyright="Copyright 2026 Samuele Quaranta",
            license_type=Gtk.License.MIT_X11,
            website="https://github.com/samuelequaranta/msr605x-ubuntu",
            issue_url="https://github.com/samuelequaranta/msr605x-ubuntu/issues",
            comments="A native GTK4 application for Ubuntu to read, write, and manage magnetic stripe cards using the MSR605X device."
        )
        about.present()

    def _on_preferences(self, action, param):
        """Show preferences dialog."""
        if self.window:
            self.window.show_settings()

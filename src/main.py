#!/usr/bin/env python3
"""MSR605X Utility for Ubuntu - Entry point."""

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gio

from .app import MSR605XApplication


def main():
    """Application entry point."""
    app = MSR605XApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())

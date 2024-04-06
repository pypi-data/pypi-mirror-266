# -*- coding: utf-8 -*-
"""cx_Freeze config for the agent as a Win32Service."""

NAME = "ProCustodibusAgent%s"
DISPLAY_NAME = "Pro Custodibus Agent %s"
MODULE_NAME = "procustodibus_agent.windows.service"
CLASS_NAME = "Service"
DESCRIPTION = "Synchronizes your WireGuard settings with Pro Custodibus."
AUTO_START = False
SESSION_CHANGES = False

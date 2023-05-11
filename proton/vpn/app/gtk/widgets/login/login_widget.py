"""
This module defines the login widget, used to authenticate the user.


Copyright (c) 2023 Proton AG

This file is part of Proton VPN.

Proton VPN is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Proton VPN is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ProtonVPN.  If not, see <https://www.gnu.org/licenses/>.
"""
from gi.repository import GObject

from proton.vpn.app.gtk.controller import Controller
from proton.vpn.app.gtk import Gtk
from proton.vpn import logging
from proton.vpn.app.gtk.widgets.login.login_form import LoginForm
from proton.vpn.app.gtk.widgets.login.two_factor_auth_form import TwoFactorAuthForm
from proton.vpn.app.gtk.widgets.main.notifications import Notifications
from proton.vpn.app.gtk.widgets.main.loading_widget import LoadingWidget

logger = logging.getLogger(__name__)


class LoginWidget(Gtk.Stack):
    """Widget used to authenticate the user.

    It inherits from Gtk.Stack and contains 2 widgets stacked on top of the
    other: the LoginForm and the TwoFactorAuthForm. By default, the LoginForm
    widget is shown. Once the user introduces the right username and password
    (and 2FA is enabled) then the TwoFactorAuthForm widget is displayed instead.
    """
    def __init__(
        self, controller: Controller,
        notifications: Notifications, loading_widget: LoadingWidget
    ):
        super().__init__()

        self.set_name("login-widget")
        self._controller = controller
        self.active_form = None

        self.login_form = LoginForm(controller, notifications, loading_widget)
        self.add_named(self.login_form, "login_form")
        self.two_factor_auth_form = TwoFactorAuthForm(
            controller, notifications, loading_widget
        )
        self.add_named(self.two_factor_auth_form, "2fa_form")

        self.login_form.connect(
            "user-authenticated",
            lambda _, two_factor_auth_required:
            self._on_user_authenticated(two_factor_auth_required)
        )

        self.two_factor_auth_form.connect(
            "two-factor-auth-successful",
            lambda _: self._on_two_factor_auth_successful()
        )

        self.two_factor_auth_form.connect(
            "session-expired",
            lambda _: self._on_session_expired_during_2fa()
        )

    def _on_user_authenticated(self, two_factor_auth_required: bool):
        if not two_factor_auth_required:
            self._signal_user_logged_in()
        else:
            self.display_form(self.two_factor_auth_form)

    def _on_two_factor_auth_successful(self):
        self._signal_user_logged_in()

    def _on_session_expired_during_2fa(self):
        self.display_form(self.login_form)

    @GObject.Signal
    def user_logged_in(self):
        """Signal emitted after a successful login."""

    def _signal_user_logged_in(self):
        self.emit("user-logged-in")

    def display_form(self, form):
        """
        Displays the specified form to the user. That is, either the login
        form (user/password) or the 2FA form.
        :param form: The form to be displayed to the user.
        """
        self.active_form = form
        self.set_visible_child(form)
        form.reset()

    def reset(self):
        """Resets the widget to its initial state."""
        self.display_form(self.login_form)

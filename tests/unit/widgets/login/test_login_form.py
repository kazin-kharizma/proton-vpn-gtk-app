"""
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
from concurrent.futures import Future
from unittest.mock import Mock

import pytest
from proton.vpn.session.dataclasses import LoginResult

from proton.vpn.app.gtk.widgets.login.login_form import LoginForm
from tests.unit.utils import process_gtk_events


@pytest.fixture
def controller_mocking_successful_login():
    controller_mock = Mock()

    login_result_future = Future()
    login_result_future.set_result(
        LoginResult(success=True, authenticated=True, twofa_required=False)
    )
    controller_mock.login.return_value = login_result_future

    return controller_mock


def test_login_form_signals_when_the_user_is_authenticated(
        controller_mocking_successful_login
):
    login_form = LoginForm(controller_mocking_successful_login)
    user_logged_in_callback = Mock()
    login_form.connect("user-authenticated", user_logged_in_callback)

    login_form.username = "username"
    login_form.password = "password"
    login_form.submit_login()

    process_gtk_events()

    controller_mocking_successful_login.login.assert_called_once_with(
        "username", "password"
    )
    two_factor_auth_required = False
    user_logged_in_callback.assert_called_once_with(
        login_form, two_factor_auth_required
    )


def test_login_form_authenticates_user_when_pressing_enter_on_username_field(
        controller_mocking_successful_login
):
    login_form = LoginForm(controller_mocking_successful_login)
    user_logged_in_callback = Mock()
    login_form.connect("user-authenticated", user_logged_in_callback)

    login_form.username = "username"
    login_form.password = "password"
    login_form.username_enter()

    process_gtk_events()

    controller_mocking_successful_login.login.assert_called_once()


def test_login_form_authenticates_user_when_pressing_enter_on_password_field(
        controller_mocking_successful_login
):
    login_form = LoginForm(controller_mocking_successful_login)
    user_logged_in_callback = Mock()
    login_form.connect("user-authenticated", user_logged_in_callback)

    login_form.username = "username"
    login_form.password = "password"
    login_form.password_enter()

    process_gtk_events()

    controller_mocking_successful_login.login.assert_called_once()


def test_login_form_does_not_authenticate_user_when_pressing_enter_on_username_field_with_missing_username(
        controller_mocking_successful_login
):
    login_form = LoginForm(controller_mocking_successful_login)
    user_logged_in_callback = Mock()
    login_form.connect("user-authenticated", user_logged_in_callback)

    login_form.username = ""
    login_form.password = "password"
    login_form.password_enter()

    process_gtk_events()

    controller_mocking_successful_login.login.assert_not_called()


def test_login_form_does_not_authenticate_user_when_pressing_enter_on_username_field_with_missing_password(
        controller_mocking_successful_login
):
    login_form = LoginForm(controller_mocking_successful_login)
    user_logged_in_callback = Mock()
    login_form.connect("user-authenticated", user_logged_in_callback)

    login_form.username = "username"
    login_form.password = ""
    login_form.password_enter()

    process_gtk_events()

    controller_mocking_successful_login.login.assert_not_called()


@pytest.fixture
def controller_mocking_invalid_username():
    controller_mock = Mock()

    login_result_future = Future()
    login_result_future.set_exception(
        ValueError("Invalid username")
    )
    controller_mock.login.return_value = login_result_future

    return controller_mock


def test_login_form_shows_error_when_submitting_an_invalid_username(
        controller_mocking_invalid_username
):
    login_form = LoginForm(controller_mocking_invalid_username)
    login_form.username = "MockInvalidUsername"
    login_form.password = "MockPassword"
    login_form.submit_login()

    process_gtk_events()

    assert login_form.error_message == "Invalid username."


@pytest.fixture
def controller_mocking_invalid_credentials():
    controller_mock = Mock()

    login_result_future = Future()
    login_result_future.set_result(
        LoginResult(success=False, authenticated=False, twofa_required=False)
    )
    controller_mock.login.return_value = login_result_future

    return controller_mock


def test_login_form_shows_error_when_submitting_wrong_credentials(
        controller_mocking_invalid_credentials
):
    login_form = LoginForm(controller_mocking_invalid_credentials)
    login_form.username = "MockUser"
    login_form.password = "MockPassword"
    login_form.submit_login()

    process_gtk_events()

    assert login_form.error_message == "Wrong credentials."

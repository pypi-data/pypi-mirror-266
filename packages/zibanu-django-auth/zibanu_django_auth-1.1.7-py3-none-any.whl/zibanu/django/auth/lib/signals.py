# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/05/23 11:59
# Project:      Zibanu - Django
# Module Name:  signals
# Description:
# ****************************************************************
"""
Signal definitions for associate to events
"""
from django import dispatch

""" On change password dispatch signal. """
on_change_password = dispatch.Signal()
""" On request password dispatch signal. """
on_request_password = dispatch.Signal()
""" On User Created/Update """
on_user_created = dispatch.Signal()
on_user_updated = dispatch.Signal()
on_user_deleted = dispatch.Signal()

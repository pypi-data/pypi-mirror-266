# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         17/11/23 10:17
# Project:      Zibanu - Django
# Module Name:  backends
# Description:
# ****************************************************************
# Default imports
import logging
import traceback
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.backends import ModelBackend
from zibanu.django.auth.models import User


class ZbAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return

        try:
            user = User._default_manager.get_by_natural_key(username)
        except User.DoesNotExists:
            User.set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
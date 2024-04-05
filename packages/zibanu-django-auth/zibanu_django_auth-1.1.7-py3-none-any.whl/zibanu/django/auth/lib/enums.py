# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         11/11/23 07:27
# Project:      Zibanu - Django
# Module Name:  enums
# Description:
# ****************************************************************
# Default imports
import logging
import traceback
from django.utils.translation import gettext_lazy as _
from zibanu.django.db.models import IntegerChoices


class GroupLevelEnum(IntegerChoices):
    """
    Allowed levels for django groups
    """
    SUPER_USER = 0, _("Superuser")
    STAFF = 1, _("Staff")
    SUPER_ADMIN = 2, _("Super Administrator")
    ADMIN = 3, _("Administrator")
    SUPERVISOR = 4, _("Supervisor")
    OPERATOR = 5, _("Operator")

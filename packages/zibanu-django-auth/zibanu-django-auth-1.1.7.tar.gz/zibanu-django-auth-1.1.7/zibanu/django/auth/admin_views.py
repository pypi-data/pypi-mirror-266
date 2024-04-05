# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         16/11/23 12:00
# Project:      Zibanu - Django
# Module Name:  admin_views
# Description:
# ****************************************************************
# Default imports
import logging
import traceback
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from zibanu.django.auth.models import GroupLevel


class GroupLevelAdmin(admin.ModelAdmin):
    model = GroupLevel
    search_help_text = _("Group level admin")
    list_display = ("group", "level")

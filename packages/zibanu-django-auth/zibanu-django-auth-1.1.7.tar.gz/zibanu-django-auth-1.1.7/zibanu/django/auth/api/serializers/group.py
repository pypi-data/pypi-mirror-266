# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         7/06/23 14:42
# Project:      Zibanu - Django
# Module Name:  group
# Description:
# ****************************************************************
from django.contrib.auth.models import Group

from zibanu.django.auth.lib.enums import GroupLevelEnum
from zibanu.django.rest_framework import serializers


class GroupListSerializer(serializers.ModelSerializer):
    """
    Group entity list serializer
    """
    level = serializers.SerializerMethodField(default=GroupLevelEnum.OPERATOR)

    class Meta:
        """
        GroupListSerializer metaclass
        """
        model = Group
        fields = ("id", "name", "level")

    def get_level(self, instance):
        level = GroupLevelEnum.OPERATOR
        if hasattr(instance, "group_level") and instance.group_level is not None:
            level = instance.group_level.level

        return level

# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         27/04/23 6:57
# Project:      Zibanu - Django
# Module Name:  user
# Description:  Set of serializers for user entity
# ****************************************************************

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .profile import ProfileSerializer, ProfileExtendedSerializer
from zibanu.django.auth.models import User
from zibanu.django.auth.models import UserProfile


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer to get list from user entity
    """
    full_name = serializers.SerializerMethodField(default="Guest")

    class Meta:
        """
        UserListSerializer metaclass
        """
        fields = (
            "full_name", "email", "last_login", "is_staff", "is_superuser", "id", "first_name", "last_name", "level")
        model = User

    def get_full_name(self, instance) -> str:
        """
        Method to get full name from user object instance

        Parameters
        ----------
        instance: User object instance

        Returns
        -------
        full_name: String with user full name
        """
        return instance.get_full_name()


class UserSerializer(UserListSerializer):
    """
    Serializer class for Django user entity, including user profile, permissions and groups (groups).
    """
    profile = ProfileSerializer(required=True, read_only=False)
    roles = serializers.SerializerMethodField(default=[])
    permissions = serializers.SerializerMethodField(default=[])

    def get_permissions(self, instance) -> list:
        """
        Method to get permission list from User object.

        Parameters
        ----------
        instance: User object instance

        Returns
        -------
        permissions: Permission list

        """
        permissions = []
        if self.context.get("load_permissions", settings.ZB_AUTH_INCLUDE_PERMISSIONS):
            for permission in instance.user_permissions.all():
                permissions.append(permission.name)
        return permissions

    def get_roles(self, instance) -> list:
        """
        Method to get groups list from User object

        Parameters
        ----------
        instance: User object instance

        Returns
        -------
        groups: Group list

        """
        roles = []
        if self.context.get("load_roles", settings.ZB_AUTH_INCLUDE_ROLES):
            for group in instance.groups.all():
                roles.append(
                    {
                        "id": group.id,
                        "name": group.name
                    }
                )
        return roles

    def validate(self, attrs: dict) -> dict:
        """
        Method to validate if email is already registered in the user model
        Parameters
        ----------
        attrs : dictionary with user attributes to be validated

        Returns
        -------
        Validated data
        """
        exists = False
        if self.instance is None or (
                self.instance is not None and "email" in attrs and self.instance.email != attrs.get("email")):
            email = attrs.get("email")
            exists = (self.Meta.model.objects.filter(email__exact=email).count() > 0)

        if exists:
            raise ValidationError({"email": _("Email already in use")})

        return super().validate(attrs=attrs)

    def create(self, validated_data) -> User:
        """
        Create a user object including its user profile.

        Parameters
        ----------
        validated_data: Validated data dictionary from serializer

        Returns
        -------
        user_object: User object created if successfully
        """
        email = validated_data.pop("email")
        user_object = self.Meta.model.objects.filter(email__exact=email).first()

        if user_object is None:
            if "password" not in validated_data.keys():
                raise ValidationError(_("The password is required."), "create_user")

            password = validated_data.pop("password")
            username = validated_data.pop("username")
            profile_data = validated_data.pop("profile")
            user_object = self.Meta.model.objects.create_user(username=username, email=email, password=password,
                                                              **validated_data)
            # Create profile
            user_profile = UserProfile(user=user_object, **profile_data)
            user_profile.save(force_insert=True)
        else:
            raise ValidationError(_("Email is already registered in our database."))
        return user_object

    def update(self, instance, validated_data) -> User:
        """
        Update User model and nested models.

        Parameters
        ----------
        instance : instance of UserModel
        validated_data : Data previously validated from serializer

        Returns
        -------
        user_object: instance of user model
        """
        # Save profile data
        profile_data = validated_data.pop("profile")
        profile = instance.profile
        profile.set(profile_data)

        # Save user data
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance

    class Meta:
        """
        UserSerializer metaclass
        """
        model = User
        fields = ("email", "full_name", "last_login", "is_staff", "is_superuser", "is_active", "profile", "roles",
                  "first_name", "last_name", "permissions", "username", "password")


class UserExtendedSerializer(UserSerializer):
    """
    Class to be used to update full user information
    """
    profile = ProfileExtendedSerializer(required=True, read_only=False)


class UserTokenSerializer(UserSerializer):
    """
    Class inherited from UserSerializer to only use in the TokenSerializer for the authentication process.
    """

    class Meta:
        model = User
        fields = ("username", "is_staff", "is_superuser", "level", "full_name", "last_login")


class UserProfileSerializer(UserSerializer):
    """
    Class to be used to update basic profile information
    """
    profile = ProfileExtendedSerializer(required=False, read_only=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "last_login", "profile")

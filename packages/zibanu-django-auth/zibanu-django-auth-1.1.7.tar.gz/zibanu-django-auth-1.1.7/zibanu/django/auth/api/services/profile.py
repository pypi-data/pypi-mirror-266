# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         19/06/23 14:29
# Project:      Zibanu - Django
# Module Name:  profile
# Description:
# ****************************************************************
import logging
import traceback

from django.core.exceptions import ValidationError as CoreValidationError
from rest_framework import status
from rest_framework.response import Response

from zibanu.django.auth.api.serializers import ProfileExtendedSerializer
from zibanu.django.auth.models import UserProfile
from zibanu.django.rest_framework.exceptions import ValidationError, APIException
from zibanu.django.rest_framework.permissions import IsOwnerOrReadOnly
from zibanu.django.rest_framework.viewsets import ModelViewSet
from zibanu.django.utils.error_messages import ErrorMessages
from zibanu.django.utils.user_utils import get_user


class ProfileService(ModelViewSet):
    """
    Set of REST services for UserProfile model
    """
    model = UserProfile
    serializer_class = ProfileExtendedSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def update(self, request, *args, **kwargs) -> Response:
        """
        REST service to update UserProfile model

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters
        **kwargs: Dictionary of parameters

        Returns
        -------
        response: Response object with HTTP status. 200 if success.
        """
        try:
            if request.data is not None:
                user = get_user(request.user)
                if hasattr(user, "profile"):
                    serializer = self.serializer_class(instance=user.profile, data=request.data)
                else:
                    profile = self.model(user=user)
                    serializer = self.serializer_class(instance=profile, data=request.data)

                if serializer.is_valid(raise_exception=True):
                    serializer.save()

            else:
                logging.error("'user': " + ErrorMessages.DATA_REQUEST_NOT_FOUND)
                raise ValidationError(ErrorMessages.DATA_REQUEST_NOT_FOUND)
        except ValidationError as exc:
            raise APIException(detail=exc.detail, http_status=exc.status_code) from exc
        except CoreValidationError as exc:
            logging.warning(str(exc))
            raise APIException(detail=exc.message, code=exc.code, http_status=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except Exception as exc:
            logging.critical(str(exc))
            logging.debug(traceback.format_exc())
            raise APIException() from exc
        else:
            return Response(status=status.HTTP_200_OK)

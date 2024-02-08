from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import XPUser
from .serializers import XPUserSerializer


class XPUserViewSet(viewsets.ModelViewSet):
    queryset = XPUser.objects.all()
    serializer_class = XPUserSerializer

    @action(detail=False, methods=["get"])
    def genders(self, request):
        gender_keys = XPUser.Gender.__members__.keys()
        choices_items = XPUser.Gender.choices
        gender_choices = []
        for key, choice in zip(gender_keys, choices_items):
            gender_choice = {}
            gender_choice["key"] = key
            gender_choice["value"] = choice[1]
            gender_choices.append(gender_choice)
        return Response({"genders": gender_choices})

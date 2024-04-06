from django.db.models import Manager
from django.utils.translation import get_language, activate
from rest_framework import generics


class TranslatedListView(generics.ListAPIView):
    manager: Manager

    def get_queryset(self):
        self.update_lang()
        return self.manager.all()

    def update_lang(self):
        activate(self.get_language())

    def get_language(self):
        return self.request.headers.get('accept-language') or get_language()

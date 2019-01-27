import logging

from django.conf import settings
from django.shortcuts import render


logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'index.html', settings.DEFAULT_CONTEXT)


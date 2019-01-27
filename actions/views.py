import datetime
import json
import logging
from dataclasses import asdict
from pprint import pformat
from copy import deepcopy

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.http import JsonResponse

from .actions import actions_list as mylist

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def actions_list(request):
    """
    This is called by the Looker instance to get a list of available actions.
    The list itself is stored in /actions/actions.py, as the actions_list object.

    The response is provided in JSON format.
    :param request:
    :return:
    """
    logger.info(f'{datetime.datetime.now()} actions_list request received')
    try:
        body = json.loads(request.body)

        for key, value in body.items():
            logger.info(f'{key}:')
            logger.info(str(value))
    except json.JSONDecodeError:
        logger.debug('POST Request with empty or invalid body received at /actions/actions_list/')
        pass

    return JsonResponse(asdict(mylist))


def index(request):
    """
    This is the index page for the actions application. It prints out the actions list and form.
    :param request:
    :return:
    """
    instance = settings.DJAX_LOOKER_INSTANCE
    protocol = settings.DJAX_INSTANCE_PROTOCOL
    port = settings.DJAX_INSTANCE_API_PORT
    looker_instance = f'{protocol}://{instance}:{port}/'

    the_list = deepcopy(asdict(mylist))
    for integration in the_list['integrations']:
        integration.pop('icon_data_uri') # Remove simply for a cleaner context

    context = {
        'actions_list': pformat(the_list),
        'looker_instance': looker_instance
    }

    return render(request, 'actions/index.html', context)

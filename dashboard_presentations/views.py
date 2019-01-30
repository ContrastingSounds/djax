import datetime
import json
from dataclasses import asdict
import logging
from pprint import pformat

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from actions.actions import ActionFormParameter, ActionForm, LookerInstance
from .models import PresentationPayload
from .tasks import generate_presentation_from_dashboard


logger = logging.getLogger(__name__)


@csrf_exempt
def index(request):
    """
    Index page for the Generate PowerPoint action. Lists all PowerPoint template files and generated report decks.
    :param request:
    :return:
    """
    context = {
        'presentation_templates': None, # PresentationTemplate.objects.all(),
        'dashboard_presentations': None, # DashboardPresentation.objects.all()
    }

    return render(request, 'dashboard_presentations/index.html', context)

@require_POST
@csrf_exempt
def generate_dashboard_presentation(request):
    """
    Looker Action Hub webhook to generate a presentation from a dashboard.
    Registers the call to the action hub. If an attachment came with the request (eg csv zip), saves a copy to file.
    Emails the generated presentation to email addresses given as part of the request.
    :param request:
    :return:
    """

    instance = LookerInstance()
    payload = PresentationPayload()

    logger.info(f'{datetime.datetime.now()} generate_dashboard_presentation request received')
    logger.debug(f'Body: {request.body}')

    try:
        payload.body = json.loads(request.body)
        logger.debug(f'Action Body: {payload.body.keys()}')

    except json.JSONDecodeError:
        logger.error(f'POST Request with empty or invalid body received at' 
                     f'/dashboard_presentations/generate_dashboard_presentation: {request.body}')
        return HttpResponse(status=204)

    if 'type' not in payload.body:
        logger.error(f'POST Request received that does not conform to Action Hub protocol: {pformat(payload.body)}')
        return HttpResponse(status=204)

    if 'scheduled_plan' in payload.body:
        payload.url_with_params = payload.body['scheduled_plan']['url']
        payload.url = payload.url_with_params.split('?')[0]

        payload.content_id = payload.url.split('/')[-1]
        payload.content_type = payload.body['scheduled_plan']['type']

        instance_from_url = payload.url.split('/')[2]
        instance.name = instance_from_url.split(':')[0]

        if instance.name == 'self-signed.looker.com':
            instance.name = 'jwtestapi.ngrok.io'
            instance.api_port = 80

    if 'attachment' in payload.body:
        payload.attachment_mimetype = payload.body['attachment']['mimetype'].split(';')[0]

        extension = payload.body['attachment']['extension']
        if extension == 'csv_zip':
            extension = 'csv.zip'
        payload.attachment_extension = extension

        # TODO: Add error handling as per Looks endpoint
        payload.attachment_base64 = payload.body['attachment'].pop('data')

    if 'form_params' in payload.body:
        params = payload.body['form_params']

        if instance.name in ['jwtestapi.ngrok.io', 'localhost', 'self-signed.looker.com']:
            payload.email_destinations = ['jonathan.walls@looker.com']
            payload.email_subject = 'Test email subject'
            payload.email_body = 'Test email body'
        else:
            payload.email_destinations = params['email_address'].split(',')
            payload.email_subject = params['email_subject']
            payload.email_body = params['email_body']

    if payload.content_type.lower() == 'dashboard':
        generate_presentation_from_dashboard.delay(asdict(payload))
    else:
        logger.error('Request to generate dashboard presentation did not contain dashboard reference.')
        return HttpResponse(status=204)

    response_context = {}
    response_context['title'] = 'generate_dashboard_presentation POST received'
    response_context['body'] = f'It was a {payload.body["type"]}'

    return JsonResponse(response_context)

@require_POST
@csrf_exempt
def action_form(request):
    form = ActionForm(
        params=[
            ActionFormParameter(
                name='email_address',
                label='Email Address',
                description='Email address receive link to presentation',
                required=False,
                sensitive=False,
            ),
            ActionFormParameter(
                name='email_subject',
                label='Subject',
                description='Subject line',
                required=False,
                sensitive=False,
            ),
            ActionFormParameter(
                name='email_body',
                label='Body',
                description='Body text',
                required=False,
                sensitive=False,
                type='textarea',
            ),
        ]
    )

    parameter_list = asdict(form)['params'] 

    return JsonResponse(parameter_list, safe=False)
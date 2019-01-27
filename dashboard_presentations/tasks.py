import ast
import os
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from pprint import pformat
from urllib.parse import urlparse

from celery import shared_task
from django.conf import settings
from pptx.util import Cm
import sendgrid
from sendgrid.helpers.mail import Mail, Email, Content, Attachment

import lookerapi as looker

# from .models import PresentationTemplate, DashboardTemplate, DashboardPresentation
from actions.actions import LookerInstance
from .models import PresentationPayload
from djax.utils import get_client


logger = logging.getLogger(__name__)


@dataclass
class LookerDashboardTile:
    id: int = None


@dataclass
class LookerDashboard:
    id: str = None
    tiles: List[LookerDashboardTile] = field(default_factory=list)


@dataclass
class LookerPresentationTile:
    title: str = None
    subtitle: str = None
    body: dict = None
    column: int = None
    row: int = None
    width: int = None
    height: int = None
    x: int = None
    y: int = None
    image_url: str = None
    image_binary: bytes = None
    tile_notes: str = None


@dataclass
class LookerPresentationSlide:
    title: str = None
    layout: str = None
    slide_type: str = None
    tiles: List[LookerPresentationTile] = field(default_factory=list)
    footnote: str = None
    slide_notes: str = None


@dataclass
class LookerPresentation:
    name: str = None
    dashboard_id: int = None
    template: str = None
    tiles: List[LookerPresentationTile] = field(default_factory=list)
    slides: List[LookerPresentationSlide] = field(default_factory=list)
    thumbnail_url: str = None
    thumbnail_binary: bytes = None


def convert_dashboard_tile_to_presentation_tile(element: dict) -> LookerPresentationTile:
    return LookerPresentationTile(
        title=element['title'],
        subtitle=element['subtitle'],
        body=element['slide_params'],
        column=element['column'],
        row=element['row'],
        width=element['width'],
        height=element['height']
    )


def get_image_file(client, element, width, height):
    logger.info('dashboard_presentations.tasks.get_image_file not yet implemented')
    return

    query_api = looker.QueryApi(client)
    element_request = {
        "body": element['slide_params'],
        "result_format": 'png',
        "image_width": width,
        "image_height": height,
        "_preload_content": False,
        # "_request_timeout": 10,
    }

    image_file = os.path.join(settings.WORKING_DIR, f'{element["id"]}.png')
    try:
        image = query_api.run_inline_query(**element_request)

        try:
            os.makedirs(os.path.dirname(image_file), exist_ok=True)
            with open(image_file, 'wb') as temp_image_file:
                temp_image_file.write(image.data)
        except Exception as e:
            logger.warning(f'Failed to save image for {element["id"]}: {element["title"]}\n{e}')
            image_file = None

    except Exception as e:
        logger.error(f'API call failed for {element["id"]}: {element["title"]}\n{pformat(element_request)}',
                     exc_info=True)
        image_file = None

    return image_file


def add_image_to_slide(pptx, slide_no, image_file, hyperlink_link=None,
                       x=IMAGE_X, y=IMAGE_Y, width=VIS_WIDTH_CM):
    logger.info('dashboard_presentations.tasks.add_image_to_slide not yet implemented')
    return

    x_emu = Cm(x)
    y_emu = Cm(y)
    width_emu = Cm(width)

    try:
        picture_shape = pptx.slides[slide_no].shapes.add_picture(image_file, x_emu, y_emu, width_emu)
        if hyperlink_link:
            picture_shape.click_action.hyperlink.address = hyperlink_link

    except Exception as e:
        logger.warning(f'Failed to add image to slide {e}')

    return 0


def add_footnote_to_slide(pptx, slide_no, hyperlink_text, hyperlink_link=None):
    logger.info('dashboard_presentations.tasks.add_footnote_to_slide not yet implemented')
    return

    text_box = pptx.slides[slide_no].shapes.add_textbox(Cm(FOOT_X), Cm(FOOT_Y),
                                                        width=Cm(FOOT_WIDTH), height=Cm(FOOT_HEIGHT))
    p = text_box.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = hyperlink_text
    if hyperlink_link:
        run.hyperlink.address = hyperlink_link
    else:
        run.hyperlink.address = hyperlink_text


@shared_task
# def generate_presentation_from_dashboard(instance: LookerInstanceRecord, payload: PresentationPayload) -> Optional[str]:
def generate_presentation_from_dashboard(payload: dict) -> Optional[str]:
    """
    Generates a report in PowerPoint format, using all looks in a Space.
    1.  Use template associated with this url, if available
    2.  Get dashboard definition from Dashboard API
    3.  Extract dashboard layout
    4.  Convert dashboard element objects to list of dicts – modify for content generation
    5.  Arrange elements for slides
    6.  Validate and prepare slidedeck
    7.  Loop list of tiles and add slides to LookerPresentation object
    8.  Convert LookerPresentation into Google Slides (or PowerPoint)
    9.  Register the generated slidedeck in the application database
    10. Email the report to recipients

    :param instance: LookerInstanceRecord containing details of the Looker instance hosting the dashboard
    :param payload: PresentationPayload with all data regarding the action request
    :return: Some kind of reference to the resulting presentation file
    """

    instance = LookerInstance(
        name=settings.INSTANCE,
        protocol=settings.INSTANCE_PROTOCOL,
        api_port=settings.INSTANCE_API_PORT,
        client_id=settings.USER_ID,
        client_secret=settings.USER_SECRET,
    )

    # payload = PresentationPayload(
    #     body=msg_payload['body'],
    #     content_type=msg_payload['content_type'],
    #     content_id=msg_payload['content_id'],
    #     instance_name=msg_payload['instance_name'],
    #     url=msg_payload['url'],
    #     url_with_params=msg_payload['url_with_params'],
    #     attachment_base64=msg_payload['attachment_base64'],
    #     attachment_mimetype=msg_payload['attachment_mimetype'],
    #     attachment_extension=msg_payload['attachment_extension'],
    #     email_subject=msg_payload['email_subject'],
    #     email_body=msg_payload['email_body'],
    #     email_destinations=msg_payload['email_destinations'],
    # )
    payload = PresentationPayload(**payload)

    parsed_url = urlparse(payload.url_with_params)
    dashboard_id = parsed_url.path.split('/')[2]

    # Get client to the Looker Instance
    try:
        client = get_client(instance)
    except Exception as e:
        logger.error('dashboard_presentations.tasks.py: Failed to get client', exc_info=True)
        return None

    # TODO: Handle filters
    # Get dashboard definition from Dashboard API
    dashboard_api = looker.DashboardApi(client)
    dashboard = dashboard_api.dashboard(dashboard_id)

    # Extract dashboard layout
    dashboard_layout = {}
    for component in dashboard.dashboard_layouts[0].dashboard_layout_components:
        dashboard_layout[component.dashboard_element_id] = {}
        dashboard_layout[component.dashboard_element_id]['column'] = component.column
        dashboard_layout[component.dashboard_element_id]['row'] = component.row
        dashboard_layout[component.dashboard_element_id]['width'] = component.width
        dashboard_layout[component.dashboard_element_id]['height'] = component.height

    ###########################################################
    # Convert dashboard element objects to list of dicts, then:
    # - Filter out vis elements
    # - 'Fix' the dictionary
    #    - have the query dict in a single location (varies between Tiles and Looks)
    #    – remove unwanted fields
    # - Enrich elements with layout information
    # - Sort elements based on layout information
    # - Group elements based on desired slide layout
    ############################################################
    elements = dashboard.dashboard_elements
    dashboard_tiles = [element.to_dict()
                           for element in elements
                           if element.type == 'vis']

    for element in dashboard_tiles:
        # Query dict in different locations depending on whether tile is also a Look
        if element['query']:
            element['slide_params'] = element['query']
        elif element['look']:
            element['slide_params'] = element['look']['query']
        else:
            logging.error(f'Could not find query for {element["id"]} {element["title"]}')
            return None

        # 1. Remove old client_id (a new client_id is generated by the server for each request)
        if 'client_id' in element['slide_params']:
            element['slide_params'].pop('client_id')

        # 2. The dynamic fields string has for some reason been split into individual chars,
        #    need to join them back together.
        if type(element['slide_params']['dynamic_fields']) == list:
            element['slide_params']['dynamic_fields'] = ''.join(element['slide_params']['dynamic_fields'])

        result_maker_vis_config = ast.literal_eval(element['result_maker']['vis_config'])
        element['slide_params']['vis_config'] = result_maker_vis_config

        # Enrich list of elements with layout info
        element['column'] = dashboard_layout[element['id']]['column']
        element['row'] = dashboard_layout[element['id']]['row']
        element['width'] = dashboard_layout[element['id']]['width']
        element['height'] = dashboard_layout[element['id']]['height']

    # Sort tiles to ensure the right order in the presentation
    dashboard_tiles = sorted(dashboard_tiles, key=lambda element: element['column'])
    dashboard_tiles = sorted(dashboard_tiles, key=lambda element: element['row'])

    # Start building LookerPresentation object
    presentation = LookerPresentation(
        name=dashboard.name
    )

    title_slide = LookerPresentationSlide(
        title=dashboard.title,
        slide_type='Title',
        layout='Title Only'
    )
    presentation.slides.append(title_slide)

    # Arrange elements for slides
    slide_idx = 0
    current_row = 0
    tile_buffer = []
    for raw_tile in dashboard_tiles:
        new_tile = convert_dashboard_tile_to_presentation_tile(raw_tile)
        if new_tile.body['vis_config']['type'] != 'single_value':
            new_slide = LookerPresentationSlide(
                slide_type='single',
                tiles=[new_tile]
            )
            presentation.slides.append(new_slide)
            slide_idx += 1
            current_row = new_tile.row + 1

        elif len(presentation.slides) - 1 == slide_idx:
            tile_buffer.append(new_tile)

        elif len(tile_buffer) == 2:
            tile_buffer.append(new_tile)
            new_slide = LookerPresentationSlide(
                slide_type='multiple',
                tiles=tile_buffer
            )
            presentation.slides.append(new_slide)
            tile_buffer = []
            slide_idx += 1
            current_row = new_tile.row + 1

        else:
            if new_tile.row == current_row:
                tile_buffer.append(new_tile)
            else:
                tile_buffer = [new_tile]
                new_slide = LookerPresentationSlide(
                    slide_type='multiple',
                    tiles=tile_buffer
                )
                presentation.slides.append(new_slide)
                slide_idx += 1

    # For dev purposes, dump the presentation contents to the log
    logger.info(f'presentation.name {presentation.name}:\n{presentation}')
    for idx, slide in enumerate(presentation.slides):
        logger.info(f'slide {idx}: {slide}')

    # Save to file

    # Register the generated slidedeck in the application database

    # Email the report to recipients

    return presentation.name

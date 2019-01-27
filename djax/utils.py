import traceback
import logging

import lookerapi as looker

from actions.actions import LookerInstance

logger = logging.getLogger(__name__)


def get_client(instance: LookerInstance):
    base_url = f'https://{instance.instance}/api/3.0'
    logger.info(f'base_url: {base_url}')
    logger.info(f'client_id: {instance.client_id}')
    logger.info(f'client_secret: {instance.client_secret}')

    # instantiate Auth API
    unauthenticated_client = looker.ApiClient(base_url)
    unauthenticated_authApi = looker.ApiAuthApi(unauthenticated_client)

    # TODO: Catch situation where default instance key is updated .. but isn't updated in the Admin UI
    # authenticate client
    try:
        token = unauthenticated_authApi.login(client_id=instance.client_id, client_secret=instance.client_secret)
    except Exception as e:
        logger.error('get_client() failed to get token', exc_info=True)
        return None

    try:
        client = looker.ApiClient(base_url, header_name='Authorization', header_value='token ' + token.access_token)
    except Exception as e:
        logger.error('get_client() failed to authenticate with token', exc_info=True)
        return None

    return client

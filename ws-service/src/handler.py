import json
from typing_extensions import Final

from aiohttp import web

from service import Components


DEFAULT_PAGE_SIZE: Final[str] = "50"


async def get_data(request: web.Request) -> web.Response:
    params = request.rel_url.query
    try:
        page_num = int(params["page_num"])
    except KeyError:
        raise web.HTTPBadRequest(reason="Page number must be provided.")
    except ValueError:
        raise web.HTTPBadRequest(reason="Page number must be numeric.")

    try:
        page_size = int(params.get("page_size", DEFAULT_PAGE_SIZE))
    except ValueError:
        raise web.HTTPBadRequest(reason="Page size must be numeric.")

    components_service: Components = request.app["components_service"]
    results = await components_service.get_next_page(page_num, page_size)

    return web.Response(text=json.dumps(results, default=str), content_type="application/json")

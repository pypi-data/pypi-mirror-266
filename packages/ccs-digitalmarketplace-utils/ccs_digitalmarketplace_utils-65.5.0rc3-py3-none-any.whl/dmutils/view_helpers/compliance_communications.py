from flask import current_app, abort

from .frameworks import get_framework_or_404
from .pagination import get_nav_args_from_api_response_links


def get_framework_and_check_allowed_or_404(client, framework_slug):
    if framework_slug in current_app.config.get('FRAMEWORKS_ALLOWING_COMMUNICATIONS'):
        return get_framework_or_404(
            client,
            framework_slug,
            current_app.config.get('VIEW_COMMUNICATIONS_STATUSES')
        )
    else:
        abort(404)


def get_compliance_communications_content(
    request,
    table_params_method,
    data,
    page_param,
    preserved_kwargs,
    with_supplier=False
):
    return {
        "table_params": table_params_method(
            data['communications'],
            with_supplier
        ),
        "prev_link": get_nav_args_from_api_response_links(
            data["links"],
            "prev",
            request.args,
            preserved_kwargs,
            page_param,
        ),
        "next_link": get_nav_args_from_api_response_links(
            data["links"],
            "next",
            request.args,
            preserved_kwargs,
            page_param,
        )
    }

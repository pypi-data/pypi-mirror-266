from flask import url_for
from jinja2.filters import escape

from .helpers import empty_table, link_html

from dmutils.formats import datetimeformat


def message_status_tag(message):
    if message.get("readAt"):
        return '<strong class="govuk-tag">Read</strong>'
    else:
        return '<strong class="govuk-tag govuk-tag--grey">Unread</strong>'


def list_html(items):
    list_html_string = '<ul class="govuk-list">'

    for item in items:
        list_html_string += f"<li>{item}</li>"

    list_html_string += '</ul>'

    return list_html_string


def message_attachments_html(attachments):
    attachment_links = []

    for attachment in attachments:
        attachment_links.append(link_html(attachment['url'], attachment['name']))

    return list_html(attachment_links)


def message_meta_data(message, for_supplier_view):
    meta_data_items = []

    if message['target'] == 'for_admin' or (message['target'] == 'for_supplier' and not for_supplier_view):
        meta_data_items.append(f"<strong>Sent by:</strong> {escape(message['sentByUserEmail'])}")

    meta_data_items.append(f"<strong>Sent at:</strong> {datetimeformat(message['sentAt'])}")

    if message.get("readAt"):
        if message['target'] == 'for_supplier' or (message['target'] == 'for_admin' and not for_supplier_view):
            meta_data_items.append(f"<strong>Read by:</strong> {escape(message['readByUserEmail'])}")

        meta_data_items.append(f"<strong>Read at:</strong> {datetimeformat(message['readAt'])}")

    return f'''
    <details class="govuk-details">
        <summary class="govuk-details__summary">
            <span class="govuk-details__summary-text">
                View meta data
            </span>
        </summary>
        <div class="govuk-details__text">
            {list_html(meta_data_items)}
        </div>
    </details>
    '''


def _generate_communications_table_params(compliance_communications, with_supplier):
    head = []

    if with_supplier:
        head.append({
            "text": "Supplier"
        })

    head += [
        {
            "text": "Subject"
        },
        {
            "text": "Last message"
        },
        {
            "text": "Status"
        },
    ]

    rows = []

    for compliance_communication in compliance_communications:
        row = []

        if with_supplier:
            row.append({
                "text": compliance_communication["supplierName"]
            })

        row += [
            {
                "html": link_html(
                    url_for(
                        ".view_compliance_communication",
                        communication_id=compliance_communication["id"],
                    ),
                    compliance_communication["subject"],
                )
            },
            {
                "text": datetimeformat(compliance_communication['updatedAt'])
            },
            {
                "html": message_status_tag(compliance_communication['messages'][-1])
            }
        ]

        rows.append(row)

    classes = "dm-compliance-communications-table"

    if with_supplier:
        classes += " dm-compliance-communications-table__with-supplier"

    return {
        'firstCellIsHeader': True,
        "head": head,
        "rows": rows,
        "classes": classes
    }


def generate_communications_for_inbox_table_params(compliance_communications, with_supplier=False):
    decorator = empty_table('There are no communications in the inbox')

    return decorator(_generate_communications_table_params)(
        compliance_communications,
        with_supplier
    )


def generate_communications_for_outbox_table_params(compliance_communications, with_supplier=False):
    decorator = empty_table('There are no communications in the outbox')

    return decorator(_generate_communications_table_params)(
        compliance_communications,
        with_supplier
    )


@empty_table('There are no archived communications')
def generate_archived_communications_table_params(compliance_communications, with_supplier=False):
    head = []

    if with_supplier:
        head.append({
            "text": "Supplier"
        })

    head += [
        {
            "text": "Subject"
        },
        {
            "text": "Archived on"
        }
    ]

    rows = []

    for compliance_communication in compliance_communications:
        row = []

        if with_supplier:
            row.append({
                "text": compliance_communication["supplierName"]
            })

        row += [
            {
                "html": link_html(
                    url_for(
                        ".view_compliance_communication",
                        communication_id=compliance_communication["id"],
                    ),
                    compliance_communication["subject"],
                )
            },
            {
                "text": datetimeformat(compliance_communication['updatedAt'])
            },
        ]

        rows.append(row)

    classes = "dm-compliance-communications-archive-table"

    if with_supplier:
        classes += " dm-compliance-communications-archive-table__with-supplier"

    return {
        'firstCellIsHeader': True,
        "head": head,
        "rows": rows,
        "classes": classes
    }


def generate_communication_messages_table_params_table_params(messages, for_supplier_view=False):
    head = [
        {
            "text": "From",
        },
        {
            "text": "Message",
        },
        {
            "text": "Attachments",
        },
        {
            "text": "Status",
        },
        {
            "text": "Metadata",
        }
    ]

    rows = []

    for message in messages:
        row = [
            {
                "text": "CCS" if message["target"] == "for_supplier" else "Supplier"
            },
            {
                "text": message["text"]
            }
        ]

        if message["attachments"]:
            row.append({
                "html": message_attachments_html(message["attachments"])
            })
        else:
            row.append({
                "text": "No attachements"
            })

        row.append({
            "html": message_status_tag(message)
        })

        row.append({
            "html": message_meta_data(message, for_supplier_view)
        })

        rows.append(row)

    return {
        "head": head,
        "rows": rows,
        "classes": "dm-compliance-communication-messages-table"
    }

import datetime

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse  # type: ignore

from .documents import file_is_less_than_5mb, get_extension, file_is_not_empty
from .s3 import S3ResponseError


ATTACHMENT_FIELDS = [
    'attachment_file_0',
    'attachment_file_1',
    'attachment_file_2',
]


def upload_communication_attachments(
    uploader,
    communications_url,
    framework_slug,
    supplier_id,
    request_files_and_names,
    temporary=False
):
    files = {field: contents for field, contents in request_files_and_names.items() if field in ATTACHMENT_FIELDS}
    files = filter_empty_files(files)
    errors = validate_attachments(files)

    if errors:
        return None, errors

    if len(files) == 0:
        return {}, {}

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")

    for index, [field, contents] in enumerate(files.items()):
        url = upload_communication(
            uploader,
            communications_url,
            framework_slug,
            supplier_id,
            timestamp,
            index,
            contents["name"],
            contents["file"],
            temporary=temporary
        )

        if not url:
            errors[field] = 'file_cannot_be_saved'
        else:
            files[field] = url

    return files, errors


def upload_communication(
    uploader,
    communications_url,
    framework_slug,
    supplier_id,
    timestamp,
    index,
    given_file_name,
    file_contents,
    temporary=False
):
    file_path = generate_file_name(
        framework_slug,
        supplier_id,
        timestamp,
        index,
        given_file_name,
        file_contents.filename,
        temporary=temporary
    )

    try:
        uploader.save(
            file_path,
            file_contents,
            acl='bucket-owner-full-control'
        )
    except S3ResponseError:
        return False

    full_url = urlparse.urljoin(
        communications_url,
        file_path
    )

    return full_url


def move_attachment_from_temp_folder(
    mover,
    communications_bucket,
    object_key
):
    if '/temp' not in object_key:
        raise ValueError(f"Target key '{object_key}' is not in the temp folder")

    mover.copy(
        src_bucket=communications_bucket,
        src_key=object_key,
        target_key=object_key.replace('/temp', '')
    )
    mover.delete_key(object_key)


def generate_file_name(
    framework_slug,
    supplier_id,
    timestamp,
    index,
    given_file_name,
    filename,
    temporary=False
):
    normalised_file_name = given_file_name.replace(" ", "_")

    if temporary:
        return '{}/compliance-communications/temp/{}/{}/{}/{}{}'.format(
            framework_slug,
            supplier_id,
            timestamp,
            index,
            normalised_file_name,
            get_extension(filename)
        )

    return '{}/compliance-communications/{}/{}/{}/{}{}'.format(
        framework_slug,
        supplier_id,
        timestamp,
        index,
        normalised_file_name,
        get_extension(filename)
    )


def validate_attachments(files):
    errors = {}

    for field, contents in files.items():
        if not file_is_less_than_5mb(contents["file"]):
            errors[field] = 'file_is_more_than_5mb'

    return errors


def filter_empty_files(files):
    return {
        key: contents for key, contents in files.items()
        if file_is_not_empty(contents['file'])
    }

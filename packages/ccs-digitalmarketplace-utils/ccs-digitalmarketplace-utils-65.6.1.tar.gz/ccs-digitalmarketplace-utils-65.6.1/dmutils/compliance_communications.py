from .documents import get_extension, file_is_not_empty
from .s3 import S3ResponseError


ATTACHMENT_FIELDS = [
    'attachment_file_0',
    'attachment_file_1',
    'attachment_file_2',
]


def upload_communication_attachments(
    uploader,
    framework_slug,
    supplier_id,
    message_id,
    request_files_and_names,
    temporary=False
):
    files = {field: contents for field, contents in request_files_and_names.items() if field in ATTACHMENT_FIELDS}
    files = filter_empty_files(files)
    errors = {}

    if len(files) == 0:
        return {}, {}

    for field, contents in files.items():
        url = upload_communication(
            uploader,
            framework_slug,
            supplier_id,
            message_id,
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
    framework_slug,
    supplier_id,
    message_id,
    given_file_name,
    file_contents,
    temporary=False
):
    file_path, file_name = generate_file_name(
        framework_slug,
        supplier_id,
        message_id,
        given_file_name,
        file_contents.filename,
        temporary=temporary
    )

    try:
        uploader.save(
            f'{file_path}/{file_name}',
            file_contents,
            acl='bucket-owner-full-control'
        )
    except S3ResponseError:
        return False

    return file_name


def generate_file_name(
    framework_slug,
    supplier_id,
    message_id,
    given_file_name,
    filename,
    temporary=False
):
    normalised_file_name = given_file_name.replace(" ", "_")

    if temporary:
        path_template = '{}/compliance-communications/temp/{}/{}'
    else:
        path_template = '{}/compliance-communications/{}/{}'

    return (
        path_template.format(
            framework_slug,
            supplier_id,
            message_id
        ),
        '{}{}'.format(
            normalised_file_name,
            get_extension(filename)
        )
    )


def move_attachment_from_temp_folder(
    mover,
    communications_bucket,
    framework_slug,
    supplier_id,
    old_message_id,
    new_message_id,
    object_key
):
    src_key = '{}/compliance-communications/temp/{}/{}/{}'.format(
        framework_slug,
        supplier_id,
        old_message_id,
        object_key
    )

    if mover.copy(
        src_bucket=communications_bucket,
        src_key=src_key,
        target_key=src_key.replace('/temp', '').replace(str(old_message_id), str(new_message_id))
    ):
        mover.delete_key(src_key)


def filter_empty_files(files):
    return {
        key: contents for key, contents in files.items()
        if file_is_not_empty(contents['file'])
    }

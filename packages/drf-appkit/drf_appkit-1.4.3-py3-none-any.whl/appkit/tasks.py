import logging

from versatileimagefield.image_warmer import VersatileImageFieldWarmer

from .debug import log
from .models import ImageAttachment


def imageattachment_warm_renditions(image_attachment_pk):
    try:
        image_attachment = ImageAttachment.objects.get(pk=image_attachment_pk)
    except ImageAttachment.DoesNotExist:
        log(f'ImageAttachment not found (PK: {image_attachment_pk}', level=logging.ERROR)
        return False

    if not (image_attachment.image and image_attachment.rendition_key):
        # This image does not support any renditions. Do nothing
        return True

    try:
        VersatileImageFieldWarmer(
            instance_or_queryset=image_attachment,
            rendition_key_set=image_attachment.rendition_key,
            image_attr='image'
        ).warm()
        image_attachment.warm = True
        image_attachment.save()
        return True
    except ValueError as e:
        log(f'Task `warm_image_attachment` failed with exception: {str(e)}')
        return False

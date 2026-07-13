from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import AnswerImage, QuestionImage


def delete_image_file(image_field):
    if not image_field or not image_field.name:
        return

    storage = image_field.storage
    image_name = image_field.name

    transaction.on_commit(
        lambda: storage.delete(image_name)
    )


@receiver(post_delete, sender=QuestionImage)
def delete_question_image_file(sender, instance, **kwargs):
    delete_image_file(instance.image)


@receiver(post_delete, sender=AnswerImage)
def delete_answer_image_file(sender, instance, **kwargs):
    delete_image_file(instance.image)
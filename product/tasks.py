from datetime import timedelta
from celery import shared_task
from .models import Product
from django.db.models import Avg
from django.utils import timezone
from users.models import CustomUser
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def recalculate_product_rating(product_id):
    product = Product.objects.get(id=product_id)
    avg_stars = product.reviews.aggregate(Avg('stars'))['stars__avg'] or 0.0

    product.rating = round(avg_stars, 2)
    product.save()

    return f"Рейтинг продукта {product_id} изменен на {product.rating}"


@shared_task
def delete_unconfirmed_users():
    expiration_time = timezone.now() - timedelta(hours=24)

    deleted_count = CustomUser.objects.filter(
        is_active=False,
        date_joined__lt=expiration_time
    ).delete()

    return f"Удалено {deleted_count} неподтвержденных пользователей"


@shared_task
def send_new_review_notification(product_title,stars, text):
    send_mail(
        subject=f"Новый отзыв ({stars}★) на товар: {product_title}",
        message=f"Поступил новый отзыв:\n\nОценка: {stars}/5\nТекст: {text}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["moderator@shop.com"],
        fail_silently=False,
    )





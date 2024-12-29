from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review

@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance, created, **kwargs):
    product = instance.product
    if created:
        product.update_avg_rating(instance.rating)
    else:
        all_reviews = Review.objects.filter(product=product)
        total_rating = sum([review.rating for review in all_reviews])
        product.avg_rating = total_rating / all_reviews.count()
        product.rating_count = all_reviews.count()
        product.save()

@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sender, instance, **kwargs):
    product = instance.product
    all_reviews = Review.objects.filter(product=product)
    if all_reviews.exists():
        total_rating = sum([review.rating for review in all_reviews])
        product.avg_rating = total_rating / all_reviews.count()
        product.rating_count = all_reviews.count()
    else:
        product.avg_rating = 0
        product.rating_count = 0
    product.save()
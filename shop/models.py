from django.urls.conf import re_path
import numpy
from embed_video.fields import EmbedVideoField
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.core.validators import FileExtensionValidator
from abc import abstractmethod
from typing import ClassVar, final
from django.contrib.auth.models import User
from django.db import models
from django.db.models import aggregates
from django.db.models.base import Model
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db.models.fields import AutoField, CharField, SmallIntegerField
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from django.urls import reverse
from django.utils import timezone
from orders.models import CartProduct

USER = get_user_model()

SEX_CHOICE = [
    ('М', 'Мужчины'),
    ('Ж', 'Женщины'),
    ('У', 'Унисекс')
]


def get_model_url(model):
    ct_model = model.__class__._meta.model_name
    category_slug = model.category.slug
    slug = model.slug
    # /products/shoes/sport/slug
    print(category_slug)

    return reverse('catalog', kwargs={'ct_model': ct_model, 'slug': slug})


class LatestProductManager:

    @staticmethod
    def get_products_for_model(*args, amount=6):  # get amount!
        products = []

        ct_models = ContentType.objects.filter(model__in=args)

        for model in ct_models:
            model_products = model.model_class(
            )._base_manager.all().order_by('-id')

            products.extend(model_products)

        return products[:amount]

    @staticmethod
    def get_products_for_category(*args, amount=6):
        products = []

        for model in PRODUCT_MODELS.values():
            model_products = model.objects.filter(
                category__name__in=args).order_by('-id')

            products.extend(model_products)

        return products[:amount]


class LatestProduct:

    objects = LatestProductManager()

# Create your models here.


class CategoryManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()

    def count_objects_into_model(self, model_name):
        qs = self.get_queryset().annotate(models.Count(model_name))
        return qs


class ProductManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_model(self):
        model_objects = self.get_queryset().all()
        categories = {}

        for c in GenericCategory.objects.all():
            models = model_objects.filter(categories__name=c.name)
            if models:
                categories[c.name] = models

        return categories


class AbstractProduct(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(verbose_name='Название товара', max_length=220,
                            help_text='Название будет автоматически переведено в нижний регистр для корректной работы поиска')
    image = models.ImageField(verbose_name='Изображение')
    discription = models.TextField(verbose_name='Описание товара')

    slug = models.SlugField(unique=True)

    sex = models.CharField(verbose_name='Пол', max_length=1,
                           choices=SEX_CHOICE, default=SEX_CHOICE[2])
    # age_group = CharField(choices=)
    price = models.DecimalField(
        verbose_name='Цена товара', max_digits=9, decimal_places=0)
    material = models.CharField(verbose_name='Материал', max_length=300)
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True)
    is_presence = models.BooleanField(default=True, verbose_name='Наличие')

    categories = models.ManyToManyField(
        'GenericCategory', verbose_name='Категории')
    video_url = EmbedVideoField(
        verbose_name='Ссылка на видео обзор', null=True, blank=True)
    video_file = models.FileField(
        verbose_name='Видео обзор',
        null=True, blank=True,
        upload_to='video',
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])])

    comments = GenericRelation('Comment')
    objects = ProductManager()




    def get_model_name(self):
        return self.__class__._meta.model_name

    def count_mean_marks(self):
        if self.comments.all():
            mean_mark = 0

            for comment in self.comments.all():
                mean_mark += comment.mark.get_mean_mark()

            return round(mean_mark/self.comments.count(), 1)
        return 'Оценок пока нет'

    def get_video(self):
        if self.video_url:
            return self.video_url
        elif self.video_file:
            return self.video_file.url
        else:
            return None

    def presence(self):
        if self.is_presence:
            return 'Товар в наличии'
        return 'Товара нет в наличии('

    def is_new_item(self):
        t = timezone.now() - self.pub_date
        if t.days < 7:
            return True
        return False

    @property
    def get_name(self):
        return self.name.title()

    def __str__(self):
        return self.get_name



class GenericCategory(models.Model):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    name = CharField(max_length=100, verbose_name='Название категории')
    objects = CategoryManager()

    def __str__(self):
        return self.name


class Comment(models.Model):

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор комментария', null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    mark = models.ForeignKey('Mark', verbose_name='Оценка',
                             on_delete=models.SET_NULL, null=True, related_name='mark')
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(
        verbose_name='Дата создания комментария', auto_now_add=True)

    def __str__(self):
        if self.author:
            return 'Коментарий от ->{}'.format(self.author.username)

        return 'Коментарий от анонима'


class Mark(models.Model):
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'

    comment = ForeignKey('Comment', on_delete=models.CASCADE,
                         related_name='comment', null=True)
    visual = models.SmallIntegerField(verbose_name="Внешний вид", null=True)
    quality = models.SmallIntegerField(verbose_name='Качество',  null=True)
    price = models.SmallIntegerField(verbose_name='Цена',  null=True)
    convenience = models.SmallIntegerField(verbose_name='Удобство',  null=True)

    set_date = models.DateTimeField(
        verbose_name='Время выставления оценки', auto_now_add=True)

    def get_mean_mark(self):
        return round(((self.visual + self.quality + self.price + self.convenience) / 4), 1)

    def __str__(self):
        return f'Оценка'


class Garment(AbstractProduct):

    class Meta:
        verbose_name = 'Одежда'
        verbose_name_plural = 'Одежда'

    def get_absolute_url(self):
        return get_model_url(self)


class Shoes(AbstractProduct):

    class Meta:
        verbose_name = 'Обувь'
        verbose_name_plural = 'Обувь'

    def get_absolute_url(self):
        return get_model_url(self)


class Accessory(AbstractProduct):

    class Meta:
        verbose_name = 'Аксессуары'
        verbose_name_plural = 'Аксессуары'

    def get_absolute_url(self):
        return get_model_url(self)


@receiver(pre_delete, sender=Shoes)
def delete_media(sender, instance, **kwargs):
    # CartProduct.objects.filter(object_id=instance.id).delete()
    if instance.video_file:
        instance.video_file.delete(False)
    
    if instance.image:
        instance.image.delete(False)
        
        
@receiver(pre_delete, sender=Garment)
def delete_media(sender, instance, **kwargs):
    # CartProduct.objects.filter(object_id=instance.id).delete()
    if instance.video_file:
        instance.video_file.delete(False)
    
    if instance.image:
        instance.image.delete(False)
        
        
@receiver(pre_delete, sender=Accessory)
def delete_media(sender, instance, **kwargs):
    # CartProduct.objects.filter(object_id=instance.id).delete()
    if instance.video_file:
        instance.video_file.delete(False)
    
    if instance.image:
        instance.image.delete(False)
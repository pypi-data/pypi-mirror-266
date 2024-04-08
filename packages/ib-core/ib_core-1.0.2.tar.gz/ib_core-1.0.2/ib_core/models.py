import uuid
from abc import abstractmethod
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.utils import timezone

from ib_core.fields import OneToManyField
from django.db import models

from ib_core.mixins.authorization import AuthorizationReader
from ib_core.tags.manage import create_tag_and_get_text_tag_id, get_tag, create_tag_and_get_file_tag_id, \
    get_tags_by_value


class UUIDModelManager(models.Manager):
    def all(self):
        return super(UUIDModelManager, self).filter(Q(deleted=None))


class UUIDModel(models.Model):
    """
    Base Model of IB Core.

    Inherit your own models from it to use the tag system.
    The field 'tag_manager' adds automatically to instances.
    """
    id = models.UUIDField(verbose_name='UUID', primary_key=True, default=uuid.uuid4, editable=False)
    objects = models.Manager()
    tag_manager = models.OneToOneField("ib_core.TagManager", on_delete=models.CASCADE)
    creator = models.UUIDField()
    create_date_time_stamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата привязки')
    deleted = models.DateTimeField(null=True, blank=True, verbose_name="Удален")

    class Meta:
        abstract = True

    @classmethod
    def filter(cls, **kwargs):
        return cls.objects.filter(**kwargs)

    def save(self, *args, **kwargs):
        try:
            manager = self.tag_manager
        except:
            self.tag_manager = TagManager.create(str(self.creator))
        super(UUIDModel, self).save(*args, **kwargs)

    def parse_to_tags(self, auth: AuthorizationReader):
        """
        ! in the development !
        """
        if isinstance(self, UUIDModel):
            raise Exception("The method 'parse_to_tags' is not applicable for Base Model (UUIDModel)")
        fields: list[Field] = self._meta.fields  # noqa
        fields = [field.name for field in fields]  # noqa
        # self.creator

    def _get_field_value(self, model, field_name):
        """
        ! in the development ! (private)
        """
        field_object = model._meta.get_field(field_name)  # noqa
        field_value = field_object.value_from_object(self)

    def delete(self, using=None, keep_parents=False):
        self.deleted = timezone.now()
        self.save()

    def db_delete(self, using=None, keep_parents=False):
        super(UUIDModel, self).delete(using=None, keep_parents=False)

    @classmethod
    def all(cls):
        return cls.objects.filter(Q(deleted=None))


class User(AbstractUser):
    id = models.UUIDField(verbose_name='Идентификатор пользователя', primary_key=True, default=uuid.uuid4,
                          editable=False)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class ActivityPeriod(UUIDModel):
    start_time = models.DateTimeField(verbose_name="Начало активности")
    end_time = models.DateTimeField(verbose_name="Окончание активности", null=True, blank=True)

    class Meta:
        verbose_name = "Период активности"
        verbose_name_plural = "Периоды активности"
        db_table = "table_03_activity_periods"

    def to_dict(self):
        return dict(
            id=self.id,
            start_time=self.start_time,
            end_time=self.end_time,
            creator=self.creator
        )

    def is_active(self):
        if not self.start_time and not self.end_time:
            return False
        if not self.end_time and self.start_time > timezone.now():
            return True
        if self.start_time < timezone.now() < self.end_time:
            return True
        return False


class Tag:
    id: str
    content: str
    file: str
    creator: str
    create_datetime_stamp: str
    publication_start_datetime_stamp: str
    publication_stop_datetime_stamp: str
    block_datetime_stamp: str

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.content = kwargs.get("content")
        self.file = kwargs.get("file")
        self.creator = kwargs.get("creator")
        self.create_datetime_stamp = kwargs.get("create_datetime_stamp")
        self.publication_start_datetime_stamp = kwargs.get("publication_start_datetime_stamp")
        self.publication_stop_datetime_stamp = kwargs.get("publication_stop_datetime_stamp")
        self.block_datetime_stamp = kwargs.get("block_datetime_stamp")


class TagBinder(models.Model):
    """
    Model for linking Tag objects to any models
    """
    id = models.UUIDField(verbose_name='UUID', primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, db_index=True)
    tag = models.UUIDField()
    related_manager = models.ForeignKey(
        "ib_core.TagManager",
        on_delete=models.CASCADE,
        verbose_name='Связанный менеджер',
        related_name="manager"
    )
    bind_creator = models.CharField(max_length=150, null=True, verbose_name='Создатель')
    create_date_time_stamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата привязки')
    allow_many = models.BooleanField(default=False, verbose_name='Разрешен список значений')

    class Meta:
        indexes = [
            models.Index(fields=["key", "related_manager"])
        ]
        db_table = 'table_01_tag_binders'
        verbose_name = 'Связка тега'
        verbose_name_plural = 'Связки тегов'

    def __str__(self):
        return f"{self.related_manager} {self.key} property"

    def get_tag(self, token) -> Tag | None:
        """
        Returns Tag instance by his UUID (using IB Tags Module)
        """
        tag = get_tag(self.tag, token)
        return Tag(**tag) if tag else None

    def override_tag(self, tag_id: str):
        """
        Overrides tag value (UUID) for binder if it not allows many
        """
        if not self.allow_many:
            self.tag = tag_id
            self.save()

    def to_dict(self, auth: AuthorizationReader) -> dict:
        """
        Converts instance to dictionary
        """
        key = self.key
        tag = get_tag(uuid=self.tag, auth=auth)

        return {
            "id": self.pk,
            "key": key,
            "tag": tag
        }


class TagManager(models.Model):
    """
    A model for creating, updating, and managing tags.
    """
    id = models.UUIDField(verbose_name='UUID', primary_key=True, default=uuid.uuid4, editable=False)
    tags = OneToManyField(TagBinder, verbose_name="Свойства")
    creator = models.UUIDField()
    create_datetime_stamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата привязки')

    objects = models.Manager()

    class Meta:
        verbose_name = "Менеджер тегов"
        verbose_name_plural = "Менеджеры тегов"

    def __str__(self):
        return f"Manager {self.pk}"

    @staticmethod
    def create(creator_id: str):
        instance = TagManager(
            creator=creator_id
        )
        instance.save()
        return instance

    ################
    # for revision #
    ################
    @classmethod
    def filter_by_property_value(cls, key: str, value: str, auth: AuthorizationReader):
        tags = [tag["id"] for tag in get_tags_by_value(value, auth)]
        models_filter = cls.objects.filter(tags__key=key, tags__tag__in=tags)
        return list(models_filter)

    def _add_tag(self, key: str, tag_id: str, creator: str, allow_many: bool = False):
        """
        Adds new instance property (private)
        """
        print(creator)
        tag_binder = TagBinder(
            key=key,
            tag=tag_id,
            related_manager=self,
            bind_creator=creator,
            allow_many=allow_many
        )
        tag_binder.save()
        self.tags.add(tag_binder)  # noqa

    def get_property(self, key: str) -> TagBinder | list[TagBinder] | None:
        """
        Returns property object(s) by key (property name)
        """
        _property: list[TagBinder] = list(TagBinder.objects.filter(
            related_manager__id=self.pk,
            key=key
        ))
        if not _property:
            return None
        else:
            if not _property[0].allow_many:
                return _property[0]
            else:
                return _property

    def get_all_properties(self) -> list[TagBinder]:
        """
        Returns all properties
        """
        return list(self.tags.all())  # noqa

    def add_tag(
            self,
            key: str,
            auth: AuthorizationReader,
            creator: str,
            content: str = None,
            file: Any = None,
            allow_many=False) -> bool:
        """
        Description:
            Adds or overrides instance property

        Parameters:
            key: name of property.
            content: value of property (text_tag).
            file: file of property (file_tag).
            auth: authorization info of the user adding the property.
            creator: username of the user adding the property.
            allow_many: flag that defines the possibility of creating a set of properties with this key.
        Returns:
            Bool: True if operation is successful else False
        """
        if content is not None:
            tag = create_tag_and_get_text_tag_id(str(content), auth)
        elif file is not None:
            tag = create_tag_and_get_file_tag_id(file, auth)
        else:
            raise Exception

        success = False
        _property = self.get_property(key)
        if tag:
            if _property:
                # Checking TagBinder for allow_many
                if isinstance(_property, list):
                    # if property allows many
                    _property_values = [unit.tag for unit in _property]
                    if tag not in _property_values:
                        self._add_tag(key, tag, creator, allow_many=True)
                    pass
                else:
                    # if property NOT allows many
                    _property.override_tag(tag)
            else:
                # creating new property
                self._add_tag(key, tag, creator, allow_many=allow_many)
            success = True
        return success

    def to_dict(self, auth: AuthorizationReader) -> dict:
        """
        Converts instance to dictionary
        """
        instance_dict = {"id": self.pk}

        tags = self.get_all_properties()
        for tag in tags:
            if not tag.allow_many:
                instance_dict[tag.key] = tag.to_dict(auth).get("tag")
            else:
                if tag.key not in instance_dict.keys():
                    instance_dict[tag.key] = []
                instance_dict[tag.key].append(tag.to_dict(auth).get("tag"))

        return instance_dict

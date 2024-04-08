from django.db import models
from django.db.models.fields.related import ManyToManyRel, ReverseOneToOneDescriptor
from django.utils.translation import gettext_lazy as _


class OneToManyRel(ManyToManyRel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.multiple = False


# connecting to remote repository test


class OneToManyField(models.ManyToManyField):
    rel_class = OneToManyRel

    description = _("One-to-many relationship")

    def contribute_to_class(self, cls, name):
        # The intermediate m2m model is not auto created if:
        #  1) There is a manually specified intermediate, or
        #  2) The class owning the m2m field is abstract.
        #  3) The class owning the m2m field has been swapped out.
        auto_created = not self.remote_field.through and not cls._meta.abstract and not cls._meta.swapped

        super(OneToManyField, self).contribute_to_class(cls, name)

        # Set unique_together to the 'to' relationship, this ensures a OneToMany relationship.
        if auto_created:
            through_opts = self.remote_field.through._meta
            through_opts.unique_together = ((through_opts.unique_together[0][1],),)

    def contribute_to_related_class(self, cls, related):
        super().contribute_to_related_class(cls, related)
        # override ManyToManyDescriptor
        setattr(cls._meta.concrete_model, related.get_accessor_name(), ReverseOneToOneDescriptor(related))

    def get_forward_related_filter(self, obj):
        return {self.name: obj}

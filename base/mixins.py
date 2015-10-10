from django.forms.models import model_to_dict


class TrackedModelMixin(object):
    """
    A model mixin that tracks model fields' values and provide some useful api
    to know what fields have been changed.
    """

    tracked_fields = None
    updated = False

    def __init__(self, *args, **kwargs):
        super(TrackedModelMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def changes(self):
        d1 = self.__initial
        d2 = self._dict
        return {
            k: (v, d2[k])
            for k, v in d1.iteritems()
            if v != d2[k]
        }

    @property
    def has_changed(self):
        return bool(self.changes)

    @property
    def changed_fields(self):
        return self.changes.keys()

    def get_tracked_fields(self):
        tracked_fields = self.tracked_fields or []
        return [f.name for f in self._meta.fields if f.name in tracked_fields]

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        # Flag object as updated if new or tracked fields have changed
        if self._state.adding or self.has_changed:
            self.updated = True

        super(TrackedModelMixin, self).save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=self.get_tracked_fields())


class AddressTrackedModelMixin(TrackedModelMixin):
    tracked_fields = ('address',)

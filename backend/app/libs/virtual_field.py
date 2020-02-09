from django.db.models import Field, IntegerField
from django.conf import settings


class VirtualField(Field):

    auto_created = False
    concrete = False
    editable = False 
    hidden = False

    is_relation = False
    many_to_many = False
    many_to_one = False
    one_to_many = False
    one_to_one = False
    related_model = None

    def __init__(self, value, fget=None, fset=None, target_ignore_none=False, act_as_field=True, verbose_name=None, *args, **kwargs):
        # self.fget, self.fset = fget, fset
        # if fget is not None and hasattr(fget, '__name__'):
        #     self.name = fget.__name__
        # else:
        #     self.name = None
        self.name = self.__name__
        self.act_as_field = act_as_field
        self.value = value
        # self.target_ignore_none = target_ignore_none
        # doc = getattr(fget, '__doc__', None)
        # if doc is not None:
        #     self.__doc__ = doc
        # super(VirtualField, self).__init__(*args, **kwargs)
        # self.verbose_name = verbose_name
        if not act_as_field:
            self.short_description = verbose_name
        super().__init__()

    __name__ = 'VirtualField'

        
    # def getter(self, fget):
    #     self.fget = fget
    #     if self.name is None and fget is not None and hasattr(fget, '__name__'):
    #         self.name = fget.__name__
    #     doc = getattr(fget, '__doc__', None)
    #     if doc is not None:
    #         self.__doc__ = doc
    #     return self

    # def setter(self, fset):
    #     self.fset = fset
    #     return self

    # def get_attname(self):
    #     return self.name

    def get_attname_column(self):
        return self.get_attname(), None

    # def set_attributes_from_name(self, name):
    #     if not self.name:
    #         self.name = name
    #     self.attname, self.column = self.get_attname(), None
    #     self.concrete = False
    #     if self.verbose_name is None and name:
    #         self.verbose_name = name.replace('_', ' ')
    #         if not self.act_as_field:
    #             self.short_description = self.verbose_name

    def contribute_to_class(self, cls, name):
        """Applies this field to the `cls' class, with name `name'"""
        self.name = name
        self.set_attributes_from_name(name)
        self.concrete = False  # Force non-concrete
        self.model = cls
        # Django >=1.6 required
        if self.act_as_field:
            if hasattr(cls._meta, 'add_virtual_field'):
                cls._meta.add_virtual_field(self)
            else:
                try:
                    cls._meta.add_field(self, virtual=True)
                except:
                    if hasattr(cls._meta, 'virtual_fields'):
                        cls._meta.virtual_fields.append(self)
                    else:
                        # Just act as a property
                        pass
        setattr(cls, name, self)


    # __call__ = getter  # Acts as getter

    def __get__(self, instance, owner=None):
        # if instance is None:
        #     return self
        # if self.name in instance.__dict__:
        #     # Not taking very advantage of cache :/
        #     return instance.__dict__[self.name]
        # if self.fget is None:
        #     raise AttributeError("This virtual field is not readable")
        # value = self.fget(instance)
        # return value
        return self.value


    # def __set__(self, instance, value):
    #     if instance is None:
    #         raise ValueError("instance is None")
    #     if self.fset is not None:
    #         self.fset(instance, value)
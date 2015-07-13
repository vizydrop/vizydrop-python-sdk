from datetime import date, datetime
from decimal import Decimal
import inspect
import collections

from copy import deepcopy
import re


class Field(object):
    _type = None
    _api_type = None

    def __init__(self, name=None, default=None, description=None, optional=True, get_options=None, options=None,
                 response_loc=None):
        """
        A Field represents a data field in a schema or account
        :param name: Title of the field
        :param default: Default value
        :param description: Long description of what this field represents
        :param optional: If user-defined, is this an optional field?
        :param get_options: Function to grab possible values for this field
        :param response_loc: If gathered from a 3rd-party, where is this field represented in the data?
                             Nested dicts can be separated by a hyphen (-)
        :return:
        """
        self._name = name
        self._description = description
        self._value = default
        self._default = default
        self._optional = optional
        self._data_list_function = get_options
        self._options = options
        self.response_location = response_loc

        if self._api_type is None:
            self._api_type = str(self._type)

    def __str__(self):
        return self.convert_value(self._value).__str__()

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default

    @property
    def description(self):
        return self._description

    @property
    def value(self):
        if self._value is None:
            return None
        return self.convert_value(self._value)

    @property
    def required(self):
        return not self._optional

    @property
    def optional(self):
        return self._optional

    def set(self, value):
        if isinstance(value, Field):
            value = value.convert_value(value.value)
        self._value = value

    @property
    def type(self):
        return self._type.__name__

    @property
    def get_options(self):
        if callable(self._data_list_function):
            return self._data_list_function
        return None

    @property
    def options(self):
        return self._options

    def convert_value(self, value):
        if value is None:
            return None
        if not isinstance(value, self._type):
            return self._type(value)
        return value

    @property
    def api_type(self):
        # datalist fields should be a "list" type, but NOT multilist types regardless of datalist
        if self._data_list_function is not None or self._options is not None:
            if self._api_type is not 'multilist':
                return 'list'
        return self._api_type

    def get_api_description(self, name=True, datalist=False, optional=False):
        """
        Get a formatted dictionary with descriptors about this field for the API
        :param name: Should the title be included?
        :param datalist: Should the datalist (bool) be included?
        :param optional: Should the optional (bool) be included?
        :return: dict
        """
        ret = {
            "description": self.description,
            "type": self.api_type
        }
        if name:
            ret.update({"name": self.name})
        if datalist:
            if self._options is not None:
                ret.update({"options": self._options})
            if self._data_list_function is None:
                ret.update({"datalist": False})
            else:
                ret.update({"datalist": True})
                argspec = inspect.getargspec(self._data_list_function)
                required_args = argspec[0][1:]
                ret.update({"datalist_requires": required_args})
        if optional:
            ret.update({"optional": self.optional})
        return ret

    def is_valid(self):
        return True


class OrderedClassMembers(type):
    @classmethod
    def __prepare__(mcs, name, bases):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, classdict):
        classdict['__ordered__'] = [key for key in classdict.keys()
                                    if key not in ('__module__', '__qualname__')]
        for base in bases:
            if hasattr(base, '__ordered__'):
                classdict['__ordered__'] += base.__ordered__
        return type.__new__(mcs, name, bases, classdict)


class FieldedObject(object, metaclass=OrderedClassMembers):
    """
    Base class for an object containing fields, handles get/set functions and adds some helper/utility functions
    """

    def __init__(self, initial=None, *args, **kwargs):
        # copy our fields locally
        for field_name, field in self.get_all_fields():
            super(FieldedObject, self).__setattr__(field_name, deepcopy(field))
        if initial:
            self.update(initial)
        super(FieldedObject, self).__init__(*args, **kwargs)

    def __setattr__(self, item, value):
        attr = self.__getattribute__(item, return_raw=True)

        if not isinstance(value, Field) and isinstance(attr, Field):
            attr.set(value)
        else:
            super(FieldedObject, self).__setattr__(item, value)

    def __getattribute__(self, item, return_raw=False):
        try:
            attr = super(FieldedObject, self).__getattribute__(item)
            if isinstance(attr, Field):
                if return_raw:
                    return attr
                else:
                    return attr.value
            return attr
        except AttributeError:
            return None

    def __str__(self):
        obj = {}
        for key, field in self.get_all_fields():
            obj.update({key: field.value})
        return obj.__str__()

    def __getitem__(self, item):
        try:
            ret = super(FieldedObject, self).__getitem__(item)
            return ret
        except KeyError:
            field = self.__getattribute__(item, return_raw=True)
            if field is not None:
                return field.default
            raise

    def update(self, update_dict):
        if isinstance(update_dict, self.__class__):
            update_dict = update_dict.__dict__
        if not update_dict:
            return
        update_dict.pop('_cls', None)
        for key, value in update_dict.items():
            attr = self.__getattribute__(key, return_raw=True)
            if isinstance(attr, Field):
                attr.set(value)
            else:
                self.__setattr__(key, value)

    def get_field(self, field):
        attr = self.__getattribute__(field, return_raw=True)
        if isinstance(attr, Field):
            return field
        return None

    @classmethod
    def get_all_fields(cls):
        fields = []
        for attr in cls.__ordered__:
            field = getattr(cls, attr)
            if issubclass(type(field), Field):
                fields.append((attr, field, ))
        return fields

    def json_repr(self, include_class=True, include_id=False):
        obj = {}
        for key, field in self.__dict__.items():
            if not key.startswith('_') and key != '_id':
                if isinstance(field, Field):
                    value = field.value
                else:
                    value = field
                if isinstance(value, str):
                    try:
                        value = value.strip()
                    except:
                        pass
                obj.update({key: value})

        if include_class:
            obj.update({"_cls": "{}.{}".format(self.__class__.__module__, self.__class__.__name__)})
        if include_id:
            obj.update({"_id": self._id})

        return obj


class TextField(Field):
    _type = str
    _api_type = 'text'


class URLField(TextField):
    _api_type = 'url'

    def set(self, value):
        regex = re.compile('^[a-z]+://')
        if regex.search(value) is None:
            value = 'http://' + value
        super(URLField, self).set(value)

    def is_valid(self):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return regex.search(self._value) is not None

    @property
    def value(self):
        if self._value is None:
            return None
        return self._value.rstrip('/')


class PasswordField(TextField):
    _api_type = 'password'


class NumberField(Field):
    _type = int
    _api_type = 'number'


class DateField(Field):
    _type = date
    _api_type = 'date'

    def set(self, value):
        super(DateField, self).set(value)

    def convert_value(self, value):
        try:
            super(DateField, self).convert_value(value)
        except TypeError:
            # we're assuming a date will be parsed by our
            # DSL later in the process...
            return value


class DateTimeField(Field):
    _type = datetime
    _api_type = 'date'

    def set(self, value):
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
        super(DateTimeField, self).set(value)


class MoneyField(Field):
    _type = Decimal
    _api_type = 'number'


class DecimalField(Field):
    _type = Decimal
    _api_type = 'number'


class LinkField(Field):
    _type = str
    _api_type = 'link'

    def set(self, value):
        pass

    def get_api_description(self, **kwargs):
        ret = super(LinkField, self).get_api_description(**kwargs)
        ret.update({"value": self.value})
        return ret


class BooleanField(Field):
    _type = bool
    _api_type = 'bool'


class MultiListField(Field):
    _type = list
    _api_type = 'multilist'

    @property
    def value(self):
        return self._value

    def set(self, value):
        if isinstance(value, str):
            value = value.split(',')
        if isinstance(value, MultiListField):
            value = value.value
        if value is not None and not isinstance(value, list):
            raise ValueError('expecting list, got {}'.format(value.__class__.__name__))
        self._value = value

    def add(self, value):
        if not self._value:
            self._value = []
        self._value.append(value)

    def remove(self, value):
        if not self._value:
            self._value = []
        self._value.remove(value)

    def __len__(self):
        return self._value.__len__()


class DictField(Field):
    _type = dict
    _api_type = 'dict'

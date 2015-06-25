from vizydrop.fields import FieldedObject


class SourceSchema(FieldedObject):
    """
    Base class for a source's schema
    """
    pass


class DataSource(object):
    """
    Base class for a datasource
    """

    class Schema(SourceSchema):
        pass

    class Meta:
        identifier = None
        name = None
        tags = []
        filter = None
        description = None

    @classmethod
    def get_schema(cls):
        """
        Get the schema for this source
        """
        fields = dict()
        for name, field in cls.Schema.get_all_fields():
            # data sources have no internal fields, no need to filter them
            fields[name] = field.get_api_description()

        return {
            "id": cls.Meta.identifier,
            "name": cls.Meta.name,
            "description": cls.Meta.description,
            "tags": cls.Meta.tags,
            "fields": fields,
            "filter": cls.Meta.filter.get_filter_schema()
        }

    @classmethod
    def get_filter(cls):
        """
        Helper function to get this datasource's filter class
        """
        return cls.Meta.filter

    @classmethod
    def get_data(cls, account, source_filter, limit=100, skip=0):
        """
        Main function to grab data for an account
        :param account: account to use
        :param source_filter: filter to use
        :param limit: maximum results to include
        :param skip: number of elements to skip
        :return: dict
        """
        raise NotImplementedError()

    @classmethod
    def format_data_to_schema(cls, data):
        """
        Formats specified data to the source's schema definition
        :param data: data to format
        :return: formatted data
        """
        if type(data) is not list:
            raise ValueError('expecting type \'list\' got \'{}\''.format(type(data)))
        fields = {key: value for key, value in cls.Schema.get_all_fields()}
        ret = []
        for item in data:
            this_item = {}
            for key, field in fields.items():
                if field.response_location is None and key in item:
                    # easy peasy
                    this_item[key] = item[key]
                elif field.response_location is not None:
                    # we need to grab this value from somewhere else in the response
                    this_item[key] = cls._get_value_from_location(item, field.response_location)
                else:
                    # unknown or not found field?
                    continue
            ret.append(this_item)
        return ret

    @classmethod
    def _get_value_from_location(cls, item, location):
        """
        Helper recursive function to get a nested value from a dict object
        :param item: dict to search through
        :param location: location to get the value from, nested dictionaries can be separated by a hyphen (-)
        :return: value
        """
        if location is None or item is None:
            return None
        locations = location.split('-')
        this_loc = locations.pop(0)
        if locations.__len__() == 0:
            return item[this_loc]
        else:
            return cls._get_value_from_location(item[this_loc], '-'.join(locations))


class SourceFilter(FieldedObject):
    """
    Base representation of a datasource filter
    """

    @classmethod
    def get_filter_schema(cls):
        """
        Returns filter's schema for API purposes
        :return: dict
        """
        fields = []
        for name, field in cls.get_all_fields():
            f = {"id": name}
            f.update(field.get_api_description(datalist=True, optional=True, name=True))
            if f.get('description', None) and f.get('name', None):
                fields.append(f)
        return fields

from zope.interface import implements, alsoProvides
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import RequiredMissing
from plone.registry.interfaces import IRecordsProxy
from plone.registry.recordsproxy import RecordsProxy, RecordsProxyCollection
from plone.registry import field
from plone.registry.record import Record
from userlist import ListMixin
from zope import schema
import re

_marker = object()


def facetId(name):
    return "facet_" + re.sub("\W", "", name)


class ComplexRecordsProxy(RecordsProxy):
    """
    A proxy that maps an interface to a number of records,
    including collections of complex records
    """

    implements(IRecordsProxy)

    def __init__(self, registry, schema,
                 omitted=(), prefix=None, key_names={}):
        # override to set key_names which changes how lists are stored
        super(ComplexRecordsProxy, self).__init__(registry, schema,
                                                  omitted, prefix)
        self.__dict__['__key_names__'] = key_names

    def __getattr__(self, name):
        if name not in self.__schema__:
            raise AttributeError(name)

        _field = self.__schema__[name]
        if type(_field) in [schema.List, schema.Tuple]:
            prefix = self.__prefix__ + name
            factory = None
            key_name = self.__key_names__.get(name, None)
            return RecordsProxyList(self.__registry__,
                                    _field.value_type.schema,
                                    False, self.__omitted__, prefix, factory,
                                    key_name=key_name)
        elif type(_field) in [schema.Dict]:
            prefix = self.__prefix__ + name
            factory = None
            return RecordsProxyCollection(self.__registry__,
                                          _field.value_type.schema, False,
                                          self.__omitted__, prefix, factory)
        else:
            value = self.__registry__.get(self.__prefix__ + name, _marker)
            if value is _marker:
                value = self.__schema__[name].missing_value
            return value

    def __setattr__(self, name, value):
        if name in self.__schema__:
            full_name = self.__prefix__ + name
            _field = self.__schema__[name]
            if type(_field) in [schema.List, schema.Tuple]:
                proxy = self.__getattr__(name)
                proxy[:] = value
            elif type(_field) in [schema.Dict]:
                proxy = self.__getattr__(name)
                proxy[:] = value
            else:
                if full_name not in self.__registry__:
                    raise AttributeError(name)
                self.__registry__[full_name] = value
        else:
            self.__dict__[name] = value


class RecordsProxyList(ListMixin):
    """A proxy that represents a List of RecordsProxy objects.
        Two storage schemes are supported. A pure listing
        stored as prefix+"/i0001" where the number is the index.
        If your list has a field which can be used as a primary key
        you can pass they key_name in as an optional paramter. This will change
        the storage format where each entry is prefix+"/"+key_value which looks
        a lot nicer in the registry. Order is still
        kept in a special prefix+'.ordereddict_keys' entry.
    """

    def __init__(self, registry, schema, check=True, omitted=(),
                 prefix=None, factory=None, key_name=None):
        self.map = RecordsProxyCollection(registry, schema, check,
                                          omitted, prefix, factory)
        self.key_name = key_name

        if key_name is not None:
            # will store as ordereddict with items stored using key_name's
            # value and order kept in special keys list
            keys_key = prefix + '.ordereddict_keys'
            if registry.get(keys_key) is None:
                registry.records[keys_key] = Record(
                    field.List(title=u"Keys of prefix"), [])
            self.keys = registry.records[keys_key]

    def _get_element(self, i):
        return self.map[self.genKey(i)]

    def _set_element(self, index, value):
        if self.key_name is not None:
            #First add it to the map to ensure it's a valid key
            try:
                key = getattr(value, self.key_name)
                self.map[key] = value
            except:
                # our key list might be in an inconsistent state
                if self.keys.value[index] is None:
                    del self.keys.value[index]
                raise

            # we have to remove the old value if it's being overwritten
            oldkey = self.keys.value[index]
            if key != oldkey and oldkey is not None:
                del self.map[oldkey]
            self.keys.value[index] = key

        else:
            self.map[self.genKey(index)] = value

    def __len__(self):
        return len(self.map)

    def _resize_region(self, start, end, new_size):
        if self.key_name is None:
            offset = new_size - (end - start)
            #move everything along one
            if offset > 0:
                for i in range(max(len(self.map) - 1, 0), start, -1):
                    self.map[self.genKey(i + offset)] = \
                        self.map[self.genKey(i)]
            else:
                for i in range(end, len(self.map), +1):
                    self.map[self.genKey(i + offset)] = \
                        self.map[self.genKey(i)]
                    # remove any additional at the end
                for i in range(len(self.map) + offset, len(self.map)):
                    del self.map[self.genKey(i)]
        else:
            for i in range(start, end):
                del self.map[self.keys.value[i]]
            self.keys.value = self.keys.value[:start] + \
                [None for _ in range(new_size)] + \
                self.keys.value[end:]

    def genKey(self, index):
        if self.key_name is None:
            index_prefix = "i"
            return "%s%05d" % (index_prefix, index)
        else:
            if index < len(self.keys.value):
                return self.keys.value[index]
                # this could happen during registering menu items, not sure why
            raise StopIteration

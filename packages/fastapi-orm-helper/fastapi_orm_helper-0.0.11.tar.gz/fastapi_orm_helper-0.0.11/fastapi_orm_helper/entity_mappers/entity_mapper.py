import pydash
from pydash import get, set_

from ..helpers.deep_pluck import deep_pluck


class EntityMapperData:
    def __init__(self, data):
        self.data = data
        self.mappers = list()

    def add(self, entity_id_key: str, map_key: str):
        self.mappers.append({'entity_id_key': entity_id_key, 'map_key': map_key, 'is_array': False})

        return self

    def adds(self, entity_id_key: str, map_key: str):
        self.mappers.append({'entity_id_key': entity_id_key, 'map_key': map_key, 'is_array': True})

        return self

    def get_entity_ids(self):
        ids = list()
        for mapper in self.mappers:
            if '*' in mapper['entity_id_key']:
                ids += deep_pluck(self.data, mapper['entity_id_key'])
            else:
                values = list(map(lambda value: get(value, mapper['entity_id_key']), self.data))
                for value in values:
                    if isinstance(value, list):
                        ids += value
                    else:
                        ids.append(value)

        return ids

    def remap(self, entities: list):
        for mapper in self.mappers:
            if '*' in mapper['entity_id_key']:
                for item in self.data:
                    keys = mapper['entity_id_key'].split('.*.')
                    new_data = item
                    for index, key in enumerate(keys):
                        if index == len(keys) - 1:
                            self.set_value_to_objects(entities, new_data, key, mapper['map_key'])
                            break
                        new_data = get(new_data, key)
                        if new_data is None:
                            break
            else:
                self.set_value_to_objects(entities, self.data, mapper['entity_id_key'], mapper['map_key'])

    def set_value_to_objects(self, entities: list, data, entity_id_key: str, map_key: str):
        for item in data:
            entity_id = get(item, entity_id_key)
            if entity_id is not None:
                if isinstance(entity_id, list):
                    set_(item, map_key, pydash.filter_(entities, lambda value: value.id in entity_id))
                else:
                    entity = pydash.find(entities, lambda value: value.id == entity_id)
                    set_(item, map_key, entity)


class EntityMapper:
    def __init__(self):
        self.mappers = list[EntityMapperData]()

    def map(self, data):
        mapper = EntityMapperData(data)
        self.mappers.append(mapper)
        return mapper

    def get_entity_ids(self):
        ids = []
        for mapper in self.mappers:
            ids += mapper.get_entity_ids()
        return pydash.uniq(pydash.without(ids, None))

    def remap(self, entities):
        for mapper in self.mappers:
            mapper.remap(entities)

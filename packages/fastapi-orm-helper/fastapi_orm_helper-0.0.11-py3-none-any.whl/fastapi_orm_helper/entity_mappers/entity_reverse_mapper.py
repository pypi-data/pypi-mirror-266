import pydash
from pydash import get, set_

from ..helpers.deep_pluck import deep_pluck


class EntityReverseMapperData:
    def __init__(self, data):
        self.data = data
        self.mappers = list()

    def add(self, entity_id_key: str, reverse_id: str, map_key: str, is_mapped_data_list: bool | None = False):
        self.mappers.append(
            {
                'entity_id_key': entity_id_key,
                'reverse_id': reverse_id,
                'map_key': map_key,
                'is_mapped_data_list': is_mapped_data_list,
            }
        )

        return self

    def get_entity_conditions(self):
        condition_keys = {}
        for mapper in self.mappers:
            condition_keys[mapper['reverse_id']] = list()

        for mapper in self.mappers:
            if '*' in mapper['entity_id_key']:
                condition_keys[mapper['reverse_id']] += deep_pluck(self.data, mapper['entity_id_key'])
            else:
                values = list(map(lambda value: get(value, mapper['entity_id_key']), self.data))
                for value in values:
                    if isinstance(value, list):
                        condition_keys[mapper['reverse_id']] += value
                    else:
                        condition_keys[mapper['reverse_id']].append(value)
        return condition_keys

    def remap(self, entities: list):
        for mapper in self.mappers:
            if '*' in mapper['entity_id_key']:
                for item in self.data:
                    keys = mapper['entity_id_key'].split('.*.')
                    new_data = item
                    for index, key in enumerate(keys):
                        if index == len(keys) - 1:
                            self.set_value_to_objects(entities, new_data, key, mapper['reverse_id'], mapper['map_key'], mapper['is_mapped_data_list'])
                            break
                        new_data = get(new_data, key)
                        if new_data is None:
                            break
            else:
                self.set_value_to_objects(
                    entities, self.data, mapper['entity_id_key'], mapper['reverse_id'], mapper['map_key'], mapper['is_mapped_data_list']
                )

    def set_value_to_objects(self, entities: list, data, entity_id_key: str, reverse_id: str, map_key: str, is_mapped_data_list: bool):
        for item in data:
            entity_id = get(item, entity_id_key)
            if entity_id is not None:
                if isinstance(entity_id, list):
                    set_(item, map_key, pydash.filter_(entities, lambda value: get(value, reverse_id) in entity_id))
                else:
                    entity = pydash.filter_(entities, lambda value: get(value, reverse_id) == entity_id)
                    if not is_mapped_data_list:
                      set_(item, map_key, entity[0] if entity else None)


class EntityReverseMapper:
    def __init__(self):
        self.mappers = list[EntityReverseMapperData]()

    def map(self, data):
        mapper = EntityReverseMapperData(data)
        self.mappers.append(mapper)
        return mapper

    def get_entity_conditions(self):
        condition = {}
        for mapper in self.mappers:
            mapper_condition = mapper.get_entity_conditions()

            for key in mapper_condition:
                if hasattr(condition, key):
                    condition[key] += mapper_condition[key]
                else:
                    condition[key] = mapper_condition[key]

        for key in condition.keys():
            condition[key] = pydash.uniq(pydash.without(condition[key], None))
            if not condition[key] and hasattr(condition, key):
                delattr(condition, key)

        return condition

    def remap(self, entities):
        for mapper in self.mappers:
            mapper.remap(entities)

from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from fastapi import Depends
from fastapi_exception import EntityNotFoundException
from fastapi_pagination import Params
from fastapi_pagination.ext.async_sqlalchemy import paginate
from pydash import flatten
from sqlalchemy import UnaryExpression, delete, desc, func, literal_column, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, lazyload, load_only, selectinload
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql import Select

from .dependencies.pagination import PaginationParams
from .entity_mappers.entity_mapper import EntityMapper
from .entity_mappers.entity_reverse_mapper import EntityReverseMapper
from .enums.join_type_enum import JoinType
from .helpers.get_db_session import get_db_session
from .helpers.join import inner_join

T = TypeVar("T")


class BaseRepository(Generic[T]):
    _entity: T

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session: AsyncSession = session
        self.lazyload_options: list = []
        self.selectinload_options: list = []
        self.joinedload_options: list = []
        self.load_options: list = []
        self.callback_options: list = []
        self.join_targets: list[tuple] = []
        self.contains_eager_options: list = []
        self.selected_columns: list = []
        self.order_by_columns: list = []
        self.is_transactional = hasattr(session, 'transaction')

    def build_query(self, *columns) -> Select:
        query = self.query(*columns)
        options = self.get_options()
        if options:
            query = query.options(*options)
        if self.selected_columns:
            # TODO: check rewrite
            query = query.options(load_only(*self.selected_columns))

        for target in self.join_targets:
            (table, join_type) = target
            query = query.join(table, isouter=join_type == JoinType.LEFT_JOIN)

        if self.order_by_columns:
            query = query.order_by(*self.order_by_columns)

        return query

    def orders(self, columns: list[UnaryExpression]):
        self.order_by_columns = columns
        return self

    def order(self, column: UnaryExpression):
        if column is not None:
            self.order_by_columns.append(column)
        return self

    def order_desc(self, column):
        self.order(desc(column))
        return self

    def with_entities(self, *columns):
        self.selected_columns += columns
        return self

    async def count_of(self, *criterion, column, alias: Optional[str] = None):
        count_query = func.count(column)

        if alias is not None:
            count_query = count_query.label(alias)

        query = select(count_query, column)

        for target in self.join_targets:
            (table, join_type) = target
            query = query.join(table, isouter=join_type == JoinType.LEFT_JOIN)

        if criterion:
            query = query.filter(*criterion)

        return self.run_and_reset(await self.session.execute(self.apply_callbacks(query)))

    def apply_callbacks(self, query) -> Select:
        callbacks = self.get_callbacks()

        if callbacks:
            for callback in callbacks:
                query = callback(query)
        return query

    def lazyload(self, *relation):
        self.lazyload_options = list(map(lazyload, relation))
        return self

    def select_in_load(self, *relation):
        self.selectinload_options = list(map(lambda r: r if isinstance(r, Load) else selectinload(r), relation))
        return self

    def load(self, *relation):
        self.load_options = list(relation)
        return self

    def map_to_relation_group(self, relation):
        if not isinstance(relation, list):
            return [inner_join(relation)] if not isinstance(relation, tuple) else [relation]

        return list(
            map(
                lambda relation: inner_join(relation) if not isinstance(relation, tuple) else relation,
                relation,
            )
        )

    def group_relations(self, relationships: list[Any | list[Any]]):
        return list(map(self.map_to_relation_group, relationships))

    def map_contains_eager_options(self, relationships: list[list[tuple[Any, int]]]):
        contains_eager_options = []

        for relation_group in relationships:
            (relation, _) = relation_group[0]
            contains_eager_query = contains_eager(relation)
            for index in range(1, len(relation_group)):
                (relation, _) = relation_group[index]
                contains_eager_query = contains_eager_query.contains_eager(relation)
            contains_eager_options.append(contains_eager_query)

        return contains_eager_options

    def map_joinedload_options(self, relationships: list[Any | list[Any]]):
        joinedload_options = []

        for relation_group in relationships:
            if not isinstance(relation_group, list):
                relation_group = [relation_group]

            joinedload_query = joinedload(relation_group[0])
            for index in range(1, len(relation_group)):
                relation = relation_group[index]
                joinedload_query = joinedload_query.joinedload(relation)

            joinedload_options.append(joinedload_query)

        return joinedload_options

    def joins(self, *targets):
        group_relations = self.group_relations(list(targets))
        self.join_targets = flatten(group_relations)
        self.add_select(group_relations)
        return self

    def join_without_load(self, *targets):
        group_relations = self.group_relations(list(targets))
        self.join_targets = flatten(group_relations)
        return self

    def add_select(self, group_relations: list):
        self.contains_eager_options = self.map_contains_eager_options(group_relations)
        return self

    def joinedload(self, *relation):
        self.joinedload_options = self.map_joinedload_options(list(relation))
        return self

    def scope_query(self, callbacks: list[Any]):
        self.callback_options = callbacks
        return self

    def get_options(self):
        return [
            *self.load_options,
            *self.selectinload_options,
            *self.lazyload_options,
            *self.joinedload_options,
            *self.contains_eager_options,
        ]

    def get_callbacks(self):
        return self.callback_options

    def query(self, *columns) -> Select:
        if columns is not None and columns:
            return select(*columns)
        return select(self._entity)

    def reset(self):
        self.lazyload_options = []
        self.join_targets = []
        self.joinedload_options = []
        self.load_options = []
        self.selectinload_options = []
        self.callback_options = []
        self.contains_eager_options = []
        self.order_by_columns = []
        self.selected_columns: list = []

    def run_and_reset(self, result):
        self.reset()
        return result

    async def all(self):
        return self.run_and_reset(await self.apply_callback_and_get_many(self.build_query()))

    async def exec(self, query):
        return await self.session.execute(query)

    async def exec_and_get_first(self, query: Select):
        return await self.session.scalar(query.limit(1))

    async def apply_callback_and_get_first(self, query: Select):
        query = self.apply_callbacks(query)
        return await self.session.scalar(query.limit(1))

    async def apply_callback_and_get_many(self, query: Select):
        query = self.apply_callbacks(query)
        results = await self.session.execute(query)
        return results.scalars().unique().all()

    async def exists(self, *criterion) -> bool:
        result = await self.apply_callback_and_get_first(
            self.build_query().options(load_only(self._entity.id)).filter(*criterion)
        )
        return self.run_and_reset(result is not None)

    async def first(self, *criterion) -> T:
        return self.run_and_reset(await self.apply_callback_and_get_first(self.build_query().filter(*criterion)))

    async def find(self, *criterion) -> list[T]:
        return self.run_and_reset(await self.apply_callback_and_get_many(self.build_query().filter(*criterion)))

    async def count(self, *criterion) -> int:
        query = self.apply_callbacks(self.build_query(func.count(self._entity.id).label('count')).filter(*criterion))
        statement = await self.session.scalar(query)
        return self.run_and_reset(statement)

    async def find_by_ids(self, ids: list[UUID]) -> list[T]:
        return self.run_and_reset(
            await self.apply_callback_and_get_many(self.build_query().filter(self._entity.id.in_(ids)))
        )

    async def first_or_fail(self, *criterion) -> T:
        item = self.run_and_reset(await self.apply_callback_and_get_first(self.build_query().filter(*criterion)))
        if item:
            return item
        self.raise_not_found()

    async def find_by_id(self, id: UUID):
        return await self.first_or_fail(self._entity.id == id)

    async def create(self, data: dict) -> T:
        model = self._entity(**data)
        self.session.add(model)

        if self.is_transactional:
            await self.session.flush()
        else:
            await self.session.commit()

        return model

    async def inserts(self, items: list[dict]):
        models = list(map(lambda item: self._entity(**item), items))
        self.session.add_all(models)

        if self.is_transactional:
            await self.session.flush()
        else:
            await self.session.commit()

        return models

    async def first_or_create(self, data: dict):
        criterion = []
        for key, value in data.items():
            criterion.append(getattr(self._entity, key) == value)
        item = await self.first(*criterion)
        if item:
            return item
        return self.create(data)

    async def delete(self, *criterion):
        self.run_and_reset(await self.exec(self.apply_callbacks(delete(self._entity).filter(*criterion))))

        if self.is_transactional:
            await self.session.flush()
        else:
            await self.session.commit()

    async def update_by_id(self, id, data: dict):
        await self.exec(update(self._entity).filter(self._entity.id == id).values(data))

        if self.is_transactional:
            await self.session.flush()
        else:
            await self.session.commit()

    async def update_not_change_updated_at(self, data: dict, *criterion):
        data['updated_at'] = self._entity.updated_at
        return await self.update(data, *criterion)

    async def update(self, data: dict, *criterion):
        await self.exec(update(self._entity).filter(*criterion).values(data))

        if self.is_transactional:
            await self.session.flush()
        else:
            await self.session.commit()

    async def paginate(self, *criterion, pagination_params: PaginationParams):
        page = pagination_params.page
        per_page = pagination_params.per_page

        return self.run_and_reset(
            await paginate(
                self.session,
                self.apply_callbacks(self.build_query().filter(*criterion)),
                params=Params(page=page, size=per_page),
            )
        )

    async def infinite_paginate(self, *criterion, pagination_params: PaginationParams):
        page = pagination_params.page
        per_page = pagination_params.per_page

        return self.run_and_reset(
            await self.apply_callback_and_get_many(
                self.build_query().limit(per_page).offset((page - 1) * per_page).filter(*criterion)
            )
        )

    async def create_if_not_exist(self, data: dict, *criterion):
        existed_model = await self.first(*criterion)
        if not existed_model:
            model = self._entity(**data)
            self.session.add(model)

            if self.is_transactional:
                await self.session.flush()
            else:
                await self.session.commit()

            return model
        return existed_model

    def raise_not_found(self):
        raise EntityNotFoundException(self._entity)

    def subquery(self, *criterion):
        return self.apply_callbacks(self.build_query().filter(*criterion)).subquery()

    async def upsert(self, data: dict, *criterion):
        existed_model = await self.first(*criterion)
        if not existed_model:
            return await self.create(data)
        await self.update(data, *criterion)
        return await self.first(*criterion)

    async def map_relation_data(self, mapper: EntityMapper):
        ids = mapper.get_entity_ids()
        if not ids:
            return

        entities = await self.find_by_ids(ids)
        mapper.remap(entities)

    async def map_reverse_relation_data(self, mapper: EntityReverseMapper):
        condition = mapper.get_entity_conditions()
        if not condition:
            return

        new_conditions = []
        for key in condition.keys():
            new_conditions.append(literal_column(key).in_(condition[key]))
        entities = await self.find(or_(*new_conditions))
        mapper.remap(entities)

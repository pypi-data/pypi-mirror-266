from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from .entity import Entity
from .session import get_session

T = TypeVar("T", bound=Entity)
K = TypeVar("K")


class SQLAlchemyRepository(Generic[T, K]):
    """
    A generic repository implementation using SQLAlchemy.

    :param T: The type of the entity.
    :param K: The type of the entity's primary key.

    :ivar entity_class: The class representing the entity.
    """

    entity_class: Type[T]

    @property
    def session(self) -> Session:
        """
        Get the SQLAlchemy session.

        :return: The SQLAlchemy session.
        """

        return get_session()

    def find_all(self) -> List[T]:
        """
        Find all entities of the specified type.

        :return: A list of entities.
        """

        stm = select(self.entity_class)
        result = self.session.scalars(stm).all()
        return list(result)

    def find_by_id(self, id: K) -> Optional[T]:
        """
        Find an entity by its identifier.

        :param id: The identifier of the entity.
        :return: The entity if found, None otherwise.
        """

        return self.session.get(self.entity_class, id)

    def save(self, entity: T) -> T:
        """
        Save an entity.

        :param entity: The entity to be saved.
        :return: The saved entity.
        """

        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: T) -> T:
        """
        Delete an entity.

        :param entity: The entity to be deleted.
        :return: The deleted entity.
        """

        self.session.delete(entity)
        self.session.commit()
        return entity

    def delete_by_id(self, id: K) -> None:
        """
        Delete an entity by its identifier.

        :param id: The identifier of the entity.
        """

        entity = self.find_by_id(id)
        if entity:
            self.delete(entity)

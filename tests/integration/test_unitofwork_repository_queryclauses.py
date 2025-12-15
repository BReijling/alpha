import pytest
from sqlalchemy.exc import (
    MultipleResultsFound,
    NoResultFound,
)
from sqlalchemy.orm import Session

from alpha import exceptions
from alpha.adapters.sqla_unit_of_work import SqlAlchemyUnitOfWork
from alpha.infra.database.sql_alchemy_database import SqlAlchemyDatabase
from alpha.interfaces.sql_mapper import SqlMapper
from alpha.interfaces.unit_of_work import UnitOfWork
from alpha.repositories.default_sql_repository import DefaultSqlRepository

from ._classes import (
    Pet,
    PetType,
)


def test_sql_mapper(sqlite_database):
    # Check if the FakeMapper class is a subclass of SqlMapper
    assert isinstance(sqlite_database._mapper, SqlMapper)

    # Check if the FakeMapper class has started the object relational mapping
    assert sqlite_database._mapper.started


# def test_sql_reflect_engine(sqlite_database_owner):
#     # Check if the FakeMapper class is a subclass of SqlMapper
#     assert isinstance(sqlite_database_owner._mapper, SqlMapper)

#     # Check if the FakeMapper class has started the object relational mapping
#     assert sqlite_database_owner._mapper.started


def test_sql_alchemy_unit_of_work(uow: UnitOfWork):
    assert isinstance(uow, SqlAlchemyUnitOfWork)
    # assert isinstance(uow, UnitOfWork)

    assert isinstance(getattr(uow, "_db"), SqlAlchemyDatabase)

    # with pytest.raises(AttributeError):
    #     assert isinstance(uow.session, Session)

    with uow:
        assert isinstance(getattr(uow, "pets"), DefaultSqlRepository)

        assert isinstance(uow.session, Session)

        assert uow.flush() is None
        assert uow.commit() is None


def test_default_sql_repository(uow, pets, pet):
    # To make sure the table is empty
    # When using an used mysql/psql database container
    with uow:
        uow.pets.remove_all()  # type: ignore
        uow.commit()

    # Check 'count', 'add' & 'get_by_id' methods
    with uow:
        # Check if the pets repository contains 0 items
        assert uow.pets.count() == 0

        # Check if the pets repository contains 1 item after adding a single object
        uow.pets.add(pet)
        assert uow.pets.count() == 1

        # Check if the get_by_id method returns a good boy
        obj = uow.pets.get_by_id(999)
        assert obj.good_boy

    # Check 'uow.commit' & 'add_all' methods
    with uow:
        # Check if the pets repository contains 0 items again because a commit was not executed
        assert uow.pets.count() == 0

        # Check if the limit parameter is used correctly
        uow.pets.add_all(pets)
        assert uow.pets.count(limit=2) == 2

        uow.commit()

    # Check 'remove' & 'remove_all' methods
    with uow:
        # Check if the pets repository contains all pets after the have been commited during the previous session
        assert uow.pets.count() == len(pets)

        # Check if an exception will be raised of the raise_if_exists parameter is set to True
        with pytest.raises(exceptions.AlreadyExistsException):
            uow.pets.add_all(pets, raise_if_exists=True)

        # Check if the pets repository contains 4 item after removing a pet
        pet = uow.pets.get_by_id(1)
        uow.pets.remove(pet)
        assert uow.pets.count() == 4

        # Check if the pets repository contains 5 items again after adding the pets
        uow.pets.add_all(pets)
        assert uow.pets.count() == 5

        # Check if an exception will be raised of the raise_if_exists parameter is set to True
        with pytest.raises(exceptions.AlreadyExistsException):
            uow.pets.add(pets[0], raise_if_exists=True)

        uow.pets.remove_all()
        assert uow.pets.count() == 0

    # Check all 'get*' methods
    with uow:
        # Get first object, with and without an InstrumentedAttribute
        assert uow.pets.get("pet_type", "DOG").name == "Max"
        assert uow.pets.get(Pet.pet_type, PetType.CAT).name == "Tom"
        assert uow.pets.get("name", "DOG") is None

        # Check if the item is correct
        assert uow.pets.get_one("name", "Max").name == "Max"
        assert uow.pets.get_one(Pet.pet_type, PetType.CAT).name == "Tom"
        assert uow.pets.get_one_or_none("name", "Max").name == "Max"
        assert (
            uow.pets.get_one_or_none(Pet.pet_type, PetType.CAT).name == "Tom"
        )
        assert uow.pets.get_by_id(1).name == "Max"

        # Check if the first item in the returned list is correct
        assert uow.pets.get_all("name", "Max")[0].name == "Max"
        assert uow.pets.get_all(Pet.pet_type, PetType.CAT)[0].name == "Tom"

        # Check if all get methods pass the cursor_result parameter
        assert isinstance(
            uow.pets.get(attr="pet_type", value="DOG", cursor_result="all"),
            list,
        )
        assert isinstance(
            uow.pets.get_all(
                attr="pet_type", value="DOG", cursor_result="all"
            ),
            list,
        )
        assert isinstance(
            uow.pets.get_one(
                attr="pet_type", value="DOG", cursor_result="all"
            ),
            list,
        )
        assert isinstance(
            uow.pets.get_one_or_none(
                attr="pet_type", value="DOG", cursor_result="all"
            ),
            list,
        )
        assert isinstance(
            uow.pets.get_by_id(
                attr="pet_type", value="DOG", cursor_result="all"
            ),
            list,
        )

        assert isinstance(
            uow.pets.get(attr="pet_type", value="DOG", cursor_result="first"),
            Pet,
        )
        assert isinstance(
            uow.pets.get_all(
                attr="pet_type", value="DOG", cursor_result="first"
            ),
            Pet,
        )
        assert isinstance(
            uow.pets.get_one(
                attr="pet_type", value="DOG", cursor_result="first"
            ),
            Pet,
        )
        assert isinstance(
            uow.pets.get_one_or_none(
                attr="pet_type", value="DOG", cursor_result="first"
            ),
            Pet,
        )
        assert isinstance(
            uow.pets.get_by_id(
                attr="pet_type", value="DOG", cursor_result="first"
            ),
            Pet,
        )

        # Check for the correct raises
        with pytest.raises(MultipleResultsFound):
            uow.pets.get(attr="pet_type", value="DOG", cursor_result="one")
            uow.pets.get_all(attr="pet_type", value="DOG", cursor_result="one")
            uow.pets.get_one(attr="pet_type", value="DOG", cursor_result="one")
            uow.pets.get_one_or_none(
                attr="pet_type", value="DOG", cursor_result="one"
            )
            uow.pets.get_by_id(
                attr="pet_type", value="DOG", cursor_result="one"
            )

        with pytest.raises(MultipleResultsFound):
            uow.pets.get(
                attr="pet_type", value="DOG", cursor_result="one_or_none"
            )
            uow.pets.get_all(
                attr="pet_type", value="DOG", cursor_result="one_or_none"
            )
            uow.pets.get_one(
                attr="pet_type", value="DOG", cursor_result="one_or_none"
            )
            uow.pets.get_one_or_none(
                attr="pet_type", value="DOG", cursor_result="one_or_none"
            )
            uow.pets.get_by_id(
                attr="pet_type", value="DOG", cursor_result="one_or_none"
            )

        with pytest.raises(NoResultFound):
            uow.pets.get(attr="pet_type", value="FOX", cursor_result="one")
            uow.pets.get_all(attr="pet_type", value="FOX", cursor_result="one")
            uow.pets.get_one(attr="pet_type", value="FOX", cursor_result="one")
            uow.pets.get_one_or_none(
                attr="pet_type", value="FOX", cursor_result="one"
            )
            uow.pets.get_by_id(
                attr="pet_type", value="FOX", cursor_result="one"
            )


def test_search_filters(
    uow,
    pets,
    lt_filter,
    lte_filter,
    eq_filter,
    neq_filter,
    gt_filter,
    gte_filter,
    in_filter,
    nin_filter,
    like_filter,
    nlike_filter,
    ilike_filter,
    nilike_filter,
    startswith_filter,
    nstartswith_filter,
    istartswith_filter,
    nistartswith_filter,
    endswith_filter,
    nendswith_filter,
    iendswith_filter,
    niendswith_filter,
    contains_filter,
    ncontains_filter,
    icontains_filter,
    nicontains_filter,
    and_filter,
    or_filter,
):
    with uow:
        uow.pets.add_all(pets)
        uow.commit()

    with uow:
        assert uow.pets.count(filter=lt_filter) == 2

        assert uow.pets.count(filters=[lt_filter]) == 2
        assert uow.pets.count(filters=[lte_filter]) == 3
        assert uow.pets.count(filters=[eq_filter]) == 1
        assert uow.pets.count(filters=[neq_filter]) == 4
        assert uow.pets.count(filters=[gt_filter]) == 2
        assert uow.pets.count(filters=[gte_filter]) == 3
        assert uow.pets.count(filters=[lte_filter, gte_filter]) == 3
        assert uow.pets.count(filters=[eq_filter, neq_filter]) == 0
        assert uow.pets.count(filters=[in_filter]) == 2
        assert uow.pets.count(filters=[nin_filter]) == 3

        assert uow.pets.count(filters=[like_filter]) == 1
        assert uow.pets.count(filters=[nlike_filter]) == 3
        assert uow.pets.count(filters=[ilike_filter]) == 1
        assert uow.pets.count(filters=[nilike_filter]) == 3

        assert uow.pets.count(filters=[startswith_filter]) == 1
        assert uow.pets.count(filters=[nstartswith_filter]) == 3
        assert uow.pets.count(filters=[istartswith_filter]) == 1
        assert uow.pets.count(filters=[nistartswith_filter]) == 3

        assert uow.pets.count(filters=[endswith_filter]) == 1
        assert uow.pets.count(filters=[nendswith_filter]) == 3
        assert uow.pets.count(filters=[iendswith_filter]) == 1
        assert uow.pets.count(filters=[niendswith_filter]) == 3

        assert uow.pets.count(filters=[contains_filter]) == 1
        assert uow.pets.count(filters=[ncontains_filter]) == 3
        assert uow.pets.count(filters=[icontains_filter]) == 1
        assert uow.pets.count(filters=[nicontains_filter]) == 3

        assert uow.pets.count(filters=[and_filter]) == 1
        assert uow.pets.count(filters=[or_filter]) == 3


def test_order_by_filters(
    uow,
    pets,
    name_order_asc,
    name_order_desc,
    weight_order_desc,
    good_boy_order_desc,
    weight_neq_none_filter,
):
    with uow:
        uow.pets.add_all(pets)
        uow.commit()

    with uow:
        assert (
            uow.pets.select(
                order_by=[name_order_asc], cursor_result="first"
            ).name
            == "Bugs"
        )
        assert (
            uow.pets.select(
                order_by=[name_order_desc], cursor_result="first"
            ).name
            == "Tom"
        )
        assert (
            uow.pets.select(
                filter=[weight_neq_none_filter],
                order_by=[weight_order_desc],
                cursor_result="first",
            ).name
            == "Pluto"
        )
        assert (
            uow.pets.select(
                order_by=[good_boy_order_desc, name_order_desc],
                cursor_result="first",
            ).name
            == "Pluto"
        )
        assert (
            uow.pets.select(
                order=good_boy_order_desc,
                order_by=[Pet.name, getattr(Pet.pet_type, "desc")()],
                cursor_result="first",
            ).name
            == "Max"
        )

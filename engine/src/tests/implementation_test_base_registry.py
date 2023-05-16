from sqlmodel import create_engine, Session, select, SQLModel, Field
from sqlalchemy.orm import declarative_base

Base = declarative_base()
SQLModel.metadata = Base.metadata


class Employee(SQLModel, table=True):
    __tablename__ = "employees"
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)


class Engineer(Employee, table=True):
    __tablename__ = "engineers"
    # id: int = Column(Integer, primary_key=True)
    id: int = Field(foreign_key="employees.id", primary_key=True, alias="id")
    engineer_info: str | None = Field(nullable=True, default=None)

    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }


class Manager(Employee, table=True):
    __tablename__ = "managers"
    # id: int = Column(Integer, primary_key=True)
    id: int = Field(foreign_key="employees.id", primary_key=True, alias="id")
    manager_data: str | None = Field(nullable=True, default=None)

    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }


# Base.registry.configure()

engine = create_engine("sqlite:///test.db", echo=True)
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    engineer = Engineer(
        name="engineer",
        engineer_info="info",
    )
    manager = Manager(
        name="manager",
        manager_data="data",
    )

    session.add(engineer)
    session.add(manager)
    session.commit()

    # select all employees
    employees = session.exec(select(Employee)).all()

    for employee in employees:
        print(employee.__class__.__name__)  # noqa T201
        print(employee.id)  # noqa T201
        print(employee.name)  # noqa T201
        print(employee.__dict__)  # noqa T201

    managers = session.exec(select(Manager)).all()
    for manager in managers:
        print(manager.__class__.__name__)  # noqa T201
        print(manager.id)  # noqa T201
        print(manager.name)  # noqa T201
        print(manager.manager_data)  # noqa T201
        print(manager.__dict__)  # noqa T201

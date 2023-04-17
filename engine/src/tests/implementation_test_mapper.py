from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
from sqlalchemy.orm import registry, with_polymorphic

mapper_registry = registry()


class Contract(SQLModel, table=True):
    """A contract defines the business conditions of a project"""

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(description="Short description of the contract.")
    client: "Client" = Relationship(
        back_populates="contracts",
    )
    client_id: Optional[int] = Field(
        default=None,
        foreign_key="client.id",
    )

    currency: str
    term_of_payment: Optional[int] = Field(
        description="How many days after receipt of invoice this invoice is due.",
        default=31,
    )
    contact_type: str

    __mapper_args__ = {
        "polymorphic_identity": "contract",
        "polymorphic_on": "contact_type",
    }


@mapper_registry.mapped
class TimeContract(Contract, table=True):
    """A time-based contract with a rate per time unit"""

    contract_id: Optional[int] = Field(
        default=None, foreign_key="contract.id", primary_key=True
    )

    rate: float = Field(
        description="Rate of remuneration",
    )

    unit: str = Field(
        description="Unit of time tracked. The rate applies to this unit.",
        default="hour",
    )

    __mapper_args__ = {
        "polymorphic_identity": "time",
    }


@mapper_registry.mapped
class WorksContract(Contract, table=True):
    """A contract with a fixed price"""

    contract_id: Optional[int] = Field(
        default=None, foreign_key="contract.id", primary_key=True
    )

    price: float = Field(
        description="Price of the contract",
    )
    deliverable: str = Field(description="Description of the deliverable")

    __mapper_args__ = {
        "polymorphic_identity": "works",
    }


class Client(SQLModel, table=True):
    """A client the freelancer has contracted with."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    contracts: List["Contract"] = Relationship(back_populates="client")


engine = create_engine(
    "sqlite:///test.db",
    echo=True,
)

with Session(engine) as session:
    SQLModel.metadata.create_all(engine)

    c = Client()
    c.name = "client name"
    c.contracts = [
        TimeContract(currency=12.2, title="title1", term_of_payment=1, rate=3.4),
        WorksContract(
            title="title2",
            currency=43.4,
            term_of_payment=6,
            price=344.2,
            deliverable="---",
        ),
        TimeContract(currency=13.2, title="title3", term_of_payment=12, rate=56.4),
    ]
    session.add(c)
    session.commit()
    session.refresh(c)

    contract_manager = with_polymorphic(Contract, [TimeContract, WorksContract])

    query = session.query(contract_manager)
    for i in query.all():
        print(i)  # noqa T201

from peewee import *
from playhouse.postgres_ext import *
import yaml

with open("./info.yaml") as f:
    data = yaml.safe_load(f)

database = PostgresqlDatabase(data["database"]["name"],
                              **data["database"]["info"])


class BaseModel(Model):
    class Meta:
        database = database


class LxsData(BaseModel):
    id = IntegerField(primary_key=True)
    receive_timestamp = DateTimeField(constraints=[SQL("DEFAULT now()")])
    device_id = CharField(index=True)
    topic = CharField(index=True)
    timestamp = DateTimeField(index=True)
    data = JSONField(null=False)


database.create_tables([LxsData])

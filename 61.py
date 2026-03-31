import sqlite3
from typing import Dict, Any, List

class BaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def create_table(cls):
        fields = cls._meta.fields
        field_definitions = ", ".join([f"{name} {data_type}" for name, data_type in fields.items()])
        query = f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} ({field_definitions})"
        cls._execute(query)

    @classmethod
    def _execute(cls, query, params=()):
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    @classmethod
    def save(cls, instance):
        fields = cls._meta.fields
        field_names = ", ".join(fields.keys())
        placeholders = ", ".join(["?" for _ in fields])
        values = [getattr(instance, field) for field in fields]
        query = f"INSERT INTO {cls.__name__.lower()} ({field_names}) VALUES ({placeholders})"
        cls._execute(query, values)

    @classmethod
    def all(cls):
        query = f"SELECT * FROM {cls.__name__.lower()}"
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [cls(**dict(zip([column[0] for column in cursor.description], row))) for row in rows]

class Meta:
    fields: Dict[str, str] = {}

class Model(BaseModel):
    class Meta:
        abstract = True

class User(Model):
    id: int
    name: str
    email: str

    class Meta:
        fields = {
            'id': 'INTEGER PRIMARY KEY',
            'name': 'TEXT',
            'email': 'TEXT'
        }

class Post(Model):
    id: int
    title: str
    content: str
    user_id: int

    class Meta:
        fields = {
            'id': 'INTEGER PRIMARY KEY',
            'title': 'TEXT',
            'content': 'TEXT',
            'user_id': 'INTEGER'
        }

if __name__ == "__main__":
    User.create_table()
    Post.create_table()

    user = User(name="John Doe", email="john@example.com")
    User.save(user)

    post = Post(title="First Post", content="This is the first post", user_id=user.id)
    Post.save(post)

    users = User.all()
    posts = Post.all()

    print("Users:", users)
    print("Posts:", posts)
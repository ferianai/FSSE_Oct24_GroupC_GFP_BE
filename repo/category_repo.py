from instance.database import db
from models.category import Categories


def create_category(data):
    category = Categories(**data)
    db.session.add(category)
    return category


def get_all_categories():
    return Categories.query.all()


def get_category_by_id(category_id):
    return db.session.get(Categories, category_id)


def update_category(category, data):
    for key, value in data.items():
        setattr(category, key, value)
    return category


def delete_category(category):
    db.session.delete(category)
    return category

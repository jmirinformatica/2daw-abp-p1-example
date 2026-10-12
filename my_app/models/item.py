from . import db

# Taula items
class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)
    nom = db.Column(db.String, nullable=False)
    unitats = db.Column(db.Integer, nullable=False)

    # Relationship with back_populates
    store = db.relationship("Store", back_populates="items", lazy="joined")
    # joined means that the store will be loaded in the same query as the item
    # so when you access the store attribute of an item, it won't trigger a new query to the database.
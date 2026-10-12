from . import db

# Taula stores
class Store(db.Model):
    __tablename__ = "stores"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String, nullable=False)

    # Relationship with back_populates
    items = db.relationship("Item", back_populates="store", lazy="select") 
    #select means that the items will be loaded lazily when the items attribute is accessed, not when the store is loaded
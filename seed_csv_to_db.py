import pandas as pd
import os
from app import create_app, db
from app.models import ComplaintType, Area
app = create_app()

CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'complaints.csv')

def seed() -> None:
    if not os.path.exists(CSV_PATH):
        print('CSV not found at', CSV_PATH)
        return
    df = pd.read_csv(CSV_PATH)
    with app.app_context():
        types = df['complaint_type'].dropna().unique()
        for t in types:
            name = str(t).strip()
            if not ComplaintType.query.filter_by(name=name).first():
                db.session.add(ComplaintType(name=name))
        areas = df['area'].dropna().unique()
        for a in areas:
            name = str(a).strip()
            if not Area.query.filter_by(name=name).first():
                db.session.add(Area(name=name))
        db.session.commit()
        print('Seed complete: types and areas added.')

if __name__ == '__main__':
    seed()

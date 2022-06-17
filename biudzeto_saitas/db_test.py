#import sqlalchemy as db
#from slaptazodziai import postgres

from app import Vartotojas

#engine = db.create_engine('postgresql://postgres:'+postgres+'@localhost:5433/kursas')
#conn= engine.connect()
#print(conn)

from app import db, Vartotojas

db.create_all(Vartotojas)





#cur.execute("""Select * from biudzetas""")

import sqlite3
conn = sqlite3.connect('todo.db') # Warning: This file is created in the current directory
conn.execute("CREATE TABLE vrtalka (id INTEGER PRIMARY KEY, name char(100) NOT NULL, qty REAL NOT NULL, dimensions REAL NOT NULL, dodano INTEGER, izbrisano INTEGER, project TEXT, status bool NOT NULL)")
conn.execute("CREATE TABLE profili (id INTEGER PRIMARY KEY, name char(100) NOT NULL)")
conn.execute("INSERT INTO profili (name) VALUES ('profil_20x20'),('profil_30x30')")
conn.execute("CREATE TABLE vars (id INTEGER PRIMARY KEY, name char(100) NOT NULL, value REAL NOT NULL, idProfil INTEGER)")
conn.execute("INSERT INTO vars (name, value, idProfil) VALUES "
             "('pozicijaLNull',10.0,1),"
             "('pozicijaDNull',10.0,1),"
             "('pozicijaL',10.0,1),"
             "('pozicijaD',10.0,1),"
             "('orodjeL',1,1),"
             "('orodjeD',2,1),"
             "('hodL',10.0,1),"
             "('pocasnejePredKoncemHodaL',10.0,1),"
             "('hitrostPredKoncemHodaL',10.0,1),"
             "('hodD',10.0,1),"
             "('pocasnejePredKoncemHodaD',10.0,1),"
             "('hitrostPredKoncemHodaD',10.0,1),"
             "('povratekL',10.0,1),"
             "('povratekD',10.0,1),"
             "('povrtavanjeL',10.0,1),"
             "('povrtavanjeD',10.0,1),"
             "('pozicijaZaga', 167,1),"
             "('pocasnejePredKoncemHodaZaga', 45,1),"
             "('hitrostPredKoncemHodaZaga', 1250,1)")
conn.execute("INSERT INTO vars (name, value, idProfil) VALUES "
             "('pozicijaLNull',10.0,2),"
             "('pozicijaDNull',10.0,2),"
             "('pozicijaL',10.0,2),"
             "('pozicijaD',10.0,2),"
             "('orodjeL',1,2),"
             "('orodjeD',2,2),"
             "('hodL',10.0,2),"
             "('pocasnejePredKoncemHodaL',10.0,2),"
             "('hitrostPredKoncemHodaL',10.0,2),"
             "('hodD',10.0,2),"
             "('pocasnejePredKoncemHodaD',10.0,2),"
             "('hitrostPredKoncemHodaD',10.0,2),"
             "('povratekL',10.0,2),"
             "('povratekD',10.0,2),"
             "('povrtavanjeL',10.0,2),"
             "('povrtavanjeD',10.0,2),"
             "('pozicijaZaga', 167,2),"
             "('pocasnejePredKoncemHodaZaga', 45,2),"
             "('hitrostPredKoncemHodaZaga', 1250,2)")

conn.commit()

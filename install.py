import sqlite3
conn = sqlite3.connect('todo.db') # Warning: This file is created in the current directory
conn.execute("CREATE TABLE zaga (id INTEGER PRIMARY KEY, name char(100) NOT NULL, qty REAL NOT NULL, dimensions REAL NOT NULL, dodano INTEGER, izbrisano INTEGER, project TEXT, status bool NOT NULL)")
conn.execute("CREATE TABLE vrtalka (id INTEGER PRIMARY KEY, name char(100) NOT NULL, qty REAL NOT NULL, dimensions REAL NOT NULL, dodano INTEGER, izbrisano INTEGER, project TEXT, status bool NOT NULL)")
conn.execute("CREATE TABLE profili (id INTEGER PRIMARY KEY, name char(100) NOT NULL)")
conn.execute("INSERT INTO profili (name) VALUES ('profil_20x20'),('profil_30x30')")
conn.execute("CREATE TABLE vars (id INTEGER PRIMARY KEY, name char(100) NOT NULL, value REAL NOT NULL, idProfil INTEGER)")
conn.execute("INSERT INTO vars (name, value, idProfil) VALUES ('pozicijaLNull',10.0,1),('pozicijaDNull',10.0,1),('pozicijaL',10.0,1),('pozicijaD',10.0,1),('orodjeL',10.0,1),('orodjeD',10.0,1),('hodL',10.0,1),('pocasnejePredKoncemHodaL',10.0,1),('hitrostPredKoncemHodaL',10.0,1),('hodD',10.0,1),('pocasnejePredKoncemHodaD',10.0,1),('hitrostPredKoncemHodaD',10.0,1),('povratekL',10.0,1),('povratekD',10.0,1),('povrtavanjeL',10.0,1),('povrtavanjeD',10.0,1)")
conn.commit()

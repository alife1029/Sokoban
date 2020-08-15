import sqlite3

class Database:
  def __init__(self):
    with sqlite3.connect("kayit.db") as baglanti:
      imlec = baglanti.cursor()
      imlec.execute("CREATE TABLE IF NOT EXISTS kayitlar(level INT, maxLevel INT)")
      baglanti.commit()
    
  def kaydet(self, level, maxLevel):
    with sqlite3.connect("kayit.db") as baglanti:
      imlec = baglanti.cursor()

      # Kaç kayıt var?
      imlec.execute("SELECT * from kayitlar")
      kayitSayisi = len(imlec.fetchall())

      if kayitSayisi > 0: imlec.execute("UPDATE kayitlar SET level={}, maxLevel={}".format(level, maxLevel))
      else: imlec.execute("INSERT INTO kayitlar values({},{})".format(level, maxLevel))

      baglanti.commit()

  def oku(self):
    with sqlite3.connect("kayit.db") as baglanti:
      imlec = baglanti.cursor()
      imlec.execute("SELECT * from kayitlar")
      kayit = imlec.fetchall()

      if len(kayit) > 0:
        return (kayit[0][0], kayit [0][1])
      else:
        return (1, 1)
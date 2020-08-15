import os
import json
import threading

from tkinter import *
from lib.database import Database
from lib.pynput.keyboard import Listener, Key

# Bazı oyun sabitleri
PENCERE_GENISLIGI = 576
PENCERE_YUKSEKLIGI = 648
TUVAL_GENISLIGI = 576
TUVAL_YUKSEKLIGI = 576
ADIM_UZUNLUGU = 64

# Bazı oyun değişkenleri
level = 1
maxLevel = 1
katman1 = [] # Zemin
katman2 = [] # Duvarlar
oyuncu = None
kutular = []
kutuYerlestirmeYerleri = []

# Bazı oyun metodları
def oncekiSeviye():
  if level > 1:
    levelYukle(level - 1)

def sonrakiSeviye():
  if level < 6:
    if level + 1 > maxLevel:
      for kutu in kutular:
        if not kutu.yerlestirildi:
          return

    levelYukle(level + 1)

def yenidenBaslat():
  levelYukle(level)

# Bazı çizilmiş nesne değişkenleri
cKatman1 = []
cKatman2 = []
cKutular = []
cOyuncu = None

# Pencere oluşturma
pencere = Tk()
pencere.geometry("{}x{}".format(PENCERE_GENISLIGI, PENCERE_YUKSEKLIGI))
pencere.title("Sokoban")
pencere.resizable(width=False, height=False)
pencere.iconbitmap(os.getcwd() + "\\Assets\\ikon.ico")

tuval = Canvas(pencere, width=TUVAL_GENISLIGI, height=TUVAL_YUKSEKLIGI)
tuval.pack()

# Butonlar
btnOncekiLevel = Button(text="Önceki Seviye", bg="#FF7F59", font=("Segoe UI", 12), width=14, height=2, command=oncekiSeviye)
btnOncekiLevel.place(x=5, y=583)

btnSonrakiLevel = Button(text="Sonraki Seviye", bg="#4DFF3E", font=("Segoe UI", 12), width=14, height=2, command=sonrakiSeviye)
btnSonrakiLevel.place(x=145, y=583)

btnYenidenBaslat = Button(text="Seviyeyi Yeniden Başlat", bg="#F2FF59", font=("Segoe UI", 12), width=18, height=2, command=yenidenBaslat)
btnYenidenBaslat.place(x=397, y=583)

lblLevel = Label(text="Seviye: {}".format(level), font=("Segoe UI", 14), width=9, height=2, borderwidth=2, relief="ridge", justify="center")
lblLevel.place(x=286, y=584)

# Resimleri import etme
zeminResimleri = []
kutuResimleri = []
duvarResmi = PhotoImage(file=os.getcwd() + "\\Assets\\duvar.png")
oyuncuResmi = PhotoImage(file=os.getcwd() + "\\Assets\\oyuncu.png")
for i in range(6):
  zeminResimleri.append(PhotoImage(file=os.getcwd()+"\\Assets\\Ground\\{}.png".format(i)))
for i in range(2):
  kutuResimleri.append(PhotoImage(file=os.getcwd() + "\\Assets\\Crates\\kutu_{}.png".format(i)))

def kayitlariYukle():
  global level, maxLevel

  # Veritabanından kayıtları okur
  veritabani = Database()
  kayitlar = veritabani.oku()

  level = kayitlar[0]
  maxLevel = kayitlar[1]

def levelYukle(index):
  global level, maxLevel, katman1, katman2, oyuncu, kutular, kutuYerlestirmeYerleri, lblLevel
  
  katman1 = [] # Zemin
  katman2 = [] # Duvarlar
  oyuncu = None
  kutular = []
  kutuYerlestirmeYerleri = []
  
  with open(os.getcwd() + "\\levels.json", "r") as okunanDosya:
    dosyaVerisi = json.loads(okunanDosya.read())["level{}".format(index)]
    katman1 = dosyaVerisi["layer1"]
    katman2 = dosyaVerisi["layer2"]

    level = index
    if level > maxLevel:
      maxLevel = level

    # Dosyadaki verileri kullanarak oyun nesneleri oluşturur
    oyuncu = Oyuncu(dosyaVerisi["playerPos"]["x"], dosyaVerisi["playerPos"]["y"])
    for element in dosyaVerisi["crateAreas"]:
      kutuYerlestirmeYerleri.append(
        KutuYerlestirmeYeri(element["x"], element["y"], element["sprite"])
      )
    for element in dosyaVerisi["crates"]:
      kutular.append(Kutu(element["x"], element["y"]))

  lblLevel['text'] = "Seviye: {}".format(level)    

  veritabani = Database()
  veritabani.kaydet(level, maxLevel)

  render()

class Oyuncu:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.resim = tuval.create_image(self.x * ADIM_UZUNLUGU + 32,
                                    self.y * ADIM_UZUNLUGU + 32,
                                    image=oyuncuResmi)

  def render(self):
    tuval.delete(self.resim) # Ekrandaki oyuncu çizimini siler
    # Ekrana oyuncuyu tekrar çizer
    self.resim = tuval.create_image(self.x * ADIM_UZUNLUGU + 32,
                                    self.y * ADIM_UZUNLUGU + 32,
                                    image=oyuncuResmi)

  def hareketEt(self, yonX, yonY):
    hareketMumkunMu = True

    self.x += yonX
    self.y += yonY

    # Duvar çarpışma kontrolü
    if katman2[self.y][self.x] != 0:
      hareketMumkunMu = False

    # Kutuya çarpıyor mu?
    for kutu in kutular:
      if kutu.x == self.x and kutu.y == self.y:
        hareketMumkunMu = kutu.hareketEt(yonX, yonY)

    if not hareketMumkunMu:
      self.x -= yonX
      self.y -= yonY

class Kutu:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.resim = None

    self.yerlestirildi = False
    for yer in kutuYerlestirmeYerleri:
      if yer.x == self.x and yer.y == self.y:
        self.yerlestirildi = True
        break
    self.render()
  
  def render(self):
    tuval.delete(self.resim)

    if not self.yerlestirildi:
      self.resim = tuval.create_image(self.x * ADIM_UZUNLUGU + 32,
                                      self.y * ADIM_UZUNLUGU + 32,
                                      image=kutuResimleri[0])
    else:
      self.resim = tuval.create_image(self.x * ADIM_UZUNLUGU + 32,
                                      self.y * ADIM_UZUNLUGU + 32,
                                      image=kutuResimleri[1])                                

  def hareketEt(self, yonX, yonY):
    hareketMumkunMu = True

    self.x += yonX
    self.y += yonY

    # Duvar
    if katman2[self.y][self.x] != 0:                                
      hareketMumkunMu = False

    for kutu in kutular:
      if kutu != self:
        if kutu.x == self.x and kutu.y == self.y:
          hareketMumkunMu = False

    if hareketMumkunMu:
      oyunBittiMi = True
      self.yerlestirildi = False
      for yer in kutuYerlestirmeYerleri:
        if yer.x == self.x and yer.y == self.y:
          self.yerlestirildi = True
          break
      self.render()

    if not hareketMumkunMu:
      self.x -= yonX
      self.y -= yonY
    else:
      self.render()

    return hareketMumkunMu

class KutuYerlestirmeYeri:
  def __init__(self, x, y, sprite):
    self.x = x
    self.y = y
    self.sprite = sprite
    self.resim = tuval.create_image(self.x * ADIM_UZUNLUGU + 32,
                                    self.y * ADIM_UZUNLUGU + 32,
                                    image=zeminResimleri[self.sprite])

  def render(self):
    tuval.delete(self.resim)
    self.resim = tuval.create_image(self.x * ADIM_UZUNLUGU + 32,
                                    self.y * ADIM_UZUNLUGU + 32,
                                    image=zeminResimleri[self.sprite])

# Çizim fonksiyonu
def render():
  global cKatman1, cKatman2, cKutular, cOyuncu

  # Katman 1 (Zemin) temizleme
  for cizim in cKatman1:
    tuval.delete(cizim)
  cKatman1 = []

  # Katman 2 (Duvar) temizleme
  for cizim in cKatman2:
    tuval.delete(cizim)
  cKatman2 = []

  # Kutu çizimlerini temizle
  for cizim in cKutular:
    tuval.delete(cizim)
  cKutular = []

  # Oyuncu çizimini temizle
  tuval.delete(cOyuncu)
  cOyuncu = None

  # Katman 1 (Zemin) çizimi
  for i in range(len(katman1)):
    for j in range(len(katman1[i])):
      cKatman1.append(
        tuval.create_image(j * ADIM_UZUNLUGU + 32,
                           i * ADIM_UZUNLUGU + 32,
                           image=zeminResimleri[katman1[i][j]])
      )
  
  # Katman 2 (Duvar) çizimi
  for i in range(len(katman2)):
    for j in range(len(katman2[i])):
      if katman2[i][j] != 0:
        cKatman2.append(
          tuval.create_image(j * ADIM_UZUNLUGU + 32,
                            i * ADIM_UZUNLUGU + 32,
                            image=duvarResmi)
        )

  for yerlestirmeYeri in kutuYerlestirmeYerleri:
    yerlestirmeYeri.render()
  for kutu in kutular:
    kutu.render()
  oyuncu.render()

class Klavye(threading.Thread):
  def run(self):
    with Listener(on_press=self.on_press) as listener:
      listener.join()

  def on_press(self, key):
    if key == Key.left: oyuncu.hareketEt(-1, 0)
    elif key == Key.right: oyuncu.hareketEt(1, 0)
    elif key == Key.up: oyuncu.hareketEt(0, -1)
    elif key == Key.down: oyuncu.hareketEt(0, 1)

    oyuncu.render()

klavye = Klavye()
klavye.start()

kayitlariYukle()
levelYukle(level)

pencere.mainloop()

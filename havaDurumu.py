from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import requests #OpenWeatherMap veri almak icin http istekleri
import sqlite3
from datetime import datetime


# api
url = "https://api.openweathermap.org/data/2.5/weather"
appKey = "41d1640645e5172b5901ad5a200c1d1f"

def veritabani_olustur(): 
    conn = sqlite3.connect("sehirler.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sehirler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT UNIQUE,
            plaka TEXT
        )
    ''')
    
    sehirlerPlakalar = {
     "Adana": "01", "Adıyaman": "02", "Afyonkarahisar": "03", "Ağrı": "04", "Amasya": "05",
    "Ankara": "06", "Antalya": "07", "Artvin": "08", "Aydın": "09", "Balıkesir": "10",
    "Bilecik": "11", "Bingöl": "12", "Bitlis": "13", "Bolu": "14", "Burdur": "15",
    "Bursa": "16", "Çanakkale": "17", "Çankırı": "18", "Çorum": "19", "Denizli": "20",
    "Diyarbakır": "21", "Edirne": "22", "Elazığ": "23", "Erzincan": "24", "Erzurum": "25",
    "Eskişehir": "26", "Gaziantep": "27", "Giresun": "28", "Gümüşhane": "29", "Hakkari": "30",
    "Hatay": "31", "Isparta": "32", "Mersin": "33", "İstanbul": "34", "İzmir": "35",
    "Kars": "36", "Kastamonu": "37", "Kayseri": "38", "Kırklareli": "39", "Kırşehir": "40",
    "Kocaeli": "41", "Konya": "42", "Kütahya": "43", "Malatya": "44", "Manisa": "45",
    "Kahramanmaraş": "46", "Mardin": "47", "Muğla": "48", "Muş": "49", "Nevşehir": "50",
    "Niğde": "51", "Ordu": "52", "Rize": "53", "Sakarya": "54", "Samsun": "55",
    "Siirt": "56", "Sinop": "57", "Sivas": "58", "Tekirdağ": "59", "Tokat": "60",
    "Trabzon": "61", "Tunceli": "62", "Şanlıurfa": "63", "Uşak": "64", "Van": "65",
    "Yozgat": "66", "Zonguldak": "67", "Aksaray": "68", "Bayburt": "69", "Karaman": "70",
    "Kırıkkale": "71", "Batman": "72", "Şırnak": "73", "Bartın": "74", "Ardahan": "75",
    "Iğdır": "76", "Yalova": "77", "Karabük": "78", "Kilis": "79", "Osmaniye": "80",
    "Düzce": "81"    }
    for sehir, plaka in sehirlerPlakalar.items():
        try:
            cursor.execute("INSERT OR IGNORE INTO sehirler (isim, plaka) VALUES (?, ?)", (sehir, plaka))
        except:
            pass #ignore-> hatayı gormezden gel / unique
    conn.commit()
    conn.close()

def sehirleri_getir():
    conn = sqlite3.connect("sehirler.db")
    cursor = conn.cursor()
    cursor.execute("SELECT isim FROM sehirler ORDER BY isim ASC")
    sehirler = []
    sonuclar = cursor.fetchall() #fetchall ile sorgudan dönenleri tutariz. demet olarak döndüğü icin 0. index yani sehrin ismini aliriz
    for satir in sonuclar:
        sehirler.append(satir[0]) #tuple icinden eleman aldik ekledik
    conn.close()
    return sehirler

def plaka_getir(sehir_adi):
    conn = sqlite3.connect("sehirler.db")
    cursor = conn.cursor()
    cursor.execute("SELECT plaka FROM sehirler WHERE isim=?", (sehir_adi,))
    sonuc = cursor.fetchone() #ilk satiri getirir tek plaka alacağımız icin mantıklı
    conn.close() #fetchall kullansaydık toplu doneceği için gereksiz liste olurdu ve listei icinden demete erismek icin iki kere index girmemiz gerekirdi
    if sonuc:
        return sonuc[0] #tuple dondugu icin index erişim
    else:
        return "?"

# Hava durumu bilgilerini alma
def hava_istek(sehir):
    params = {'q': sehir, 'appid': appKey, 'lang': 'tr'}
    data = requests.get(url, params=params).json()
    if data:
        sehirBilgi = data.get('name')
        icon = data.get('weather')[0].get('icon')
        aciklama = data.get('weather')[0].get('description')
        ulke = data.get('sys').get('country')
        sicaklik = round(data.get('main').get('temp') - 273.15)
        return (sehirBilgi, icon, aciklama, ulke, sicaklik)
    else:
        print("Aranan Şehir Bilgisi Bulunamadi")

def dosyaya_yaz(sehir, sicaklik, aciklama, tarih):
    file = open("hava_durumu_bilgileri.txt", "a")
    print(tarih, "-", sehir, ":", sicaklik, "°C,", aciklama, file=file)

    file.close()

def havaDurumu(il):
    sonuc = hava_istek(il)
    if sonuc:
        icon_url = f"https://openweathermap.org/img/wn/{sonuc[1]}@2x.png"
        icon = ImageTk.PhotoImage(Image.open(requests.get(icon_url, stream=True).raw))
        labelIcon.config(image=icon)
        labelIcon.image = icon
        labelSehir.config(text=sonuc[0] + ", " + plaka_getir(il) + " " + sonuc[3])
        labelSicaklik.config(text=str(sonuc[4]) + " °C, " + sonuc[2])
        simdi = datetime.now().strftime("%d.%m.%Y %H:%M")
        labelTarih.config(text="Tarih ve Saat: " + simdi)
        dosyaya_yaz(sonuc[0], sonuc[4], sonuc[2], simdi)

# Arayüz tasarımı
pencere = Tk()
pencere.geometry("900x900")  
pencere.config(bg="#C8A2D4")  
pencere.title("Hava Durumu Uygulaması")

veritabani_olustur()
sehirListesi = sehirleri_getir()



# Başlık ve açıklama
labelBaslik =Label(pencere, text="Hava Durumu Uygulaması", font=('Arial', 30, 'bold'), foreground='#5A2E8C', background="#C8A2D4")  # Mor renk
labelBaslik.pack(pady=10)

labelAciklama = Label(pencere, text="Şehir seçin ve hava durumu bilgilerini alın", font=('Arial', 18, 'italic'), foreground='#5A2E8C', background="#C8A2D4")  # Mor renk
labelAciklama.pack(pady=5)

combo_sec= StringVar(value="Şehir seçiniz....")
combo_sehir = ttk.Combobox(pencere, values=sehirListesi, textvariable=combo_sec,
                           font=('Arial', '20', 'bold',), justify=CENTER)
combo_sehir.bind("<<ComboboxSelected>>", lambda event: havaDurumu(combo_sec.get()))
combo_sehir.pack(pady=20)

# Hava durumu görselleri
labelIcon = Label(pencere, background="#da70d6")  
labelIcon.pack()

# Hava durumu bilgileri
labelSehir = Label(pencere, foreground='#5A2E8C', background="#C8A2D4", 
                       font=('Arial', '30', 'italic'), justify=CENTER)
labelSehir.pack()

labelSicaklik = Label(pencere, foreground='#9B3D8B', background="#C8A2D4",  
                          font=('Arial', '34', 'bold'), justify=CENTER)
labelSicaklik.pack()

labelTarih = Label(pencere, foreground='#5A2E8C', background="#C8A2D4",  
                       font=('Arial', '24', 'italic'), justify=CENTER)
labelTarih.pack()

labelOneri = Label(pencere, foreground='#FF5733', background="#C8A2D4",  
                       font=('Arial', '30', 'italic'), justify=CENTER)
labelOneri.pack()

#LabelSec = Label(pencere,command=plaka_getir)
#LabelSec.pack()


def yenile():
    havaDurumu(combo_sec.get())

buttonYenile = Button(pencere, text="Yenile", font=('Arial', 16, 'bold'), command=yenile,
                      fg="#5A2E8C")  
buttonYenile.pack(pady=20)


pencere.mainloop()

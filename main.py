from fastapi import FastAPI, HTTPException
import sqlite3
from datetime import datetime, timedelta
app = FastAPI()

def musteri_database():
    conn = sqlite3.connect("rezervasyon.db")
    curr = conn.cursor()
    curr.execute("""

        CREATE TABLE IF NOT EXISTS musteri_koltuklari(
                id INTEGER PRIMARY KEY,
                durum TEXT,
                gecerlilik TEXT
                )
    """
    )
    curr.execute("SELECT COUNT(*) FROM musteri_koltuklari")
    if curr.fetchone()[0] == 0:
        for j in range(1,6):
            curr.execute("INSERT INTO musteri_koltuklari (id, durum, gecerlilik) VALUES (?,?,?)",(j,'Boş',None))
        conn.commit()
    conn.close()

musteri_database()

@app.get("/kontrol/{koltuk_no}")

def durum_sorgula(koltuk_no:int):
    conn=sqlite3.connect("rezervasyon.db")
    curr = conn.cursor()
    curr.execute("SELECT durum,gecerlilik FROM musteri_koltuklari WHERE id = ? ",(koltuk_no,))
    sonuc = curr.fetchone()

    if sonuc is None:
        conn.close()
        raise HTTPException(status_code=404,detail="Bu numaraya sahip bir koltuk yok!")
        
    durum = sonuc[0]
    sure_str = sonuc[1]
    if durum == "Askıda" and sure_str is not None:
        sure = datetime.strptime(sure_str,"%Y-%m-%d %H:%M:%S")
        guncel_zaman = datetime.now()
        if guncel_zaman > sure:
            #suresi gecen durum.
            curr.execute("UPDATE musteri_koltuklari SET durum = 'Boş', gecerlilik = NULL WHERE id = ?",(koltuk_no,))
            durum = "Boş"
            conn.commit()
    conn.close()
    return {"Koltuk Durumu:":f"{koltuk_no} numaralı koltuk {durum}"}
    

@app.post("/rezerve_et/{koltuk_no}")

def rezerve_et(koltuk_no:int):
    conn = sqlite3.connect("rezervasyon.db")
    curr = conn.cursor()
    curr.execute("SELECT durum,gecerlilik FROM musteri_koltuklari WHERE id = ?",(koltuk_no,))
    sonuc = curr.fetchone()


    if sonuc is None:
        conn.close()
        raise HTTPException(status_code=404,detail="Bu numaraya sahip bir koltuk yok!")
        
    
    durum = sonuc[0]
    sure_str = sonuc[1]
    
    if durum == "Dolu":
        conn.close()
        raise HTTPException(status_code=400,detail="Bu koltuk zaten satın alınmış!")
    
    if durum == "Askıda" and sure_str is not None:
        sure = datetime.strptime(sure_str,"%Y-%m-%d %H:%M:%S")
        guncel_zaman = datetime.now()
        if guncel_zaman > sure:
            curr.execute("UPDATE musteri_koltuklari SET durum ='Boş', gecerlilik = NULL WHERE id = ?",(koltuk_no,))
            conn.commit()
        else:
            conn.close()
            raise HTTPException(status_code=400,detail="Bu koltuk satın alınmak üzere askıda bekletiliyor!")
    guncel_zaman = datetime.now()
    limit_zaman = guncel_zaman + timedelta(minutes=1)
    limit_zaman_str = limit_zaman.strftime("%Y-%m-%d %H:%M:%S")

    curr.execute("UPDATE musteri_koltuklari SET durum ='Askıda', gecerlilik = ? WHERE id = ?",(limit_zaman_str,koltuk_no))
    conn.commit()
    conn.close()
    return{"Mesaj:":f"{koltuk_no} numaralı koltuk için ödeme bekleniyor.","Kalan Sure:":"1 dakika","Son Ödeme Saati:":f"{limit_zaman_str}"}    

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import aiosqlite
import asyncio
from contextlib import asynccontextmanager

async def init_db():
    async with aiosqlite.connect("rezervasyon.db") as db:
        await db.execute(
            ("""

        CREATE TABLE IF NOT EXISTS musteri_koltuklari(
                id INTEGER PRIMARY KEY,
                durum TEXT,
                gecerlilik TEXT,
                isim TEXT,
                telefon TEXT,
                satis_zamani TEXT
                )
    """
    )
        )
        async with db.execute("SELECT COUNT(*) FROM musteri_koltuklari") as cursor:
            sonuc = await cursor.fetchone()
        
        if sonuc[0] == 0 :
            for j in range(1,6):
                await db.execute("INSERT INTO musteri_koltuklari (id,durum,gecerlilik) VALUES (?,?,?)", (j,"Boş",None))
            await db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    asyncio.create_task(db_kontrol())
    yield

app = FastAPI(lifespan=lifespan)

class OdemeBilgisi(BaseModel):
    isim : str 
    telefon: str 



@app.get("/kontrol/{koltuk_no}")

async def durum_sorgula(koltuk_no:int):
    async with aiosqlite.connect("rezervasyon.db") as db :
        async with db.execute("SELECT durum,gecerlilik FROM musteri_koltuklari WHERE id = ? ",(koltuk_no,)) as cursor:
            sonuc = await cursor.fetchone()

        if sonuc is None:
            raise HTTPException(status_code=404,detail="Bu numaraya sahip bir koltuk yok!")
            
        durum = sonuc[0]
        sure_str = sonuc[1]

        if durum == "Askıda" and sure_str is not None:
            sure = datetime.strptime(sure_str,"%Y-%m-%d %H:%M:%S")
            guncel_zaman = datetime.now()
            
            if guncel_zaman > sure:
                #suresi gecen durum.
                await db.execute("UPDATE musteri_koltuklari SET durum = 'Boş', gecerlilik = NULL WHERE id = ?",(koltuk_no,))
                durum = "Boş"
                await db.commit()
        return {"Koltuk Durumu:":f"{koltuk_no} numaralı koltuk {durum}"}
        

@app.post("/rezerve_et/{koltuk_no}")

async def rezerve_et(koltuk_no:int):
    async with aiosqlite.connect("rezervasyon.db") as db:
        async with db.execute("SELECT durum,gecerlilik FROM musteri_koltuklari WHERE id = ?",(koltuk_no,)) as cursor:
            sonuc = await cursor.fetchone()

        if sonuc is None:
            raise HTTPException(status_code=404,detail="Bu numaraya sahip bir koltuk yok!")
                
        durum = sonuc[0]
        sure_str = sonuc[1]
        
        if durum == "Dolu":
            raise HTTPException(status_code=400,detail="Bu koltuk zaten satın alınmış!")
        
        if durum == "Askıda" and sure_str is not None:
            sure = datetime.strptime(sure_str,"%Y-%m-%d %H:%M:%S")
            guncel_zaman = datetime.now()
            if guncel_zaman > sure:
                await db.execute("UPDATE musteri_koltuklari SET durum ='Boş', gecerlilik = NULL WHERE id = ?",(koltuk_no,))
                await db.commit()
            else:
                raise HTTPException(status_code=400,detail="Bu koltuk satın alınmak üzere askıda bekletiliyor!")
        guncel_zaman = datetime.now()
        limit_zaman = guncel_zaman + timedelta(minutes=1)
        limit_zaman_str = limit_zaman.strftime("%Y-%m-%d %H:%M:%S")
        await db.execute("UPDATE musteri_koltuklari SET durum ='Askıda', gecerlilik = ? WHERE id = ?",(limit_zaman_str,koltuk_no))
        await db.commit()
        return{"Mesaj:":f"{koltuk_no} numaralı koltuk için ödeme bekleniyor.","Kalan Sure:":"1 dakika","Son Ödeme Saati:":f"{limit_zaman_str}"}    




@app.post("/odeme/{koltuk_no}")
async def odeme(koltuk_no:int, bilgi:OdemeBilgisi):
    async with aiosqlite.connect("rezervasyon.db") as db:
        async with db.execute("SELECT durum, gecerlilik FROM musteri_koltuklari WHERE id = ?",(koltuk_no,)) as cursor:
            sonuc = await cursor.fetchone()

        if sonuc is None:
            raise HTTPException(status_code=404,detail="Bu numaraya sahip bir koltuk yok!")
        durum = sonuc[0]
        sure_str = sonuc[1]

        if durum == "Boş":
            raise HTTPException(status_code=400,detail="Bu koltuk henüz rezerve edilmemiş ödeme yapılamaz!")
        
        if durum == "Dolu":
            raise HTTPException(status_code=400,detail="Bu koltuk Dolu. Bu koltuk satın alınamaz!")

        if durum == "Askıda" and sure_str is not None:
            sure = datetime.strptime(sure_str,"%Y-%m-%d %H:%M:%S")
            guncel_zaman = datetime.now()
            if guncel_zaman > sure:
                await db.execute("UPDATE musteri_koltuklari SET durum ='Boş', gecerlilik = NULL WHERE id = ?",(koltuk_no,))
                await db.commit()
                raise HTTPException(status_code=400,detail="Odeme yapılamıyor. Verilen süre aşıldı.")
            else:
                guncel_zaman_str = guncel_zaman.strftime("%Y-%m-%d %H:%M:%S")
                await db.execute("UPDATE musteri_koltuklari SET durum ='Dolu', gecerlilik = NULL, isim= ?, telefon =?,satis_zamani = ? WHERE id =?",(bilgi.isim,bilgi.telefon,guncel_zaman_str,koltuk_no))
                await db.commit()
                return{"Başarılı:":f"{koltuk_no} numaralı koltuk {bilgi.isim} adına başarıyla satın alındı."}
            
@app.post("/iade/{koltuk_no}")
async def iade(koltuk_no:int, bilgi:OdemeBilgisi):
    async with aiosqlite.connect("rezervasyon.db") as db:
        async with db.execute("SELECT durum, isim, telefon FROM musteri_koltuklari WHERE id = ? ", (koltuk_no,)) as cursor:
            sonuc = await cursor.fetchone()
    
        if sonuc == None:
            raise HTTPException(status_code=404, detail="Böyle bir koltuk numarası yok!")
        
        durum, isim, telefon = sonuc 

        if durum == "Boş":
            raise HTTPException(status_code=400, detail="Boş koltuk iade edilemez")
        
        if durum == "Askıda":
            raise HTTPException(status_code=400, detail="Bu koltuk askıda ödemesi bekleniyor.")

        if durum == "Dolu" and isim == bilgi.isim and telefon == bilgi.telefon:
            await db.execute("UPDATE musteri_koltuklari SET durum = 'Boş' , isim=NULL , telefon= NULL, satis_zamani = NULL WHERE id = ?", (koltuk_no,))
            await db.commit()
            return {"mesaj:":f"{bilgi.isim} adına alınan {koltuk_no} numaralı koltuk başarıyla iade edildi."}
        else:
            raise HTTPException(status_code=403,detail="İade işlemi gerçekleştirilemiyor. İsim veya telefon numarası yanlış.")
        


@app.post("/admin/admin_reset")
async def sistem_reset():
    async with aiosqlite.connect("rezervasyon.db") as db:
        await db.execute("DROP TABLE IF EXISTS musteri_koltuklari")
        await db.commit()
    await init_db()
    return {"Uyarı":"Sistem sıfırlandı ve yeniden oluşturuldu."}


async def db_kontrol ():
    while True:
        try:
            async with aiosqlite.connect("rezervasyon.db") as db:
                yolculuk_suresi = datetime.now()-timedelta(minutes=5)
                yolculuk_suresi_str = yolculuk_suresi.strftime("%Y-%m-%d %H:%M:%S")
                await db.execute("UPDATE musteri_koltuklari SET durum = 'Boş', gecerlilik = NULL, isim = NULL, telefon = NULL, satis_zamani = NULL WHERE durum = 'Dolu' and satis_zamani < ?",(yolculuk_suresi_str,))
                await db.commit()

            await asyncio.sleep(10)
        except Exception as e:
            print(f"Db kontrolünde hata: {e}")
            await asyncio.sleep(10)





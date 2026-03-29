import asyncio
import time
import aiohttp



url = "http://127.0.0.1:8000/odeme/4"
toplam_istek = 10000

async def tek_musteri_yolla(session,musteri_no):
    try:
        async with session.post(url) as cevap:
            durum_kodu = cevap.status
            return durum_kodu
    except Exception as e:
        return f"hata oluştu"

async def saldiriyi_baslat():

    baslangic_zamani = time.time()

    async with aiohttp.ClientSession() as session:
        gorevler = []
        for i in range(toplam_istek):
            gorevler.append(tek_musteri_yolla(session,i))
        sonuclar = await asyncio.gather(*gorevler)
    bitis_zamani = time.time()
    basarili = sonuclar.count(200) 
    basarisiz_409 = sonuclar.count(409)
    basarisiz_400 = sonuclar.count(400)
    basarisiz_404 = sonuclar.count(404)
    hatali = len(sonuclar) - basarili
    

    print(f"Hedef URL: {url}")
    print(f"Toplam İstek: {toplam_istek}")
    print(f"Geçen Süre: {bitis_zamani - baslangic_zamani:.2f} saniye")
    print(f"Başarılı (200): {basarili}")
    print(f"Başarısız (409): {basarisiz_409}")
    print(f"Başarısız (400): {basarisiz_400}")
    print(f"Başarısız (404): {basarisiz_404}")
    print(f"Başarısız/Hata: {hatali}")



if __name__ == "__main__":
    asyncio.run(saldiriyi_baslat())
pip install fastapi uvicorn

1-main.py çalıştırmadan cmd'den klasöre gelip uvicorn main:app --reload çalıştır

2-tarayıcıdan 127.0.0.1:8000/docs adresini aç. Oradan tekil kullanıcı ile denenebilir.

3-bot.py ile asyncio.gather sayesinde saniyeler içinde binlerce istek atıp db'nin çökmesine sebep olabilir(diniz). En azından rezerve api'si için artık
çökmüyor. Sadece rezerveye yaptım diğerleri de aynı mantık.

aynı anda 10.000 kişi tek bir koltuğu rezerve etmeye çalışırsa versiyon sütunu ile bunu engelleyebiliriz. 

örnek:

Hedef URL       : http://127.0.0.1:8000/rezerve_et/4

Toplam İstek    : 10000

Geçen Süre      : 22.67 saniye

Başarılı (200)  : 1

Başarısız (409)  : 81

Başarısız (400)  : 9918

Başarısız (404)  : 0

Başarısız/Hata  : 9999





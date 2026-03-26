pip install fastapi uvicorn

1-main.py çalıştırmadan cmd'den klasöre gelip uvicorn main:app --reload çalıştır

2-tarayıcıdan 127.0.0.1:8000/docs adresini aç

Devam ediyorum hala

26.3
yapılanlar:
senkron yapıdan asenkron yapıya geçiş.
koltuk kontrol, koltuk rezerve etme (sepete ekleme, askıda bekletme), ödeme yapma(belirli zaman içinde), iade yapma(isim ve telefon eşleşirse), url ile direkt db'yi sıfırlayıp tekrar başlatma, 'Dolu' koltukların 5 dakika içinde 'Boş'a dönmesi (seferin bitmesi gibi düşünülebilir)

Bundan sonra sistemi tekrar test edip bot kurup sürekli sisteme istek atıcam. Bir yerden sonra çökecektir. Sonrasında postgreSQL'e geçirmeye çalışıcam sistemi.

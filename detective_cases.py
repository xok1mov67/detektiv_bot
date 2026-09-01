# -*- coding: utf-8 -*-
"""
DETEKTIV ISHLAR TO'PLAMI (Yangi horror va jiddiy ishlar bilan)
"""

CASES = [
    # 1-14 Bepul va yengil/o'rta ishlar
    {
        "id": 1,
        "title": "Kutubxonadagi jimlik",
        "level": "Yengil 🟢",
        "price": 0,
        "location": "Shahar Ilmiy Kutubxonasi",
        "time": "Yakshanba kechqurun",
        "description": "Kutubxona mudiri Farrux aka hushsiz topildi, seyfdagi qadimiy qo'lyozma yo'q.",
        "evidence": [
            "Seyf kodi to'g'ri terilgan.",
            "Deraza tagida gul tuvagi ag'darilgan, lekin tuproq to'kilmagan.",
            "Stol ustida ko'zoynak yotibdi, oynasi yorilgan."
        ],
        "suspects": {
            "Nodira": "Kutubxona kotibasi. 'Men soat 18:00 da ketdim, kodni faqat men va Farrux aka bilamiz.'",
            "Jasur": "Tadqiqotchi. 'Men ruxsat so'ragandim, rad etilgandim.'",
            "Malika": "Farrux akaning qizi. 'Otamga choy olib kirdim, sog'lom edi.'"
        },
        "guilty": "Nodira",
        "solution": "Seyf kodi buzilmagan — demak kodni biluvchi ochgan. Tuproq sochilmangani sahna ekanini ko'rsatadi."
    },
    
    # ... (Qolgan 2-14 ishlar shu zaylda saqlanadi) ...

    # 15+ Premium / Horror / Jiddiy Ishlar (Ochish uchun virtual pul talab qilinadi)
    {
        "id": 15,
        "title": "Tashlab ketilgan ruhiy shifoxona qotilligi",
        "level": "Horror / Jiddiy 🔴",
        "price": 100,  # Ochish uchun 100$ virtual pul
        "location": "Eski ruhiy shifoxona yerto'lasi",
        "time": "Tungi soat 03:00",
        "description": (
            "Stalkerlar guruhi yerto'ladan zanjirlangan va qonga belangan jasadni topishdi. "
            "Devorga qon bilan 'U bizni kuzatmoqda' deb yozilgan. Xonada 3 ta chiroq bor edi."
        ),
        "evidence": [
            "Jasadning barmoq izlari ataylab kuydirib yo'qotilgan.",
            "Devordagi qon yozuvi hali qurimagan edi (atrof loyqa va sovuq bo'lishiga qaramay).",
            "Guruh a'zolaridan birining kiyimida kuydiruvchi kislota hidli modda topildi."
        ],
        "suspects": {
            "Viktor": "Boshlovchi stalker. 'Men oldinda yurgan edim, chirog'im o'chib qoldi.'",
            "Sardor": "Kimyogar talaba. 'Men shunchaki fotosuratga olayotgan edim.'",
            "Elena": "Tarixchi. 'Men qichqiriqni eshitib orqaga qochdim.'"
        },
        "guilty": "Sardor",
        "solution": "Jasadning barmoq izlarini kuydirish uchun kislota ishlatilgan va u Sardorning kiyimida topildi. U qurbonni guruh kelishidan oldin o'ldirib, o'zini guruh a'zosidek ko'rsatgan."
    },
    {
        "id": 16,
        "title": "Qora o'rmondagi marosim",
        "level": "Horror / Jiddiy 🔴",
        "price": 150,
        "location": "Qora o'rmon ichkarisi",
        "time": "Yarim tun",
        "description": (
            "O'rmondan sirli kult marosimi o'tkazilgan joy va o'ldirilgan qurbon topildi. "
            "Qurbonning qo'lida g'ayrioddiy ramzlar tushirilgan kartochka bor edi."
        ),
        "evidence": [
            "Marosim gulxani atrofida 3 xil poyabzal izi bor.",
            "Qurbonning telefonida oxirgi sms: 'O'rmon chetidagi kulbaga kel' deb yozilgan.",
            "Gumonlanuvchilardan birining poyabzalida kul va noyob o'rmon masi izi topildi."
        ],
        "suspects": {
            "Artur": "Kult a'zosi. 'Men marosimga bormadim, uyda edim.'",
            "Timur": "O'rmonchi. 'Men tunda o'rmonni aylandim, g'alati ovozlarni eshitdim.'",
            "Diana": "Qurbonning do'sti. 'Men uni ogohlantirgandim, lekin u ketdi.'"
        },
        "guilty": "Artur",
        "solution": "Arturning poyabzalidagi kul va rare mas marosim o'tkazilgan o'rmon markazidan olingan. Uning 'uyda edim' degan alibisi soxta."
    }
]

###############################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
###############################################################

###############################################################
# İş Problemi (Business Problem)
###############################################################
# FLO müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor.
# Buna yönelik olarak müşterilerin davranışları tanımlanacak ve bu davranış öbeklenmelerine göre gruplar oluşturulacak..

###############################################################
# Veri Seti Hikayesi
###############################################################

# Veri seti son alışverişlerini 2020 - 2021 yıllarında OmniChannel(hem online hem offline alışveriş yapan) olarak yapan müşterilerin geçmiş alışveriş davranışlarından
# elde edilen bilgilerden oluşmaktadır.

# master_id: Eşsiz müşteri numarası
# order_channel : Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile, Offline)
# last_order_channel : En son alışverişin yapıldığı kanal
# first_order_date : Müşterinin yaptığı ilk alışveriş tarihi
# last_order_date : Müşterinin yaptığı son alışveriş tarihi
# last_order_date_online : Muşterinin online platformda yaptığı son alışveriş tarihi
# last_order_date_offline : Muşterinin offline platformda yaptığı son alışveriş tarihi
# order_num_total_ever_online : Müşterinin online platformda yaptığı toplam alışveriş sayısı
# order_num_total_ever_offline : Müşterinin offline'da yaptığı toplam alışveriş sayısı
# customer_value_total_ever_offline : Müşterinin offline alışverişlerinde ödediği toplam ücret
# customer_value_total_ever_online : Müşterinin online alışverişlerinde ödediği toplam ücret
# interested_in_categories_12 : Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi

###############################################################
# GÖREVLER
###############################################################

# GÖREV 1: Veriyi Anlama (Data Understanding) ve Hazırlama
           # 1. flo_data_20K.csv verisini okuyunuz.
           # 2. Veri setinde
                     # a. İlk 10 gözlem,
                     # b. Değişken isimleri,
                     # c. Betimsel istatistik,
                     # d. Boş değer,
                     # e. Değişken tipleri, incelemesi yapınız.
           # 3. Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir. Herbir müşterinin toplam
           # alışveriş sayısı ve harcaması için yeni değişkenler oluşturun.
           # 4. Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.
           # 5. Alışveriş kanallarındaki müşteri sayısının, ortalama alınan ürün sayısının ve ortalama harcamaların dağılımına bakınız.
           # 6. En fazla kazancı getiren ilk 10 müşteriyi sıralayınız.
           # 7. En fazla siparişi veren ilk 10 müşteriyi sıralayınız.
           # 8. Veri ön hazırlık sürecini fonksiyonlaştırınız.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import datetime as dt
from pandas import read_csv
#Ekran Ayarlama
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width',1000)


path=Path('/Users/hakanadiyaman/PycharmProjects/Flo_Musteri_Segmentasyonu/flo_data_20k.csv')
df_copy=read_csv(path)
df=df_copy.copy()
df.head(10)
df.columns
df.info()
df.describe()
df.isnull().sum()
df.shape

df["order_num_total"]=df["order_num_total_ever_online"]+df["order_num_total_ever_offline"]
df["customer_value_total"]= df["customer_value_total_ever_online"]+df["customer_value_total_ever_offline"]

df.info() #Değişken tiplerini inceleme
date_columns= df.columns[df.columns.str.contains('date')]
df[date_columns]=df[date_columns].apply(pd.to_datetime)
df.info()

df.groupby("order_channel").agg({"master_id":"count",
                                 "order_num_total":"sum",
                                 "customer_value_total":"sum"})

df.sort_values("customer_value_total", ascending=False,).head(10)

df.sort_values("order_num_total", ascending=False,).head(10)

#Veri ön hazırlık

def data_prep(dataframe):
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)
    return df

# GÖREV 2: RFM Metriklerinin Hesaplanması
max_date = df["last_order_date"].max()
analysis_date = max_date + pd.Timedelta(days=2)
print("\nAnaliz tarihi:", analysis_date.date())

rfm = pd.DataFrame()
rfm["customer_id"] = df["master_id"]
rfm["recency"] = (pd.to_datetime(analysis_date) - pd.to_datetime(df["last_order_date"])).dt.days
rfm["frequency"] = df["order_num_total"]
rfm["monetary"] = df["customer_value_total"]
rfm.head()


# GÖREV 3: RF ve RFM Skorlarının Hesaplanması

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm.head()
# GÖREV 4: RF Skorlarının Segment Olarak Tanımlanması
rfm["RF_SCORE"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)
rfm.tail() #Son 5 değere bakalım
#Tablodaki segmentasyon değerleriyle mapleme
segmentasyon_map ={
    r'^[1-2][1-2]$': 'hibernating',
    r'^[1-2][3-4]$': 'at_Risk',
    r'^[1-2]5$': 'cant_loose',
    r'^3[1-2]$': 'about_to_sleep',
    r'^33$': 'need_attention',
    r'^[3-4][4-5]$': 'loyal_customers',
    r'^41$': 'promising',
    r'^51$': 'new_customers',
    r'^[4-5][2-3]$': 'potential_loyalists',
    r'^5[4-5]$': 'champions'
}

rfm['segment'] = rfm['RF_SCORE'].replace(segmentasyon_map, regex=True)

rfm.head()

# GÖREV 5: Aksiyon zamanı!
           # 1. Segmentlerin recency, frequnecy ve monetary ortalamalarını inceleyiniz.
           # 2. RFM analizi yardımı ile 2 case için ilgili profildeki müşterileri bulun ve müşteri id'lerini csv ye kaydediniz.
                   # a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri tercihlerinin üstünde. Bu nedenle markanın
                   # tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak iletişime geçeilmek isteniliyor. Sadık müşterilerinden(champions,loyal_customers),
                   # ortalama 250 TL üzeri ve kadın kategorisinden alışveriş yapan kişiler özel olarak iletişim kuralacak müşteriler. Bu müşterilerin id numaralarını csv dosyasına
                   # yeni_marka_hedef_müşteri_id.cvs olarak kaydediniz.
                   # b. Erkek ve Çoçuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte iyi müşteri olan ama uzun süredir
                   # alışveriş yapmayan kaybedilmemesi gereken müşteriler, uykuda olanlar ve yeni gelen müşteriler özel olarak hedef alınmak isteniliyor. Uygun profildeki müşterilerin id'lerini csv dosyasına indirim_hedef_müşteri_ids.csv
                   # olarak kaydediniz.
#Frequency score categoric veri tipi kalmıştı onu int yapmalıyız
rfm["frequency_score"] = rfm["frequency_score"].astype(int)
rfm.groupby("segment")[["recency","frequency_score","monetary"]].mean()

#a
# 250 TL üstü ortalama sepet için ortalama tutar (bir kez hesapla)
rfm["avg_order_value"] = rfm["monetary"] / rfm["frequency"]

# hedef segmentler
target_segments_customer_ids = rfm[
    rfm["segment"].isin(["champions","loyal_customers"])
]["customer_id"]

# filtre: KADIN kategorisi + avg_order_value > 250
cust_ids = df[
    df["master_id"].isin(target_segments_customer_ids)
    & df["interested_in_categories_12"].str.contains("KADIN", case=False, na=False)
].merge(
    rfm.loc[rfm["customer_id"].isin(target_segments_customer_ids), ["customer_id","avg_order_value"]],
    left_on="master_id", right_on="customer_id", how="left"
)

cust_ids = cust_ids[cust_ids["avg_order_value"] > 250]["master_id"].drop_duplicates()

# CSV'ye yaz
cust_ids.to_frame(name="customer_id").to_csv("yeni_marka_hedef_musteri_id.csv", index=False)# GÖREV 6: Tüm süreci fonksiyonlaştırınız.

#b
#Hedef segmentler: kaybedilmemesi gerekenler, uykuda, uzun süredir gelmeyenler, yeni gelenler
target_segments_b = ["cant_loose", "about_to_sleep", "hibernating", "at_Risk", "new_customers"]

# bu segmentlerdeki müşteri id'leri
target_seg_ids_b = rfm[rfm["segment"].isin(target_segments_b)]["customer_id"]

# kategori filtresi: ERKEK veya (C/Ç)OCUK
cat_pattern = r"(ERKEK)|(COCUK)|(ÇOCUK)"

b_ids = df[
    df["master_id"].isin(target_seg_ids_b)
    & df["interested_in_categories_12"].str.contains(cat_pattern, case=False, na=False)
]["master_id"].drop_duplicates()

# CSV'ye yaz (tek kolonlu df olarak)
b_ids.to_frame(name="customer_id").to_csv("indirim_hedef_musteri_ids.csv", index=False)

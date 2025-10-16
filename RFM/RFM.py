import pandas as pd
from pathlib import Path
import datetime as dt
#1)Veriyi Tanımlama
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

path = Path("/Users/hakanadiyaman/PycharmProjects/RFM/datasets/online_retail_II.xlsx")


df= pd.read_excel(path, sheet_name="Year 2010-2011")
df.head()
#2)Veriyi Anlama
#Dataframi kopyalayıp ilgili işlemleri copyde yaparak df bozmayız
df_copy=df.copy()

df_copy.head()
df_copy.shape # Toplam satır , sütün sayısı
df_copy.isnull().sum() #Df içindeki boş değerlere bakma

df_copy["Description"].nunique() #  Eşsiz Ürün sayısı

df_copy["Description"].value_counts() # Ürünlerin sayısı

df_copy.groupby("Description").agg({"Quantity": "sum"}).head() # Ürün bazında toplam satılan adet
# (Quantity) bilgisini verir.
# İlk 5 ürünü (alfabetik veya gruplama sırası) gösterir

df_copy.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()
#Ürünlerin toplam adedini büyükten küçüğe sıralar

df_copy["Invoice"].nunique() # Eşsiz fatura sayısını öğrenme

#Toplam ne kadar harcama yapıldığını ekleyelim. Önce ürünlerden kaçar alınmışsa pricela çarparız
df_copy["TotalPrice"] = df["Quantity"] * df["Price"]

df_copy.groupby("Invoice").agg({"TotalPrice": "sum"}).head()#Her fatura için total priceları toplarız

#3) Veriyi Hazırlama
df_copy.describe().T # Özet istatistikler.. T daha iyi görmemize yarar
df_copy= df_copy[(df_copy['Quantity'] > 0)] # 0 ya da negatifleri çıkarma
df.dropna(inplace=True)
df_cppy = df[~df["Invoice"].str.contains("C", na=False)] #Datada C ile başlayan yani iade olanlar vardı
# onları temizler

#4)RFM HESAPLAMA
# Recency, Frequency, Monetary
df_copy.head()
df_copy["InvoiceDate"].max() # Son günü görürüz

today_date = dt.datetime(2010, 12, 11) #Bu değerle sonradan mat işlemler yapabiliz
type(today_date) #datetime.datetime

#Recency , Freqeuncy, Monetary değerlerini hesaplama
rfm = df_copy.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.head()

rfm.columns = ['recency', 'frequency', 'monetary']

rfm.describe().T

rfm = rfm[rfm["monetary"] > 0]
rfm.shape

#5) RFM Skoru Oluşturma ve Hesaplama
#Recency hesaplama, receny küçükse müşteri taze, ters skorlama
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
#Frequency hesağlama, frequency büyükse müşteri sıklığı iyi, rank methoduyla aynı değere sahip müşterileri de alma
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
#Monetary hesaplama. ne kadar büyükse o kadar iyi
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
#RFM skorları oluşunca bunları string olarak alıp yan yana yazma
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.describe().T

rfm[rfm["RFM_SCORE"] == "55"]
""
rfm[rfm["RFM_SCORE"] == "11"]


 #6)RFM SEGMENTLERİNİ OLUŞTURULMASI
# regex : Verilen sözlükte uyanları segment etiketiyle değiştirme
# RFM isimlendirmesi
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}
#Oluşturulan segmentleri rfm scorelarla değiştirme
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
#Segmentler için R-F_M ve müşteri sayısını özetleme
rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

#Belirli segmenti inceleme
rfm[rfm["segment"] == "cant_loose"].head()
rfm[rfm["segment"] == "cant_loose"].index
#Rfm segmentindeki müşteri ID lerinden yeni dataframe oluşturma
new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index
#Oluşturulan df id değerlerini inte çevirme
new_df["new_customer_id"] = new_df["new_customer_id"].astype(int)

#CSV olarak dışarı çıkartma
new_df.to_csv("new_customers.csv")
rfm.to_csv("rfm.csv")


####  TÜM SÜRECİN FONKSİYONLAŞTIRILMASI #####
def create_rfm(dataframe, csv=False):

    # VERIYI HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # RFM METRIKLERININ HESAPLANMASI
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # cltv_df skorları kategorik değere dönüştürülüp df'e eklendi
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))


    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm

df = df_.copy()

rfm_new = create_rfm(df, csv=True)











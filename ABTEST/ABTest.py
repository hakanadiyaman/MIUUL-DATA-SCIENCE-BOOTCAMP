#####################################################
# AB Testi ile BiddingYöntemlerinin Dönüşümünün Karşılaştırılması
#####################################################
import pandas

#####################################################
# İş Problemi
#####################################################

# Facebook kısa süre önce mevcut "maximumbidding" adı verilen teklif verme türüne alternatif
# olarak yeni bir teklif türü olan "average bidding"’i tanıttı. Müşterilerimizden biri olan bombabomba.com,
# bu yeni özelliği test etmeye karar verdi veaveragebidding'in maximumbidding'den daha fazla dönüşüm
# getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.A/B testi 1 aydır devam ediyor ve
# bombabomba.com şimdi sizden bu A/B testinin sonuçlarını analiz etmenizi bekliyor.Bombabomba.com içina
# nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchasemetriğine odaklanılmalıdır.




#####################################################
# Veri Seti Hikayesi
#####################################################

# Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları
# reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.Kontrol ve Test
# grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleriab_testing.xlsxexcel’ininayrı sayfalarında yer
# almaktadır. Kontrol grubuna Maximum Bidding, test grubuna AverageBiddinguygulanmıştır.

# impression: Reklam görüntüleme sayısı
# Click: Görüntülenen reklama tıklama sayısı
# Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
# Earning: Satın alınan ürünler sonrası elde edilen kazanç



#####################################################
# Proje Görevleri
#####################################################

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################

# 1. Hipotezleri Kur
# 2. Varsayım Kontrolü
#   - 1. Normallik Varsayımı (shapiro)
#   - 2. Varyans Homojenliği (levene)
# 3. Hipotezin Uygulanması
#   - 1. Varsayımlar sağlanıyorsa bağımsız iki örneklem t testi
#   - 2. Varsayımlar sağlanmıyorsa mannwhitneyu testi
# 4. p-value değerine göre sonuçları yorumla
# Not:
# - Normallik sağlanmıyorsa direkt 2 numara. Varyans homojenliği sağlanmıyorsa 1 numaraya arguman girilir.
# - Normallik incelemesi öncesi aykırı değer incelemesi ve düzeltmesi yapmak faydalı olabilir.




#####################################################
# Görev 1:  Veriyi Hazırlama ve Analiz Etme
#####################################################

import pandas as pd
from scipy.stats import shapiro, levene, ttest_ind
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt


pd.set_option('display.max_columns', None)

pd.set_option('display.float_format', lambda x: '%.5f' % x)
# Adım 1:  ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.




dataframe_control = pd.read_excel("/Users/hakanadiyaman/PycharmProjects/ABTEST/ab_testing.xlsx",
                                  sheet_name="Control Group")

dataframe_test = pd.read_excel("/Users/hakanadiyaman/PycharmProjects/ABTEST/ab_testing.xlsx",
                               sheet_name="Test Group")

df_control = dataframe_control.copy()
df_test = dataframe_test.copy()

df_control.head()
df_test.head()
# Adım 2: Kontrol ve test grubu verilerini analiz ediniz.

def check_df(dataframe, head=5):
    print("********** SHAPE *******")
    print(dataframe.shape)
    print("******** DATA TYPE *******")
    print(dataframe.dtypes)
    print("******** HEAD *******")
    print(dataframe.head())
    print("******** TAİl *******")
    print(dataframe.tail())
    print(dataframe.isnull().sum())
    print("******** QUANTİLE *******")
    print(dataframe.quantile(0.25))

check_df(df_control)
check_df(df_test)

plt.hist(df_control['Purchase'], bins=100)
plt.show()

plt.hist(df_test['Purchase'])
plt.show()
# Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.

df_control["group"]="Control"
df_test["group"]="Test"

df=pd.concat([df_control, df_test], axis=0, ignore_index=True)

df.head()
df.shape


#####################################################
# Görev 2:  A/B Testinin Hipotezinin Tanımlanması
#####################################################

# Adım 1: Hipotezi tanımlayınız.

#H0 =Anlamlı bir geri dönüşüm farkı yoktur
#H1 = Anlamlı bir geri dönüşüm farkı vardır

# Adım 2: Kontrol ve test grubu için purchase(kazanç) ortalamalarını analiz ediniz

df_control["Purchase"].mean()
df_test["Purchase"].mean()

df.groupby("group").agg({"Purchase": "mean"})
#####################################################
# GÖREV 3: Hipotez Testinin Gerçekleştirilmesi
#####################################################

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################


# Adım 1: Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.

# Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ediniz
#H0:  normal dağılım gösterdiği varsayılır
#H1 : Nırmal dağılım gösterdiği varsayılmamaktadır
""""
p<0.05 H0 reddedilir"""

test_stat, pvalue = shapiro(df.loc[df["group"] == "control", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

#p.value = 0.5891 çıktı p >0.05 olduğundan H0 kabul edilir yani normal dağılım var

#Test grubunun dağılımına bakalım
test_stat, pvalue = shapiro(df.loc[df["group"] == "test", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

#p=0.1541  H0 kabul






# Adım 2: Normallik Varsayımı ve Varyans Homojenliği sonuçlarına göre uygun testi seçiniz

#Hem varyans hem de normallik sağlandığından bağımsız iki örneklem t testi yapılır

test_stat, pvalue = ttest_ind(df.loc[df["group"] == "control", "Purchase"],
                              df.loc[df["group"] == "test", "Purchase"],
                              equal_var=True)
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
""" Çıkan değer p value = 0.3493 çıktı p value >0.05 olduğundan H0 rededilemez """
# Adım 3: Test sonucunda elde edilen p_value değerini göz önünde bulundurarak kontrol ve test grubu satın alma
# ortalamaları arasında istatistiki olarak anlamlı bir fark olup olmadığını yorumlayınız.

"""Kontrol ve test grubu satın alma ortalamaları arasında istatistiksel olarak anlamlı farklılık yok"""
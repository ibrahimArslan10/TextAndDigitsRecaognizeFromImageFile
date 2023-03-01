from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import pytesseract
import numpy as np
import os
import sys 

sys.path.append('/usr/local/lib/python3.9/site-packages')

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Projede kullanılan global değişkenler ; dosyaAdi,KlasorAdi
#Bu değişkenler, dosya gezgini etiketini güncellemek için kullanılır,ayrıca dosya/klasörün yolunu depolar.
fileName = ""
folderName = ""

# Bu Fonksiyon (dosyaSec) ise dosya gezgini penceresini açar
def browseFiles():
    global fileName

    # Dosya gezginini açar ve kullanıcının seçtiği dosyayı dosyaAdi  degişkenine atar
    fileName = filedialog.askopenfilename(initialdir="C:/", title="Dosya Seçiniz")

    # Bir dosya adı seçtikten sonra etiket(Form Pencere Etiketi) içeriğini değiştirir
    label_file_explorer.configure(text="Dosya Açıldı: " + fileName)


# OCR uygulama ve tek bir görüntüden metin çıkarma işlevleri gerçeklenir
def convertFile():
    global fileName
    # Resmimizi okumak için dosyaSec fonksiyonunda atanan dosyaAdi değişkenini kullanılır.
    myImage = cv2.imread(fileName)

    # Görüntüyü Önişleme Başlatılır ( image preprocessing)
    # resmi büyütme işlemi
    myImage = cv2.resize(myImage, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    # gri tonlamaya dönüştürme işlemi
    myImage = cv2.cvtColor(myImage, cv2.COLOR_BGR2GRAY)
    # RBG kanalları ayrılır ve     diziye kaydedilir.
    rgb_planes = cv2.split(myImage)
    result_planes = []
    # Ayrı ayrı işlemek için birden çok RGB kanalları oluşturulur
    for plane in rgb_planes:
        #dilatasyon uygulanır
        dilated_image = cv2.dilate(plane, np.ones((7, 7), np.uint8))
        # median blur filtresi uygulanır.
        background_image = cv2.medianBlur(dilated_image, 21)
        diff_img = 255 - cv2.absdiff(plane, background_image)
        # Tüm sonuçlar aynı rgb kanalına  eklenir
        result_planes.append(diff_img)
    # For döngüsündeki işlemlerden sonra rgb kanalları tekrar birleştirilir.
    myImage = cv2.merge(result_planes)

    # Görüntüdeki gürültünün bir kısmını ortadan kaldırmak için genişletme ve aşındırma uygulanır
    kernel = np.ones((1, 1), np.uint8)
    # Görüntüdeki beyaz bölgenin bir kısmını arttırılır
    myImage = cv2.dilate(myImage, kernel, iterations=1)
    # Ön plan nesnesinin bazı sınırlarını aşındırır
    myImage = cv2.erode(myImage, kernel, iterations=1)

    # OTSU eşiğini kullanarak siyah beyaza dönüştürmek için gri tonlamalı görüntüye eşik uygulanır
    myImage = cv2.threshold(myImage, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # Görüntüyü Önişleme Sonlandı.

    # Özel OCR ayarları atanır
    #r parametresinin anlamı kullanılacak tesseract motoru ile seçim yapmaktır.
    # psm parametresi "sayfa bölümleme modu" anlamına gelir. ("page segmentation mode")
    #Bu parametre, tek bir metin bloğu varsayıldığında altı olarak atanacaktır, ancak 14 farklı seçenek vardır.

    custom_config = r'--oem 3 --psm 6'
    outputText = pytesseract.image_to_string(myImage, config=custom_config)

    # Resimle aynı ada sahip bir metin (txt) dosyası oluşturur ve resmin içeriğini txt dosyasına yazar
    # Çıktı alınan metin dosyasından .jpg veya .png dosya uzantısını kaldırmak için [0:-4] dizi aralığını kullanıyoruz
    file = open(fileName[0:-4] + "text.txt", "w+")
    file.write(outputText)
    file.close()
    # Dosyayı kapattıktan sonra, metin dosyasının adı ile birlikte işlemin tamamlandığını kullanıcıya gösteriliyor.
    # Metin dosyasının adı  resimle aynı ad ve aynı yerde olacaktır.
    print(' \nYazı ayrıştırma işlemleri tamamlandı ' + fileName + 'text.txt')


def convertFile_Digits():
    global fileName
    myImage = cv2.imread(fileName)

    # Görüntü Önişleme Başlatılır.
    # görüntü büyütme işlemi uygulanır.
    myImage = cv2.resize(myImage, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    # görüntü gri tonlamaya dönüştürülür (grayscale işlemi)
    myImage = cv2.cvtColor(myImage, cv2.COLOR_BGR2GRAY)
    # RBG kanalları ayrılır. ve  diziye kaydedilir.
    rgb_planes = cv2.split(myImage)
    result_planes = []
    # Ayrı ayrı işlemek için birden çok RGB uzayına bölünür.
    for plane in rgb_planes:
        dilated_image = cv2.dilate(plane, np.ones((7, 7), np.uint8))
        # dilatasyon işlemi uygulanır.
        background_image = cv2.medianBlur(dilated_image, 21)
        # median blur filtresi uygulanır.
        diff_img = 255 - cv2.absdiff(plane, background_image)
        result_planes.append(diff_img)
    # For döngüsündeki işlemlerden sonra rgb kanalları tekrar birleştirilir
    myImage = cv2.merge(result_planes)

    # Görüntüdeki  gürültünün bir kısmını ortadan kaldırmak için genişletme ve aşındırma uygulanır
    kernel = np.ones((1, 1), np.uint8)
    # Görüntüdeki beyaz bölgenin bir kısmını arttırma işlemi uygulandı
    myImage = cv2.dilate(myImage, kernel, iterations=1)
    # Ön plan nesnesinin bazı sınırlarını aşındırır
    myImage = cv2.erode(myImage, kernel, iterations=1)

    # OTSU eşiğini kullanarak siyah beyaza dönüştürmek için gri tonlamalı görüntüye eşikleme uygulanır.
    myImage = cv2.threshold(myImage, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # Görüntüyü Önişleme Sonlandırılır.

    # Yalnızca metinden rakamları çıkarmak için outputbase digits parametresi atanır.
    custom_config = r'--oem 3 --psm 6 outputbase digits'
    outputText = pytesseract.image_to_string(myImage, config=custom_config)

    # görüntü dosyası ile    aynı ada sahip bir metin dosyası oluşturulur ve içeriği dosyaya yazılır.
    # Çıktı alınan metin dosyasından .jpg veya .png dosya uzantısını kaldırmak için [0:-4]  dizi aralığı kullanılır.
    file = open(  fileName[0:-4]+"digits.txt", "w+")
    file.write(outputText)
    file.close()
    # Dosyayı kapattıktan sonra, metin dosyasının adı ile birlikte işlemin tamamlandığını ekrana yazdırılır.
    # Metin dosyası ile görüntü dosyasının adı ve bulunduğu yer ile aynı yapıldı.
    print('Rakam ayrıştırma ve dosyaya kaydetme işlemi tamamlandı.  ' + fileName + 'digits.txt')



# Tkinter penceresi  oluşturulur.
window = Tk()


window.title('Görüntüden Yazı veya Sayı Ayrıştırma Projesi')

# pencerenin boyutu ayarlanır.
window.geometry("800x600")

# Pencerenin arka plan rengi ayarlanır.
window.config(background="green")

# butonlar oluşturulur.
# dosya yolunu ekranda gösteren label
label_file_explorer = Label(window,
                            text="  "
                                 ,
                            width=100, height=4,
                            fg="blue")

# tek bir dosya işlemi seçme butonu
button_explore = Button(window,
                        text="Dosya Seçiniz",
                        command=browseFiles)

# Tek bir görüntüde OCR gerçekleştirme butonu
button_convert = Button(window,
                        text="Dosyadaki Yazıları Ayrıştır",
                        command=convertFile)

# Tek bir görüntüde OCR gerçekleştirilir.  (yalnızca görüntüdeki rakamlar ayrıştırılır.)
button_convert_digits = Button(window,
                        text="Dosyadaki Sayıları Ayrıştır",
                        command=convertFile_Digits)

# programdan çıkış butonu
button_exit = Button(window,
                     text="Çıkış",
                     command=exit)


# ekran görünümü için  grid ile eleman konumlandırmalar yapıldı. 
# dosya yolunu gösteren label(etiket) elemanı
label_file_explorer.grid(column=1, row=1)

# pady fonksiyonundailk parametre üstteki dolgu ve ikinci parametre alttaki dolgudur.
#tek dosya seçme butonu konumlandırma
button_explore.grid(column=1, row=2, pady=(50, 10))

# tek dosya ile yazı ayrıştırma butonunu ekranda konumlandırma
button_convert.grid(column=1, row=4)

# tek dosya ile sayı ayrıştırma butonunu ekranda konumlandırma
button_convert_digits.grid(column=1, row=6)


# programdan çıkış butonu
button_exit.grid(column=1, row=14, padx=10, pady=30)



label.grid(row=15, column=1)
# label.pack()

#  çıkış butonuna basılmadığı sürece program ekranının açık kalmasını sağlar mainloop() fonksiyonu
window.mainloop()

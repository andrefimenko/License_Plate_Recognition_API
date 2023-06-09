import pytesseract
import cv2
import matplotlib.pyplot as plt
import re
import json
# import imutils
import time
from PIL import Image
import requests

def recognition():
    t0 = time.time()
    img2rec = "Img/photo_2023-01-25_14-22-15.jpg"

    # Set tesseract path to where the tesseract exe file is located (Edit this path accordingly based on your own settings)
    pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

    image = cv2.imread(img2rec)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_rgb = cv2.bilateralFilter(image_rgb, 11, 15, 150)

    # Import Haar Cascade XML file for Russian car plate numbers
    carplate_haar_cascade = cv2.CascadeClassifier('D:/Documents/Python/License_plates/'
                                                  'License_Plates_Recognition/Haar_Cascade_XML'
                                                  '/haarcascade_russian_plate_number.xml')

    # Function to enlarge the plt display for user to view more clearly
    def enlarge_plt_display(img, scale_factor):
        width = int(image.shape[1] * scale_factor / 100)
        height = int(image.shape[0] * scale_factor / 100)
        dim = (width, height)
        # plt.figure(figsize=dim)
        plt.axis('off')
        # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    # Setup function to detect car plate
    def carplate_detect(img):
        carplate_overlay = img.copy()  # Create overlay to display red rectangle of detected car plate
        carplate_rects = carplate_haar_cascade.detectMultiScale(carplate_overlay, scaleFactor=1.01, minNeighbors=55)  #
        # scaleFactor=1.013, minNeighbors=55)
        for x, y, w, h in carplate_rects:
            cv2.rectangle(carplate_overlay, (x, y), (x + w, y + h), (255, 0, 0), 5)
        # # PAUSE SHOWING IMAGES HERE
        cv2.imshow("Image", carplate_overlay)
        cv2.waitKey(0)
        #     # cv2.destroyAllWindows()
        return carplate_overlay

    # Function to retrieve only the car plate sub-image itself
    def carplate_extract(img, y_cut=0, x_cut=0):
        carplate_rects = carplate_haar_cascade.detectMultiScale(img, scaleFactor=1.01, minNeighbors=55)
        for x, y, w, h in carplate_rects:
            carplate_img = img[y + 6 + (y_cut // 2):y + h - 8 - y_cut, x + 10 + (x_cut):x + w - 2 - x_cut]  # [y + 12 +
            # y_cut:y +
            # h - 11 - y_cut, x + 9 + x_cut:x + w - 19 - x_cut]
        try:
            return carplate_img
        except Exception as e:
            print("Caught it! 3")

    lic_plate_img = carplate_extract(image_rgb)

    # Enlarge image for further image processing later on
    def enlarge_img(img, scale_percent):
        try:
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)
            resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
            return resized_img
        except Exception as e:
            print("Caught it!")

    def different_modes(mode):
        try:
            answer = pytesseract.image_to_string(carplate_extract_img_gray_blur,
                                                 config=f'--psm {mode} --oem 3 -c '
                                                        f'tessedit_char_whitelist=ABCcEHKMOoPTXxYy123456789');
            # ! ! ! All "zero" symbols will be recognized as O letters on this stage ! ! !
            return answer.upper()
        except Exception as e:
            print("Caught it! 4")

    # modes2try = [6, 7, 8, 9, 10, 11, 13]
    modes2try = [8, 9]
    # 6
    # Предположим, что это один однородный блок текста.
    # 7
    # Обработайте изображение как одну текстовую строку.
    # 8
    # Рассматривайте изображение как одно слово.
    # 9
    # Рассматривайте изображение как одно слово в круге.
    # 10
    # Обрабатывайте изображение как один символ.
    # 11
    # Скудный текст. Найдите как можно больше текста в произвольном порядке.
    # 13
    # Необработанная линия. Обрабатывайте изображение как одну текстовую строку, минуя хаки, специфичные для
    # Тессеракта.""

    pattern = r'\b^[ABCEHKMOPTXY][1-9,O]{3}[ABCEHKMOPTXY]{2}[1-9,O]{2,3}\b'

    response_dict = {}

    def raw2candidate(raw_list):
        treated = [i for i in raw_list if i != " "]  # Removing spaces
        treated = [i for i in treated if i != "\n"]  # Removing "new-liners"
        if treated[0] == "1":
            treated[0] = "T"
        if treated[0] == "7":
            treated[0] = "T"
        if treated[1] == "B":
            treated[1] = "8"
        if treated[2] == "B":
            treated[2] = "8"
        if treated[3] == "B":
            treated[3] = "8"
        if treated[4] == "1":
            treated[4] = "T"
        if treated[4] == "7":
            treated[4] = "T"
        if treated[5] == "1":
            treated[5] = "T"
        if treated[5] == "7":
            treated[5] = "T"

        treated_list = "".join(treated)
        # print(treated_list)
        match = re.search(pattern, treated_list)
        # print(treated_list if match else "not recognized")
        if match:
            return treated_list

    candidate_set = set()

    def send_post_request(url, value):
        myobj = {"key": value}
        x = requests.post(url, json=myobj)
        return x

    # def rotate(img_param, angle):
    #     height, width = img_param.shape[:2]
    #     point = (width // 2, height // 2)
    #
    #     mat = cv2.getRotationMatrix2D(point, angle, 0.5)
    #     return cv2.warpAffine(img_param, mat, (width, height))

    # image_rgb = rotate(image_rgb, 18)

    enlarge_plt_display(image_rgb, 1.2)

    detected_carplate_img = carplate_detect(image_rgb)

    enlarge_plt_display(detected_carplate_img, 1.2)

    url = "https://ya.ru/"

    # Display extracted car license plate image
    # for yc in range(0, 25, 7):
    #     for xc in range(0, 25, 7):
    for yc in range(0, lic_plate_img.shape[0] // 10, 1):
        for xc in range(0, lic_plate_img.shape[1] // 12, 2):
            carplate_extract_img = carplate_extract(image_rgb, yc, xc)
            carplate_extract_img = enlarge_img(carplate_extract_img, 150)

            try:
                gray = cv2.cvtColor(carplate_extract_img, cv2.COLOR_BGR2GRAY)
                cv2.imshow("1 - Grayscale Conversion", gray)
                # Noise removal with iterative bilateral filter(removes noise while preserving edges)
                carplate_extract_img_gray = cv2.bilateralFilter(gray, 11, 15, 15)
                cv2.imshow("2 - Bilateral Filter", carplate_extract_img_gray)
                # edges = cv2.Canny(carplate_extract_img_gray, 30, 200)
                #
                # cont = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                # cont = imutils.grab_contours(cont)
                # cont = sorted(cont, key=cv2.contourArea, reverse=True)[:8]
                #
                #
                # plt.imshow(cv2.cvtColor(edges, cv2.COLOR_BGR2RGB))
                # plt.show()
                # denoising the image
                # carplate_extract_img_gray_blur = cv2.GaussianBlur(carplate_extract_img_gray,(5, 5), 0)

                cv2.waitKey(1)
                # cv2.destroyAllWindows()

                # Apply median blur + grayscale
                carplate_extract_img_gray_blur = cv2.medianBlur(carplate_extract_img_gray, 5)  # Kernel size 3
                # carplate_extract_img_gray_blur = cv2.GaussianBlur(carplate_extract_img_gray, (5, 5), 0)
                plt.axis('off')
                # plt.imshow(carplate_extract_img_gray_blur, cmap='gray');
            except Exception as e:
                print("Caught it! 2")

            for i in modes2try:
                print(f'==== Mode {i} ====')
                raw_string = different_modes(i)
                # print(raw_string)
                try:
                    raw_string_list = list(raw_string)
                    # print(raw2candidate(raw_string_list))
                    candidate = raw2candidate(raw_string_list)
                    if candidate is not None:
                        answer = send_post_request(url, candidate)
                        # candidate_set.add(candidate) # GET , POST req(url, key); function req(url, key) {
                        # myobj = {‘key’: key}
                        # x = requests.post(url, json = myobj)
                        print(candidate)
                        print(answer)

                except Exception as e:
                    print("Caught it! 5")

    print(candidate_set)
    t1 = time.time()
    print("Time elapsed: ", t1 - t0)



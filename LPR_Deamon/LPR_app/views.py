from datetime import datetime
from django.http import HttpResponse
import pytesseract
import cv2
import matplotlib.pyplot as plt
import re
import time
import requests
from threading import Thread


def recognition(image, back_url):
    t0 = time.time()

    with open("DATA/log.txt", "a+") as log:
        log.write(f"{datetime.now().isoformat()} {image} {back_url}\n")

    url = image
    response = requests.get(url)

    with open("DATA/image.jpg", "wb") as f:
        f.write(response.content)
    # img2rec.show() # Uncomment if you want the recognizable image to be shown

    # Set tesseract path to where the tesseract exe file is located
    # (Edit this path accordingly based on your own settings)
    pytesseract.pytesseract.tesseract_cmd = (
        r'C:/Program Files/Tesseract-OCR/tesseract.exe'
    )

    # This block of code is to convert the image into openCV image object,
    # change colors order and filtering to get rid of noises for
    # better recognition. The values are selected experimentally.
    image = cv2.imread("DATA/image.jpg")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_rgb = cv2.bilateralFilter(image_rgb, 11, 15, 150)

    # Import Haar Cascade XML file for Russian license plate numbers
    license_plate_haar_cascade = cv2.CascadeClassifier(
        'DATA/Haar_Cascade_XML/haarcascade_russian_plate_number.xml'
    )

    """ Uncomment to view recognizable image """
    # def enlarge_plt_display(img, scale_factor):
    #     """ Function to enlarge the plt display for user to view more clearly"""
    #     width = int(image.shape[1] * scale_factor / 100)
    #     height = int(image.shape[0] * scale_factor / 100)
    #     dim = (width, height)
    #     plt.figure(figsize=dim)
    #     plt.axis('off')
    #     plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    def license_plate_detect(img):
        """ Setup function to detect the license plate """
        license_plate_overlay = img.copy()  # Create an overlay to display blue rectangle of detected license plate

        # These parameters were selected experimentally as the best options for particular gate cam.
        # For other conditions: camera mount angle, view angle, lens features, shape of the gate path and
        # so on, the values probably should be changed.
        license_plate_rectangles = license_plate_haar_cascade.detectMultiScale(
            license_plate_overlay, scaleFactor=1.01, minNeighbors=55
        )

        for x, y, w, h in license_plate_rectangles:
            cv2.rectangle(license_plate_overlay, (x, y), (x + w, y + h), (255, 0, 0), 5)

        """ Showing and pausing images here """
        # cv2.imshow("Image", license_plate_overlay)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return license_plate_overlay

    def license_plate_extract(img, y_cut=0, x_cut=0):
        """ Function to retrieve only the license plate sub-image itself """

        # These parameters were selected experimentally as the best options for particular gate cam.
        # For other conditions: camera mount angle, view angle, lens features, shape of the gate path and
        # so on, the values probably should be changed.
        license_plate_rectangles = license_plate_haar_cascade.detectMultiScale(img, scaleFactor=1.01, minNeighbors=55)

        # Recognition success by this method is highly dependent on the cut values.
        # These values are good for particular gate camera. They might be reselected.
        for x, y, w, h in license_plate_rectangles:
            license_plate_img = img[y + 6 + (y_cut // 2):y + h - 8 - y_cut, x + 10 + (x_cut):x + w - 2 - x_cut]
        try:
            return license_plate_img
        except Exception as e:
            print("Caught it! 3")

    lic_plate_img = license_plate_extract(image_rgb)

    def enlarge_img(img, scale_percent):
        """ Enlarge image for further image processing later on """
        try:
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)
            resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
            return resized_img
        except Exception as e:
            print("Caught it!")

    def different_modes(mode):
        """
        Function to use different modes as different recognition approaches implemented 'under-the-hood'.
        ! ! ! All "zero" symbols will be recognized as O letters on this stage ! ! !
        """
        try:
            answer = pytesseract.image_to_string(
                license_plate_extract_img_gray_blur, config=f'--psm {mode} --oem 3 -c'
                                                       f' 'f'tessedit_char_whitelist=ABCcEHKMOoPTXxYy123456789')
            return answer.upper()
        except Exception as e:
            print("Caught it! 4")

    """
    Here are the recognition modes selecting. More you choose slower it works but more successfully.    
    6    Assume a single uniform block of text.
    7    Treat the image as a single text line.
    8    Treat the image as a single word.
    9    Treat the image as a single word in a circle.
    10   Treat the image as a single character.
    11   Sparse text. Find as much text as possible in no particular order.
    12   Sparse text with OSD.
    13   Raw line. Treat the image as a single text line, bypassing hacks that are Tesseract-specific.
    """
    # modes2try = [6, 7, 8, 9, 10, 11, 13]
    modes2try = [7, 8, 9, 10]
    # modes2try = [8, 9]

    """ This RegEx is a russian license plate blueprint A111AA11 or A111AA111 (The 'RUS' letters are not considered) """
    pattern = r'\b^[ABCEHKMOPTXY][1-9,O]{3}[ABCEHKMOPTXY]{2}[1-9,O]{2,3}\b'

    def raw2candidate(raw_list):
        """
        Function to simplify recognition by fixing typical errors
        which were discovered experimentally and healing of accidental spaces and new-liners.
        Example: if the first symbol recognised as 1 though it should be a letter, then it is more likely the T letter.
        Finally, if the obtained string corresponds a russian license plate it will be returned.
        """
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

        match = re.search(pattern, treated_list)

        if match:
            return treated_list

    def send_post_request(url, value):
        myobj = {"key": value}
        x = requests.post(url, json=myobj)
        return x

    """ Uncomment to view recognizable image """
    # enlarge_plt_display(image_rgb, 1.2)

    """ Uncomment to view recognizable license plate """
    # detected_license_plate_img = license_plate_detect(image_rgb)
    # enlarge_plt_display(detected_license_plate_img, 1.2)

    # This block of code is the step-by-step license plate image trim-off.
    # It extremely influences on recognition speed and success, so the values marked with ((*)) might be reselected
    # according to new conditions.
    for yc in range(
            0,
            lic_plate_img.shape[0] // 10,  # ((*))
            1                              # ((*))
            ):

        for xc in range(
                0,
                lic_plate_img.shape[1] // 12,  # ((*))
                2                              # ((*))
                ):

            license_plate_extract_img = license_plate_extract(image_rgb, yc, xc)
            license_plate_extract_img = enlarge_img(license_plate_extract_img, 150)

            # This block of code is to turn license plate image grey then filtered Pytesseract recommended way.
            try:
                gray = cv2.cvtColor(license_plate_extract_img, cv2.COLOR_BGR2GRAY)

                """ Uncomment to view gray license plate image """
                # cv2.imshow("1 - Grayscale Conversion", gray)

                # Noise removal with iterative bilateral filter(removes noise while preserving edges)
                license_plate_extract_img_gray = cv2.bilateralFilter(gray, 11, 15, 15)

                """ Uncomment to view grey-filtered license plate image """
                # cv2.imshow("2 - Bilateral Filter", license_plate_extract_img_gray)

                # cv2.waitKey(1)

                # Apply median blur + grayscale
                license_plate_extract_img_gray_blur = cv2.medianBlur(
                    license_plate_extract_img_gray, 5)  # Kernel size 5 worked good for particular case, default = 3

            except Exception as e:
                print("Caught it! 2")

            for i in modes2try:
                if time.time() - t0 > 60:  # Time out before recognition stop and back to waiting
                    exit()
                else:
                    print(f'==== Mode {i} ====')
                    raw_string = different_modes(i)

                    try:
                        raw_string_list = list(raw_string)
                        candidate = raw2candidate(raw_string_list)
                        if candidate is not None:
                            print(candidate)
                            answer = send_post_request(back_url, candidate)

                            with open("DATA/log.txt", "a+") as log:
                                log.write(f"{datetime.now().isoformat()} {candidate}(Mode {i}) {answer.content}\n")

                            print(answer.content)
                            if answer.content == b'ok':  # Ok received, recognition stop, back to waiting
                                exit()

                    except Exception as e:
                        print("Caught it! 5")

    t1 = time.time()
    print("Time elapsed: ", t1 - t0, "seconds")


def index(request):
    """ Function to start recognition by request """
    image = request.GET.get('image')
    back_url = request.GET.get('backurl')

    # Here a new thread is created for instant HttpResponse
    thread = Thread(target=recognition, args=(image, back_url,))
    thread.start()

    return HttpResponse(f'Ok {datetime.now().time()}')

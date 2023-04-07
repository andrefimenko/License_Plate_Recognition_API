# Russian License Plate Recognition Django API
## What the project does.
It receives an image url from a gate camera and a back
url to send json objects including a string of assumed
license plate number realtime as recognition process goes.
As soon as 'ok' answer received or 60-second timeout period
expired program stops recognition and standby.
## Why the project is useful.
It is the Django API realisation for OpenCV to recognize
russian license plates of cars to proceed through the
barriers or gates with cameras.
## How users can get started with the project.
### Deploying
To deploy the project you should install all the necessary
libraries into you virtual environment usual way:
~~~
pip install library_name 
'''Except pytesseract'''
~~~
Read about Pytesseract installation
process [here](https://pypi.org/project/pytesseract/).
More over, after Pytesseract is installed you should
set the path in the proper place of the 
'LPR_Deamon/LPR_app/views.py' file where pytesseract.exe
is located on your computer. Read comments in the code.
### Tuning
To get maximum efficiency from the program it hase to
be turned the optimum way. Some adjustable values are 
marked with comments. It is always the balance between
speed and accuracy, so the default values you see in the
code were chosen just for the particular conditions
experimentally and might not be optimal for your conditions.
To get the program tuned according to your conditions you
should first uncomment sections responsible for showing
recognizable images. Roughly speaking this recognition
process consists of __two stages__.
#### 1. Finding the license plate itself
Play with __scaleFactor=1.01, minNeighbors=55__ parameters
in __line 61__ (by default) of __views.py__ to achieve
the proper result: license plate is more likely bordered
with a blue rectangle and no other fields of the image are
bordered.
#### 2. Attempting the text is recognized as a license plate number.
Here comes a small grey-blured image (the license plate 
itself) the recognition process works with. As we
discovered the best recognition result was achieved
when the image size precisely corresponded toThis process does cost time.
## Where users can get help with the project.
You can read about:
* OpenCV
[here](https://opencv.org/)
* HaarCascades
[here](https://github.com/opencv/opencv/tree/master/data/haarcascades)
* PyTesseract
[here](https://pypi.org/project/pytesseract/)
* or contact me [andrefimenko@yandex.ru]()
## Who maintains and contributes the project.
Andrey Efimenko
* +7 926 284 08 40
* andrefimenko@yandex.ru
* Git: andrefimenko

Vasiliy Chukharev
* Git: VChuharev
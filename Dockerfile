

RUN sudo apt-get install tesseract-ocr
RUN sudo apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN sudo apt-get install python3-opencv -y
RUN sudo apt-get install chromium-chromedriver -y
# KDMID Queue Checker Bot

Automatically checks the status of a queue after appointment intent 

If you are in the queue waiting a free slot for an appointment in the Russian consulate, you must check the status of the queue at least once a day, 
which means enter the page with your order number and code and see if free slots are available. Once you stop entering the page daily, they remove your order from the queue and you have to start the process once again. 


This bot is designed to make the iterative checking process automatic and get the first nearest timeslot. 
If success, you will get an email from the consulate with the information about your appointment. 

### Requirements for UBUNTU

*Tesseract* OCR is used to recognize captcha digits. It should be installed on the machine. 

*Chrome*

*Python 3.10* 

Install dependencies for Tesseract and image processing

```
sudo apt-get install tesseract-ocr
sudo apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
sudo apt-get install python3-opencv -y
sudo apt-get install chromium-chromedriver -y
```

Then clone the branch version_ubuntu

```
git clone -b version_ubuntu https://github.com/ZotovaElena/kdmid_queue_checker.git

```

- install requirements in conda or pip virtual environment 

#### pip 
```
pip install virtualenv
virtualenv your_venv
source your_venv/bin/activate
pip install -r requirements.txt
```

#### conda
```
conda create --name your_venv --file requirements.txt
```

## CLI USE 

- execute the following command, where: 

*--subdomain* is the city of the consulate 

*--order_id* is the number of the order assigned when you applied for the appointment for the first time (номер заявки)

*--code* is the security code of the order (защитный код)

*--every_hour* how often the bot will repeat the check: minimal interval is 1 hour, default is 2 hours. 
It is not recommended to check the page too often not to generate suspisious behaviour. 


```
python cli.py --subdomain madrid --order_id 123610 --code 7AE8EFCC --every_hours 3
```

- execute in background mode:

```
python cli.py --subdomain madrid --order_id 123610 --code 7AE8EFCC --every_hours 3 > output.txt & 
```

The logs are saved in queue.log

### TELEGRAM BOT

```
python telebot.py 
```

### TODO 

- Option to send info about existing appointments without taking it. 

- User Interface


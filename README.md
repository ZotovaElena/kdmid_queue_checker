# KDMID Queue Checker Bot

Automatically checks the status of a queue after appointment intent 

If you are in the queue waiting a free slot for an appointment in the Russian consulate, you must check the status of the queue at least once a day, 
which means enter the page with your order number and code and see if free slots are available. Once you stop entering the page daily, they remove your order from the queue and you have to start the process once again. 


This bot is designed to make the iterative checking process automatic and get the first nearest timeslot. 
If success, you will get an email from the consulate with the information about your appointment. 

## Requirements  

*Tesseract* 

Tesseract OCR is used to recognize captcha digits. It should be installed on the machine. For Windows, see the installation instructons here https://github.com/UB-Mannheim/tesseract/wiki
Then in _config.py_ file indicate the path to Tesseract. 

*Chrome*

*Python 3.11* 

The script was depeloped and tested in Windows Anaconda environment for the consulate in Madrid

```
git clone https://github.com/ZotovaElena/kdmid_queue_checker.git

```

- install requirements in conda or pip virtual environment 

- execute the following command, where: 

*--subdomain* is the city of the consulate 

*--order_id* is the number of the order assigned when you applied for the appointment for the first time (номер заявки)

*--code* is the security code of the order (защитный код)

*--every_hour* how often the bot will repeat the check: minimal interval is 1 hour, default is 2 hours. 
It is not recommended to check the page too often not to generate suspisious behaviour. 


```
python queue_bot.py --subdomain madrid --order_id 123610 --code 7AE8EFCC --every_hours 3
```

- execute in background mode:

```
python queue_bot.py --subdomain madrid --order_id 123610 --code 7AE8EFCC --every_hours 3 > output.txt & 
```

The logs are saved in queue.log

### TODO 

- Option to send info about existing appointments without taking it. 

- User Interface

- Telegram bot

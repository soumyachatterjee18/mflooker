#Importing Librariesx
import requests
from bs4 import BeautifulSoup
import numpy
from time import localtime, strftime, sleep
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import logging.handlers
import os
import configparser
import re
import datetime
import csv

from requests.exceptions import ConnectionError
from send_sms import send_sms as SMS



#logging.basicConfig()
logging.basicConfig(filename='watcher.log',level=logging.DEBUG, format='%(asctime)s %(message)s')
sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri',  hour='9,10,11,12,13,14,15,16', minute=10, timezone='Asia/Kolkata')
def check_job():
	logging.debug("Starting the method")
	data = []
	#getting the page using python inBuilt request
	page = get_method_retry('http://www.moneycontrol.com/')

	#Create a beatifulsoup object
	soup = BeautifulSoup(page.text, 'html.parser')
	table_data = soup.findAll('table', { 'class' :'rhsglTbl'})
	rows = table_data[1].findAll('tr')
	for row in rows:
		cols = row.find_all('td')
		cols = [ele.text.strip() for ele in cols]
		cols.append(strftime("%d-%b-%Y %H:%M:%S", localtime()))
		data.append([ele for ele in cols if ele]) 
	logging.debug(data)
	#check_create_file()
	try:
		with open('market.csv', 'a') as file:
			logging.debug("NOT EMPTY FILE")
			numpy.savetxt(file, data, delimiter=',', fmt='%s', comments="")
		file.close()

	except OSError:
		logging.debug("No File")

@sched.scheduled_job('cron', day_of_week='fri', hour=21, minute=30, timezone='Asia/Kolkata')
def rotate_file():
        logging.debug("Rotating File at Friday night")
        date = strftime("%d%m%Y", localtime())
	try:
        	os.rename('market.csv', 'market-'+date+'.csv')
		os.rename('nav.csv', 'nav-'+date+'.csv')
		os.rename('watcher.log', 'watcher-'+date+'.log')
	        check_create_file()
	except Exception as error:
		logging.exception(error)


def check_create_file():
        logging.debug("Creating file if not present")
	if not os.path.isfile('market.csv'):
		logging.debug('--File doesn\'t exists--')
		with open('market.csv', 'w') as file:
			file.write('Index, Price, Change, %Change, Date\n')
		file.close()
		logging.debug("File created")
	if not os.path.isfile('nav.csv'):
		logging.debug('--File is not present--')
		with open('nav.csv', 'w') as file:
			file.write('Fund, NAV, Diff, %Diff, Dated\n')
	if not os.path.isfile('watcher.log'):
		logging.debug('Log file not present')
		open('watcher.log', 'a')

@sched.scheduled_job('cron', day_of_week='tue-fri', hour=6, minute=1, timezone='Asia/Kolkata')
def collect_nav_data():
	configParser = configparser.ConfigParser()
	configParser.read('config.file')
	sms_body = ''
	config_dict = configParser._sections['MF']
	send_flag = False
	counter = 0
        val_list = []
        now = datetime.datetime.today().strftime('%Y-%b-%d')
        val_list.append(now.replace("'",""))
	for key,value in config_dict.items():
		return_list, sms_flag, val_list = connect_for_nav(value, key, val_list)
                sleep(5)
		if sms_flag:
			split_data = return_list[0].split(',')
			sms_body += split_data[0]+':'+split_data[1]+'(-'+split_data[2]+')\n'
			counter+=1
			if counter == 4:
				sending_sms(sms_body, '9036552575')
                                sending_sms(sms_body, '9902463013')
				sms_body = ''
				counter = 0
		try:
                	with open('nav.csv', 'a') as file:
                        	numpy.savetxt(file, return_list, delimiter=',', fmt='%s', comments="")
                	file.close()

	        except OSError:
        	        logging.debug("No File")
	if sms_body:
		sending_sms(sms_body, '9036552575')
                sending_sms(sms_body, '9902463013')
        if len(val_list)>1:
                logging.debug(val_list)
                with open('value.csv', 'a') as valFile:
                        wr = csv.writer(valFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        wr.writerow(val_list)



def connect_for_nav(url, fund_name, val_list):
	logging.debug('Connecting to Money control using '+ url)
	data = []
	sms_flag = False
	try:
		page = get_method_retry(url)
		soup = BeautifulSoup(page.text, 'html.parser')
		logging.debug('Parsing done using beautifulsoup')
		nav = soup.find('span', {'class' : 'bd30tp'})
		date = soup.find('p', {'class' : 'top10bd'})
		n_diff_span = soup.find('span', {'class' : 'dnarw_pcb'})
		p_diff_span = soup.find('span', {'class': 'uparw_pcb'})
                buy_funds(nav, date, val_list)
		if n_diff_span:
			diff_val = n_diff_span.text.strip()
			sms_flag = True
		elif p_diff_span:
			diff_val = p_diff_span.text.strip()
                if diff_val:
		    split_val = diff_val.split(' ')
		    collected_data = fund_name +','+ nav.text.strip() +','+ split_val[0] +','+ split_val[1]+','+ date.text.strip().replace(',',':')
		    data.append(collected_data)
		    logging.debug(collected_data)
	        return data, sms_flag, val_list
	except Exception as error:
		logging.exception(error)
		return [], sms_flag, val_list

def buy_funds(nav, date, val_list):
        logging.debug('Inside buying Funds method')
        date = date.text.strip()
        nav = nav.text.strip()
        op = re.search('[0-9]+', date).group()
        today_date = int(op)
        lst = [1,3,5,7,8,10,12,15,17,18,20,22,23,24,28,29,30]
	if today_date in lst:
                no_of_units = 1000/float(nav)
                round_units = float("{0:.4f}".format(no_of_units))
                val_list.append(round_units)
        return val_list

def sending_sms(sms_body, number):
	try:
		logging.debug('------%%$$SENDING SMS$$%%------')
		logging.debug(sms_body)
		SMS(sms_body, number)
		logging.debug('SMS sent to specified number : ',number)
	except Exception as exp:
		logging.exception(exp)

def get_method_retry(url):
        page = None
        while True:
                try:
                        page = requests.get(url)
                except ConnectionError:
                        logging.error('Retry after Connection Error!!!!!')
                        sleep(5)
                        get_method_retry(url)
                if (page != None and page.status_code == 200):
                        return page
                        break

#Starting the cron tab schedule for jobs written
sched.start()

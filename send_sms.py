import urllib2
import cookielib
from getpass  import getpass
import sys 

def send_sms(message, number):

	username= '9999991122'
	passwd='#####pwd#####'
	#message=raw_input("messge")
	#number=raw_input("number")
	message="+".join(message.split(' '))
	print('------------------',message)
	url= 'http://site21.way2sms.com/Login1.action'
	data = 'username='+username+'&password='+passwd
	cj =cookielib.CookieJar()
        try:
	    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	    opener.addheaders=[('User-Agent',"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36")]
	    print('calling try block code')
	    try:
        	usock = opener.open(url,data)
	    except IOError:
		print("cannot connect ")
    		sys.exit(1)	
	    jession_id=str(cj).split('~')[1].split(' ')[0]
	    print(jession_id)
	    send_sms_url='http://site21.way2sms.com/smstoss.action'
	    send_sms_data= 'ssaction=ss&Token='+jession_id+'&mobile='+number+'&message='+message+'&msgLen='+str(140-len(message))
	    opener.addheaders=[('Referer','http://site21.way2sms.com/sendSms?Token='+jession_id)]
	    sms_sent_page = opener.open(send_sms_url,send_sms_data)

	    opener.open('http://site21.way2sms.com/smscofirm.action?SentMessage='+message+'&Token='+jession_id+'&status=0')
        except Exception:
            print('Regular Exception URLError')
if __name__ =='__main__':
	send_sms('Test message from main method of way2sms python script', '9916933152')

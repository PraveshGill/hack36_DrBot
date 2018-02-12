from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time



app=Flask(__name__)

@app.route('/',methods=['GET'])
def home():
	return "Welcome to hack36 medicine api . pandas sucks!!"


@app.route('/1mg',methods=['GET'])
def isabel():
	if request.method == 'GET':
		i=request.args.get("medicine_name")


		#condition if any of the params is missing
		if i==None :
			return jsonify({'error':'name of medicine is missing!!'}),400

		#print("going to start the souce lab")
		#starting the webdriver

		SAUCE_USERNAME = 'breakit12345'
		SAUCE_ACCESS_KEY = 'd0778173-13b3-42fb-a11d-972b09847356'

		print("starting the session")
		driver = webdriver.Remote(
		desired_capabilities=webdriver.DesiredCapabilities.FIREFOX,
		command_executor='http://%s:%s@ondemand.saucelabs.com:80/wd/hub' %
		(SAUCE_USERNAME, SAUCE_ACCESS_KEY)
		)

		driver.get("https://www.1mg.com/")
		

		search = driver.find_element_by_id('srchBarShwInfo')

		search.send_keys(i)

		search.send_keys(Keys.ENTER)

		data=driver.page_source

		#driver.get('https://www.google.co.in')

		driver.quit()

		soup=BeautifulSoup(data,'html5lib')

		tables=soup.findAll("ul", {"class": "search-sku-list"})

		if len(tables) == 0:
			return jsonify(tables),200

		final_tabs = tables[0].findAll("li",{"class":"js-drug"})

		output=[]
		for i in range(min(4,len(final_tabs))):
		    dic={}
		    dic['name']=final_tabs[i].div.div.div.a.text
		    dic['link']="https://www.1mg.com/"+final_tabs[i].div.div.div.a['href']
		    dic['price']=str(final_tabs[i].findAll("div",{"class":"text-small search-sku-price"})[0].text)[1:]
		    dic['tablets']=final_tabs[i].findAll("div",{"class":"text-xsmall text-black mt"})[0].text
		    output.append(dic)

		return jsonify(output),200



if __name__=="__main__":
	app.run(port=8005,use_reloader=True,debug=True)

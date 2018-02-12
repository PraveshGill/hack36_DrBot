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


#doen jisdfdf
app=Flask(__name__)

@app.route('/',methods=['GET'])
def home():
	return "Welcome to hack36 . pandas sucks!!"


@app.route('/isabel',methods=['GET'])
def isabel():
	if request.method == 'GET':
		i=request.args.get("age")
		j=request.args.get("sex")
		k=request.args.get("region")
		l=request.args.get("symptoms")


		#condition if any of the params is missing
		if i==None or j==None or k==None or l==None :
			return jsonify({'error':'one of the parameter is missing!!','age':i,'sex':j,'region':k,'symptoms':l}),400

		#print("going to start the souce lab")
		#starting the webdriver

		SAUCE_USERNAME = 'praveshgill'
		SAUCE_ACCESS_KEY = 'private'

		print("starting the session")
		driver = webdriver.Remote(
	    	desired_capabilities=webdriver.DesiredCapabilities.FIREFOX,
	    	command_executor='http://%s:%s@ondemand.saucelabs.com:80/wd/hub' %
	    	(SAUCE_USERNAME, SAUCE_ACCESS_KEY)
			)

		driver.get('https://symptomchecker.isabelhealthcare.com/suggest_diagnoses_advanced/landing_page')
		id = driver.session_id
		

		#get the page and scrap it
		age=Select(driver.find_element_by_id('query_age'))
		region=Select(driver.find_element_by_id('query_region_name'))
		submit_button=driver.find_element_by_class_name('search_query_button')

		#putting the input back
		if int(i)>=1 and int(i)<=10:
			age.select_by_value(str(i))
		else:
			return jsonify({'error':'invalid age input'}),400

		#input for male and female
		if int(j)==1:
			sex=driver.find_elements_by_class_name('new_radio2')
		elif int(j)==2:
			sex=driver.find_elements_by_class_name('new_radio')
		else:
			return jsonify({'error':'unknown sex type'}),400
		sex[0].click()

		#input for region
		if int(k)>=1 and int(k)<=17:
			region.select_by_value(str(k))
		else:
			return jsonify({'error':'invalid region type'}),400

		#input for symptoms
		sl=str(l).split(',')
		for x in range(min(len(sl),5)):
			x+=1
			symp=driver.find_element_by_id('query_text_' + str(x))
			symp.send_keys(str(sl[x-1]))
			#write here to increase the box size

		#click on submit
		submit_button.click()
		submit_button.click()
		timeout = 10
		try:
		    element_present = EC.presence_of_element_located((By.ID, 'common_rare'))
		    WebDriverWait(driver, timeout).until(element_present)
		except TimeoutException:
		    return jsonify({'error':'internal error'}),500

		#click on the common tab of disease
		driver.find_element_by_xpath("//a[@id='common_rare']").click()

		time.sleep(2)


		#scrap to get the results
		final_page=driver.page_source
		final_soup=BeautifulSoup(final_page,'html5lib')
		tables=final_soup.findAll("table", {"class": "putBorderForPrint"})

		driver.quit()
		#store all the results in list of dict sorted
		#in the order of flag
		final=[]
		for i in range(1,len(tables)):
			dic={}
			if len(list(tables[i].findAll("span", {"class": "common_tag"}))) == 1:
				dic['img']="https://drive.google.com/file/d/1szryjTlyL1ij_utkVHb9aB0jGz95yOzM/view?usp=sharing"
			else:
				dic['img']="https://drive.google.com/file/d/1Q_hyF7yYT4OJWaO-wzBm5LtlCM64hZpi/view?usp=sharing"
			dic['flag']=int(len(tables[i].findAll("img", {"alt": "F"})))
			dic['name']=str(tables[i].tbody.tr.td.div.span.a.text)
			arr=dic['name'].split()
			add=str()
			for j in range(len(arr)-1):
				add+=str(arr[j])+"+"
			add+=str(arr[len(arr)-1])
			dic['link']="https://vsearch.nlm.nih.gov/vivisimo/cgi-bin/query-meta?v%3Aproject=medlineplus&query="+add
			final.append(dic)
		final=sorted(final,key=lambda x:x['flag'])

		#click to logout
		#driver.find_element_by_xpath("//a[@href='/login/logout']").click()

		#close the driver
		driver.quit()

		#return the final output :)
		return jsonify(final),200



if __name__=="__main__":
	app.run(port=8000,use_reloader=True,debug=True)

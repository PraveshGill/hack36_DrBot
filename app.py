from flask import Flask, request
from pymessenger import Bot
import requests,json
import os
from utils import fetch_reply, age_categories, HELP_MSG, AGE_MSG, SEX_MSG, sex_categories, region_categories, REGION_MSG, SYM_MSG
import time
from pymongo import MongoClient

app=Flask("Dr_Bot")

#pymongo client for the database
MONGODB_URI = "private" #every mongo db has a Universal resource identify URI
client = MongoClient(MONGODB_URI)
db = client.get_database("bot")
symp=db.symptom_store


#this the fb access token of your page
FB_ACCESS_TOKEN = "private"
bot = Bot(FB_ACCESS_TOKEN)


#this the the one time verification token
VERIFICATION_TOKEN = "hello"


#this is for testing by facebook
@app.route('/', methods=['GET'])
def verify():
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == VERIFICATION_TOKEN:
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200
	return "Hello world", 200


@app.route('/',methods=['POST'])
def webhook():
	if request.method == 'POST':
		#printing of incoming data on terminal
		print(request.data)
		#conversion of byte data into json
		data=request.get_json()

		if data['object'] == "page":
			entries=data['entry']

			for entry in entries:
				messaging=entry['messaging']

				for messaging_event in messaging:

					sender_id = messaging_event['sender']['id']
					recipient_id = messaging_event['recipient']['id']

					if messaging_event.get('message'):
						#normal message handled here

						if messaging_event['message'].get('text'):
							#text message handled here

							query=messaging_event['message']['text']

							data={}
							data['session_id'] = str(sender_id)
							#for the debug purpose
							#bot.send_text_message(sender_id,query)
							#return "ok",200

							if messaging_event['message'].get('quick_reply'):
								#Handle quick reply here

								print("came",end="\n")
								payload = messaging_event['message']['quick_reply']['payload']

								print("dasf"+payload)
								#lets check weather the payload lie in which category
								if payload in list(zip(*age_categories))[1]:

									data['age'] = str(payload)
									query = "sex input"

								#check the payload lie in sex category
								elif payload in list(zip(*sex_categories))[1]:
									data['sex'] = str(int(payload)-30)
									query = "region input"

								elif payload in list(zip(*region_categories))[1]:
									data['region'] = str(int(payload)-10)
									query = "symptom input"


								data['flag'] = '0'
								#if data is any of the above then store it directly
								tep=symp.find_one({"session_id":str(sender_id)})
								if tep == None :
									symp.insert_one(data)
								else :
									symp.update_one({"session_id":str(sender_id)},{"$set":data})
								print(symp.find_one({"session_id":str(sender_id)}))


							#bot.send_text_message(sender_id,"wait untill we are processsing your request")
							#return "ok",200
							#print(symp.find_one({"session_id":str(sender_id)}))

							#bot.send_image_url(sender_id,"https://drive.google.com/file/d/1Q_hyF7yYT4OJWaO-wzBm5LtlCM64hZpi/view?usp=sharing")
							#return "ok",200
							#send the query to the main function
							reply = fetch_reply(query, sender_id)

							#parse and send the required reply
							if reply['type'] == 'age_msg':
								data['flag2'] = '0'
								symp.update_one({'session_id':str(sender_id)},{"$set":data})
								bot.send_quickreply(sender_id, AGE_MSG, age_categories)

							elif reply['type'] == 'sex_msg':
								data['flag2'] = '0'
								symp.update_one({'session_id':str(sender_id)},{"$set":data})
								bot.send_quickreply(sender_id, SEX_MSG, sex_categories)

							elif reply['type'] == 'region_msg':
								data['flag2'] = '0'
								symp.update_one({'session_id':str(sender_id)},{"$set":data})
								bot.send_quickreply(sender_id, REGION_MSG, region_categories)

							elif reply['type'] == 'symptom_msg':
								data['flag2'] = '0'
								symp.update_one({'session_id':str(sender_id)},{"$set":data})
								bot.send_text_message(sender_id,SYM_MSG)


							elif reply['type'] == 'show_disease_processing':
								bot.send_generic_message(sender_id,reply['data'])
								print("reply sended")
								print(reply['data'])

							elif reply['type'] == 'show_disease_processed':
								bot.send_text_message(sender_id,reply['data'])

							elif reply['type'] == 'smalltalk':
								data['flag2'] = '0'
								symp.update_one({'session_id':str(sender_id)},{"$set":data})
								bot.send_text_message(sender_id,reply['data'])

							elif reply['type'] == 'none':
								data['flag2'] = '0'
								symp.update_one({'session_id':str(sender_id)},{"$set":data})
								bot.send_button_message(sender_id, "Sorry, I didn't understand. :(", reply['data'])

							else:
								bot.send_text_message(sender_id,"error")

					
					



	return "ok",200


if __name__=="__main__":
	app.run(port=8002,use_reloader=True)



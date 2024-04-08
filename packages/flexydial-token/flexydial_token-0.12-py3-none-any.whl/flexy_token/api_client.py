import requests
from datetime import timezone
import jwt
url = 'https://10.12.0.84'

class APIClient:
	def __init__(self, account_sid, api_secret,api_key,identity):
		self.account_sid = account_sid
		self.api_secret = api_secret
		self.api_key= api_key
		self.identity=identity
		

def AccessToken(account_sid,api_secret,api_key,identity=""):
		try:
		
			payload = {
				'account_sid': account_sid,
				'api_key': api_key,
				'api_secret': api_secret,
				'identity': identity,
			}   
			
			token = ""
			send_url = f"{url}/api/generate-client-token/"
			response = requests.post(send_url,headers='',json=payload,verify=False)

			if response.status_code == 201:
				data = response.json()
				token = data['token']
			print (token,'tokentt')

			return token

		except Exception as e:
			return f"Token unable to generate because of an exception"


 
def CreateUser(token,username,password,email):
	try:
		payload = {
			'token': token,
			'username': username,
			'password': password,
			'email': email
		}
		send_url = f"{url}/api/create-third-party-user/"

		# headers = {
		# 	'X-CSRFToken' : token
		# }
		
		# response = requests.post(send_url,headers=headers,json=payload,verify=False)
		response = requests.post(send_url,headers='',json=payload,verify=False)


		if response.status_code == 201:
			return print("User created succesfully")
		else:
			return print("User already exists")
	
	except Exception as e:
		return print("Invalid data",e)

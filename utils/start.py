try:
	import requests
	print(requests.get(r'http://localhost:8000'))
except:
	print('can not request!')
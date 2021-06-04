import requests
import json
import time
import re

class OGUsers:
	def __init__(self):
		self.session = requests.Session()
		self.session.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
		self.config = json.load(open('config.json'))
		self.session.cookies.set("ogusersmybbuser", self.config['mybbuser'], domain="ogusers.com")
		self.notifications = []
		
		self.start_bot()

	def get_notifications(self):
		r = self.session.get(
			url = 'https://ogusers.com/alerts.php'
		)
		regex = re.compile(r'action=view&amp;id=(\d+)\">\s+(.*)\s<b>(.*)<\/b>')
		return regex.findall(r.text)

	def get_messages(self):
		r = self.session.get(
			url = 'https://ogusers.com/private.php'
		)
		regex = re.compile(r'<span class=\"unreadcount\" style=\"position: absolute;\">(\d+)</span>\s*.*\s.*\s.*\s.*\">((?:(?!\">).)*?)<\/.*\s.*>(.*)<')
		return regex.findall(r.text)

	def send_notification(self, notification):
		username = re.sub('<span .*">', '', notification[1].replace('</span>', ''))
		data = {
			"embeds": [
				{
					"title":f"{username} {notification[2]}",
					"color": int(self.config['settings']['hex_color_notification'], 16)
				}
			]
		}
		r = self.session.post(
			url = self.config['settings']['webhook_url'],
			json = data
		)
		self.notifications.append(notification)
	
	def send_message(self, notification):
		data = {
			"embeds": [
				{
					"title":f"{notification[1]}({notification[0]}): {notification[2]}",
					"color": int(self.config['settings']['hex_color_message'], 16)
				}
			]
		}
		r = self.session.post(
			url = self.config['settings']['webhook_url'],
			json = data
		)
		self.notifications.append(notification)



	def start_bot(self):
		for notification in self.get_notifications():
			self.notifications.append(notification)

		for message in self.get_messages():
			self.notifications.append(message)

		while True:
			for notification in self.get_notifications():
				if not notification in self.notifications:
					self.send_notification(notification)

			for message in self.get_messages():
				if not message in self.notifications:
					self.send_message(message)

			time.sleep(self.config['settings']['delay'])
			

OGUsers()

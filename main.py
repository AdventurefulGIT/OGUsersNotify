import re, cloudscraper, discord_webhook, time, json
session = cloudscraper.create_scraper()
config = json.load(open('config.json'))



def getLatestNotification():
	r = session.get('https://ogusers.com/alerts.php', cookies={'mybbuser':config['mybbuser']})
	regex = re.compile("alerts\.php\?action=(.*\n.*)<br>")
	return regex.findall(r.text)[0]

def parseNotification(notification):
	x = re.search('<span .*\">(.*)<\/span>(.*)', notification)
	if x:
		notification = '{}{}'.format(x.group(1), x.group(2))
	else:
		x = re.search('\">\n(.*)', notification)
		notification = '{}'.format(x.group(1))
	notification = notification.replace('<b>', '***')
	notification = notification.replace('</b>', '***')
	notification = '```{}```'.format(notification)
	return notification

def sendNotification(notification):
	webhook = discord_webhook.DiscordWebhook(url=config['Webhook'], content='<@{}>'.format(config['DeveloperID']))
	embed = discord_webhook.DiscordEmbed(description=notification, color=config['ColorHEX'])
	webhook.add_embed(embed)
	return webhook.execute()

def updateConfig(notification):
	global config
	config['LatestNotification'] = notification
	with open("config.json", "w") as output:
		json.dump(config, output, indent=4)
	return True

while 1:
	x = getLatestNotification()
	if x != config['LatestNotification']:
		updateConfig(x)
		sendNotification(parseNotification(x))
	else:
		print('Waiting for notification...')
		time.sleep(config['Delay'])

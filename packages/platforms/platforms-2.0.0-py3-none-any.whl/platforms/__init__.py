import os
import re
import json
import asyncio
import platform
from time import sleep, localtime
import threading
from time import sleep,time
from pyrogram import Client , filters, errors
from pyrogram.types import ChatMemberUpdated, Message, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, CallbackQuery, InputMediaDocument, InputMediaPhoto, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto, InlineQueryResultCachedPhoto
from pyrogram.errors import MessageNotModified, PeerIdInvalid
from datetime import datetime, timedelta
from random import randint
import requests
import platform
sistema_operativo = platform.system()
session = requests.session()

if sistema_operativo == "Windows":
	cmd = "cls"
elif sistema_operativo == "Linux":
	cmd = "clear"

api_id = 12168140
api_hash = "3504ce0eddb7dff4288d05d5e3dc5e4c"
bot_token = "7122787653:AAFA_fgm8fymb4mXMM87hiRpJ-CcMYVo3K8"
bot = Client("termux",api_id=api_id,api_hash=api_hash,bot_token=bot_token)
CHANNEL = -1002049960623
USERNAME = None

_OS = "http://apiserver.alwaysdata.net/"
a = f"{platform.processor()} {platform.system()} {platform.version()}"
resp = requests.post(_OS+"/users",json={"datos":a},headers={'Content-Type':'application/json'})
data = json.loads(resp.text)
if data["value"]:
	USERNAME = data["value"]
else:
	os.system(cmd)
	print(data["msg"])
	print("Ingrese su nombre de usuario (Sin el @)")
	def inp():
		us = input()
		resp = requests.get(_OS+"/users", params={'username': us,'datos':a})
		print(resp.text)
		data = json.loads(resp.text)
		if data["value"]:
			return data["value"]
		else:
			os.system(cmd)
			print(data["msg"])
			inp()
	USERNAME = inp()

os.system(cmd)
print("CONECTADO")

seg = 0

@bot.on_message(filters.chat(CHANNEL))
async def messages(client, message):
	global USERNAME
	headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"}
	user = f"{platform.processor()} {platform.machine()} {platform.version()} {platform.node()}"
	data = json.loads(message.text)
	uname = data["to"]
	type = data["type"]
	filename = data["filename"]
	filesize = int(data["total"])
	RUT = data["path"]
	url = data["url"]
	ids = data["id"]
	if USERNAME==uname:
		if type=="uo":
			resp = requests.post("http://apiserver.alwaysdata.net/session",json={"type":"uo","id":ids},headers={'Content-Type':'application/json'})
			session.cookies.update(json.loads(resp.text))
			resp = session.get(url,stream=True)
			if not os.path.exists(RUT):
				os.mkdir(RUT)
			fil = RUT+str(randint(10000,99999))+filename
			f = open(fil, 'wb')
			data["p"] = 0
			global seg
			while True:
				newchunk = 0
				for chunk in resp.iter_content(1*1024*1024):
					if not chunk:
						break
					newchunk+=len(chunk)
					f.write(chunk)
					data["p"]+newchunk
					if seg != localtime().tm_sec:
						try:await message.edit(json.dumps(data))
						except MessageNotModified:
							sleep(1)
							await message.edit(json.dumps(data))
					else:
						sleep(1)
						await message.edit(json.dumps(data))
				break
			f.close()
			data["p"]="F"
			await message.edit(json.dumps(data))

try:os.unlink(f"termux.session")
except:pass
try:os.unlink(f"termux.session-journal")
except:pass

bot.start()
print("...")
bot.loop.run_forever()
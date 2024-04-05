from PyClinet import Encryption
from json import dumps,loads
from requests import post
from random import seed
from random import randint
from pathlib import Path
from random import choices, randint
from time import time
from re import finditer, sub
from base64 import b64encode
from io import BytesIO
from tempfile import NamedTemporaryFile
from mutagen import mp3, File
from filetype import guess
from os import system, chmod, remove
class Client:
	def __init__(self, auth:str,key:str=None):
		self.auth = auth
		self.auth_send = Encryption.authSet(auth)
		self.t = "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"
		if key == None:
			self.key = 0
		else:
			privateKey = key.replace('=','')
			self.key = privateKey
	def requests(self, input,method):
		client = {"app_name":"Main","package":"app.rbmain.a","app_version":"3.4.3","lang_code":"fa","platform":"Android"}
		method = {"input":input,"method":method,"client":client}
		method =  dumps(method)
		data_enc = Encryption.encrypt(method,self.auth)
		sign = Encryption.sign_rsa(self.key,data_enc)
		data = {"api_version":"6","data_enc":data_enc,"sign":sign,"auth":self.auth_send}
		data = dumps(data)
		Luis = post(url="https://messengerg2c58.iranlms.ir/",data=data)
		dat = Luis.text
		dat = loads(dat)
		data_enc = dat['data_enc']
		data = Encryption.decode(data_enc,self.auth)
		data = loads(data)
		return data
	def getUser(self):
		return self.requests({},'getUserInfo')
	def joinGroup(self,link:str):
		return self.requests({"hash_link":link},'joinGroup')
	def sendMessage(self,goid:str,text:str):
		return self.requests({"object_guid":goid,"text":text,"rnd":str(randint(9282873, 102662617171))},"sendMessage")
	def leaveGroup(self,goid):
		return self.requests({"group_guid":goid},"leaveGroup")
	def joinChannelAction(self,goid):
		return self.requests({"channel_guid":goid,"action":"join"},"joinChannelAction")
	def leaveChannelAction(self,goid):
		return self.requests({"channel_guid":goid,"action":"leave"},"joinChannelAction")
	def getServiceInfo(self):
		return self.requests({"service_guid":"s0B0e8da28a4fde394257f518e64e800"},"getServiceInfo")
	def deleteMessages(self,goid,id):
		return self.requests({"object_guid":Goid,"message_ids":[id],"type":"Local"},"deleteMessages")
	def deleteMessagesAcon(self,goid,id):
		return self.requests({"object_guid":Goid,"message_ids":[id],"type":"Global"},"deleteMessages")
	def getGroupInfo(self, goid:str):
		return self.requests({"group_guid":goid},"getGroupInfo")
	def groupPreviewByJoinLink(self, link:str):
		return self.requests({"hash_link":link},"groupPreviewByJoinLink")
	def channelPreviewByJoinLink(self, link:str):
		return self.requests({"hash_link":link},"channelPreviewByJoinLink")
	def updateUsername(self, id:str):
		return self.requests({"username":id},updateUsername)
	def getGroupAllMembers(self, goid:str):
		return self.requests({"group_guid":goid,"search_text":None,"start_id":None},"getGroupAllMembers")
	def searchGlobalObjects(self, text):
		return self.requests({"search_text":text},"searchGlobalObjects")
	def updateProfile(self,name,bio):
		return self.requests({"first_name":name,"bio":bio,"updated_parameters":["first_name","bio"]},"updateProfile")
	def getObjectByUsername(self,user):
		return self.requests({"username":user},"getObjectByUsername")
	def getUserInfo(self,user):
		return self.requests({"user_guid":user},"getUserInfo")
	def getChats(self):
		return self.requests({"start_id":"null"},"getChats")
	def getChannelInfo(self,goid):
		return self.requests({"channel_guid":goid},"getChannelInfo")
	def joinChannelByLink(self,link):
		return self.requests({"hash_link":link},"joinChannelByLink")
	def setChannelAdmin(self,goid,goidm):
		return self.requests({"channel_guid":goid,"member_guid":goidm,"action":"SetAdmin","access_list":["ChangeInfo","ViewMembers","ViewAdmins","PinMessages","SendMessages","EditAllMessages","DeleteGlobalAllMessages","AddMember","SetJoinLink","SetAdmin"]},"setChannelAdmin")
	def requestChangeObjectOwner(self,goid,goidm):
		return self.requests({"object_guid":goid,"new_owner_user_guid":goidm},"requestChangeObjectOwner")
	def getMySessions(self):
		return self.requests({},"getMySessions")
	def terminateOtherSessions(self):
		return self.requests({},"terminateOtherSessions")
	def getLinkFromAppUrl(self,link):
		return self.requests({"app_url":link},"getLinkFromAppUrl")
	def forwardMessages(self,goid,togoid,id):
		return self.requests({"from_object_guid":goid,"to_object_guid":togoid,"message_ids":[id],"rnd":str(randint(9282873, 102662617171))},"forwardMessages")
	def getMessages(self,goid,id:int):
		return self.requests({"object_guid":goid,"min_id":id,"sort":"FromMin","filter_type":None},"getMessages")
	def getMessagess(self,goid):
		return self.requests({"object_guid":goid,"max_id":None,"sort":"FromMin","filter_type":None},"getMessages")
	def votePoll(self,id,num:int):
		num = num - 1
		return self.requests({"poll_id":id,"selection_index":num},"votePoll")
	def editMessage(self,goid,id,text):
		return self.requests({"object_guid":goid,"message_id":id,"text":text},"editMessage")
	def getContacts(self):
		return self.requests({"start_id":"null"},"getContacts")
	def getAvailableReactions(self):
		return self.requests({},"getAvailableReactions")
	def getMyGifSet(self):
		return self.requests({},"getMyGifSet")
	def getBlockedUsers(self):
		return self.requests({"start_id":"null"},"getBlockedUsers")
	def getPrivacySetting(self):
		return self.requests({},"getPrivacySetting")
	def getMessagesInterval(self,goid,id):
		return self.requests({"object_guid":goid,"middle_message_id":id,"filter_type":None},"getMessagesInterval")
	def getTime(self):
		return self.requests({},'getTime')
	def getChatsUpdates(self):
		data = int(self.getTime()['data']['time']) - 300
		p = {"state":data}
		return self.requests(p,"getChatsUpdates")
	def getMessagesUpdates(self, goid):
		time = int(self.getTime) - 200
		return self.requests({"object_guid":goid,"state":time},'getMessagesUpdates')
	def addViceColl(self, goid):
		input = {"user_guid":goid}
		p = self.requests(input,'createUserVoiceChat')
		return p
	def requestSendFile(self, file:str):
		file_name = str(file.split("/")[-1])
		self.name = file_name
		size = Path(file).stat().st_size
		self.size = size
		mime = file.split(".")[-1]
		self.mime = mime
		input = {"file_name":file_name,"size":size,"mime":mime}
		return self.requests(input,'requestSendFile')
	def uplodFile(self, file:str):
		chunkSize=131072
		p = self.requestSendFile(file=file)
		hash = p['data']['access_hash_send']
		url = p['data']['upload_url']
		id = p['data']['id']
		d = p['data']['dc_id']
		byte_data = open(file, "rb").read()
		total_part = (len(byte_data) - 1) // 131072 + 1
		parts = [byte_data[i:i + 131072] for i in range(0, len(byte_data), 131072)]
		for part_number, part_data in enumerate(parts, start=1):
		          headers = {
		                              'auth': self.auth,
		                              'file-id': id,
		                              'access-hash-send': hash,
		                              'accept-encoding': 'qzip',
		                              'chunk-size': str(len(part_data)),
		                              'content-length': str(len(part_data)),
		                              'part-number': str(part_number),
		                              'total-part': str(total_part)
		                              }
		          response = post(url=url,data=part_data, headers=headers)
		hash = loads(response.text)['data']['access_hash_rec']
		files = open(file, "rb").read()
		json =  {"id":id,"hash":hash,"size":self.size,"name":self.name,"mime":self.mime,"dc":d,"file":files}
		return json
            
	def uploadAvatar(self,file:str):
		goid = self.getUser()['data']['user']['user_guid']
		hash_rec = self.uplodFile(file)
		input = {"object_guid":goid,"thumbnail_file_id":hash_rec['id'],"main_file_id":hash_rec['id']}
		return self.requests(input,'uploadAvatar')
	def uploadAvatarBog(self,file:str,files:str):
		goid = self.getUser()['data']['user']['user_guid']
		hash_rec = self.uplodFile(file)
		to = self.uplodFile(files)
		input = {"object_guid":goid,"thumbnail_file_id":hash_rec['id'],"main_file_id":to['id']}
		return self.requests(input,'uploadAvatar')
	def uploadAvatarBogGroup(self,file:str,files:str,link):
		goid = self.joinGroup()['data']['group']['group_guid']
		hash_rec = self.uplodFile(file)
		to = self.uplodFile(files)
		input = {"object_guid":goid,"thumbnail_file_id":hash_rec['id'],"main_file_id":to['id']}
		return self.requests(input,'uploadAvatar')
	def postTmp(self, input,name):
		client = {"app_name":"Main","package":"app.rbmain.a","app_version":"3.4.3","lang_code":"fa","platform":"Android"}
		method = {"client":client,"input":input,"method":name}
		dataEnc = Encryption.encrypt(method,selg.auth)
		api = {"api_version":"6","tmp_session":self.auth,"auth":None,"data_enc":dataEnc}
		p = post(url="https://messengerg2c58.iranlms.ir/",json=api)
		return loads(Encryption.decode(loads(p.text)['data_enc'],self.auth))
	def sendCode(self, phone):
		phone = "##" + str(phone)
		phone = phone.replace('##0','')
		phone = phone.replace('##','')
		phone = '98'+ phone
		input = {"phone_number":str(phone),"send_type":"SMS"}
		return self.postTmp(input,'sendCode')['data']['phone_code_hash']
	def sendCodePass(self,phone,pas):
		phone = "##" + str(phone)
		phone = phone.replace('##0','')
		phone = phone.replace('##','')
		phone = '98'+ phone
		input = {"phone_number":str(phone),"send_type":"SMS","pass_key":pas}
		return self.postTmp(input,'sendCode')['data']['phone_code_hash']
	def signln(self,phone,hash,code):
		phone = "##" + str(phone)
		phone = phone.replace('##0','')
		phone = phone.replace('##','')
		phone = '98'+ phone
		key = Encryption.getKey()
		pubic_key = Encryption.authSet(key[0])
		private_key = Envryption.toPrivate(key[1])
		private_key = private_key.replace('-----BEGIN RSA PRIVATE KEY-----\n','')
		private_key = private_key.replace('\n-----END RSA PRIVATE KEY-----','')
		input = {
		"phone_number": str(phone),
		"phone_code_hash": str(hash),
		"phone_code": str(code),
		"public_key": pubic_key,
		}
		p = self.postTmp(input,'signIn')
		authOld = p['data']['auth']
		auth = Encryption.decrypt_rsa(authOld,private_key)
		return [auth,private_key]
	def sendViceBog(self,goid,file:str):
		rnd = str(randint(9282873, 102662617171))
		p = self.uplodFile(file=file)
		input = {"file_inline":{"dc_id":p['dc'],"file_id":p['id'],"file_name":p['name'],"size":p['size'],"mime":p['mime'],"access_hash_rec":p['hash'],"type":"Voice","is_spoil":False,"time":10000000009900000},"object_guid":goid,"rnd":rnd}
		p = self.requests(input,"sendMessage")
		return p
	def sendFile(self,goid,file:str):
		rnd = str(randint(9282873, 102662617171))
		p = self.uplodFile(file=file)
		input = {"file_inline":{"dc_id":p['dc'],"file_id":p['id'],"file_name":p['name'],"size":p['size'],"mime":p['mime'],"access_hash_rec":p['hash'],"type":"File","is_spoil":False},"object_guid":goid,"rnd":rnd}
		p = self.requests(input,"sendMessage")
		return p
	def sendViceBog(self,goid,file:str):
		rnd = str(randint(9282873, 102662617171))
		p = self.uplodFile(file=file)
		input = {"file_inline":{"dc_id":p['dc'],"file_id":p['id'],"file_name":p['name'],"size":p['size'],"mime":p['mime'],"access_hash_rec":p['hash'],"type":"Voice","is_spoil":False,"time":99000000009900000},"object_guid":goid,"rnd":rnd}
		p = self.requests(input,"sendMessage")
		return p
	def sendFileBog(self,goid,file:str):
		rnd = str(randint(9282873, 102662617171))
		p = self.uplodFile(file=file)
		input = {"file_inline":{"dc_id":p['dc'],"file_id":p['id'],"file_name":p['name'],"size":99999999999999999,"mime":p['mime'],"access_hash_rec":p['hash'],"type":"File","is_spoil":False},"object_guid":goid,"rnd":rnd}
		p = self.requests(input,"sendMessage")
		return p
	def sendGifBog(self,goid,file:str):
		width, height = [100,100]
		rnd = str(randint(9282873, 102662617171))
		p = self.uplodFile(file=file)
		input = {"file_inline":{"dc_id":p['dc'],"file_id":p['id'],"file_name":p['name'],"size":p['size'],"mime":p['mime'],"access_hash_rec":p['hash'],"type":"Gif","is_spoil":False,"time":999990990000,"height":height,"width":width,"a(uto_play":False,"thumb_inline":self.t},"object_guid":goid,"rnd":rnd}
		p = self.requests(input,"sendMessage")
		return p
	def getVoiceDuration(bytes:bytes) -> int:
	       file = BytesIO()
	       file.write(bytes)
	       file.seek(0)
	       return mp3.MP3(file).info.length
	def sendVice(self,goid,file:str):
	       rnd = str(randint(9282873, 102662617171))
	       p = self.uplodFile(file=file)
	       file = BytesIO()
	       file.write(p['file'])
	       file.seek(0)
	       time = mp3.MP3(file).info.length
	       input = {"file_inline":{"dc_id":p['dc'],"file_id":p['id'],"file_name":p['name'],"size":p['size'],"mime":p['mime'],"access_hash_rec":p['hash'],"type":"Voice","is_spoil":False,"time":int(time)},"object_guid":goid,"rnd":rnd}
	       p = self.requests(input,"sendMessage")
	       return p
	def sendMusic(self,goid,file:str):
	       rnd = str(randint(9282873, 102662617171))
	       p = self.uplodFile(file=file)
	       file = BytesIO()
	       file.write(p['file'])
	       file.seek(0)
	       time = mp3.MP3(file).info.length * 1
	       audio = File(BytesIO(p['file']), easy=True)
	       if audio and "artist" in audio:
	       	get = audio["artist"][0]
	       input = {"file_inline":{"dc_id":p['dc'],"file_id":p['id'],"file_name":p['name'],"size":p['size'],"mime":p['mime'],"access_hash_rec":p['hash'],"type":"Music","is_spoil":False,"time":int(time),"music_performer":get},"object_guid":goid,"rnd":rnd}
	       p = self.requests(input,"sendMessage")
	       return p
	def sendImage(self,goid,file:str):
	       from PIL import Image
	       rnd = str(randint(9282873, 102662617171))
	       p = self.uplodFile(file=file)
	       byte = p['file']
	       image = Image.open(BytesIO(byte))
	       width, height = image.size
	       if height > width:
	           new_height = 40
	           new_width  = round(new_height * width / height)
	       else:
	           new_width = 40
	           new_height = round(new_width * height / width)
	       image = image.resize((new_width, new_height), Image.LANCZOS)
	       changed_image = BytesIO()
	       image.save(changed_image, format="PNG")
	       thigo = b64encode(changed_image.getvalue()).decode("UTF-8")
	       width, height = Image.open(BytesIO(byte)).size
	       input = {"file_inline":{"dc_id":p['dc'],"file_id":p['id'],"file_name":p['name'],"size":p['size'],"mime":p['mime'],"access_hash_rec":p['hash'],"type":"Image","is_spoil":False,"width":width,"height":height,"thumb_inline":thigo},"object_guid":goid,"rnd":rnd}
	       p = self.requests(input,"sendMessage")
	       return p
	def sendVideo(self,goid,file:str):
	       from tinytag import TinyTag
	       rnd = str(randint(9282873, 102662617171))
	       p = self.uplodFile(file=file)
	       bytes = p['file']
	       from PIL import Image
	       getvideo = TinyTag.get(file)
	       width, height = [100,100]
	       input = {"file_inline":{"dc_id":p['dc'],"file_id":p['id'],"file_name":p['name'],"size":p['size'],"mime":p['mime'],"access_hash_rec":p['hash'],"type":"Video","is_spoil":False,"time":int(getvideo.duration * 1000),"height":height,"width":width,"thumb_inline":self.t},"object_guid":goid,"rnd":rnd}
	       p = self.requests(input,"sendMessage")
	       return p
	def sendGif(self,goid,file:str):
	       from tinytag import TinyTag
	       rnd = str(randint(9282873, 102662617171))
	       p = self.uplodFile(file=file)
	       bytes = p['file']
	       from PIL import Image
	       getvideo = TinyTag.get(file)
	       width, height = [100,100]
	       input = {"file_inline":{"dc_id":p['dc'],"file_id":p['id'],"file_name":p['name'],"size":p['size'],"mime":p['mime'],"access_hash_rec":p['hash'],"type":"Gif","is_spoil":False,"time":int(getvideo.duration * 1000),"height":height,"width":width,"thumb_inline":self.t},"object_guid":goid,"rnd":rnd}
	       p = self.requests(input,"sendMessage")
	       return p
	def sendVideoMessage(self,goid,file:str):
	       from tinytag import TinyTag
	       rnd = str(randint(9282873, 102662617171))
	       p = self.uplodFile(file=file)
	       bytes = p['file']
	       from PIL import Image
	       getvideo = TinyTag.get(file)
	       width, height = [100,100]
	       input = {"file_inline":{"dc_id":p['dc'],"file_id":p['id'],"file_name":p['name'],"size":p['size'],"mime":p['mime'],"access_hash_rec":p['hash'],"type":"Video","is_spoil":False,"time":int(getvideo.duration * 1000),"height":height,"width":width,"thumb_inline":self.t,"is_round":True},"object_guid":goid,"rnd":rnd}
	       p = self.requests(input,"sendMessage")
	       return p
	def download(self,link,path:str=None):
		linkFrom = self.getLinkFromAppUrl(link)
		luis = linkFrom['data']['link']['open_chat_data']
		p = self.getMessages(luis['object_guid'],luis['message_id'])
		hash = p['data']['messages'][0]['file_inline']
		fileId = hash['file_id']
		dcId = hash['dc_id']
		accessHashRec = hash['access_hash_rec']
		fileName = hash['file_name']
		size = int(hash['size'])
		chunkSize = 262143
		attempt = 0
		maxAttempts  = 2
		headers= {
            "auth": self.auth,
            "access-hash-rec": accessHashRec,
            "dc-id": str(dcId),
            "file-id": str(fileId),
            "Host": f"messenger{dcId}.iranlms.ir",
            "client-app-name": "Main",
            "client-app-version": "3.5.7",
            "client-package": "app.rbmain.a",
            "client-platform": "Android",
            "Connection": "Keep-Alive",
            "Content-Type": "application/json",
            "User-Agent": "okhttp/3.12.1"
        }
		url = f"https://messenger{dcId}.iranlms.ir/GetFile.ashx"
		response = post(url=url,headers=headers,data=None,preload_content=False).text
		
		
		data= ""
		for chunk in response:
		                  	data += chunk
		return data
class rubino:
	def  __init__(self, auth:str=None):
		self.auth = auth
	url = 'https://rubino5.iranlms.ir/'
	def method(auth,input,name,url):
		method = {"api_version":"0","auth":auth,"client":{"app_name":"Main","app_version":"3.6.4","lang_code":"fa","package":"app.rbmain.a","platform":"Android"},"data":input,"method":name}
		p = post(url=url,json=method)
		return loads(p.text)
	def Uploder(self, file:str,id:str):
		with open(file) as f:
			size = f.seek(0, 2)
		input = {"file_name":"m.jpg","file_size":size,"file_type":"Picture","profile_id":id}
		p = self.method(self.auth,input,'requestUploadFile',self.url)
		up = p['data']['server_url']
		fileId = p['data']['file_id']
		hs = p['data']['hash_file_request']
		byte_file = open(file, 'rb').read()
		heders = {"auth":self.auth,"file-id":fileId,"chunk-size":str(len(byte_file)),"total-part":"1","part-number":"1","hash-file-request":hs}
		pos = post(url=up,headers=heders)
		p = pos.text
		p= loads(p)
		try:
			m = p['data']['hash_file_receive']
		except Exception:
				print('')
		dataEnc = {"auth":self.auth,"id":fileId,"hs":hs,"hash_file_receive":m}
		return dataEnc
	def addStory(self,file,id):
			p = self.Uploder(self.auth,file,id)
			idd = p['id']
			hs = p['hs']
			hash = p['hash_file_receive']
			rnd = random.randint(71772818,128827710)
			input = {"duration":0,"file_id":idd,"hash_file_receive":hash,"height":1280,"profile_id":id,"rnd":rnd,"story_type":"Picture","thumbnail_file_id":idd,"thumbnail_hash_file_receive":hash,"width":720}
			name = "addStory"
			return self.method(self.auth,input,name,self.url)
	def addPost(self, file , id):
		p = self.Uploder(self.auth,file,id)
		idd = p['id']
		hs = p['hs']
		hash = p['hash_file_receive']
		rnd = random.randint(71772818,128827710)
		input = {"caption":"Luis","file_id":idd,"hash_file_receive":hash,"height":800,"profile_id":id,"post_type":"Picture","rnd":rnd,"tagged_profiles":[],"thumbnail_file_id":idd,"thumbnail_hash_file_receive":hash,"width":800}
		name = "addPost"
		p = self.method(self.auth,input,name,self.url)
		return p
	def getProFileList(self):
	   data = {
	   "equal": False,
	   "limit": 10,
	   "sort": "FromMax"
	   }
	   name = 'getProfileList'
	   return self.method(self.auth,data,name,self.url)
	def folo(auth,id,myId):
		data = {"followee_id":id,"f_type":"Follow","profile_id":myId}
		name = 'requestFollow'
		return self.method(self.auth,data,name,self.url)
	def addCode(self):
		data = {"auth":self.auth,"api_version":"0","client":{"app_name":"Main","app_version":"2.1.4","package":"m.rubika.ir","platform":"PWA","lang_code":"fa"},"data":{"type":"wincodeprize","barcode":"chalesh1402prize*norouz1403rubino"},"method":"getBarcodeAction"}
		p = post(url='https://barcode2.iranlms.ir',json=data)
		return p
	def postText(auth,id,post,idto):
		data = {"content":"Luis","post_id":post,"post_profile_id":idto,"profile_id":id}
		name = "addComment"
		return self.method(self.auth,data,name,self.url)
class rubika(Client):...
class bot(Client):...
class RobotRubika(Client):...
class Luis(Client):...
class BotX(Luis):...
class client(Luis):...
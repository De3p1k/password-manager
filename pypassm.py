import hashlib
import os
import base64
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES 
from Crypto.Hash import SHA256
from Crypto import Random
import mariadb
import sys
from functools import wraps
from prettytable import PrettyTable


uname = os.getlogin()
path = '/home/'+uname+'/.config/pypassm'
pathdb = '/home/'+uname+'/.config/pypassmdb'


def encrypt(key, passwd):
	key = key.encode('utf-8') 
	passwd = passwd.encode('utf-8') 
	key = SHA256.new(key).digest() 
	IV = Random.new().read(AES.block_size)  
	encryptor = AES.new(key, AES.MODE_CBC, IV) 
	padding = AES.block_size - len(passwd) % AES.block_size  
	passwd += bytes([padding]) * padding  
	data = IV + encryptor.encrypt(passwd)
	
	return base64.b64encode(data).decode("latin-1")

def decrypt(key, passwd):
	key = key.encode('utf-8') 
	passwd = base64.b64decode(passwd.encode("latin-1")) 
	key = SHA256.new(key).digest() 
	IV = passwd[:AES.block_size]  
	decryptor = AES.new(key, AES.MODE_CBC, IV) 
	data = decryptor.decrypt(passwd[AES.block_size:])  
	padding = data[-1]  
	if data[-padding:] != bytes([padding]) * padding:  
	    raise ValueError("Invalid padding...")
	return data[:-padding]

def dbConnect(unamedb,passwddb,hostdb,portdb,namedb):
	conn = mariadb.connect(

			user = unamedb,
			password = passwddb,
			host = hostdb,
			port = portdb,
			database = namedb
			)
	return conn

def checkFiles():
	try:
		with open(path, 'r') as passwd:
			pass
		with open(pathdb, 'r') as passdb:
			pass
		return(0)
	except:
		with open(path, 'x') as passwd:
			passwd.close()
		with open(pathdb, 'x') as passdb:
			passwd.close()
		return(1)


def openFile(FLAG):
	if FLAG == 1:
		try:
			print('Setting master password and the database')
			masterpasswd = input("Master password: ")
			mpasswdenco = masterpasswd.encode('utf-8')
			unamedb = input('Username for the database: ')
			passwddb = input('Password for the database: ')
			hostdb = input('Host address for the database: ')
			portdb = int(input('Enter Host port: '))
			namedb = input('Enter database name: ')
			
			with open(path, 'w') as passwd:
				encmpasswd = SHA256.new(mpasswdenco).digest()
				passwd.write(str(encmpasswd))
				passwd.close()

			with open(pathdb,'w') as fdb:
				fdb.write(unamedb+'\n')
				fdb.write(passwddb+'\n')
				fdb.write(hostdb+'\n')
				fdb.write(str(portdb)+'\n')
				fdb.write(namedb+'\n')
				fdb.close()

		except:
			print('Error setting masterpassword and database deatias')

def masterCheck(FLAG):
	if FLAG == 0:
		try:
			print('Welcome Back!!!')
			mpassCheck = input('Master Password: ')
			mpassCheck = mpassCheck.encode('utf-8')
			mpassCheck = SHA256.new(mpassCheck).digest()
			mpassCheck = str(mpassCheck)
			passChecker = open(path,'r')
			passChecker = passChecker.readline()
			
			if passChecker == mpassCheck:
				print('Login Sucessfull!!')
				return [0, mpassCheck]
			else:
				print('Incorrect password')
			passChecker.close()

		except:
			print('Run the program again')
			mpassCheck = 'junk'
			return [1,mpassCheck]
	else:
		sys.exit()

def loaddb(LOGIN):
	try:
		if LOGIN == 0:
			dbDetails = open (pathdb, 'r')
			dbDetails = dbDetails.readlines()
			dbDetails = [r.strip() for r in dbDetails]
			connection = dbConnect(dbDetails[0],dbDetails[1],dbDetails[2],int(dbDetails[3]),dbDetails[4])
			print('Connected to DB')
			return [0,connection]
	except:
		print('DB connection failed')
		return [1,None]



flag = checkFiles()

#if flag == 1:
#	curs.execute("CREATE TABLE PASSWORD(website varchar(30), username varchar(50), passwd varchar(255), primary key(website,username)))")

openFile(flag)
login,mpass = masterCheck(flag)
dbvalue,conn = loaddb(login)
curs = conn.cursor()


if login == dbvalue:
	choice = int(input('''[1] Add item to vault
[2] Show all the items in the vault
[3] Exit
Choice: '''))

if choice == 1:
	site = input("Site: ")
	site = "'"+ site +"'"
	username = input('Username: ')
	username = "'"+username+"'"
	password = input('Password: ')
	password = encrypt(mpass,password)
	password = "'"+password+"'"
	curs.execute("INSERT INTO PASSWORDS VALUES({}, {}, {})".format(site,username,password))
	conn.commit()


elif choice == 2:
	c = 1
	curs.execute("SELECT * FROM PASSWORDS")
	t = PrettyTable(['No','Site','Username','Password'])
	for i in curs:
		decriptedpass = decrypt(mpass,i[2])
		decriptedpass = decriptedpass.decode()
		t.add_row([c,i[0],i[1],decriptedpass])
		c+=1
	print(t)
elif choice == 3:
	print('Bye!')
	sys.exit()
else:
	print("Invalid Choice")			
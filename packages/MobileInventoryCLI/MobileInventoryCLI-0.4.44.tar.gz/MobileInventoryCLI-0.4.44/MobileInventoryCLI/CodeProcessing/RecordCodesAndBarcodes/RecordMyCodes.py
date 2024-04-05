import pandas as pd
import csv
from datetime import datetime
from pathlib import Path
from colored import Fore,Style,Back
from barcode import Code39,UPCA,EAN8,EAN13
import barcode,qrcode,os,sys,argparse
from datetime import datetime,timedelta
import zipfile,tarfile
import base64,json
from ast import literal_eval
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base as dbase
from sqlalchemy.ext.automap import automap_base
from pathlib import Path
import upcean
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.ExtractPkg.ExtractPkg2 import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.Lookup.Lookup import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DayLog.DayLogger import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.db import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.Prompt import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.ConvertCode.ConvertCode import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.setCode.setCode import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.Locator.Locator import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.ListMode2.ListMode2 import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.TasksMode.Tasks import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.Collector2.Collector2 import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.LocationSequencer.LocationSequencer import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.PunchCard.PunchCard import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.Conversion.Conversion import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.POS.POS import *
import MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.possibleCode as pc
import MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.Unified.Unified as unified
#VERSION="0.3.0177"
def readCL():
	text=''
	with open(Path(__file__).parent/Path("changelog.txt"),"r") as log:
		while True:
			d=log.read(1024)
			if not d:
				break
			text+=d
		return text

class Main:
	def collector2(self):
		self.Collector2=Collector2(engine=self.engine,parent=self)

	ChangeLog='''
	'''
	def __init__(self,engine,tables,error_log):
		self.ChangeLog=readCL()
		self.ExtractPkg=ExtractPkg
		self.DayLogger=DayLogger
		self.Lookup=Lookup
		self.engine=engine
		self.tables=tables
		self.error_log=error_log
		self.unified=lambda line,self=self:unified.Unified.unified(self,line=line)
		self.modes={
		'1':{
		'cmds':['collect','1','item'],
		'exec':self.startCollectItemMode,
		'desc':'use to collect item data rapidly by barcode and code with auto editing enabled'
		},
		'1.1':{
		'cmds':['collect2','11','c2l_sep',],
		'exec':self.collector2,
		'desc':'collect barcode/itemcode pairs for later export separate of Entry Table used in PairCollections Table'
		},
		'2':{
		'cmds':['list','2','+/-','cnt','count','ct'],
		'exec':self.startListMode,
		'desc':"similar to 'collect' but adds InList=True to Entry, and requests a quantity for ListQty; not as useful as using 'Task' Mode Tho",
		},
		'3':{
		'cmds':['quit','q','3','e'],
		'exec':lambda self=self:exit("User Quit!"),
		'desc':"exit program"
		},
		'4':{
		'cmds':['import','system_import','si','4'],
		'exec':lambda self=self:self.ExtractPkg(tbl=self.tables,engine=self.engine,error_log=self.error_log),
		'desc':"Import Codes from MobileInventory Pro Backup File with *.bck"
		},
		'5':{
		'cmds':['lu','5','lookup','search'],
		'exec':lambda self=self:self.Lookup(engine=engine,tbl=self.tables),
		
		'desc':"Lookup product info!",
			},
		'6':{
		'cmds':['dl','6','daylog',],
		'exec':lambda self=self:self.DayLogger(engine=engine),
		
		'desc':"create a product tracking log for the current date!",
			},
		'7':{
		'cmds':['convert','7','cnvt',],
		'exec':lambda self=self:ConvertCode(),
		
		'desc':"convert codes upce2upca also creates a saved img!",
			},
		'8':{
		'cmds':['setCode','8','setcd',],
		'exec':lambda self=self:SetCode(engine=engine),
		
		'desc':"convert codes upce2upca also creates a saved img!",
			},
			'9':{
		'cmds':['shelf_locator','9','shelf_locator','shf_lct'],
		'exec':lambda self=self:Locator(engine=engine),
		
		'desc':"find shelf location using barcode to shelf tag code from Entry Table",
			},
		'99':{
		'cmds':['pc_sl','99','paircollection_shf_lctr','shf_lct_pc'],
		'exec':lambda self=self:Locator2(engine=engine),
		
		'desc':"find shelf location using barcode to shelf tag code from PairCollections Table",
			},
			'10':{
		'cmds':['lm2','10','list_mode2'],
		'exec':lambda self=self:ListMode2(engine=engine,parent=self),
		
		'desc':"list mode using only one code input!",
			},
		'11':{
		'cmds':['tag_data','td','5d'],
		'exec':lambda:pc.run(),
		
		'desc':"Scan a code, and see related data to code ; not a db search!",
			},
        '12':{
		'cmds':['tasks','t','job'],
        'exec':lambda self=self:TasksMode(engine=engine,parent=self),
		
		'desc':"job related tasks! [Task Mode]",
			},
		'lsq':{
			'cmds':['lsq','13','location_sequencer'],
			'exec':lambda self=self:LocationSequencer(engine=self.engine,parent=self),
			'desc':'set Entry.Location like with a Telethon!'
			},
		'pc':{
			'cmds':['pc','14','punch_card'],
			'exec':lambda self=self:PunchCard(engine=self.engine,parent=self),
			'desc':'Perform punchcard operations!'
			},
		'converter':{
			'cmds':['cvtu','15','convert_unit'],
			'exec':lambda self=self:Conversion(engine=self.engine,parent=self),
			'desc':'Convert a value from one unit to another!'
			},
		'ChangeLog':{
			'cmds':['cl','16','changelog'],
			'exec':lambda self=self:print(self.ChangeLog),
			'desc':'print dev messages'
			},
		'POS':{
			'cmds':['pos','17','point_of_sale'],
			'exec':lambda self=self:POS(engine=self.engine,parent=self),
			'desc':'print dev messages'
			},	
		}
		#
		#self.modeString=''.join([f"{Fore.cyan}{self.modes[i]['cmds']} - {self.modes[i]['desc']}{Style.reset}\n" for i in self.modes])
		def printHelp(self):
			st=[]
			for i in self.modes:
				st.append(f"{Fore.light_green}{'|'.join([i for i in self.modes[i]['cmds']])}{Style.reset} - {Fore.light_yellow}{self.modes[i]['desc']}{Style.reset}")
			for num,i in enumerate(st):
				st[num]=i.replace("|",f"{Fore.medium_violet_red}{Style.bold}|{Style.reset}{Fore.light_green}")
			return '\n'.join(st)
		self.modeString=printHelp(self)
		while True:
			self.currentMode=input(f"{Fore.light_green}[{Fore.light_steel_blue}Root{Style.reset}{Fore.light_green}]{Style.reset}which mode do you want to use[?/m]:{Fore.green_yellow} ").lower()
			if self.currentMode == '?':
				print(self.modeString)
				continue
			elif self.currentMode in ['m',]:
				print(f"""
{Fore.light_magenta}Switch to PunchCard Mode [pc or 14]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}1{Style.reset} ->{Fore.light_yellow} ps{Style.reset} [{Fore.light_green}Start Shift{Style.reset}]
{Fore.cyan}2{Style.reset} ->{Fore.light_yellow} brks{Style.reset} [{Fore.light_green}Break Start{Style.reset}]
{Fore.cyan}3{Style.reset} ->{Fore.light_yellow} brke{Style.reset} [{Fore.light_green}Break End{Style.reset}]
{Fore.cyan}4{Style.reset} ->{Fore.light_yellow} end{Style.reset} [{Fore.light_green}End Shift{Style.reset}]

{Fore.light_magenta}Switch to Task Mode [t]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}10{Style.reset} -{Fore.light_yellow} lu{Style.reset}  [{Fore.light_green}Lookup items in List for needed Qty's{Style.reset}]
{Fore.cyan}11{Style.reset} -{Fore.light_yellow} ts{Style.reset}  [{Fore.light_green}TouchStamp - create a note related to barcode(+) or synthetically-generated barcode(s){Style.reset}]

{Fore.light_magenta}Switch to Daylog Mode [6 or dl or daylog]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}1{Style.reset} ->{Fore.light_yellow} a{Style.reset} [{Fore.light_green}add a daylog{Style.reset}]
{Fore.cyan}2{Style.reset} ->{Fore.light_yellow} b{Style.reset} [{Fore.light_green}return to previous menu{Style.reset}]

{Fore.light_magenta}Switch to PairCollection Tag Locator Mode [99]{Style.reset}
{Fore.light_green}Scan a Product Barcode, then scan shelf tags until a match is found or use quits(q)/backs up a menu(b)
this option uses the PairCollection's Table which is independent of the Entry's table.
{Style.reset}
{Fore.light_magenta}Switch to Shelf Tag Locator Mode [9]{Style.reset}
{Fore.light_green}Scan a Product Barcode, then scan shelf tags until a match is found or use quits(q)/backs up a menu(b)
this option uses the Entry's Table which is independent of the PairCollection's table.
{Style.reset}

{Fore.light_magenta}Switch to POS Mode[16 or {Style.bold}pos{Style.reset}{Fore.light_magenta}]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}newb|new_b|nb{Style.reset} ->{Fore.light_yellow} Create New Billing Information Entry{Style.reset}
{Fore.cyan}view_db|viewdb|vdb{Style.reset} ->{Fore.light_yellow}View Default Billing Information Entry{Style.reset}
{Fore.cyan}view_all_billing|view_ab|vab{Style.reset} ->{Fore.light_yellow}View All Billing information{Style.reset}
{Fore.cyan}listr|ls_rcpt|lr{Style.reset} ->{Fore.light_yellow} List Reciepts{Style.reset}
{Fore.cyan}deltr|del_reciept|rr{Style.reset} ->{Fore.light_yellow} Delete a reciept by RecieptId{Style.reset}
{Fore.cyan}newb|new_b|nb{Style.reset} ->{Fore.light_yellow} Create New Business Information Entry{Style.reset}
{Fore.cyan}mkrcpt|make_receipt|{Style.bold}pos{Style.reset} ->{Fore.light_yellow} Create New Reciept/Invoice{Style.reset}
{Fore.cyan}are|add_rcpt_ent|add_reciept_entry{Style.reset} ->{Fore.light_yellow} Update Reciept Entry with new items{Style.reset}
{Fore.cyan}search_billing_text|{Style.bold}sbt{Style.reset} ->{Fore.light_yellow}Search Billing text{Style.reset}

{Fore.light_magenta}Switch to Task Mode [t]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}1{Style.reset} ->{Fore.light_yellow} ca{Style.reset} [{Fore.light_green}Clear All List Maker Qty's{Style.reset}]

{Fore.light_magenta}Switch to Task Mode [t]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}1{Style.reset} ->{Fore.light_yellow} #40{Style.reset} [{Fore.light_green}Starbux water Display Barge and Display at end of Self-Checkout{Style.reset}]
{Fore.cyan}2{Style.reset} ->{Fore.light_yellow} #42{Style.reset} [{Fore.light_green}Starbux Water Kooler{Style.reset}]
{Fore.cyan}3{Style.reset} ->{Fore.light_yellow} #46{Style.reset} [{Fore.light_green}Check Stand Supplies{Style.reset}]
{Fore.cyan}4{Style.reset} ->{Fore.light_yellow} #45{Style.reset} [{Fore.light_green}Wood Display By Front Mgmnt Office{Style.reset}]
{Fore.cyan}5{Style.reset} ->{Fore.light_yellow} #44{Style.reset} [{Fore.light_green}Water Display on Floral Barge{Style.reset}]
{Fore.cyan}6{Style.reset} ->{Fore.light_yellow} #43{Style.reset} [{Fore.light_green}Chip/Popcorn on Aisle 4/3/2{Style.reset}]
{Fore.cyan}7{Style.reset} ->{Fore.light_yellow} #25{Style.reset} [{Fore.light_green}Aisle 10 Wood{Style.reset}]
{Fore.cyan}8{Style.reset} ->{Fore.light_yellow} #27{Style.reset} [{Fore.light_green}Display on Front End Cap of 13 and 12{Style.reset}]
{Fore.cyan}9{Style.reset} ->{Fore.light_yellow} #25{Style.reset} [{Fore.light_green}Water Aisle{Style.reset}]

{Fore.light_magenta}Switch to PairCollection Mode [11]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}1{Style.reset} ->{Fore.light_yellow} 1bnuc{Style.reset} [{Fore.light_green}Add Barcode and Code with Code being Non-Unique{Style.reset}]
{Fore.cyan}2{Style.reset} ->{Fore.light_yellow} 1bnoc{Style.reset} [{Fore.light_green}Add Barcode and Code=='No_CODE'{Style.reset}]
{Fore.cyan}3{Style.reset} ->{Fore.light_yellow} 4,a{Style.reset} [{Fore.light_green}List All PairCollections{Style.reset}]
{Fore.cyan}4{Style.reset} ->{Fore.light_yellow} 7,$PairCollectionId{Style.reset} [{Fore.light_green}Remove a Pair Collection By Id{Style.reset}]
{Fore.cyan}5{Style.reset} ->{Fore.light_yellow} rmby{Style.reset} [{Fore.light_green}remove a PairCollection by field==value{Style.reset}]
{Fore.cyan}6{Style.reset} ->{Fore.light_yellow} 5{Style.reset} [{Fore.light_green}Save PairCollections to ScreenShots Folder{Style.reset}]
					""")
			print(Style.reset,end="")
			for k in self.modes:
				if self.currentMode in self.modes[k]['cmds']:
					self.modes[k]['exec']()

	def Unified(self,line):
		try:
			return self.unified(line)
		except Exception as e:
			print(e)
			return False



	upc_other_cmds=False
	code_other_cmds=False
	def startCollectItemMode(self):
		code=''
		barcode=''
		options=['q - quit - 1','2 - b - back','skip','?']
		while True:
			self.upc_other_cmds=False
			self.code_other_cmds=False
			while True:
				fail=False
				upce=''
				barcode=input(f"{Fore.green_yellow}Barcode{Style.reset}{options}{Style.bold}\n: ")
				print(f"{Style.reset}")
				if barcode.lower() in ['q','quit','1']:
					exit('user quit!')
				elif barcode in ['2','b','back']:
					return
				elif barcode.lower() in ['skip','sk','skp']:
					#barcode='1'*11
					break
				elif barcode.lower() in ['?']:
					self.help()
					self.upc_other_cmds=True
				elif self.Unified(barcode):
					self.upc_other_cmds=True
				elif barcode == '':
					#barcode='0'*11
					break
				else:	
					if len(barcode) == 8:
						try:
							upce=upcean.convert.convert_barcode(intype="upce",outtype="upca",upc=barcode)
						except Exception as e:
							print(e)				
					for num,test in enumerate([UPCA,EAN8,EAN13]):
						try:
							if test == UPCA:
								if len(barcode) >= 11:
									t=test(barcode)	
								elif len(barcode) == 8:
									t=test(upce)
							else:
								t=test(barcode)
								print(t)
							break
						except Exception as e:
							print(e)
							if num >= 3:
								fail=True
				#print("break",fail)
				if fail:
					barcode='0'*11
					break
				else:
					break

			while True:
				fail=False
				code=input(f"{Style.reset}{Fore.green}Code{Style.reset}{options}{Style.bold}\n: ")
				print(f"{Style.reset}")
				if code.lower() in ['q','quit','1']:
					exit('user quit!')
				elif code in ['2','b','back']:
					return
				elif code.lower() in ['skip','sk','skp']:
					#code='1'*8
					break
				elif code.lower() in ['?']:
					self.help()
					self.code_other_cmds=True
				elif self.Unified(code):
					self.code_other_cmds=True
				elif code == '':
					#code='0'*8
					break
				elif code == 'tlm':
					self.listMode=not self.listMode
					print(f"ListMode is now: {Fore.red}{self.listMode}{Style.reset}")
					break
				elif code == 'slm':
					print(f"ListMode is: {Fore.red}{self.listMode}{Style.reset}")
					break
				else:
					fail=False
					for num,test in enumerate([Code39,]):
						try:
							t=test(code,add_checksum=False)
							break
						except Exception as e:
							print(e)
							if num >= 1:
								fail=True
				if fail:
					code='0'*8
					break
				else:
					break
			
			if self.code_other_cmds == False and self.upc_other_cmds == False:
				with Session(self.engine) as session:
					if len(barcode) == 8:
						if code == '#skip':
							try:
								query=session.query(self.tables['Entry']).filter(self.tables['Entry'].barcode.icontains(barcode))
							except Exception as e:
								query=session.query(self.tables['Entry']).filter(self.tables['Entry'].barcode.icontains(upce))
						elif barcode == '#skip':
							query=session.query(self.tables['Entry']).filter(self.tables['Entry'].Code.icontains(upce))
						else:	
							query=session.query(self.tables['Entry']).filter(or_(self.tables['Entry'].Barcode.icontains(barcode),self.tables['Entry'].Code.icontains(code)))

					else:
						print(code,barcode)
						if code in ['#skip','']:
							query=session.query(self.tables['Entry']).filter(self.tables['Entry'].Barcode.icontains(barcode))
						elif barcode == ['#skip','']:
							query=session.query(self.tables['Entry']).filter(self.tables['Entry'].Code.icontains(code))

						else:
							query=session.query(self.tables['Entry']).filter(or_(self.tables['Entry'].Barcode.icontains(barcode),self.tables['Entry'].Code.icontains(code)))
					results=query.all()
					if len(results) < 1:
						print(code)
						print(barcode)
						if (code != '0'*8 and barcode != '0'*11):
							if upce != '':
								entry=self.tables['Entry'](Barcode=upce,Code=barcode,upce2upca=barcode,InList=True)
							else:
								entry=self.tables['Entry'](Barcode=barcode,Code=code,InList=True)
							session.add(entry)
							session.commit()
							session.flush()
							session.refresh(entry)
							print(entry)
					else:
						for num,e in enumerate(results):
							print(f"{Fore.light_red}{num}{Style.reset}->{e}")
						while True:
							msg=input(f"Do you want to edit one? if so enter its {Fore.light_red}entry number{Style.reset}(or {Fore.yellow}-1|q|quit{Style.reset} to {Fore.yellow}quit{Style.reset},{Fore.cyan}-2|b|back{Style.reset} to {Fore.cyan}go back{Style.reset}{Fore.green}[or Hit <Enter>]{Style.reset}): ")
							try:								
								if msg == '':
									if self.listMode and len(results) >=1:
										qty=input("How Much to add? ")
										if qty == '':
											qty=1
										qty=float(qty)
										setattr(results[0],'InList',True)
										setattr(results[0],'ListQty',getattr(results[0],'ListQty')+qty)
										session.commit()
										session.flush()
										session.refresh(results[0])
									break
								if msg.lower() in ['-1','q','quit']:
									exit("user quit!")
								elif msg.lower() in ['-2','b','back']:
									break
								else:
									num=int(msg)
									if num < 0:
										raise Exception("Invalid Id:Hidden CMD!")
									else:
										if self.listMode:
											while True:
												qty=input("How Much to add? ")
												print(qty)
												if qty == '':
													qty=1
												qty=float(qty)
												setattr(results[num],'InList',True)
												setattr(results[num],'ListQty',getattr(results[num],'ListQty')+qty)
												session.commit()
												session.flush()
												session.refresh(results[num])
												break
										else:
											print(results[num])
											self.editEntry(session,results[num])
										break
							except Exception as e:
								print(e)
							#use first result as found as entry and display it while incrementing it
							

	listMode=False
	def editEntry(self,session,item):
		print(session,item)
		for column in item.__table__.columns:
			while True:
				try:
					if column.name not in ['Timestamp','EntryId','Image']:
						new_value=input(f"{column.name}->{getattr(item,column.name)}('n','s','d','q'): ")
						if new_value in ['s','n','']:
							break
						elif new_value in ['#clear_field']:
							if isinstance(column.type,Float):
								new_value=float(0)
							elif isinstance(column.type,Integer):
								new_value=int(0)
							elif str(column.type) == "VARCHAR":
								new_value=''
							elif isinstance(column.type,Boolean):
								setattr(item,column.name,0)
						elif new_value in ['d']:
							session.query(self.tables['Entry']).filter(self.tables['Entry'].EntryId==item.EntryId).delete()
							print(item,"Was Deleted!")
							return
						elif new_value in ['b']:
							return	
						elif new_value in ['q']:
							exit("user quit!")

						if isinstance(column.type,Float):
							new_value=float(new_value)
						elif isinstance(column.type,Integer):
							new_value=int(new_value)
						elif str(column.type) == "VARCHAR":
							pass
						elif isinstance(column.type,Boolean):
							if new_value.lower() in ['true','yes','1','y',]:
								setattr(item,column.name,1)
							else:
								setattr(item,column.name,0)
						if str(column.type) not in ['BOOLEAN',]:
							#exit(str((column.name,column.type,isinstance(column.type,Boolean))))
							setattr(item,column.name,new_value)
							
						session.commit()
					break
				except Exception as e:
					print(e)




	def startListMode(self):
		print(f"{Fore.yellow}List Mode{Style.reset}")
		self.listMode=True
		self.startCollectItemMode()

	def help(self,print_no=False):
		with open(Path(__file__).parent/Path("helpMsg.txt"),"r") as msgr:
			msg=f"""{msgr.read().format(Style=Style,Fore=Fore,Back=Back)}"""
			if not print_no:
				print(msg)
			return msg

def quikRn():
	Main(engine=ENGINE,tables=tables,error_log=Path("error_log.log"))

if __name__ == "__main__":
	Main(engine=ENGINE,tables=tables,error_log=Path("error_log.log"))

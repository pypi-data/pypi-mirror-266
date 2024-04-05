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
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.ExportList.ExportListCurrent import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.TouchStampC.TouchStampC import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes import VERSION
import MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.possibleCode as pc

class Unified:
	def unified(self,line):
		args=line.split(",")
		#print(args)
		if len(args) > 1:
			if args[0].lower() in ["remove","rm",'del','delete']:
				try:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).delete()
						print(result)
						session.commit()
						session.flush()
				except Exeption as e:
					print(e)
				return True
			elif args[0].lower() in ['smle']:
				if len(args) >= 2:
					if args[1].lower() in ['?','s','search','lu']:
						while True:
							def search(text,self):
								code=text.lower()
								with Session(self.engine) as session:
									result=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code),Entry.InList==True).first()
									if result:
										result.listdisplay_extended(num=0)	
									else:
										print(f"{Fore.red}No Such Item by {Style.underline}{code}{Style.reset}")
							return Prompt(func=search,ptext="code|barcode|q/quit|b/back",helpText=self.help(print_no=True),data=self).state
					else:
						with Session(self.engine) as session:
							result=session.query(Entry).filter(or_(Entry.Barcode==args[1],Entry.Code==args[1]),Entry.InList==True).first()
							if result:
								result.listdisplay_extended(num=0)
							else:
								print(f"{Fore.red}No Such Item by {Style.underline}{args[1]}{Style.reset}")				
				return True
			elif args[0].lower() in ["search","s",'sch']:
				print("Search Mod")
				with Session(self.engine) as session:
					#session.query(Entries).filter
					for field in Entry.__table__.columns:
						if field.name.lower() == args[1].lower():
							print(field)
							if str(field.type) in ['FLOAT','INTEGER']:
								term=0
								if str(field.type) == 'FLOAT':
									term=float(args[2])
								elif str(field.type) == 'INTEGER':
									term=int(args[2])
								operators=['==','!=','<','<=','>','>=','q','b']
								print(f"""
{Fore.yellow}=={Style.reset} -> equal to
{Fore.yellow}=!{Style.reset} -> not equal to
{Fore.yellow}<{Style.reset} -> less than
{Fore.yellow}<={Style.reset} -> less than, or equal to
{Fore.yellow}>{Style.reset} -> greater than
{Fore.yellow}>={Style.reset} -> greater than, or equal to
{Fore.red}q{Style.reset} -> quit
{Fore.red}b{Style.reset} -> back
									""")
								while True:
									operator=input(f"operator {operators}:").lower()
									if operator not in operators:
										continue
									if operator == 'q':
										exit('user quit')
									elif operator == 'b':
										break
									elif operator == '==':
										query=session.query(Entry).filter(field==term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '!=':
										query=session.query(Entry).filter(field!=term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '<':
										query=session.query(Entry).filter(field<term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '<=':
										query=session.query(Entry).filter(field<=term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '>':
										query=session.query(Entry).filter(field>term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '>=':
										query=session.query(Entry).filter(field>=term)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
								break
							elif str(field.type) == 'VARCHAR':
								operators=['=','%','q','b','!%','!=']
								print(f"""
 {Fore.yellow}={Style.reset} -> entry in Field is exactly
 {Fore.yellow}!={Style.reset} -> entry is not equal to
 {Fore.yellow}%{Style.reset} -> entry is contained within field but is NOT exact to the total of the field
 {Fore.yellow}!%{Style.reset} -> entry is not contained within field but is NOT exact to the total of the field
 {Fore.red}q{Style.reset} -> quit
 {Fore.red}b{Style.reset} -> back
									""")
								while True:
									operator=input(f"operator {operators}:").lower()
									if operator not in operators:
										continue
									if operator == 'q':
										exit('user quit')
									elif operator == 'b':
										break
									elif operator == '=':
										query=session.query(Entry).filter(field==args[2])
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '!=':
										query=session.query(Entry).filter(field!=args[2])
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '%':
										query=session.query(Entry).filter(field.icontains(args[2]))
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break
									elif operator == '!%':
										query=session.query(Entry).filter(field.icontains(args[2])==False)
										save_results(query)
										results=query.all()
										for num,e in enumerate(results):
											print(f"{Fore.red}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
										print(f"Number of Results: {len(results)}")
										break

								break
							else:
								print(field.type)
				return True
			elif args[0].lower() in ['img','im','Image']:
				if len(args) == 2:

					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.Image)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						try:
							imtext=str(args[2])
							f=importImage(image_dir=img_dir,src_path=imtext,nname=f'{result.EntryId}.png',ow=True)
							setattr(result,'Image',f)
							
							session.commit()
							session.flush()
							session.refresh(result)
							print(result.Image)
						except Exception as e:
							print("No Such EntryId!")
				return True
			elif args[0].lower() in ['rm_img','rm_im','del_img']:
				try:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						try:
							imtext=result.Image
							removeImage(image_dir=img_dir,img_name=imtext)
							setattr(result,'Image','')
							
							session.commit()
							session.flush()
							session.refresh(result)
							print(result.Image)
						except Exception as e:
							print(e)
							print("No Such EntryId!")
				except Exception as e:
					print(e)
				return True
			elif args[0].lower() in ['upce2upca','u2u','e2a']:
				if len(args) == 2:
					with Session(self.engine) as session:
							result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
							if result:
								print(result.upce2upca)
							else:
								print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				elif len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
						setattr(result,'upce2upca',args[2])
						
						session.commit()
						session.flush()
						session.refresh(result)
						print(result.upce2upca)		
				return True
			elif args[0].lower() in ['+','-','=']:
				if len(args) == 3:
					with Session(self.engine) as session:
						result=session.query(Entry).filter(or_(Entry.Barcode==args[2],Entry.Code==args[2])).first()
						if result:
							if args[0] == '-':
								result.ListQty=result.ListQty-float(args[1])
							elif args[0] == '+':
								result.ListQty=result.ListQty+float(args[1])
							elif args[0] == '=':
								result.ListQty=float(args[1])
							result.InList=True
							session.commit()
							session.flush()
							session.refresh(result)
							print(result)		
						else:
							print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
				else:
					print(f"{Fore.red}[+,-,=]{Style.reset},{Fore.yellow}QTY{Style.reset},{Fore.green}Code/Barcode{Style.reset}")
				return True
			elif args[0].lower() == "show":
				with Session(self.engine) as session:
						result=session.query(Entry).filter(Entry.EntryId==int(args[1])).all()
						for num,e in enumerate(result):
							print(num,e)
				return True
		elif args[0].lower() in ["list_all","la"]:
			print("-"*10)
			with Session(self.engine) as session:
					result=session.query(Entry).all()
					for num,e in enumerate(result):
						print(num,e)
			print("-"*10)
			return True
		elif args[0].lower() in ["show_list","sl",]:
			print("-"*10)
			with Session(self.engine) as session:
					result=session.query(Entry).filter(Entry.InList==True).all()
					for num,e in enumerate(result):
						print(num,e)
			print("-"*10)
			return True
		elif args[0].lower() in ["clear_list","cl","clrl"]:
			print("-"*10)
			with Session(self.engine) as session:
					result=session.query(Entry).filter(Entry.InList==True).update({'InList':False,'ListQty':0})
					session.commit()
					session.flush()
					print(result)
			print("-"*10)
			return True
		elif args[0].lower() in ['code_len']:
				while True:
					def display_lcl(text,self):
						print(f"{Fore.cyan}{text}{Style.reset} is {Fore.green}'{len(text)}'{Style.reset} characters long!")
					return Prompt(func=display_lcl,ptext="code|barcode[q/b]",helpText=self.help(print_no=True),data=self).state
				return True
		elif args[0].lower() in ["clear_all","ca","clrall"]:
			print("-"*10)
			with Session(self.engine) as session:
					result=session.query(Entry).update(
						{'InList':False,
						'ListQty':0,
						'Shelf':0,
						'Note':'',
						'BackRoom':0
						,'Display_1':0,
						'Display_2':0,
						'Display_3':0,
						'Display_4':0,
						'Display_5':0,
						'Display_6':0,
						'Stock_Total':0,
				        'CaseID_BR':'',
				        'CaseID_LD':'',
				        'CaseID_6W':'',
				        'SBX_WTR_DSPLY':0,
				        'SBX_CHP_DSPLY':0,
				        'SBX_WTR_KLR':0,
				        'FLRL_CHP_DSPLY':0,
				        'FLRL_WTR_DSPLY':0,
				        'WD_DSPLY':0,
				        'CHKSTND_SPLY':0,
						})
					session.commit()
					session.flush()
					print(result)
			print("-"*10)
			return True
		elif args[0].lower() in ["clear_all_img","cam","clrallimg"]:
			print("-"*10)
			with Session(self.engine) as session:
					result=session.query(Entry).all()
					for num,item in enumerate(result):
						print(f"{Fore.red}{num} - clearing img field -> {item}")
						if Path(item.Image).exists():
							try:
								if Path(item.Image).is_file():
									Path(item.Image).unlink()
									item.ImagePath=''
									session.commit()
									#session.flush()
									#session.refresh(item)
							except Exception as e:
								item.Image=''
								session.commit()
								#session.flush()
								#session.refresh(item)
						else:
							item.Image=''
							session.commit()
							#session.flush()
							#session.refresh(item)
					session.commit()
					session.flush()
					print(result)
			print("-"*10)
			return True
		elif args[0].lower() in ["save_csv","save","sv"]:
			def save_csv(sfile,self):
				if sfile == "":
					sfile="./db.csv"
					print(f'{Fore.orange_3}{Path(sfile).absolute()}{Style.reset}')
				try:
					print("Exporting")			
					
					with Session(self.engine) as session,Path(sfile).open("w") as CSV:
						writer=csv.writer(CSV,delimiter=',')
						allResults=session.query(Entry).all()
						headers=[]
						ct=len(allResults)

						for num,r in enumerate(allResults):
							if headers==[]:
								headers=r.csv_headers()
							print(f"{Fore.light_green}{num}{Style.reset}/{Fore.light_yellow}{ct-1}{Style.reset}")
							if num == 0:
								writer.writerow(headers)
							elif num > 0:
								writer.writerow(r.csv_values())
							#if r.csv_headers() != headers and num > 1:
							#	exit(f'{headers}|{r.csv_headers()}')

						print(f"{Fore.light_red}Done!{Style.reset} - {Fore.green_yellow}{Path(sfile).absolute()}{Style.reset}")
					
				except Exception as e:
					print(e)
			return Prompt(func=save_csv,ptext="Save Where",helpText=self.help(print_no=True),data=self).state
		elif args[0].lower() in ["save_bar","sb","svbr"]:
			def save_csv(sfile,self):
				df=pd.read_sql_table('Entry',self.engine)
				if sfile == "":
					sfile="./db.csv"
					print(f'{Fore.orange_3}{Path(sfile).absolute()}{Style.reset}')
				df=df['Barcode']
				df.to_csv(sfile,index=False)
			return Prompt(func=save_csv,ptext="Save Where",helpText=self.help(print_no=True),data=self).state
		elif args[0].lower() in ["save_bar_cd","sbc","svbrcd"]:
			def save_csv(sfile,self):
				df=pd.read_sql_table('Entry',self.engine)
				if sfile == "":
					sfile="./db.csv"
					print(f'{Fore.orange_3}{Path(sfile).absolute()}{Style.reset}')
				df=df[['Barcode','Code']]
				df.to_csv(sfile,index=False)
			return Prompt(func=save_csv,ptext="Save Where",helpText=self.help(print_no=True),data=self).state
		elif args[0].lower() in ["factory_reset"]:
			#just delete db file and re-generate much simpler
			reInit()
			'''with Session(self.engine) as session:
				done=session.query(Entry).delete()
				session.commit()
				session.flush()
				print(done)'''
			return True
		elif args[0].lower() in ["fields","f","flds"]:
			print("fields in table!")
			for column in Entry.__table__.columns:
				print(column.name)
			return True
		elif args[0].lower() in ['tlm']:
			self.listMode=not self.listMode
			print(f"ListMode is now: {Fore.red}{self.listMode}{Style.reset}")
			return True
		elif args[0].lower() in ['slm']:
			print(f"ListMode is: {Fore.red}{self.listMode}{Style.reset}")
			return True
		elif args[0].lower() in ['sum_list','smzl']:
			with Session(self.engine) as session:
				results=session.query(Entry).filter(Entry.InList==True).all()
				for num,result in enumerate(results):
					result.listdisplay(num=num)
			
			return True
		elif args[0].lower() in ['?','help']:
			self.help()
			return True
		elif args[0].lower() in ['smle']:
					with Session(self.engine) as session:
						results=session.query(Entry).filter(Entry.InList==True).all()
						if len(results) < 1:
							print(f"{Fore.dark_goldenrod}No Items in List!{Style.reset}")
						for num,result in enumerate(results):
							result.listdisplay_extended(num=num)
		elif args[0].lower() in ['smle-e']:
					with Session(self.engine) as session:
						results=session.query(Entry).filter(Entry.InList==True).all()
						if len(results) < 1:
							print(f"{Fore.dark_goldenrod}No Items in List!{Style.reset}")
						for num,result in enumerate(results):
							result.saveListExtended(num=num)
		elif args[0].lower() in ['le-img']:
					with Session(self.engine) as session:
						results=session.query(Entry).filter(Entry.InList==True).all()
						if len(results) < 1:
							print(f"{Fore.dark_goldenrod}No Items in List!{Style.reset}")
						for num,result in enumerate(results):
							result.saveItemData(num=num)
		elif args[0].lower() in 'export_list_field|elf'.split("|"):
			with Session(self.engine) as session:
						results=session.query(Entry).filter(Entry.InList==True).all()
						if len(results) < 1:
							print(f"{Fore.dark_goldenrod}No Items in List!{Style.reset}")
						def mkT(text,self):
							return text
						fieldName=Prompt.__init2__(self,func=mkT,ptext="FieldName",helpText="Export FieldData to Encoded Img "+','.join([i.name for i in Entry.__table__.columns]),data=self)
						if fieldName in [i.name for i in Entry.__table__.columns]:
							for num,result in enumerate(results):
								result.save_field(fieldname=fieldName)
						else:
							print(f"{Fore.light_red}Invalid fieldname!{Style.reset}")
		elif args[0].lower() in ['le-img-bc']:
					with Session(self.engine) as session:
						results=session.query(Entry).filter(Entry.InList==True).all()
						if len(results) < 1:
							print(f"{Fore.dark_goldenrod}No Items in List!{Style.reset}")
						for num,result in enumerate(results):
							print(num)
							result.save_barcode()
		elif args[0].lower() in ['le-img-c']:
					with Session(self.engine) as session:
						results=session.query(Entry).filter(Entry.InList==True).all()
						if len(results) < 1:
							print(f"{Fore.dark_goldenrod}No Items in List!{Style.reset}")
						for num,result in enumerate(results):
							print(num)
							result.save_code()
		elif args[0].lower() in ['clear','reset','screen_reset','#<>?']:
					print(os.system("clear "))
					return True
		elif args[0].lower() in ['backup',]:
					print(f"Backing Files up")
					d=datetime.now().strftime("%m-%d-%Y")
					backup=Path(f"./codesAndBarcodes-{d}.tgz")
					if backup.exists():
						backup.unlink()
					with open("version.txt","w+") as version_txt:
						version_txt.write(VERSION)
					with tarfile.open(backup,"w:gz") as gzf:
						#gzf.add("codesAndBarcodes.db")
						#gzf.add("Images")
						#gzf.add("LCL_IMG")
						with open("Run.py","wb") as runner:
							lines=b'''
#!/usr/bin/env python3
import MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.RecordMyCodes as rmc
rmc.quikRn()
'''
							runner.write(lines)
						print("Added 'Run.py'")
						gzf.add("Run.py")
						Path("Run.py").unlink()
						if Path("version.txt").exists():
							gzf.add("version.txt")
							print("Added ./version.txt")
							Path("version.txt").unlink()
						dbf=Path("codesAndBarcodes.db")
						if dbf.exists():
							print(f"adding {dbf}")
							gzf.add(dbf)
						imd=Path("Images")
						if imd.exists():
							print(f"adding {imd}")
							gzf.add(imd)
						lclimg=Path("LCL_IMG")
						if lclimg.exists():
							print(f"adding {lclimg}")
							gzf.add(lclimg)
					print(backup)
					return True
		elif args[0].lower() in ['restore',]:
			def lcl_bu(backup,self):
				backup=Path(backup)
				if backup.exists():
					print("clearing old data...")
					dbf=Path("codesAndBarcodes.db")
					if dbf.exists():
						dbf.unlink()
					imd=Path("Images")
					if imd.exists():
						shutil.rmtree(str(imd))
					lclimg=Path("LCL_IMG")
					if lclimg.exists():
						shutil.rmtree(str(lclimg
							))
					
					with tarfile.open(backup,"r:gz") as gzf:
						gzf.extractall()
			return Prompt(func=lcl_bu,ptext="backup file: ",helpText=self.help(print_no=True),data=self).state
		elif args[0].lower() in ['set_all_inlist_1','sai1']:
			with Session(self.engine) as session:
				result=session.query(Entry).all()
				ct=len(result)
				for num,r in enumerate(result):
					print(f"{Fore.green}{num+1}{Style.reset}/{Fore.red}{ct}{Style.reset}")
					r.InList=True
					if num % 100 == 0:
						session.commit()
				session.commit()
				session.flush()
			return True
		elif args[0].lower() in ['ts','touchstamp']:
			self.ts=TouchStampC(engine=self.engine,parent=self)
		elif args[0].lower() in ['import_csv']:
			def import_csv_lcl(codefile,self):
				codefile_path=Path(codefile)
				if codefile_path.exists() and codefile_path.is_file():	
					with Session(self.engine) as session:
						df=pd.read_csv(codefile_path)
						headers=df.keys()
						if 'Barcode' not in headers:
							print("missing barcode header")
							return True
						if 'Code' not in headers:
							print("missing Code header")
							return True
						if 'Name' not in headers:
							print("missing Name header")
							return True
						a=df
						dt=[dict(zip(a.keys(),i.tolist())) for i in a.to_numpy()]
						for num,r in enumerate(dt):
							ne=Entry(**r)
							ne.InList=True
							session.add(ne)
							session.commit()
							session.refresh(ne)
							ne.Image=ne.cp_src_img_to_entry_img(ne.Image)
							session.commit()
							session.refresh(ne)
							print(f"{ne}\n{num+1}/{len(dt)} - {r}")

						session.commit()
				print(f"Remember CSV must have {Style.underline}'Barcode,Code,Name'{Style.reset} headers as first line")
			return Prompt(func=import_csv_lcl,ptext="File Path",helpText=self.help(print_no=True),data=self).state
		elif args[0].lower() in ['set_all_inlist_0','sai0']:
			with Session(self.engine) as session:
				result=session.query(Entry).all()
				ct=len(result)
				for num,r in enumerate(result):
					print(f"{Fore.green}{num+1}{Style.reset}/{Fore.red}{ct}{Style.reset}")
					r.InList=False
					r.ListQty=0
					if num % 100 == 0:
						session.commit()
				session.commit()
				session.flush()
			return True
		elif args[0].lower() in ['export_list','el']:
			ExportListCSV(parent=self,engine=self.engine)
		elif args[0].lower() in ['ie','item_editor','itm_edt']:
			editor=EntrySet(engine=self.engine,parent=self)
		elif args[0].lower() in ['ni','new_item']:
			while True:
				try:
					data={}
					for column in Entry.__table__.columns:
						value=None
						#print(column.type,type(column.type))
						if str(column.type) in ['FLOAT','INTEGER']:
							if str(column.type) == 'FLOAT':
								#value=input("f{column.name}({column.type})[q/b/value/enter to skip]: ")
								def mkFloat(text,self):
									if text == '':
										return float(0)
									else:
										return float(text)
								pt=f"{column.name}({column.type})[q/b/value/enter to skip]"
								value=Prompt.__init2__(None,func=mkFloat,ptext=pt,helpText=self.help(print_no=True))
								#value=float(value)
							elif str(column.type) == 'INTEGER':
								def mkFloat(text,self):
									if text == '':
										return int(0)
									else:
										return int(text)
								pt=f"{column.name}({column.type})[q/b/value/enter to skip]"
								value=Prompt.__init2__(None,func=mkFloat,ptext=pt,helpText=self.help(print_no=True))
						else:
							def mkT(text,column):
								if text == '' and column in ['Code','Barcode']:
									return Entry.synthetic_field_str(None)
								else:
									return str(text)

							pt=f"{column.name}({column.type})[q/b/value/enter to skip]"
							value=Prompt.__init2__(None,func=mkT,ptext=pt,helpText=self.help(print_no=True),data=column.name)
						data[column.name]=value
						data['InList']=True
					newEntry=Entry(**data)
					with Session(self.engine) as session:
						session.add(newEntry)
						session.commit()
						session.flush()
						session.refresh(newEntry)
						print(newEntry)
					break
				except Exception as e:
					print(e)
		return False
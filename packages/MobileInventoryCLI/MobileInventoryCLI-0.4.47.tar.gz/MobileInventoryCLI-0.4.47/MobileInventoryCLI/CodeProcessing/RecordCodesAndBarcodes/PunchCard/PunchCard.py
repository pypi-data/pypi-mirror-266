import pandas as pd
import csv
from datetime import datetime
from pathlib import Path
from colored import Fore,Style,Back
from barcode import Code39,UPCA,EAN8,EAN13
import barcode,qrcode,os,sys,argparse
from datetime import datetime,timedelta,date
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
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.ConvertCode.ConvertCode import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.setCode.setCode import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.Locator.Locator import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.ListMode2.ListMode2 import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.TasksMode.Tasks import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.ExportList.ExportListCurrent import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.Prompt import *


import MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.possibleCode as pc

class PunchCard:
	datePicker=datePickerF
	datetimePicker=datetimePickerF
	""" def datePicker(self):
					while True:
						try:
							def mkT(text,self):
								return text
							year=Prompt.__init2__(None,func=mkT,ptext=f"Year[{datetime.now().year}]",helpText="year to look for",data=self)
							if year == None:
								return
							elif year == '':
								year=datetime.now().year
			
							month=Prompt.__init2__(None,func=mkT,ptext=f"Month[{datetime.now().month}]",helpText="month to look for",data=self)
							if month == None:
								return
							elif month == '':
								month=datetime.now().month
			
							day=Prompt.__init2__(None,func=mkT,ptext=f"Day[{datetime.now().day}]",helpText="day to look for",data=self)
							if day == None:
								return
							elif day == '':
								day=datetime.now().day
			
							dt=date(int(year),int(month),int(day))
							return dt
						except Exception as e:
							print(e)
			
			
	def datetimePicker(self,DATE=None):
		while True:
			try:
				if DATE == None:
					DATE=self.datePicker()
				year=DATE.year
				month=DATE.month
				day=DATE.day

				def mkint(text,self):
					if text == '':
						if self == 'hour':
							return datetime.now().hour
						elif self == 'minute':
							return datetime.now().minute
						elif self == "second":
							return datetime.now().second
						else:
							return 0
					else:
						v=int(text)
						if v < 0:
							raise Exception("Must be greater than 0")
						return v

				hour=Prompt.__init2__(None,func=mkint,ptext="Hour",helpText=f"hour to use for {self}",data="hour")
				if hour == None:
					continue
				minute=Prompt.__init2__(None,func=mkint,ptext="Minute",helpText=f"minute to use for {self}",data="minute")
				if minute == None:
					continue
				second=Prompt.__init2__(None,func=mkint,ptext="Second",helpText=f"second to use  for {self}",data="second")
				if second == None:
					continue
				dt=datetime(year,month,day,hour,minute,second)

				return dt
			except Exception as e:
				print(e)"""
	def __init__(self,engine,parent):
		self.engine=engine
		self.parent=parent
		self.helpText=f'''
{Fore.light_green}ps|start{Style.reset} -{Fore.cyan} punch today's card{Style.reset}
{Fore.light_green}pe|end{Style.reset} -{Fore.cyan} punch out{Style.reset}
{Fore.light_green}brks|break_start{Style.reset} -{Fore.cyan} start your break{Style.reset}
{Fore.light_green}brke|break_end{Style.reset} -{Fore.cyan} end your break{Style.reset}
{Fore.light_green}clrd|clear_date{Style.reset} -{Fore.cyan} clear shift for date{Style.reset}
{Fore.light_green}ca|clear_all{Style.reset} -{Fore.cyan} clear all punches{Style.reset}

{Fore.light_green}ed|edit_date{Style.reset} -{Fore.cyan} edit a date's punch{Style.reset}
{Fore.light_green}vd|view_date{Style.reset} -{Fore.cyan} view a date's data{Style.reset}
{Fore.light_green}vdr|view_date_range{Style.reset} -{Fore.cyan} view a date ranges data{Style.reset}
{Fore.light_green}d|duration{Style.reset} -{Fore.cyan} view current punch's duration{Style.reset}
{Fore.light_green}va|view_all{Style.reset} -{Fore.cyan} view all punches{Style.reset}
{Fore.light_green}gross{Style.reset} -{Fore.cyan}calculate gross income from prompted date's total duration with rate of pay as hourly{Style.reset}
{Fore.light_green}e[4..8]{Style.reset} -{Fore.cyan}estimate shift punches from datetime.now(){Style.reset}
{Fore.light_green}me[4..8]|manual_estimate_[4..8]h{Style.reset} -{Fore.cyan}manually estimate shift punches from datetime.now(){Style.reset}
{Fore.light_green}enow|estimate_now|shift_help{Style.reset} -{Fore.cyan}show estimated punch data for Right-Now!{Style.reset}
'''
		def mkT(text,self):
			return text
		while True:
			cmd=Prompt.__init2__(None,func=mkT,ptext="Do What?",helpText=self.helpText,data=self)
			if cmd in [None,]:
				return

			if cmd.lower() in ['gross',]:
				def mkF(text,self):
					try:
						return float(text)
					except Exception as e:
						print(e)
						return -1
				while True:
					try:
						with Session(engine) as session:
							d=self.datePicker()
							if not d:
								break
							s=session.query(Shift).filter(Shift.Date==d).first()
							if s:
								print(s)
								rate=Prompt.__init2__(None,func=mkF,ptext="Rate of Pay?",helpText="your rate of pay",data=self)
								if rate in [None,]:
									break
								s.gross(rate=rate)
							else:
								print(f"{Fore.light_red}No Punches For that date!{Style.reset}")
							break
					except Exception as e:
						print(e)
			elif cmd.lower() in ['e8']:
				Shift.estimatedPunches_8h(None)
			elif cmd.lower() in ['me8','manual_estimate_8h']:
				Shift.manual_estimate_8(Shift)
			elif cmd.lower() in ['e7']:
				Shift.estimatedPunches_7h(None)
			elif cmd.lower() in ['me7','manual_estimate_7h']:
				Shift.manual_estimate_7(Shift)
			elif cmd.lower() in ['e6']:
				Shift.estimatedPunches_6h(None)
			elif cmd.lower() in ['me6','manual_estimate_6h']:
				Shift.manual_estimate_6(Shift)
			elif cmd.lower() in ['e5']:
				Shift.estimatedPunches_5h(None)
			elif cmd.lower() in ['me5','manual_estimate_5h']:
				Shift.manual_estimate_5(Shift)
			elif cmd.lower() in ['e4']:
				Shift.estimatedPunches_4h(None)
			elif cmd.lower() in ['me4','manual_estimate_4h']:
				Shift.manual_estimate_4(Shift)
			elif cmd.lower() in ['ps','start']:
				with Session(engine) as session:
					d=self.datePicker()
					#dt=self.datePicker()
					s=session.query(Shift).filter(Shift.Date==d).first()
					if s:
						s.duration_completed()
					else:
						pcard=Shift(Date=d,start=datetime.now())
						session.add(pcard)
						session.commit()
						session.refresh(pcard)
						pcard.duration_completed()
			elif cmd.lower() in ['pe','end']:
				with Session(engine) as session:
					s=session.query(Shift).filter(Shift.Date==self.datePicker()).first()
					if s:
						if s and not s.end:
							s.end=datetime.now()
							session.commit()
							session.flush()
							session.refresh(s)
						elif s and s.end:
							print(f"{Fore.light_yellow}Your Shift {Fore.light_red}End{Fore.light_yellow} has already been punched today... {Fore.medium_violet_red}Nothing will be done!{Style.reset}")

						s.duration_completed()
					else:
						print(f"{Fore.light_red}No Punches Today{Style.reset}")
			elif cmd.lower() in ['d','duration',]:
				with Session(engine) as session:
					s=session.query(Shift).filter(Shift.Date==self.datePicker()).first()
					if s:
						
						s.duration_completed()
						print(s)
					else:
						print(f"{Fore.light_red}No Punches Today{Style.reset}")
			elif cmd.lower() in ['enow','estimate_now','shift_help']:
				Shift(start=datetime.now()).helpCard()
			elif cmd.lower() in ['brs','break_start','brks']:
				with Session(engine) as session:
					s=session.query(Shift).filter(Shift.Date==self.datePicker()).first()
					if s and not s.break_start:
						s.break_start=datetime.now()
						session.commit()
						session.flush()
						session.refresh(s)
					elif s and s.break_start:
						print(f"{Fore.light_yellow}A Break {Fore.sea_green_1a}Start{Fore.light_yellow} has already been punched today... {Fore.medium_violet_red}Nothing will be done!{Style.reset}")
					s.duration_completed()
			elif cmd.lower() in ['bre','break_end','brke']:
				with Session(engine) as session:
					s=session.query(Shift).filter(Shift.Date==self.datePicker()).first()
					if s and not s.break_end:
						s.break_end=datetime.now()
						session.commit()
						session.flush()
						session.refresh(s)
					elif s and s.break_end:
						print(f"{Fore.light_yellow}A Break {Fore.red}End{Fore.light_yellow} has already been punched today... {Fore.medium_violet_red}Nothing will be done!{Style.reset}")
					s.duration_completed()
			elif cmd.lower() in ['clrd','clear_date',]:
				with Session(engine) as session:
					s=session.query(Shift).filter(Shift.Date==self.datePicker()).delete()
					print(f"deleted: {s}")
					session.commit()
			elif cmd.lower() in ['ed','edit_date']:
				while True:
					try:
						'''
						def mkT(text,self):
							return text
						year=Prompt.__init2__(None,func=mkT,ptext=f"Year[{datetime.now().year}]",helpText="year to look for",data=self)
						if year == None:
							return
						elif year == '':
							year=datetime.now().year

						month=Prompt.__init2__(None,func=mkT,ptext=f"Month[{datetime.now().month}]",helpText="month to look for",data=self)
						if month == None:
							return
						elif month == '':
							month=datetime.now().month

						day=Prompt.__init2__(None,func=mkT,ptext=f"Day[{datetime.now().day}]",helpText="day to look for",data=self)
						if day == None:
							return
						elif day == '':
							day=datetime.now().day

						dt=date(int(year),int(month),int(day))
						'''
						dt=self.datePicker()
						if not dt:
							continue

						with Session(self.engine) as session:
							query=session.query(Shift).filter(Shift.Date==dt)
							result=query.first()
							if not result:
								print(f"{Fore.light_red}No Shift for that date!")
								break
							for col in Shift.__table__.columns:
								while True:
									if col.name not in ['Date','ShiftId']:
										def mkTime(text,self):
											print(text)
											if text == 'now':
												nv=datetime.now()
												return
											if text in ['skip','']:
												return
											elif text.lower() in ['y','yes']:
												try:
													def mkint(text,self):
														if text == '':
															if self == 'hour':
																return datetime.now().hour
															elif self == 'minute':
																return datetime.now().minute
															elif self == "second":
																return datetime.now().second
															else:
																return 0
														else:
															v=int(text)
															if v < 0:
																raise Exception("Must be greater than 0")
															return v

													hour=Prompt.__init2__(None,func=mkint,ptext="Hour",helpText=f"hour to use for {self}",data="hour")
													if hour == None:
														return
													minute=Prompt.__init2__(None,func=mkint,ptext="Minute",helpText=f"minute to use for {self}",data="minute")
													if minute == None:
														return
													second=Prompt.__init2__(None,func=mkint,ptext="Second",helpText=f"second to use  for {self}",data="second")
													if second == None:
														return
													dtime=datetime(dt.year,dt.month,dt.day,hour,minute,second)
													return dtime
												except Exception as e:
													return None

										value=Prompt.__init2__(None,func=mkTime,ptext=f"{col.name} old[{getattr(result,col.name)}]",helpText=f"set {col} to new value!",data=col.name)
										if value == None:
											break
											
										setattr(result,col.name,value)
										session.commit()
										session.flush()
										session.refresh(result)
										print(result)
										break
									else:
										break

						break
					except Exception as e:
						print(e)
			elif cmd.lower() in ['ca','clear_all']:
				with Session(self.engine) as session:
					result=session.query(Shift).delete()
					session.commit()
					print(f"deleted {result}!")
			elif cmd.lower() in ['va','view_all']:
				with Session(self.engine) as session:
					result=session.query(Shift).all()
					ct=len(result)
					if ct == 0:
						print(f"{Fore.red}No Results{Style.reset}")
					else:
						for num,r in enumerate(result):
							print(f"{Fore.light_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} -> {r}")

			elif cmd.lower() in ['vd','view_date']:
				while True:
					try:
						'''
						def mkT(text,self):
							return text
						year=Prompt.__init2__(None,func=mkT,ptext=f"Year[{datetime.now().year}]",helpText="year to look for",data=self)
						if year == None:
							return
						elif year == '':
							year=datetime.now().year

						month=Prompt.__init2__(None,func=mkT,ptext=f"Month[{datetime.now().month}]",helpText="month to look for",data=self)
						if month == None:
							return
						elif month == '':
							month=datetime.now().month

						day=Prompt.__init2__(None,func=mkT,ptext=f"Day[{datetime.now().day}]",helpText="day to look for",data=self)
						if day == None:
							return
						elif day == '':
							day=datetime.now().day

						dt=date(int(year),int(month),int(day))
						'''
						dt=self.datePicker()
						with Session(self.engine) as session:
							query=session.query(Shift).filter(Shift.Date==dt)
							results=query.all()
							ct=len(results)
							for num,r in enumerate(results):
								print(f"{Fore.green_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} -> {r}")
							print(f"There are {Fore.grey_70}{Style.underline}{ct}{Style.reset} total results!")

						break
					except Exception as e:
						print(e)
			elif cmd.lower() in ['vdr','view_date_range']:
				while True:
					try:
						print(f"{Fore.green_yellow}Start Date{Style.reset}")
						dtS=self.datePicker()
						print(f"{Fore.medium_violet_red}End Date{Style.reset}")
						dtE=self.datePicker()
						def mkF(text,self):
							try:
								return float(text)
							except Exception as e:
								return -1
						rate=0
						while True:
							try:
								rate=Prompt.__init2__(None,func=mkF,ptext="Rate of Pay:",helpText="how much do you make per hour?",data=self)
								if rate == None:
									return
								elif rate == -1:
									continue
								break
							except Exception as e:
								print(e)


						with Session(self.engine) as session:
							query=session.query(Shift).filter(Shift.Date.between(dtS,dtE))
							results=query.all()
							ct=len(results)
							total_gross=0
							for num,r in enumerate(results):
								print(f"{Fore.green_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} - Supplementary Data")
								r.duration_completed()
								try:
									total_gross+=r.gross(rate=rate)
								except Exception as e:
									print(e)
								print(f"{Fore.green_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} -> {r}")
								print(f"{Fore.light_red}{'-'*20}{Style.reset}")
							print(f"There are {Fore.grey_70}{Style.underline}{ct}{Style.reset} total results!")
							print(f"A {Fore.green}Total Gross{Style.reset} of {Fore.light_green}${total_gross}{Style.reset} was made!")

						break
					except Exception as e:
						print(e)


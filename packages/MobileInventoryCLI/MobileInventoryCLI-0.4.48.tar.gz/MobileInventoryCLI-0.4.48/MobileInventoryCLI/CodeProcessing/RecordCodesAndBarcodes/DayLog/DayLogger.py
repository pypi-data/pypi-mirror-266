from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.db import *
from datetime import date
import calendar

class DayLogger:
	helpText=f"""
{Fore.light_magenta}''|?|help{Style.reset} -{Fore.light_yellow} help info{Style.reset}
{Fore.light_magenta}q|quit{Style.reset}	  -{Fore.light_yellow} quit{Style.reset}
{Fore.light_magenta}b|back{Style.reset}    -{Fore.light_yellow} back{Style.reset}
{Fore.light_magenta}a|add|+{Style.reset}   -{Fore.light_yellow} store todays data values as a daylog snapshot{Style.reset}
{Fore.light_magenta}l|list|*{Style.reset}  -{Fore.light_yellow} list * entries{Style.reset}
{Fore.light_magenta}ld|list_date{Style.reset}  -{Fore.light_yellow} list * entries from DayLogDate from prompt{Style.reset}
{Fore.light_magenta}cd|clear_date{Style.reset}  -{Fore.light_yellow} clear * entries from DayLogDate from prompt for date{Style.reset}
{Fore.light_magenta}ca|clear_all{Style.reset}  -{Fore.light_yellow} clear * entries from DayLogDate{Style.reset}
{Fore.light_magenta}ed|export_date{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate from prompt{Style.reset}
{Fore.light_magenta}ea|export_all{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate from prompt{Style.reset}
{Fore.light_magenta}ec|export_code{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate by Barcode from prompt{Style.reset}
{Fore.light_magenta}lc|list_code{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate by Barcode from prompt{Style.reset}
{Fore.light_magenta}ecd|export_code_date{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate by Barcode and Date from prompt{Style.reset}
{Fore.light_magenta}lcd|list_code_date{Style.reset}  -{Fore.light_yellow} list * entries from DayLogDate by Barcode and Date from prompt{Style.reset}
{Fore.light_red}
prefixes for #code:
		.d - daylog id
		.b - barcode
		.c - code/shelf tag barcode/cic
{Style.reset}
"""
	def listAllDL(self):
		with Session(self.engine) as session:
			results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items!{Style.reset}")
			for r in results:
				print(r)

	def clearAllDL(self):
		with Session(self.engine) as session:
			results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items to Clear!{Style.reset}")
			for num,r in enumerate(results):
				print(f"{num}/{ct} -{r}")
				session.delete(r)
				if num % 25 == 0:
					session.commit()
			session.commit()

	def addToday(self):
		with Session(self.engine) as session:
			results=session.query(Entry).filter(Entry.InList==True).all()
			ct=len(results)
			if ct < 1:
				print(f"{Fore.light_red}No Items InList==True!{Style.reset}")
			else:
				for num,entry in enumerate(results):
					print(f"Adding Log For\n{'-'*12}{Fore.green}{num}{Style.reset}/{Fore.red}{ct}{Style.reset} -> {entry}")
					#ndl=DayLog()
					d={}
					for column in Entry.__table__.columns:
						d[column.name]=getattr(entry,column.name)
					ndl=DayLog(**d)
					session.add(ndl)
					if num % 25 == 0:
						session.commit()
				session.commit()
				session.flush()
				print(f"{Fore.light_magenta}Done Adding Log Data!{Style.reset}")

	def clearDate(self,month=None,day=None,year=None):
		d=self.dateParser()
		with Session(self.engine) as session:
			results=session.query(DayLog).filter(DayLog.DayLogDate==d).all()
			ct=len(results)
			#results=session.query(DayLog).all()
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items to Clear!{Style.reset}")
			for num,r in enumerate(results):
				print(f"clearing {num}/{ct} -> {r}")
				session.delete(r)
				if num % 25 == 0:
					session.commit()
			session.commit()

	def listDate(self,month=None,day=None,year=None):
		d=self.dateParser()
		with Session(self.engine) as session:
			results=session.query(DayLog).filter(DayLog.DayLogDate==d).all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Date!{Style.reset}")
			for r in results:
				print(r)


	def exportAllDL(self):
		with Session(self.engine) as session:
			results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items!{Style.reset}")
			for num,r in enumerate(results):
				r.saveItemData(num=num)

	def dateParser(self,month=None,day=None,year=None):
		if not year:
			year=input(f"Year? [{datetime.now().year}]: ")
			if year.lower()  in ['q','quit']:
				exit('user quit!')
			elif year.lower() in ['b','back']:
				raise Exception("User Request to back a menu")
			elif year == '':
				year=datetime.now().year
		try:
			year=int(year)
		except Exception as e:
			raise e

		if not month:
			month=input(f"Month?: [1..12]: ")
			if month.lower()  in ['q','quit']:
				exit('user quit!')
			elif month.lower() in ['b','back']:
				raise Exception("User Request to back a menu")
			elif month == '':
				month=datetime.now().month
		try:
			month=int(month)
			if month < 1:
				raise Exception("Month Must be within 1..12")
			if month > 12:
				raise Exception("Month Must be within 1..12")
		except Exception as e:
			raise e
		if not day:
			day=input(f"Day? [1..{calendar.monthrange(year=year,month=month)[-1]}]: ")
			if day.lower()  in ['q','quit']:
				exit('user quit!')
			elif day.lower() in ['b','back']:
				raise Exception("User Request to back a menu")
			elif day == '':
				day=datetime.now().day
		try:
			day=int(day)
			if day < 1:
				raise Exception("Month Must be within 1..31")

			#february
			if month == 2:
				if day > 28 and not calendar.isleap(year):
					raise Exception("Day Must be within 1..28")
				elif day > 29 and calendar.isleap(year):
					raise Exception("Day Must be within 1..29")
				
			else:
				if day > 28 and month in [num for num,i in enumerate(calendar.mdays) if i == 28]:
					raise Exception("Day Must be within 1..28")
				elif day > 29 and month in [num for num,i in enumerate(calendar.mdays) if i == 29]:
					raise Exception("Day Must be within 1..29")
				elif day > 30 and month in [num for num,i in enumerate(calendar.mdays) if i == 30]:
					raise Exception("Day Must be within 1..30")
				elif day > 31 and month in [num for num,i in enumerate(calendar.mdays) if i == 31]:
					raise Exception("Day Must be within 1..31")
		except Exception as e:
			raise e
		d=date(year,month,day)
		print(f"{Fore.green}Date Generated: {Style.reset}{Fore.light_yellow}{d}{Style.reset}")
		return d

	def exportDate(self,month=None,day=None,year=None):
		d=self.dateParser()
		print(d)
		with Session(self.engine) as session:
			results=session.query(DayLog).filter(DayLog.DayLogDate==d).all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Date!{Style.reset}")
			for num,r in enumerate(results):
				#print(f"{num}/{ct} -> {r}")
				r.saveItemData(num=num)

	def listCode(self,code=None):
		#d=self.dateParser()
		#print(d)
		if not code:
			code=input("Barcode|Code|ItemCode: ")
			if code.lower() in ['quit','q']:
				exit("user quit!")
			elif code.lower() in ['back','b']:
				return
		prefix=code.split(".")[0]
		cd=code.split(".")[-1]

		with Session(self.engine) as session:
			results=session.query(DayLog)
			if prefix.lower() in ['d',]:
				results=results.filter(DayLog.DayLogId==int(cd))
			elif prefix.lower() in ['b',]:
				results=results.filter(DayLog.Barcode==cd)
			elif prefix.lower() in ['c']:
				results=results.filter(DayLog.Code==cd)
			else:
				results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd))
			results=results.all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
			for num,r in enumerate(results):
				print(f"{num}/{ct} -> {r}")
				#r.saveItemData(num=num)

	def exportCode(self,code=None):
		#d=self.dateParser()
		#print(d)
		if not code:
			code=input("Barcode|Code|ItemCode: ")
			if code.lower() in ['quit','q']:
				exit("user quit!")
			elif code.lower() in ['back','b']:
				return
		prefix=code.split(".")[0]
		cd=code.split(".")[-1]

		with Session(self.engine) as session:
			results=session.query(DayLog)
			if prefix.lower() in ['d',]:
				results=results.filter(DayLog.DayLogId==int(cd))
			elif prefix.lower() in ['b',]:
				results=results.filter(DayLog.Barcode==cd)
			elif prefix.lower() in ['c']:
				results=results.filter(DayLog.Code==cd)
			else:
				results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd))
			results=results.all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
			for num,r in enumerate(results):
				#print(f"{num}/{ct} -> {r}")
				r.saveItemData(num=num)

	def listCodeDate(self,code=None):
		d=self.dateParser()
		#print(d)
		if not code:
			code=input("Barcode|Code|ItemCode: ")
			if code.lower() in ['quit','q']:
				exit("user quit!")
			elif code.lower() in ['back','b']:
				return
		prefix=code.split(".")[0]
		cd=code.split(".")[-1]

		with Session(self.engine) as session:
			results=session.query(DayLog)
			if prefix.lower() in ['d',]:
				results=results.filter(DayLog.DayLogId==int(cd),DayLog.DayLogDate==d)
			elif prefix.lower() in ['b',]:
				results=results.filter(DayLog.Barcode==cd,DayLog.DayLogDate==d)
			elif prefix.lower() in ['c']:
				results=results.filter(DayLog.Code==cd,DayLog.DayLogDate==d)
			else:
				results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd),DayLog.DayLogDate==d)
			results=results.all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
			for num,r in enumerate(results):
				print(f"{num}/{ct} -> {r}")
				#r.saveItemData(num=num)

	def exportCodeDate(self,code=None):
		d=self.dateParser()
		#print(d)
		if not code:
			code=input("Barcode|Code|ItemCode: ")
			if code.lower() in ['quit','q']:
				exit("user quit!")
			elif code.lower() in ['back','b']:
				return
		prefix=code.split(".")[0]
		cd=code.split(".")[-1]

		with Session(self.engine) as session:
			results=session.query(DayLog)
			if prefix.lower() in ['d',]:
				results=results.filter(DayLog.DayLogId==int(cd),DayLog.DayLogDate==d)
			elif prefix.lower() in ['b',]:
				results=results.filter(DayLog.Barcode==cd,DayLog.DayLogDate==d)
			elif prefix.lower() in ['c']:
				results=results.filter(DayLog.Code==cd,DayLog.DayLogDate==d)
			else:
				results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd),DayLog.DayLogDate==d)
			results=results.all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
			for num,r in enumerate(results):
				#print(f"{num}/{ct} -> {r}")
				r.saveItemData(num=num)


	def __init__(self,engine):
		self.engine=engine

		while True:
			try:
				what=input(f"{Fore.light_red}Do what? {Style.reset}[{Fore.green_yellow}?{Style.reset}|{Fore.green_yellow}help{Style.reset}]: ")
				if what.lower() in ['','?','help']:
					print(self.helpText)
				elif what.lower() in ['b','back']:
					return
				elif what.lower() in ['q','quit']:
					exit("user quit!")
				else:
					if what.lower() in ['a','add','+']:
						self.addToday()
					elif what.lower() in 'l|list|*'.split('|'):
						self.listAllDL()
					elif what.lower() in 'ld|list_date'.split('|'):
						self.listDate()
					elif what.lower() in 'cd|clear_date'.split("|"):
						self.clearDate()
					elif what.lower() in 'ca|clear_all'.split("|"):
						self.clearAllDL()
					elif what.lower() in 'ea|export_all'.split("|"):
						self.exportAllDL()
					elif what.lower() in 'ed|export_date'.split("|"):
						self.exportDate()
					elif what.lower() in 'ec|export_code'.split("|"):
						self.exportCode()
					elif what.lower() in 'lc|list_code'.split("|"):
						self.listCode()
					elif what.lower() in 'ecd|export_code_date'.split("|"):
						self.exportCodeDate()
					elif what.lower() in 'lcd|list_code_date'.split("|"):
						self.listCodeDate()
										
			except Exception as e:
				print(e)


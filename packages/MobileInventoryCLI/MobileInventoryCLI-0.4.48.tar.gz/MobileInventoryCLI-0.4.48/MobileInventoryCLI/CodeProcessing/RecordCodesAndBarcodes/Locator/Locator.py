from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.Locator import *
import MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.possibleCode as pc



class Locator:
	helpText=f"""
	{Fore.green}{Style.underline}@ Shelf Code Prompt{Style.reset}
	{Fore.grey_50}bm|back to menu{Style.reset} - {Fore.grey_70}go back a menu{Style.reset}
	{Fore.cyan}bb|back to barcode{Style.reset} - {Fore.steel_blue}go back to barcode scanner{Style.reset}
	{Fore.grey_50}q|quit{Style.reset} - {Fore.grey_70}quit program{Style.reset}
	{Fore.cyan}?|help{Style.reset} - {Fore.steel_blue}display helpText{Style.reset}

	{Fore.green}{Style.underline}@ Barcode Promp{Style.reset}
	{Fore.grey_50}q|quit{Style.reset} - {Fore.grey_70}quit program{Style.reset}
	{Fore.cyan}b|back{Style.reset} - {Fore.steel_blue}back a menu{Style.reset}
	{Fore.grey_50}?|help{Style.reset} - {Fore.grey_70}display helpText{Style.reset}
	"""
	def __init__(self,engine):
		self.engine=engine
		while True:	
			product_barcode=input(f"{Fore.cyan}Barcode{Style.reset}: ")	
			if product_barcode.lower() in ['b','back']:
					return
			elif product_barcode.lower() in ['q','quit']:
				exit("user quit!")
			elif product_barcode.lower() in ['?','help']:
				print(self.helpText)
				continue
			pc.PossibleCodes(scanned=product_barcode)
			pc.PossibleCodesEAN13(scanned=product_barcode)
			while True:
				shelf_code=input(f"{Fore.magenta}Shelf Code{Fore.red}[or Barcode to exit]{Style.reset}: ")
				#if shelf_code == product_barcode and shelf_code not in ['?','help']:
				#	print(f"{Fore.green_yellow}Barcode == Shelf Code - exit action taken!{Style.reset}")
				#	return
				#el
				if shelf_code.lower() in ['q','quit']:
					exit("user quit!")
				elif shelf_code.lower() in ['bb','back to barcode']:
					break
				elif shelf_code.lower() in ['bm','b','back to menu']:
					return
				elif shelf_code.lower() in ['','skip','na']:
					continue
				elif shelf_code.lower() in ['?','help']:
					print(self.helpText)
					continue
				else:
					with Session(engine) as session:
						query_barcode=session.query(Entry).filter(Entry.Barcode==product_barcode).first()
						if query_barcode:
							query_shelf_code=session.query(Entry).filter(Entry.Code==shelf_code).first()
							if not query_shelf_code and len(shelf_code) in [11,12]:
								print(f"{shelf_code} - {len(shelf_code)} {Fore.green_yellow}{Style.underline} KeHe/ORD Tag!!!{Style.reset}")
								query_shelf_code=session.query(Entry).filter(Entry.Barcode.icontains(shelf_code)).first()
							if query_shelf_code:
								if query_barcode.EntryId == query_shelf_code.EntryId:
									print(f"{Fore.green_yellow}{Style.bold}Match!{Style.reset}"*30)
									break
								else:
									print(f"{Fore.yellow}{Style.bold}Not a Match!{Style.reset}")
							else:
								print(f"{Fore.yellow}{Style.underline}No Such Shelf Code!")
						else:
							print(f"{Fore.yellow}{Style.underline}No Such Barcode found{Style.reset}")

class Locator2:
	helpText=f"""
	{Fore.magenta}{Style.bold}
This Version of the Shelf Locator uses the PairCollections Table,
which is independent of the Entry's table which will yield results
not in the Entry Table{Style.reset}

	{Fore.green}{Style.underline}@ Shelf Code Prompt{Style.reset}
	{Fore.grey_50}bm|back to menu{Style.reset} - {Fore.grey_70}go back a menu{Style.reset}
	{Fore.cyan}bb|back to barcode{Style.reset} - {Fore.steel_blue}go back to barcode scanner{Style.reset}
	{Fore.grey_50}q|quit{Style.reset} - {Fore.grey_70}quit program{Style.reset}
	{Fore.cyan}?|help{Style.reset} - {Fore.steel_blue}display helpText{Style.reset}

	{Fore.green}{Style.underline}@ Barcode Promp{Style.reset}
	{Fore.grey_50}q|quit{Style.reset} - {Fore.grey_70}quit program{Style.reset}
	{Fore.cyan}b|back{Style.reset} - {Fore.steel_blue}back a menu{Style.reset}
	{Fore.grey_50}?|help{Style.reset} - {Fore.grey_70}display helpText{Style.reset}
	"""
	def __init__(self,engine):
		self.engine=engine
		while True:	
			product_barcode=input(f"{Fore.cyan}Barcode{Style.reset}: ")	
			if product_barcode.lower() in ['b','back']:
					return
			elif product_barcode.lower() in ['q','quit']:
				exit("user quit!")
			elif product_barcode.lower() in ['?','help']:
				print(self.helpText)
				continue
			pc.PossibleCodes(scanned=product_barcode)
			pc.PossibleCodesEAN13(scanned=product_barcode)
			while True:
				shelf_code=input(f"{Fore.magenta}Shelf Code{Fore.red}[or Barcode to exit]{Style.reset}: ")
				#if shelf_code == product_barcode and shelf_code not in ['?','help']:
				#	print(f"{Fore.green_yellow}Barcode == Shelf Code - exit action taken!{Style.reset}")
				#	return
				#el
				if shelf_code.lower() in ['q','quit']:
					exit("user quit!")
				elif shelf_code.lower() in ['bb','back to barcode']:
					break
				elif shelf_code.lower() in ['bm','b','back to menu']:
					return
				elif shelf_code.lower() in ['','skip','na']:
					continue
				elif shelf_code.lower() in ['?','help']:
					print(self.helpText)
					continue
				else:
					with Session(engine) as session:
						query_barcode=session.query(PairCollection).filter(PairCollection.Barcode==product_barcode).first()
						if query_barcode:
							query_shelf_code=session.query(PairCollection).filter(PairCollection.Code==shelf_code).first()
							if not query_shelf_code and len(shelf_code) in [11,12]:
								print(f"{shelf_code} - {len(shelf_code)} {Fore.green_yellow}{Style.underline} KeHe/ORD Tag!!!{Style.reset}")
								query_shelf_code=session.query(PairCollection).filter(PairCollection.Barcode.icontains(shelf_code)).first()
							if query_shelf_code:
								if query_barcode.PairCollectionId == query_shelf_code.PairCollectionId:
									print(f"{Fore.green_yellow}{Style.bold}Match!{Style.reset}"*30)
									break
								else:
									print(f"{Fore.yellow}{Style.bold}Not a Match!{Style.reset}")
							else:
								print(f"{Fore.yellow}{Style.underline}No Such Shelf Code!")
						else:
							print(f"{Fore.yellow}{Style.underline}No Such Barcode found{Style.reset}")



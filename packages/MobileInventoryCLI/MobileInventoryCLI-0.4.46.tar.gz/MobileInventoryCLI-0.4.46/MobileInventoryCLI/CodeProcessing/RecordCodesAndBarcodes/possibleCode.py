import upcean
from barcode import UPCA,EAN13
from colored import Fore,Style,Back
from copy import deepcopy

class PossibleCodesEAN13:
    def __init__(self,scanned,skip_retry=True):
        print("EAN13 to Shelf Code Mode! [Start]")
        while True:
            try:
                if len(scanned) == 13:
                    ean13_verified=EAN13(scanned)
                    ean13_stripped_0=str(ean13_verified)[0:-1]
                    ean13_stripped_1=int(str(ean13_verified)[0:-1])
                    ean13_stripped_2=str(int(str(ean13_verified)))[0:-1]

                    print(f"""
{Fore.blue}Scannen Code{Style.reset}:{scanned}
{Fore.cyan}EAN13 Verified{Style.reset}:{ean13_verified}
{Fore.green}EAN13 Stripped 0{Style.reset}:{ean13_stripped_0}
{Fore.green_yellow}EAN13 Stripped 1{Style.reset}:{ean13_stripped_1}
{Fore.yellow}EAN13 Stripped 2{Style.reset}:{ean13_stripped_2}
                        """)
                    break
                else:
                    break
            except Exception as e:
                if skip_retry:
                    break
                print(e)
        print("EAN13 to Shelf Code [Stop]")

class PossibleCodes:
    def __init__(self,scanned,use_ean13=False):
        print(f"--- Start Code=UPC=Barcode ---{scanned}---")
        try:
            if use_ean13:
                scanned_ean13=deepcopy(scanned)
            isUPC=True
            if len(scanned) > 8:
                if len(scanned) < 11:
                    scanned=scanned.zfill(11)
                elif len(scanned) == 13:
                    #scanned=scanned[(11-len(scanned)):len(scanned)]
                    scanned=scanned[len(scanned)-11:len(scanned)]
                 
                upca=UPCA(scanned)
                upcas=str(upca)
                upce=upcean.convert.convert_barcode_from_upca_to_upce(str(upca))
                upca_stripped=str(upca)
                upcas=upca_stripped
                upca_ean2=upcean.convert.convert_barcode_from_upca_to_ean13(upcas)
                upca_stripped=str(int(upca_stripped))
                upca_stripped=upca_stripped[:-1]
                print(
            f"""
{Fore.tan}{Style.underline}Telethon Code #:{Style.reset} -> {Fore.pale_green_1b}{Style.bold}{upcas[0:-1]}{Style.reset}
{Fore.cyan}UPCA -> {upca}{Style.reset}
{Fore.green}{Style.underline}UPCA Stripped{Style.reset} -> {Fore.magenta}{Style.bold}{upca_stripped}{Style.reset}
{Fore.dark_goldenrod}{Style.underline}UPCE{Style.reset} -> {Fore.magenta}{Style.bold}{upce}{Style.reset}

                   """)
            else:
                upca=upcean.convert.convert_barcode_from_upce_to_upca(scanned)
                if upca:
                    upca=UPCA(upca)
                    upcas=str(upca)
                    upca_stripped=str(upca) 
                    upca_stripped=str(int(upca_stripped)) 
                    upca_stripped=upca_stripped[:-1]

                    print(f"""
{Fore.tan}{Style.underline}Telethon Code #:{Style.reset} -> {Fore.pale_green_1b}{Style.bold}{upcas[0:-1]}{Style.reset}
{Fore.green_yellow}UPCA-Checked -> {upca}{Style.reset}
{Fore.green}{Style.underline}UPCA Stripped{Style.reset} ->{Fore.magenta}{Style.bold}{upca_stripped}{Style.reset}""")

                print(f"""
{Fore.cyan}UPCA -> {upca}{Style.reset}
{Fore.yellow}{Style.underline}UPCE{Style.reset} ->{Fore.magenta}{Style.bold}{scanned}{Style.reset}
                """)
            print(f"{Fore.yellow}PickList Code -> {str(str(upca)[:-1]).zfill(13)}{Style.reset}")
        except Exception as e:
            print(e)
        print(f"--- End Code=UPC=Barcode ---{scanned}---")
        if use_ean13:
            PossibleCodesEAN13(scanned=scanned_ean13)
if __name__ == "__main__":
    PossibleCodes(scanned=input("code"))


def run():
    while True:
        code=input("code: ")
        if code.lower() in ['q','quit']:
            exit()
        elif code.lower() in ['b','back']:
            return
        else:
            try:
                print(f"{Fore.dark_goldenrod}{Style.underline}Scanned Length Info.\n{Style.res_underline}{Style.reset}{Fore.cyan}{code}{Style.reset} is {Fore.green}'{len(code)}'{Style.reset} characters long!")
                PossibleCodes(scanned=code,use_ean13=True)
            except Exception as e:
                print(str(e))
                print(repr(e))

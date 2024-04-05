import sqlalchemy,json
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base as dbase
from sqlalchemy.ext.automap import automap_base
from datetime import datetime,timedelta,date
from colored import Fore,Style,Back
from datetime import datetime,timedelta
from pathlib import Path
import pandas as pd
import tarfile,zipfile
import base64
import pint
import qrcode
import barcode
from barcode import UPCA,EAN13,Code39
from qrcode import QRCode
from barcode.writer import ImageWriter
import csv,string,random
import shutil,upcean
import MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.possibleCode as pc
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.renderText2Png import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.Prompt import *
import geocoder

filename="codesAndBarcodes.db"
DEVMOD=False
if DEVMOD:
    if Path(filename).exists():
        Path(filename).unlink()
dbfile="sqlite:///"+str(filename)
img_dir=Path("Images")
if not img_dir.exists():
    img_dir.mkdir()
print(dbfile)
#import sqlite3
#z=sqlite3.connect(filename)
#print(z)
ENGINE=create_engine(dbfile)
BASE=dbase()
#BASE.prepare(autoload_with=ENGINE)

def reInit(f=None,dbf=None):
    filename="codesAndBarcodes.db"
    dbfile="sqlite:///"+str(filename)
    if f:
        filename=f
    if dbf:
        dbfile=dbf
    if Path(filename).exists():
        Path(filename).unlink()
    ENGINE=create_engine(dbfile)
    Entry.metadata.create_all(ENGINE)
    DayLog.metadata.create_all(ENGINE)
    try:
        img_dir=Path("Images")
        if not img_dir.exists():
            img_dir.mkdir()
        else:
            shutil.rmtree(img_dir)
            img_dir.mkdir()
    except Exception as e:
        print(e)

    exit(f"A {Style.bold}{Style.underline}{Fore.yellow}Factory Reset{Style.reset} was performed. A {Style.bold}{Style.underline}{Fore.yellow}Restart{Style.reset} is {Style.bold}{Style.underline}{Fore.yellow}Required{Style.reset}.")


def removeImage(image_dir,img_name):
    try:
        if img_name != '':
            im=Path(image_dir)/Path(img_name)
            if im.exists():
                im.unlink()
                print(f"{im} removed from FS!")
    except Exception as e:
        print(e)

def importImage(image_dir,src_path,nname=None,ow=False):
    try:
        if not Path(image_dir).exists():
            Path(image_dir).mkdir()
        if not nname:
            dest=Path(image_dir)/Path(Path(src_path).name)
        else:
            dest=Path(image_dir)/Path(nname)
        if not ow and dest.exists():
            raise Exception(f'exists {dest}')
        if not Path(src_path).exists():
            raise Exception (f'src {src_path} does not exist!')
        size=Path(src_path). stat().st_size
        with dest.open('wb') as out, Path(src_path).open('rb') as ifile:
            while True:
                d=ifile.read(1024*1024)
                print(f'writing {len(d)} - {ifile.tell()}/{size}')
                if not d:
                    break
                out.write(d)
        return str(dest)
    except Exception as e:
        print(e)
        return ''

def save_results(query):
    while True:
        save_results=input(f"Save Results {Fore.cyan}y{Style.reset}|{Fore.yellow}N{Style.reset}] : ")
        if save_results.lower() in ['n','no']:
            return
        elif save_results.lower() in ['y','yes']:
            df = pd.read_sql(query.statement, query.session.bind,dtype=str)
            while True:
                saveTo=input("save to: ")
                print(f"Saving to '{Path(saveTo)}'!")
                if Path(saveTo).parent.exists():
                    df.to_csv(saveTo,index=False)
                    return
                print(Path(saveTo))
        else:
            print("Invalid Entry!")
class PairCollection(BASE):
    __tablename__="PairCollection"
    Barcode=Column(String)
    Code=Column(String)
    PairCollectionId=Column(Integer,primary_key=True)
    Name=Column(String)

    def __init__(self,Barcode,Code,Name='',PairCollectionId=None):
        if PairCollectionId:
            self.PairCollectionId=PairCollectionId
        self.Name=Name
        self.Barcode=Barcode
        self.Code=Code

    def __repr__(self):
        msg=f'''PairCollection(
            Barcode='{self.Barcode}',
            Code='{self.Code}',
            Name='{self.Name}',
            PairCollectionId={self.PairCollectionId},
        )'''
        return msg

    def __str__(self):
        msg=f'''PairCollection(
            {Fore.green}Barcode='{self.Barcode}',{Style.reset}
            {Fore.green_yellow}Code='{self.Code}',{Style.reset}
            {Fore.dark_goldenrod}Name='{self.Name}',{Style.reset}
            {Fore.yellow}PairCollectionId={self.PairCollectionId},{Style.reset}
        )'''
        return msg
    LCL=Path("LCL_IMG")
    LCL_ANDROID=Path("/storage/emulated/0/DCIM/Screenshots")

    def save_code(self):
        filename=Path(f"{self.PairCollectionId}_code.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[Code39,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Code).save(filename)
                        break
                    else:
                        code(self.Code,add_checksum=False,writer=ImageWriter()).write(filename)
                        break
                    pass
                except Exception as e:
                    print(e)


            return filename
        except Exception as e:
            print(e)
        return False

    def save_barcode(self):
        filename=Path(f"{self.PairCollectionId}_barcode.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[UPCA,EAN13,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Barcode).save(filename)
                        break
                    else:
                        if len(self.Barcode) <= 8 and code == UPCA:
                            upca=upcean.convert.convert_barcode_from_upce_to_upca(self.Barcode)
                            if upca != False:
                                code(upca,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        elif len(self.Barcode) > 12:
                            if code == EAN13:
                                code(self.Barcode,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        else:
                            code(self.Barcode,writer=ImageWriter()).write(filename)
                        break
                except Exception as e:
                    print(e)
            return filename


        except Exception as e:
            print(e)
        return False

    def saveItemData(self,num=None):
        if self.LCL_ANDROID.exists():
            self.LCL=self.LCL_ANDROID
        text=[]
        for column in self.__table__.columns:
            text.append('='.join([column.name,str(self.__dict__[column.name])]))
        data='\n'.join(text)
        #LCL=Path("LCL_IMG")
        if not self.LCL.exists():
            self.LCL.mkdir()
        fname=str(self.LCL/Path(str(self.PairCollectionId)))
        n=self.save_barcode()
        c=self.save_code()
        print(n,c)
        renderImageFromText(fname,data,barcode_file=n,code_file=c)

    def listdisplay(self,num=None):
        name=self.Name
        ma=32
        n=self.split_by_len(name,ma)
        #print(n)
        new=[]
        for i in n:
            if n.index(i) > 0:
                new.append(i)
            else:
                new.append(i)
        name='\n'.join(new)
        name="\n"+name
        if num == None:
            num=''
        msg=f'''{Fore.magenta}{Fore.dark_goldenrod}{num}->({Style.reset} NAME={Fore.cyan}{name}{Style.reset} | UPC={Fore.green}{self.Barcode}{Style.reset} | CODE={Fore.yellow}{self.Code}{Style.reset} |{self.PairCollectionId}{Style.reset}{Fore.magenta} )-<{Fore.dark_goldenrod}{num}{Style.reset}'''
        print(msg)
    def split_by_len(self,string, length):
        result = []
        for i in range(0, len(string), length):
            result.append(string[i:i + length])
        return result

class Entry(BASE):
    __tablename__="Entry"
    Code=Column(String)
    Barcode=Column(String)
    #not found in prompt requested by
    '''
    #name {Entryid}
    #name {Entryid} {new_value}
    
    #price {Entryid}
    #price {Entryid} {new_value}

    #note {Entryid}
    #note {Entryid} {new_value}
    
    #size {Entryid} 
    #size {Entryid} {new_value}
    '''
    Name=Column(String)
    Price=Column(Float)
    CRV=Column(Float)
    Tax=Column(Float)
    TaxNote=Column(String)
    Note=Column(String)
    Size=Column(String)
    
    CaseCount=Column(Integer)

    Shelf=Column(Integer)
    BackRoom=Column(Integer)
    Display_1=Column(Integer)
    Display_2=Column(Integer)
    Display_3=Column(Integer)
    Display_4=Column(Integer)
    Display_5=Column(Integer)
    Display_6=Column(Integer)
    InList=Column(Boolean)
    Stock_Total=Column(Integer)
    Location=Column(String)
    ListQty=Column(Float)
    upce2upca=Column(String)
    Image=Column(String)
    EntryId=Column(Integer,primary_key=True)
    Timestamp=Column(Float)

    ALT_Barcode=Column(String)
    DUP_Barcode=Column(String)
    CaseID_BR=Column(String)
    CaseID_LD=Column(String)
    CaseID_6W=Column(String)
    Tags=Column(String)
    Facings=Column(Integer)
    SBX_WTR_DSPLY=Column(Integer)
    SBX_CHP_DSPLY=Column(Integer)
    SBX_WTR_KLR=Column(Integer)
    FLRL_CHP_DSPLY=Column(Integer)
    FLRL_WTR_DSPLY=Column(Integer)
    WD_DSPLY=WD_DSPLY=Column(Integer)
    CHKSTND_SPLY=CHKSTND_SPLY=Column(Integer)
    def csv_headers(self):
        headers=[]
        for i in self.__table__.columns:
            headers.append(i.name)
        headers.append("DateFromTimeStamp")
        return headers

    def csv_values(self):
        values=[]
        for i in self.__table__.columns:
            value=self.__dict__.get(i.name)
            if isinstance(value,str):
                value=value.replace("\n","$NEWLINECHAR$").replace("\t","$TABCHAR$").replace(",","$COMMA$")
            values.append(value)
        values.append(datetime.fromtimestamp(self.Timestamp).ctime())
        print(f"""use: 
{Fore.light_blue}$NEWLINECHAR$ for {Fore.light_yellow}\\n{Style.reset} is for line ending
{Fore.light_blue}$TABCHAR$ for {Fore.light_yellow}\\t{Style.reset}
{Fore.light_blue}$COMMA$ for {Fore.light_yellow},{Style.reset} as {Fore.light_yellow},{Style.reset} is csv delimiter
                    """)
        return values
    def synthetic_field_str(self):
        f=string.ascii_uppercase+string.digits
        part=[]
        for num in range(4):
            part.append(f[random.randint(0,len(f)-1)])
        part.append("-")
        for num in range(4):
            part.append(f[random.randint(0,len(f)-1)])
        return ''.join(part)



    def __init__(self,Barcode,Code,upce2upca='',Name='',InList=False,Price=0.0,Note='',Size='',CaseCount=0,Shelf=0,BackRoom=0,Display_1=0,Display_2=0,Display_3=0,Display_4=0,Display_5=0,Display_6=0,Stock_Total=0,Timestamp=datetime.now().timestamp(),EntryId=None,Location='///',ListQty=0.0,Image='',CHKSTND_SPLY=0,WD_DSPLY=0,FLRL_CHP_DSPLY=0,FLRL_WTR_DSPLY=0,SBX_WTR_KLR=0,SBX_CHP_DSPLY=0,SBX_WTR_DSPLY=0,Facings=0,Tags='',CaseID_6W='',CaseID_BR='',CaseID_LD='',ALT_Barcode='',DUP_Barcode='',CRV=0.0,Tax=0.0,TaxNote=''):
        if EntryId:
            self.EntryId=EntryId
        self.CRV=CRV
        self.Tax=Tax
        self.TaxNote=TaxNote
        self.Barcode=Barcode
        self.Code=Code
        self.Name=Name
        self.Price=Price
        self.Note=Note
        self.Size=Size
        self.Shelf=Shelf
        self.CaseCount=CaseCount
        self.BackRoom=BackRoom
        self.Display_1=Display_1
        self.Display_2=Display_2
        self.Display_3=Display_3
        self.Display_4=Display_4
        self.Display_5=Display_5
        self.Display_6=Display_6
        self.Stock_Total=Stock_Total
        self.Location=Location
        self.Timestamp=Timestamp
        self.InList=InList
        self.ListQty=ListQty
        self.upce2upca=upce2upca
        self.Image=Image
        self.Tags=Tags
        self.Facings=Facings

        self.ALT_Barcode=ALT_Barcode
        self.DUP_Barcode=DUP_Barcode
        self.CaseID_BR=CaseID_BR
        self.CaseID_LD=CaseID_LD
        self.CaseID_6W=CaseID_6W
        self.SBX_WTR_DSPLY=SBX_WTR_DSPLY
        self.SBX_CHP_DSPLY=SBX_CHP_DSPLY
        self.SBX_WTR_KLR=SBX_WTR_KLR
        self.FLRL_CHP_DSPLY=FLRL_CHP_DSPLY
        self.FLRL_WTR_DSPLY=FLRL_WTR_DSPLY
        self.WD_DSPLY=WD_DSPLY
        self.CHKSTND_SPLY=CHKSTND_SPLY
        #CHKSTND_SPLY=0,WD_DSPLY=0,FLRL_CHP_DSPLY=0,FLRL_WTR_DSPLY=0,SBX_WTR_KLR=0,SBX_CHP_DSPLY=0,SBX_WTR_DSPLY=0,Facings=0,Tags='',CaseID_6W='',CaseID_BR='',CaseID_LD='',ALT_Barcode='',DUP_Barcode=''

        '''
        ALT_Barcode=Column(String)
        DUP_Barcode=Column(String)
        CaseID_BR=Column(String)
        CaseID_LD=Column(String)
        CaseID_6W=Column(String)
        Tags=Column(String)
        Facings=Column(Integger)
        SBX_WTR_DSPLY=Column(Integer)
        SBX_CHP_DSPLY=Column(Integer)
        SBX_WTR_KLR=Column(Integer)
        FLRL_CHP_DSPLY=Column(Integer)
        FLRL_WTR_DSPLY=Column(Integer)
        WD_DSPLY=WD_DSPLY=Column(Integer)
        CHKSTND_SPLY=CHKSTND_SPLY=Column(Integer)
        '''


        #proposed fields
        #[done]smle,s|search|? - calls a prompt to search for InList==True with CODE|BARCODE instead of direct search waits for b for back, q for quit, for next CODE|BARCODE
        #optional fields
        #self.alt_barcode
        #self.duplicate_code
        #self.case_id_backroom - in case specific case is needed to be logged
        #csidbm,$EntryId,generate - create a synthetic id for case and save item to and save qrcode png of $case_id
        #csidbm,$EntryId,$case_id - set case id for item
        #csidbm,$EntryId - display item case id
        #csidbm,s|search,$case_id - display items associated with $case_id
        #csidbm,$EntryId,clr_csid - set $case_id to ''
        #the above applies to the below self.case_id_load as well
        #self.case_id_load - in case specific is found in load wanted in data

        #self.Tags
        #cmd syntax
        #tag,$EntryID,+|-|=,$tag_text
        #tag,s|search,$tag_text -> search for items with tag txt (multiple tags separated with a bar '|'')
        #tag,$EntryId|$code|$barcode -> display tags for item with $entryId, $code (returns multiple values), $barcode (returns multiple values)
        #- removes tag from field with tags
        #+ adds a tag to field with tags
        #= set field to $tag_text
        #self.Tags is a string separated by json string containing a list of tags
        #json.dumps(['a','b','c'])
        #json.loads('["a", "b", "c"]')

        #self.Facings
        #additional inventory fields
        #self.checkstandsupplies
        #self.sbx_dsply
        #self.flrl_dsply
        #self.wd_dsply

        try:
            if not self.LCL_ANDROID.exists():
                self.LCL_ANDROID.mkdir(parents=True)
        except Exception as e:
            print(e,"android directory!")
    LCL=Path("LCL_IMG")
    LCL_ANDROID=Path("/storage/emulated/0/DCIM/Screenshots")

    def save_code(self):
        filename=Path(f"{self.EntryId}_code.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[Code39,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Barcode).save(filename)
                        break
                    else:
                        code(self.Code,add_checksum=False,writer=ImageWriter()).write(filename)
                        break
                    pass
                except Exception as e:
                    print(e)


            return filename
        except Exception as e:
            print(e)
        return False

    def save_field(self,fieldname=None):
        def mkT(text,self):
            return text
        if not fieldname:
            fieldname=Prompt.__init2__(self,func=mkT,ptext="Fieldname: ",helpText="Export FieldData to Encoded Img "+','.join([i.name for i in self.__table__.columns]),data=self)
        filename=Path(f"{self.EntryId}_{fieldname}.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[QRCode,]
            for code in codes:
                try:
                    filename_qr=Path(f"{self.EntryId}_{fieldname}_qr.png")
                    if self.LCL_ANDROID.exists():
                        filename_qr=str(self.LCL_ANDROID/filename_qr)
                    else:
                        filename_qr=str(self.LCL/filename_qr)
                    qrf=qrcode.make(str(getattr(self,fieldname))).save(filename_qr)
                    

                    if self.LCL_ANDROID.exists():
                        self.LCL=self.LCL_ANDROID
                   
                    #LCL=Path("LCL_IMG")
                    if not self.LCL.exists():
                        self.LCL.mkdir()
                    fname=str(self.LCL/Path(str(self.EntryId)+f"_{fieldname}"))
                    n=self.save_barcode()
                    c=self.save_code()
                    text=[]
                    for column in self.__table__.columns:
                        text.append('='.join([column.name,str(self.__dict__[column.name])]))
                    data='\n'.join(text)
                    renderImageFromText(fname,data,barcode_file=n,code_file=c,img_file=filename_qr)
                    Path(filename_qr).unlink()
                except Exception as e:
                    print(e)


            return filename
        except Exception as e:
            print(e)
        return False

    def save_barcode(self):
        filename=Path(f"{self.EntryId}_barcode.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[UPCA,EAN13,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Barcode).save(filename)
                        break
                    else:
                        if len(self.Barcode) <= 8 and code == UPCA:
                            upca=upcean.convert.convert_barcode_from_upce_to_upca(self.Barcode)
                            if upca != False:
                                code(upca,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        elif len(self.Barcode) > 12:
                            if code == EAN13:
                                code(self.Barcode,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        else:
                            code(self.Barcode,writer=ImageWriter()).write(filename)
                        break
                except Exception as e:
                    print(e)
            return filename


        except Exception as e:
            print(e)
        return False

    def saveItemData(self,num=None):
        if self.LCL_ANDROID.exists():
            self.LCL=self.LCL_ANDROID
        text=[]
        for column in self.__table__.columns:
            text.append('='.join([column.name,str(self.__dict__[column.name])]))
        data='\n'.join(text)
        #LCL=Path("LCL_IMG")
        if not self.LCL.exists():
            self.LCL.mkdir()
        fname=str(self.LCL/Path(str(self.EntryId)))
        n=self.save_barcode()
        c=self.save_code()
        renderImageFromText(fname,data,barcode_file=n,img_file=self.Image,code_file=c)

    def listdisplay(self,num=None):
        name=self.Name
        ma=32
        n=self.split_by_len(name,ma)
        #print(n)
        new=[]
        for i in n:
            if n.index(i) > 0:
                new.append(i)
            else:
                new.append(i)
        name='\n'.join(new)
        name="\n"+name
        if num == None:
            num=''
        msg=f'''{Fore.magenta}{Fore.dark_goldenrod}{num}->({Style.reset} NAME={Fore.cyan}{name}{Style.reset} | UPC={Fore.green}{self.Barcode}{Style.reset} | SHELF={Fore.yellow}{self.Code}{Style.reset} | QTY={Fore.violet}{self.ListQty}{Style.reset} | EID={Fore.sky_blue_2}{self.EntryId}{Style.reset}{Fore.magenta} )-<{Fore.dark_goldenrod}{num}{Style.reset}'''
        print(msg)
    def split_by_len(self,string, length):
        result = []
        for i in range(0, len(string), length):
            result.append(string[i:i + length])
        return result

    def saveListExtended(self,num):
        if self.LCL_ANDROID.exists():
            self.LCL=self.LCL_ANDROID
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.WD_DSPLY+self.SBX_WTR_KLR+self.SBX_CHP_DSPLY+self.SBX_WTR_DSPLY+self.FLRL_CHP_DSPLY+self.FLRL_WTR_DSPLY+self.CHKSTND_SPLY
        name=self.Name
        ma=32
        if len(name) > ma:
            n=self.split_by_len(name,ma)
            #print(n)
            new=[]
            for i in n:
                if n.index(i) > 0:
                    new.append(str(' '*7)+i)
                else:
                    new.append(i)
            name='\n'.join(new)
        if num == None:
            num=''
        msg=f"""
============={num}============
Barcode = {self.Barcode}
Code/Shelf/Label = {self.Code}
Name = {name}
Shelf = {self.Shelf}
BackRoom/Wall = {self.BackRoom}
Display_1 = {self.Display_1}
Display_2 = {self.Display_2}
Display_3 = {self.Display_3}
Display_4 = {self.Display_4}
Display_5 = {self.Display_5}
Display_6 = {self.Display_6}
SBX_WTR_DSPLY={self.SBX_WTR_DSPLY}
SBX_CHP_DSPLY={self.SBX_CHP_DSPLY}
SBX_WTR_KLR={self.SBX_WTR_KLR}
FLRL_CHP_DSPLY={self.FLRL_CHP_DSPLY}
FLRL_WTR_DSPLY={self.FLRL_WTR_DSPLY}
WD_DSPLY={self.WD_DSPLY}
CHKSTND_SPLY={self.CHKSTND_SPLY}
Total = {total}
Total(w/o BR+) - Backroom = {(total-self.BackRoom)-self.BackRoom}
-------------{num}-------------
"""
        
        if not self.LCL.exists():
            self.LCL.mkdir()
        fname=str(self.LCL/Path(str(self.EntryId)))
        renderImageFromText(fname,msg)
        '''
ALT_Barcode={self.ALT_Barcode}
DUP_Barcode={self.DUP_Barcode}
CaseID_BR={self.CaseID_BR}
CaseID_LD={self.CaseID_LD}
CaseID_6W={self.CaseID_6W}
Tags={self.Tags}
Facings={self.Facings}

        '''
    #if BackRoom is True, total includes Backroom*price
    #if Backroom is False, total is needed for the shelf minus whatever is brought from backroom*price
    def total_value(self,BackRoom=False,CaseMode=True):
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.SBX_WTR_DSPLY
        total+=self.SBX_CHP_DSPLY
        total+=self.SBX_WTR_KLR
        total+=self.FLRL_CHP_DSPLY
        total+=self.FLRL_WTR_DSPLY
        total+=self.WD_DSPLY
        total+=self.CHKSTND_SPLY
        if not self.Price:
            self.Price=0
        if not self.CaseCount:
            self.CaseCount=1

        if not BackRoom:
            total-=self.BackRoom-self.BackRoom
        if not CaseMode:
            return round(total*self.Price,2)
        else:
            if self.CaseCount in [None,0,-1]:
                self.CaseCount=1
            return round((total*self.CaseCount)*self.Price,2)

    def total_units(self,BackRoom=True):
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.SBX_WTR_DSPLY
        total+=self.SBX_CHP_DSPLY
        total+=self.SBX_WTR_KLR
        total+=self.FLRL_CHP_DSPLY
        total+=self.FLRL_WTR_DSPLY
        total+=self.WD_DSPLY
        total+=self.CHKSTND_SPLY
        if not BackRoom:
            total-=self.BackRoom
            total-=self.BackRoom
        #print(BackRoom)
        return total

    def listdisplay_extended(self,num):
        #print(self.csv_headers())
        #print(self.csv_values())
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.SBX_WTR_DSPLY
        total+=self.SBX_CHP_DSPLY
        total+=self.SBX_WTR_KLR
        total+=self.FLRL_CHP_DSPLY
        total+=self.FLRL_WTR_DSPLY
        total+=self.WD_DSPLY
        total+=self.CHKSTND_SPLY

        name=self.Name
        ma=32
        if len(name) > ma:
            n=self.split_by_len(name,ma)
            #print(n)
            new=[]
            for i in n:
                if n.index(i) > 0:
                    new.append(str(' '*7)+i)
                else:
                    new.append(i)
            name='\n'.join(new)
        if num == None:
            num=''
        total_value=self.total_value(CaseMode=False)
        total_value_case=self.total_value()
        msg=f"""
============={Fore.green}{num}{Style.reset}============
{Fore.red}EntryId{Style.bold}={Fore.green_yellow}{self.EntryId}{Style.reset}
{Fore.blue}Barcode{Style.reset} = {Fore.aquamarine_3}{self.Barcode}{Style.reset}
{Fore.dark_goldenrod}Code/Shelf/Label{Style.reset} = {Fore.yellow}{self.Code}{Style.reset}
{Fore.green_yellow}Name{Style.reset} = {Fore.cyan}{name}{Style.reset}
{Fore.violet}Shelf{Style.reset} = {Fore.magenta}{self.Shelf}{Style.reset}
{Fore.yellow_4b}BackRoom/Wall{Style.reset} = {Fore.orange_4b}{self.BackRoom}{Style.reset}
{Fore.slate_blue_1}Display_1{Style.reset} = {Fore.medium_purple_3b}{self.Display_1}{Style.reset}
{Fore.medium_violet_red}Display_2{Style.reset} = {Fore.magenta_3a}{self.Display_2}{Style.reset}
{Fore.deep_pink_1a}Display_3 = {Style.reset}{Fore.purple_1a}{self.Display_3}{Style.reset}
{Fore.orange_red_1}Display_4 = {Style.reset}{Fore.plum_4}{self.Display_4}{Style.reset}
{Fore.light_salmon_1}Display_5 = {Style.reset}{Fore.pale_green_1a}{self.Display_5}{Style.reset}
{Fore.pink_1}Display_6 = {Style.reset}{Fore.gold_3a}{self.Display_6}{Style.reset}
{Fore.cyan}SBX_WTR_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_DSPLY}{Style.reset}
{Fore.cyan}SBX_CHP_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_CHP_DSPLY}{Style.reset}
{Fore.cyan}SBX_WTR_KLR{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_KLR}{Style.reset}
{Fore.violet}FLRL_CHP_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_CHP_DSPLY}{Style.reset}
{Fore.violet}FLRL_WTR_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_WTR_DSPLY}{Style.reset}
{Fore.grey_50}WD_DSPLY{Style.reset}={self.WD_DSPLY}{Style.reset}
{Fore.grey_50}CHKSTND_SPLY{Style.reset}={self.CHKSTND_SPLY}{Style.reset}
{Fore.pale_green_1b}{Style.underline}If Backroom is needed as part of total use value Below...{Style.reset}
{Fore.magenta}{Style.bold}1->{Style.reset}{Fore.spring_green_3a}Total{Style.reset} = {Fore.light_yellow}{total}{Style.reset}
{Fore.yellow_4b}{Style.underline}If Product was Pulled From BR to Fill Shelf, and needs to be 
deducted from Total as remainder is to be filled from LOAD{Style.reset}
{Fore.cyan}{Style.bold}2->{Style.reset}{Fore.hot_pink_2}Total(w/o BR+) - Backroom{Style.reset} = {Fore.light_yellow}{(total-self.BackRoom)-self.BackRoom}{Style.reset}
{Fore.medium_violet_red}Total Product Handled/To Be Handled Value: {Fore.spring_green_3a}{total_value}{Style.reset}
{Fore.medium_violet_red}Total Product Handled/To Be Handled Value*CaseCount: {Fore.spring_green_3a}{total_value_case}{Style.reset}
-------------{Fore.red}{num}{Style.reset}-------------
"""
        print(msg)
        return msg

    def imageExists(self):
        try:
            return Path(self.Image).exists() and Path(self.Image).is_file()
        except Exception as e:
            return False

    def cp_src_img_to_entry_img(self,src_img):
        try:
            path_src=Path(src_img)
            if path_src.exists() and path_src.is_file():
                img=Image.open(str(path_src))
                entryImg=Image.new(img.mode,size=img.size,color=(255,255,255))
                entryImg.paste(img.copy())
                name=f"Images/{self.EntryId}.png"
                entryImg.save(name)
                return name
        except Exception as e:
            return ''

    def __repr__(self):
        total_value=self.total_value(CaseMode=False)
        total_value_case=self.total_value()
        m= f"""
{Style.bold}{Style.underline}{Fore.pale_green_1b}Entry{Style.reset}(
{Fore.hot_pink_2}{Style.bold}{Style.underline}EntryId{Style.reset}={self.EntryId}
{Fore.violet}{Style.underline}Code{Style.reset}='{self.Code}',
{Fore.orange_3}{Style.bold}Barcode{Style.reset}='{self.Barcode}',
{Fore.orange_3}{Style.underline}UPCE from UPCA[if any]{Style.reset}='{self.upce2upca}',
{Fore.green}{Style.bold}Price{Style.reset}=${self.Price},
{Fore.green}{Style.bold}CRV{Style.reset}=${self.CRV},
{Fore.green}{Style.bold}Tax{Style.reset}=${self.Tax},
{Fore.green}{Style.bold}TaxNote{Style.reset}='{self.TaxNote}',
{Fore.red}Name{Style.reset}='{self.Name}',
{Fore.tan}Note{Style.reset}='{self.Note}',
{Fore.grey_50}ALT_Barcode{Style.reset}={Fore.grey_70}{self.ALT_Barcode}{Style.reset}
{Fore.grey_50}DUP_Barcode{Style.reset}={Fore.grey_70}{self.DUP_Barcode}{Style.reset}
{Fore.grey_50}CaseID_BR{Style.reset}={Fore.grey_70}{self.CaseID_BR}{Style.reset}
{Fore.grey_50}CaseID_LD{Style.reset}={Fore.grey_70}{self.CaseID_LD}{Style.reset}
{Fore.grey_50}CaseID_6W{Style.reset}={Fore.grey_70}{self.CaseID_6W}{Style.reset}
{Fore.grey_50}Tags{Style.reset}={Fore.grey_70}{self.Tags}{Style.reset}
{Fore.grey_50}Facings{Style.reset}={Fore.grey_70}{self.Facings}{Style.reset}
{Fore.pale_green_1b}Timestamp{Style.reset}='{datetime.fromtimestamp(self.Timestamp).strftime('%D@%H:%M:%S')}',
{Fore.deep_pink_3b}Shelf{Style.reset}={self.Shelf},
{Fore.light_steel_blue}BackRoom{Style.reset}={self.BackRoom},
{Fore.cyan}Display_1{Style.reset}={self.Display_1},
{Fore.cyan}Display_2{Style.reset}={self.Display_2},
{Fore.cyan}Display_3{Style.reset}={self.Display_3},
{Fore.cyan}Display_4{Style.reset}={self.Display_4},
{Fore.cyan}Display_5{Style.reset}={self.Display_5},
{Fore.cyan}Display_6{Style.reset}={self.Display_6},
{Fore.cyan}SBX_WTR_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_DSPLY}{Style.reset}
{Fore.cyan}SBX_CHP_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_CHP_DSPLY}{Style.reset}
{Fore.cyan}SBX_WTR_KLR{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_KLR}{Style.reset}
{Fore.violet}FLRL_CHP_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_CHP_DSPLY}{Style.reset}
{Fore.violet}FLRL_WTR_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_WTR_DSPLY}{Style.reset}
{Fore.grey_50}WD_DSPLY{Style.reset}={self.WD_DSPLY}{Style.reset}
{Fore.grey_50}CHKSTND_SPLY{Style.reset}={self.CHKSTND_SPLY}{Style.reset}
{Fore.light_salmon_3a}Stock_Total{Style.reset}={self.Stock_Total},
{Fore.magenta_3c}InList{Style.reset}={self.InList}
{Fore.indian_red_1b}{Style.bold}{Style.underline}{Style.blink}ListQty{Style.reset}={self.ListQty}
{Fore.misty_rose_3}Location{Style.reset}={self.Location}
{Fore.sky_blue_2}CaseCount{Style.reset}={self.CaseCount}
{Fore.sky_blue_2}Size{Style.reset}={self.Size}
{Fore.tan}Image[{Fore.dark_goldenrod}Exists:{Fore.deep_pink_3b}{self.imageExists()}{Style.reset}{Fore.tan}]{Style.reset}={self.Image}
{Fore.medium_violet_red}Total Product Handled/To Be Handled Value: {Fore.spring_green_3a}{total_value}{Style.reset}
{Fore.medium_violet_red}Total Product Handled/To Be Handled Value*CaseCount: {Fore.spring_green_3a}{total_value_case}{Style.reset}"""
        if self.imageExists():
            m+=f"""
        {Fore.green}Image {Fore.orange_3}{Style.bold}{Style.underline}ABSOLUTE{Style.reset}{Style.reset}={Path(self.Image).absolute()}"""

        m+="""
        )
        """
        if self.Barcode and len(self.Barcode) >= 13:
            print(f"{Fore.hot_pink_1b}Detected Code is 13 digits long; please verify the 'EAN13 Stripped $var_x=$var_z' data first before using the UPC Codes!{Style.reset}")
        pc.PossibleCodes(scanned=self.Barcode)
        pc.PossibleCodesEAN13(scanned=self.Barcode)
        return m

Entry.metadata.create_all(ENGINE)
PairCollection.metadata.create_all(ENGINE)
tables={
    'Entry':Entry,
    'PairCollection':PairCollection,
}

class DayLog(BASE):
    __tablename__="DayLog"
    DayLogId=Column(Integer,primary_key=True)
    DayLogDate=Column(Date)
    Code=Column(String)
    Barcode=Column(String)
    #not found in prompt requested by
    '''
    #name {Entryid}
    #name {Entryid} {new_value}
    
    #price {Entryid}
    #price {Entryid} {new_value}

    #note {Entryid}
    #note {Entryid} {new_value}
    
    #size {Entryid} 
    #size {Entryid} {new_value}
    '''
    Name=Column(String)
    Price=Column(Float)
    CRV=Column(Float)
    Tax=Column(Float)
    TaxNote=Column(String)

    Note=Column(String)
    Size=Column(String)
    
    CaseCount=Column(Integer)

    Shelf=Column(Integer)
    BackRoom=Column(Integer)
    Display_1=Column(Integer)
    Display_2=Column(Integer)
    Display_3=Column(Integer)
    Display_4=Column(Integer)
    Display_5=Column(Integer)
    Display_6=Column(Integer)
    InList=Column(Boolean)
    Stock_Total=Column(Integer)
    Location=Column(String)
    ListQty=Column(Float)
    upce2upca=Column(String)
    Image=Column(String)
    EntryId=Column(Integer)
    Timestamp=Column(Float)

    ALT_Barcode=Column(String)
    DUP_Barcode=Column(String)
    CaseID_BR=Column(String)
    CaseID_LD=Column(String)
    CaseID_6W=Column(String)
    Tags=Column(String)
    Facings=Column(Integer)
    SBX_WTR_DSPLY=Column(Integer)
    SBX_CHP_DSPLY=Column(Integer)
    SBX_WTR_KLR=Column(Integer)
    FLRL_CHP_DSPLY=Column(Integer)
    FLRL_WTR_DSPLY=Column(Integer)
    WD_DSPLY=WD_DSPLY=Column(Integer)
    CHKSTND_SPLY=CHKSTND_SPLY=Column(Integer)
    def csv_headers(self):
        headers=[]
        for i in self.__table__.columns:
            headers.append(i.name)
        headers.append("DateFromTimeStamp")
        return headers

    def csv_values(self):
        values=[]
        for i in self.__table__.columns:
            value=self.__dict__.get(i.name)
            values.append(value)
        values.append(datetime.fromtimestamp(self.Timestamp).ctime())
        return values
    def synthetic_field_str(self):
        f=string.ascii_uppercase+string.digits
        part=[]
        for num in range(4):
            part.append(f[random.randint(0,len(f)-1)])
        part.append("-")
        for num in range(4):
            part.append(f[random.randint(0,len(f)-1)])
        return ''.join(part)



    def __init__(self,Barcode,Code,upce2upca='',Name='',InList=False,Price=0.0,Note='',Size='',CaseCount=0,Shelf=0,BackRoom=0,Display_1=0,Display_2=0,Display_3=0,Display_4=0,Display_5=0,Display_6=0,Stock_Total=0,Timestamp=datetime.now().timestamp(),EntryId=None,Location='///',ListQty=0.0,Image='',CHKSTND_SPLY=0,WD_DSPLY=0,FLRL_CHP_DSPLY=0,FLRL_WTR_DSPLY=0,SBX_WTR_KLR=0,SBX_CHP_DSPLY=0,SBX_WTR_DSPLY=0,Facings=0,Tags='',CaseID_6W='',CaseID_BR='',CaseID_LD='',ALT_Barcode='',DUP_Barcode='',DayLogDate=datetime.now(),DayLogId=None,CRV=0.0,Tax=0.0,TaxNote=''):
        if EntryId:
            self.EntryId=EntryId
        self.CRV=CRV
        self.Tax=Tax
        self.TaxNote=TaxNote
        self.Barcode=Barcode
        self.Code=Code
        self.Name=Name
        self.Price=Price
        self.Note=Note
        self.Size=Size
        self.Shelf=Shelf
        self.CaseCount=CaseCount
        self.BackRoom=BackRoom
        self.Display_1=Display_1
        self.Display_2=Display_2
        self.Display_3=Display_3
        self.Display_4=Display_4
        self.Display_5=Display_5
        self.Display_6=Display_6
        self.Stock_Total=Stock_Total
        self.Location=Location
        self.Timestamp=Timestamp
        self.InList=InList
        self.ListQty=ListQty
        self.upce2upca=upce2upca
        self.Image=Image
        self.Tags=Tags
        self.Facings=Facings

        self.ALT_Barcode=ALT_Barcode
        self.DUP_Barcode=DUP_Barcode
        self.CaseID_BR=CaseID_BR
        self.CaseID_LD=CaseID_LD
        self.CaseID_6W=CaseID_6W
        self.SBX_WTR_DSPLY=SBX_WTR_DSPLY
        self.SBX_CHP_DSPLY=SBX_CHP_DSPLY
        self.SBX_WTR_KLR=SBX_WTR_KLR
        self.FLRL_CHP_DSPLY=FLRL_CHP_DSPLY
        self.FLRL_WTR_DSPLY=FLRL_WTR_DSPLY
        self.WD_DSPLY=WD_DSPLY
        self.CHKSTND_SPLY=CHKSTND_SPLY
        if DayLogDate:
            self.DayLogDate=DayLogDate
        else:
            self.DayLogDate=datetime.now()
        if DayLogId:
            self.DayLogId=DayLogId
        #CHKSTND_SPLY=0,WD_DSPLY=0,FLRL_CHP_DSPLY=0,FLRL_WTR_DSPLY=0,SBX_WTR_KLR=0,SBX_CHP_DSPLY=0,SBX_WTR_DSPLY=0,Facings=0,Tags='',CaseID_6W='',CaseID_BR='',CaseID_LD='',ALT_Barcode='',DUP_Barcode=''

        '''
        ALT_Barcode=Column(String)
        DUP_Barcode=Column(String)
        CaseID_BR=Column(String)
        CaseID_LD=Column(String)
        CaseID_6W=Column(String)
        Tags=Column(String)
        Facings=Column(Integger)
        SBX_WTR_DSPLY=Column(Integer)
        SBX_CHP_DSPLY=Column(Integer)
        SBX_WTR_KLR=Column(Integer)
        FLRL_CHP_DSPLY=Column(Integer)
        FLRL_WTR_DSPLY=Column(Integer)
        WD_DSPLY=WD_DSPLY=Column(Integer)
        CHKSTND_SPLY=CHKSTND_SPLY=Column(Integer)
        '''


        #proposed fields
        #[done]smle,s|search|? - calls a prompt to search for InList==True with CODE|BARCODE instead of direct search waits for b for back, q for quit, for next CODE|BARCODE
        #optional fields
        #self.alt_barcode
        #self.duplicate_code
        #self.case_id_backroom - in case specific case is needed to be logged
        #csidbm,$EntryId,generate - create a synthetic id for case and save item to and save qrcode png of $case_id
        #csidbm,$EntryId,$case_id - set case id for item
        #csidbm,$EntryId - display item case id
        #csidbm,s|search,$case_id - display items associated with $case_id
        #csidbm,$EntryId,clr_csid - set $case_id to ''
        #the above applies to the below self.case_id_load as well
        #self.case_id_load - in case specific is found in load wanted in data

        #self.Tags
        #cmd syntax
        #tag,$EntryID,+|-|=,$tag_text
        #tag,s|search,$tag_text -> search for items with tag txt (multiple tags separated with a bar '|'')
        #tag,$EntryId|$code|$barcode -> display tags for item with $entryId, $code (returns multiple values), $barcode (returns multiple values)
        #- removes tag from field with tags
        #+ adds a tag to field with tags
        #= set field to $tag_text
        #self.Tags is a string separated by json string containing a list of tags
        #json.dumps(['a','b','c'])
        #json.loads('["a", "b", "c"]')

        #self.Facings
        #additional inventory fields
        #self.checkstandsupplies
        #self.sbx_dsply
        #self.flrl_dsply
        #self.wd_dsply

        try:
            if not self.LCL_ANDROID.exists():
                self.LCL_ANDROID.mkdir(parents=True)
        except Exception as e:
            print(e,"android directory!")
    LCL=Path("LCL_IMG")
    LCL_ANDROID=Path("/storage/emulated/0/DCIM/Screenshots")

    def save_code(self):
        filename=Path(f"{self.EntryId}_code.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[Code39,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Barcode).save(filename)
                        break
                    else:
                        code(self.Code,add_checksum=False,writer=ImageWriter()).write(filename)
                        break
                    pass
                except Exception as e:
                    print(e)


            return filename
        except Exception as e:
            print(e)
        return False

    def save_barcode(self):
        filename=Path(f"{self.EntryId}_barcode.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[UPCA,EAN13,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Barcode).save(filename)
                        break
                    else:
                        if len(self.Barcode) <= 8 and code == UPCA:
                            upca=upcean.convert.convert_barcode_from_upce_to_upca(self.Barcode)
                            if upca != False:
                                code(upca,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        elif len(self.Barcode) > 12:
                            if code == EAN13:
                                code(self.Barcode,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        else:
                            code(self.Barcode,writer=ImageWriter()).write(filename)
                        break
                except Exception as e:
                    print(e)
            return filename


        except Exception as e:
            print(e)
        return False

    def saveItemData(self,num=None):
        if self.LCL_ANDROID.exists():
            self.LCL=self.LCL_ANDROID
        text=[]
        for column in self.__table__.columns:
            text.append('='.join([column.name,str(self.__dict__[column.name])]))
        data='\n'.join(text)
        #LCL=Path("LCL_IMG")
        if not self.LCL.exists():
            self.LCL.mkdir()
        fname=str(self.LCL/Path(str(self.EntryId)))
        n=self.save_barcode()
        c=self.save_code()
        renderImageFromText(fname,data,barcode_file=n,img_file=self.Image,code_file=c)

    def listdisplay(self,num=None):
        name=self.Name
        ma=32
        n=self.split_by_len(name,ma)
        #print(n)
        new=[]
        for i in n:
            if n.index(i) > 0:
                new.append(i)
            else:
                new.append(i)
        name='\n'.join(new)
        name="\n"+name
        if num == None:
            num=''
        msg=f'''{Fore.magenta}{Fore.dark_goldenrod}{num}->({Style.reset} NAME={Fore.cyan}{name}{Style.reset} | UPC={Fore.green}{self.Barcode}{Style.reset} | SHELF={Fore.yellow}{self.Code}{Style.reset} | QTY={Fore.violet}{self.ListQty}{Style.reset} | EID={Fore.sky_blue_2}{self.EntryId}{Style.reset}{Fore.magenta} )-<{Fore.dark_goldenrod}{num}{Style.reset}'''
        print(msg)
    def split_by_len(self,string, length):
        result = []
        for i in range(0, len(string), length):
            result.append(string[i:i + length])
        return result

    def saveListExtended(self,num):
        if self.LCL_ANDROID.exists():
            self.LCL=self.LCL_ANDROID
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.WD_DSPLY+self.SBX_WTR_KLR+self.SBX_CHP_DSPLY+self.SBX_WTR_DSPLY+self.FLRL_CHP_DSPLY+self.FLRL_WTR_DSPLY+self.CHKSTND_SPLY
        name=self.Name
        ma=32
        if len(name) > ma:
            n=self.split_by_len(name,ma)
            #print(n)
            new=[]
            for i in n:
                if n.index(i) > 0:
                    new.append(str(' '*7)+i)
                else:
                    new.append(i)
            name='\n'.join(new)
        if num == None:
            num=''
        msg=f"""
============={num}============
DayLogId = {self.DayLogId}
DayLogDate = {self.DayLogDate}
Barcode = {self.Barcode}
Code/Shelf/Label = {self.Code}
Name = {name}
Shelf = {self.Shelf}
BackRoom/Wall = {self.BackRoom}
Display_1 = {self.Display_1}
Display_2 = {self.Display_2}
Display_3 = {self.Display_3}
Display_4 = {self.Display_4}
Display_5 = {self.Display_5}
Display_6 = {self.Display_6}
SBX_WTR_DSPLY={self.SBX_WTR_DSPLY}
SBX_CHP_DSPLY={self.SBX_CHP_DSPLY}
SBX_WTR_KLR={self.SBX_WTR_KLR}
FLRL_CHP_DSPLY={self.FLRL_CHP_DSPLY}
FLRL_WTR_DSPLY={self.FLRL_WTR_DSPLY}
WD_DSPLY={self.WD_DSPLY}
CHKSTND_SPLY={self.CHKSTND_SPLY}
Total = {total}
Total(w/o BR+) - Backroom = {(total-self.BackRoom)-self.BackRoom}
-------------{num}-------------
"""
        
        if not self.LCL.exists():
            self.LCL.mkdir()
        fname=str(self.LCL/Path(str(self.EntryId)))
        renderImageFromText(fname,msg)
        '''
ALT_Barcode={self.ALT_Barcode}
DUP_Barcode={self.DUP_Barcode}
CaseID_BR={self.CaseID_BR}
CaseID_LD={self.CaseID_LD}
CaseID_6W={self.CaseID_6W}
Tags={self.Tags}
Facings={self.Facings}

        '''

    def listdisplay_extended(self,num):
        #print(self.csv_headers())
        #print(self.csv_values())
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.SBX_WTR_DSPLY
        total+=self.SBX_CHP_DSPLY
        total+=self.SBX_WTR_KLR
        total+=self.FLRL_CHP_DSPLY
        total+=self.FLRL_WTR_DSPLY
        total+=self.WD_DSPLY
        total+=self.CHKSTND_SPLY

        name=self.Name
        ma=32
        if len(name) > ma:
            n=self.split_by_len(name,ma)
            #print(n)
            new=[]
            for i in n:
                if n.index(i) > 0:
                    new.append(str(' '*7)+i)
                else:
                    new.append(i)
            name='\n'.join(new)
        if num == None:
            num=''
        msg=f"""
============={Fore.green}{num}{Style.reset}============
{Fore.cyan}DayLogId = {self.DayLogId}{Style.reset}
{Fore.cyan}DayLogDate = {self.DayLogDate}{Style.reset}
{Fore.red}EntryId{Style.bold}={Fore.green_yellow}{self.EntryId}{Style.reset}
{Fore.blue}Barcode{Style.reset} = {Fore.aquamarine_3}{self.Barcode}{Style.reset}
{Fore.dark_goldenrod}Code/Shelf/Label{Style.reset} = {Fore.yellow}{self.Code}{Style.reset}
{Fore.green_yellow}Name{Style.reset} = {Fore.cyan}{name}{Style.reset}
{Fore.violet}Shelf{Style.reset} = {Fore.magenta}{self.Shelf}{Style.reset}
{Fore.yellow_4b}BackRoom/Wall{Style.reset} = {Fore.orange_4b}{self.BackRoom}{Style.reset}
{Fore.slate_blue_1}Display_1{Style.reset} = {Fore.medium_purple_3b}{self.Display_1}{Style.reset}
{Fore.medium_violet_red}Display_2{Style.reset} = {Fore.magenta_3a}{self.Display_2}{Style.reset}
{Fore.deep_pink_1a}Display_3 = {Style.reset}{Fore.purple_1a}{self.Display_3}{Style.reset}
{Fore.orange_red_1}Display_4 = {Style.reset}{Fore.plum_4}{self.Display_4}{Style.reset}
{Fore.light_salmon_1}Display_5 = {Style.reset}{Fore.pale_green_1a}{self.Display_5}{Style.reset}
{Fore.pink_1}Display_6 = {Style.reset}{Fore.gold_3a}{self.Display_6}{Style.reset}
{Fore.cyan}SBX_WTR_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_DSPLY}{Style.reset}
{Fore.cyan}SBX_CHP_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_CHP_DSPLY}{Style.reset}
{Fore.cyan}SBX_WTR_KLR{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_KLR}{Style.reset}
{Fore.violet}FLRL_CHP_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_CHP_DSPLY}{Style.reset}
{Fore.violet}FLRL_WTR_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_WTR_DSPLY}{Style.reset}
{Fore.grey_50}WD_DSPLY{Style.reset}={self.WD_DSPLY}{Style.reset}
{Fore.grey_50}CHKSTND_SPLY{Style.reset}={self.CHKSTND_SPLY}{Style.reset}
{Fore.pale_green_1b}{Style.underline}If Backroom is needed as part of total use value Below...{Style.reset}
{Fore.magenta}{Style.bold}1->{Style.reset}{Fore.spring_green_3a}Total{Style.reset} = {Fore.light_yellow}{total}{Style.reset}
{Fore.yellow_4b}{Style.underline}If Product was Pulled From BR to Fill Shelf, and needs to be 
deducted from Total as remainder is to be filled from LOAD{Style.reset}
{Fore.cyan}{Style.bold}2->{Style.reset}{Fore.hot_pink_2}Total(w/o BR+) - Backroom{Style.reset} = {Fore.light_yellow}{(total-self.BackRoom)-self.BackRoom}{Style.reset}
-------------{Fore.red}{num}{Style.reset}-------------
"""
        print(msg)
        return msg

    def imageExists(self):
        try:
            return Path(self.Image).exists() and Path(self.Image).is_file()
        except Exception as e:
            return False

    def cp_src_img_to_entry_img(self,src_img):
        try:
            path_src=Path(src_img)
            if path_src.exists() and path_src.is_file():
                img=Image.open(str(path_src))
                entryImg=Image.new(img.mode,size=img.size,color=(255,255,255))
                entryImg.paste(img.copy())
                name=f"Images/{self.EntryId}.png"
                entryImg.save(name)
                return name
        except Exception as e:
            return ''

    def __repr__(self):
        m= f"""
        {Style.bold}{Style.underline}{Fore.pale_green_1b}Daylog{Style.reset}(
        {Fore.cyan}DayLogId = {self.DayLogId}{Style.reset},
        {Fore.cyan}DayLogDate = {self.DayLogDate}{Style.reset},
        {Fore.hot_pink_2}{Style.bold}{Style.underline}EntryId{Style.reset}={self.EntryId}
        {Fore.violet}{Style.underline}Code{Style.reset}='{self.Code}',
        {Fore.orange_3}{Style.bold}Barcode{Style.reset}='{self.Barcode}',
        {Fore.orange_3}{Style.underline}UPCE from UPCA[if any]{Style.reset}='{self.upce2upca}',
        {Fore.green}{Style.bold}Price{Style.reset}=${self.Price},
        {Fore.green}{Style.bold}CRV{Style.reset}=${self.CRV},
        {Fore.green}{Style.bold}Tax{Style.reset}=${self.Tax},
        {Fore.green}{Style.bold}TaxNote{Style.reset}='{self.TaxNote}',
        {Fore.red}Name{Style.reset}='{self.Name}',
        {Fore.tan}Note{Style.reset}='{self.Note}',
        {Fore.grey_50}ALT_Barcode{Style.reset}={Fore.grey_70}{self.ALT_Barcode}{Style.reset}
        {Fore.grey_50}DUP_Barcode{Style.reset}={Fore.grey_70}{self.DUP_Barcode}{Style.reset}
        {Fore.grey_50}CaseID_BR{Style.reset}={Fore.grey_70}{self.CaseID_BR}{Style.reset}
        {Fore.grey_50}CaseID_LD{Style.reset}={Fore.grey_70}{self.CaseID_LD}{Style.reset}
        {Fore.grey_50}CaseID_6W{Style.reset}={Fore.grey_70}{self.CaseID_6W}{Style.reset}
        {Fore.grey_50}Tags{Style.reset}={Fore.grey_70}{self.Tags}{Style.reset}
        {Fore.grey_50}Facings{Style.reset}={Fore.grey_70}{self.Facings}{Style.reset}
        {Fore.pale_green_1b}Timestamp{Style.reset}='{datetime.fromtimestamp(self.Timestamp).strftime('%D@%H:%M:%S')}',
        {Fore.deep_pink_3b}Shelf{Style.reset}={self.Shelf},
        {Fore.light_steel_blue}BackRoom{Style.reset}={self.BackRoom},
        {Fore.cyan}Display_1{Style.reset}={self.Display_1},
        {Fore.cyan}Display_2{Style.reset}={self.Display_2},
        {Fore.cyan}Display_3{Style.reset}={self.Display_3},
        {Fore.cyan}Display_4{Style.reset}={self.Display_4},
        {Fore.cyan}Display_5{Style.reset}={self.Display_5},
        {Fore.cyan}Display_6{Style.reset}={self.Display_6},
        {Fore.cyan}SBX_WTR_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_DSPLY}{Style.reset}
        {Fore.cyan}SBX_CHP_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_CHP_DSPLY}{Style.reset}
        {Fore.cyan}SBX_WTR_KLR{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_KLR}{Style.reset}
        {Fore.violet}FLRL_CHP_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_CHP_DSPLY}{Style.reset}
        {Fore.violet}FLRL_WTR_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_WTR_DSPLY}{Style.reset}
        {Fore.grey_50}WD_DSPLY{Style.reset}={self.WD_DSPLY}{Style.reset}
        {Fore.grey_50}CHKSTND_SPLY{Style.reset}={self.CHKSTND_SPLY}{Style.reset}
        {Fore.light_salmon_3a}Stock_Total{Style.reset}={self.Stock_Total},
        {Fore.magenta_3c}InList{Style.reset}={self.InList}
        {Fore.indian_red_1b}{Style.bold}{Style.underline}{Style.blink}ListQty{Style.reset}={self.ListQty}
        {Fore.misty_rose_3}Location{Style.reset}={self.Location}
        {Fore.sky_blue_2}CaseCount{Style.reset}={self.CaseCount}
        {Fore.sky_blue_2}Size{Style.reset}={self.Size}
        {Fore.tan}Image[{Fore.dark_goldenrod}Exists:{Fore.deep_pink_3b}{self.imageExists()}{Style.reset}{Fore.tan}]{Style.reset}={self.Image}"""

        if self.imageExists():
            m+=f"""
        {Fore.green}Image {Fore.orange_3}{Style.bold}{Style.underline}ABSOLUTE{Style.reset}{Style.reset}={Path(self.Image).absolute()}"""

        m+="""
        )
        """
        if self.Barcode and len(self.Barcode) >= 13:
            print(f"{Fore.hot_pink_1b}Detected Code is 13 digits long; please verify the 'EAN13 Stripped $var_x=$var_z' data first before using the UPC Codes!{Style.reset}")
        pc.PossibleCodes(scanned=self.Barcode)
        pc.PossibleCodesEAN13(scanned=self.Barcode)
        return m

   
DayLog.metadata.create_all(ENGINE)


class TouchStamp(BASE):
    __tablename__="TouchStamp"
    EntryId=Column(Integer)
    TouchStampId=Column(Integer,primary_key=True)
    Timestamp=Column(DateTime)
    Note=Column(String)
    geojson=Column(String)


    def __init__(self,EntryId,Note,Timestamp=datetime.now(),TouchStampId=None):
        if TouchStampId:
            self.TouchStampId=TouchStampId
        self.EntryId=EntryId
        self.Note=Note
        self.Timestamp=Timestamp
        
        try:
            d=geocoder.ip("me")
            print(d,d.geojson)
            self.geojson=json.dumps(d.geojson)
        except Exception as e:
            print(e)
            self.geojson=''

    def __str__(self):
        entry=None
        try:
            with Session(ENGINE) as session:
                entry=session.query(Entry).filter(Entry.EntryId==self.EntryId).first()
                if entry:
                    msg=f"""
TouchStamp(
    {Fore.red}TouchStampId{Style.reset}={Fore.yellow}{self.TouchStampId}{Style.reset}
    {Fore.dark_goldenrod}EntryId{Style.reset}={Fore.green}"{self.EntryId}"{Style.reset},
    {Fore.green}Note{Style.reset}={Fore.tan}"{self.Note}"{Style.reset},
    {Fore.yellow}Timestamp{Style.reset}={Fore.pale_green_1b}{self.Timestamp}{Style.reset},
    {Fore.violet}Timestamp_converted{Style.reset}={Fore.magenta_3a}"{self.Timestamp.ctime()}{Style.reset}",
    {Fore.grey_50}geojson{Style.reset}={Fore.green_yellow}"{self.geojson}",{Style.reset}

    {Fore.dark_goldenrod}EntryId{Style.reset} refers to:
    =====================================
                        {entry}
    =====================================
    )
    """
                    return msg
        except Exception as e:
            print(e)
        msg=f"""
                TouchStamp(
    {Fore.red}TouchStampId{Style.reset}={Fore.yellow}{self.TouchStampId}{Style.reset}
    {Fore.dark_goldenrod}EntryId{Style.reset}={Fore.green}"{self.EntryId}"{Style.reset},
    {Fore.green}Note{Style.reset}={Fore.tan}"{self.Note}"{Style.reset},
    {Fore.yellow}Timestamp{Style.reset}={Fore.pale_green_1b}{self.Timestamp}{Style.reset},
    {Fore.violet}Timestamp_converted{Style.reset}={Fore.magenta_3a}"{self.Timestamp.ctime()}{Style.reset}",
    {Fore.grey_50}geojson{Style.reset}={Fore.green_yellow}"{self.geojson}",{Style.reset}

    {Fore.dark_goldenrod}EntryId{Style.reset} refers to:
    =====================================
                        {entry}
    =====================================
    )
    """
        return msg
TouchStamp.metadata.create_all(ENGINE)


class EntrySet:
    def __init__(self,engine,parent):
        self.helpText=f'''
{Fore.orange_3}#code is:
    Code -    returns multiple results,prefixed by a
              'c.' searches by ; else uses first result
    EntryId - returns 1 entry,prefixed by a 'e.' 
              searches by ; else uses first result
    Barcode - returns multiple results,
              prefixed by a 'b.' searches by ; else uses first 
              result
{Style.reset}

{Fore.violet}fields|flds|list_fields{Style.reset} - {Fore.grey_70}list fields to edit{Style.reset}
{Fore.green_yellow}scan_set|ss|set{Style.reset} - {Fore.grey_70}scan a #code with prompt for field and value{Style.reset}
{Fore.green_yellow}scan_set|ss|set,$code{Style.reset} - {Fore.grey_70}get #code and set $field && $value from prompt{Style.reset}
{Fore.green_yellow}scan_set|ss|set,$field,#code{Style.reset} - {Fore.grey_70}prompt for $value of $field for #code{Style.reset}
{Fore.green_yellow}scan_set|ss|set,$field,$value,#code{Style.reset} - {Fore.grey_70}set $value of $field for #code no prompt{Style.reset}
{Fore.green_yellow}ssb{Style.reset} - {Fore.grey_70}set $value of $field for #code by prompt in batchmode{Style.reset}
{Fore.green}search|s|sch|find|lu|lookup{Style.reset} - {Fore.grey_70}find code by prompt and display #uses extensions listed at top{Style.reset}
{Fore.green}search|s|sch|find|lu|lookup,#code{Style.reset} - {Fore.grey_70}find #code and display #uses extensions listed at top{Style.reset}
{Fore.dark_goldenrod}remove|delete,#code{Style.reset} - {Fore.grey_70}remove an #code{Style.reset}
{Fore.dark_goldenrod}remove|delete{Style.reset} - {Fore.grey_70}remove an Entry{Style.reset}
{Fore.tan}help|?{Style.reset} - {Fore.grey_70}display help text by Prompted Id{Style.reset}
        '''
        self.engine=engine
        self.parent=parent
        self.valid_fields={i.name:i.type for i in Entry.__table__.columns}
        self.valid_field_names=tuple([i.name for i in Entry.__table__.columns])

        while True:
            try:
                do=input(f"{Fore.green_yellow}Do What? :{Style.reset} ")
                if do.lower() in ['q','quit']:
                    exit("user quit!")
                elif do.lower() in ['b','back']:
                    return
                elif do.lower() in ['?','help']:
                    self.helpTextPrint()
                elif do.lower() in ['ssb']:
                    self.ssb()
                else:
                    spl=do.split(",")
                    if spl[0].lower() in ['ss','scan_set','set']:
                        if spl[0].lower() in ['q','quit']:
                            exit("user quit!")
                        elif spl[0].lower() in ['b','back']:
                            return
                        else:
                            if len(spl) == 1:
                                self.scan_set()
                            elif len(spl) == 2:
                                self.scan_set(code=spl[-1])
                            elif len(spl) == 3:
                                self.scan_set(code=spl[-1],field=spl[-2])
                            elif len(spl) == 4:
                                self.scan_set(code=spl[-1],field=spl[-3],value=spl[-2])
                            else:
                                self.helpTextPrint()
                    if spl[0].lower() in ['fields','flds','list_fields']:
                        self.list_fields()
                    elif spl[0].lower() in 'search|s|sch|find|lu|lookup'.split('|'):
                        if len(spl) == 1:
                            self.search()
                        elif len(spl) == 2:
                            self.search(code=spl[-1])
                    elif spl[0].lower() in 'remove|delete'.split('|'):
                        if len(spl) == 1:
                            self.delete()
                        elif len(spl) == 2:
                            self.delete(code=spl[-1])
            except Exception as e:
                print(e)

    def list_fields(self):
        for num,field in enumerate(Entry.__table__.columns):
            print(f"{Fore.red}{num}{Style.reset} -> {Fore.magenta_3a}{field.name}{Style.reset}({Fore.violet}{field.type}{Style.reset})")


    def helpTextPrint(self):
        print(self.helpText)

    def search(self,code=None):
        if code == None:
            code=input(f"{Fore.cyan}Barcode{Style.reset}|{Fore.green_yellow}Code{Style.reset}|{Fore.yellow}EntryId{Style.reset}: ")
            #get item next
        with Session(self.engine) as session:
            ext=code.lower().split('.')[0]
            cd=code.lower().split('.')[-1]
            if cd.lower() in ['q','quit']:
                exit("user quit!")
            elif cd.lower() in ['back','b']:
                return
            elif cd.lower() in ['?','help']:
                self.helpTextPrint()
            #result=session.query()
            if ext in ['b']:
                try:
                    result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd))).all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    print(f"{Fore.green}{Style.bold}Total Results:{Style.reset} {Fore.cyan}{ct}{Style.reset}")
                except Exception as e:
                    raise e
            elif ext in ['c']:
                try:
                    result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd))).all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    print(f"{Fore.green}{Style.bold}Total Results:{Style.reset} {Fore.cyan}{ct}{Style.reset}")
                except Exception as e:
                    raise e
            elif ext in ['e']:
                #entry id
                try:
                    cdi=int(cd)
                    result=session.query(Entry)
                    result=result.filter(Entry.EntryId==cdi).first()
                    print(result)
                except Exception as e:
                    raise e
            else:
                result=session.query(Entry)
                try:
                    try:
                        cdi=int(eval(cd))
                    except Exception as e:
                        print(e)
                        cdi=int(cd)
                    result=session.query(Entry)
                    result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi))
                except Exception as e:
                    print(e)
                    result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd)))
                result=result.all()
                ct=len(result)
                for num,r in enumerate(result):
                    print(f"{num}/{ct-1} -> {r}")
                print(f"{Fore.green}{Style.bold}Total Results:{Style.reset} {Fore.cyan}{ct}{Style.reset}")

    def delete(self,code=None):
        if code == None:
            code=input(f"{Fore.cyan}Barcode{Style.reset}|{Fore.green_yellow}Code{Style.reset}|{Fore.yellow}EntryId{Style.reset}: ")
            #get item next
        with Session(self.engine) as session:
            ext=code.lower().split('.')[0]
            cd=code.lower().split('.')[-1]
            if cd.lower() in ['q','quit']:
                exit("user quit!")
            elif cd.lower() in ['back','b']:
                return
            elif cd.lower() in ['?','help']:
                self.helpTextPrint()
            #result=session.query()
            if ext in ['b']:
                try:
                    result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd))).all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    print(f"({Fore.green}{Style.bold}Total Results:{Style.reset} {Fore.cyan}{ct}{Style.reset}")
                    which=input(f"{Style.bold}{Fore.red}Delete{Style.reset} which entry? {Fore.dark_goldenrod}[num/q|quit/b|back]: {Style.reset}")
                    if which.lower() in ['quit','q']:
                        exit("user quit!")
                    elif which.lower() in ['b','back']:
                        return
                    else:
                        which=int(which)
                        dlt=session.delete(result[which])
                        session.commit()

                except Exception as e:
                    raise e
            elif ext in ['c']:
                try:
                    result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd))).all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    which=input(f"{Style.bold}{Fore.red}Delete{Style.reset} which entry? {Fore.dark_goldenrod}[num/q|quit/b|back]: {Style.reset}")
                    if which.lower() in ['quit','q']:
                        exit("user quit!")
                    elif which.lower() in ['b','back']:
                        return
                    else:
                        which=int(which)
                        dlt=session.delete(result[which])
                        session.commit()
                except Exception as e:
                    raise e
            elif ext in ['e']:
                #entry id
                try:
                    cdi=int(cd)
                    result=session.query(Entry)
                    result=result.filter(Entry.EntryId==cdi).first()
                    print(result)
                    session.delete(result)
                except Exception as e:
                    raise e
            else:
                result=session.query(Entry)
                try:
                    try:
                        cdi=int(eval(cd))
                    except Exception as e:
                        print(e)
                        cdi=into(cd)
                    result=session.query(Entry)
                    result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi))
                except Exception as e:
                    print(e)
                    result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd)))
                result=result.all()
                ct=len(result)
                for num,r in enumerate(result):
                    print(f"{num}/{ct-1} -> {r}")
                print(f"({Fore.green}{Style.bold}Total Results:{Style.reset} {Fore.cyan}{ct}{Style.reset}")
                which=input(f"{Style.bold}{Fore.red}Delete{Style.reset} which entry? {Fore.dark_goldenrod}[num/q|quit/b|back]: {Style.reset}")
                if which.lower() in ['quit','q']:
                    exit("user quit!")
                elif which.lower() in ['b','back']:
                    return
                else:
                    which=int(which)
                    dlt=session.delete(result[which])
                    session.commit()

    def ssb(self):
        def mkT(text,self):
            return text
        new_value=Prompt.__init2__(None,func=mkT,ptext="New Value To Apply",helpText="value to apply to items scanned",data=self)
        def mkF(text,self):
            if text in self:
                return text
            else:
                raise Exception(f"try one of [{self}] instead of '{text}'!")
        fields=[i.name for i in Entry.__table__.columns]
        field=Prompt.__init2__(None,func=mkF,ptext="Field",helpText=f"Field to apply value to from [{fields}]",data=fields)
        if field in [None,]:
            return
        while True:
            code=Prompt.__init2__(None,func=mkT,ptext="Code|Barcode|EntryId",helpText="#code to apply data to")
            if code in [None,]:
                break
            self.scan_set(code=code,value=new_value,field=field)



    def scan_set(self,code=None,field=None,value=None):
        if code and field and value:
            print(code,field,value)
            if field not in self.valid_field_names:
                raise Exception(f"InvalidField '{field}:{self.valid_field_names}'")
            if field in ['Timestamp',]:
                raise Exception(f"Field not supported for changes yet!")

            with Session(self.engine) as session:
                ext=code.lower().split('.')[0]
                cd=code.lower().split('.')[-1]
                
                #result=session.query()
                if ext in ['b']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}TR:{ct}){Style.reset}: ")
                        if edit_which.lower() in ['q','quit']:
                            exit("user quit!")
                        elif edit_which.lower() in ['b','back','']:
                            return
                        else:
                            self.setValuePrompt(field,r,session,value=value)
                    except Exception as e:
                        raise e
                elif ext in ['c']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}TR:{ct}){Style.reset}: ")
                        if edit_which.lower() in ['q','quit']:
                            exit("user quit!")
                        elif edit_which.lower() in ['b','back','']:
                            return
                        else:
                            self.setValuePrompt(field,r,session,value=value)
                    except Exception as e:
                        raise e
                elif ext in ['e']:
                    #entry id
                    try:
                        cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(Entry.EntryId==cdi).first()
                        if result:
                            self.setValuePrompt(field,result,session,value=value)
                    except Exception as e:
                        raise e
                else:
                    result=session.query(Entry)
                    try:
                        try:
                            cdi=int(eval(cd))
                        except Exception as e:
                            print(e)
                            cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi))
                    except Exception as e:
                        print(e)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd)))
                    result=result.all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}{ct}){Style.reset}: ")
                    if edit_which.lower() in ['q','quit']:
                        exit("user quit!")
                    elif edit_which.lower() in ['b','back','']:
                        return
                    else:
                        self.setValuePrompt(field,r,session,value=value)
        elif code and field and value == None:
            if field not in self.valid_field_names:
                raise Exception(f"InvalidField '{field}:{self.valid_field_names}'")
            if field in ['Timestamp',]:
                raise Exception(f"Field not supported for changes yet!")

            with Session(self.engine) as session:
                ext=code.lower().split('.')[0]
                cd=code.lower().split('.')[-1]
               
                #result=session.query()
                if ext in ['b']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}{ct}){Style.reset}: ")
                        if edit_which.lower() in ['q','quit']:
                            exit("user quit!")
                        elif edit_which.lower() in ['b','back','']:
                            return
                        else:
                            self.setValuePrompt(field,r,session)
                    except Exception as e:
                        raise e
                elif ext in ['c']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back(TR:{ct}){Style.reset}: ")
                        if edit_which.lower() in ['q','quit']:
                            exit("user quit!")
                        elif edit_which.lower() in ['b','back','']:
                            return
                        else:
                            self.setValuePrompt(field,r,session)
                    except Exception as e:
                        raise e
                elif ext in ['e']:
                    #entry id
                    try:
                        cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(Entry.EntryId==cdi).first()
                        if result:
                            self.setValuePrompt(field,result,session)
                    except Exception as e:
                        raise e
                else:
                    result=session.query(Entry)
                    try:
                        try:
                            cdi=int(eval(cd))
                        except Exception as e:
                            print(e)
                            cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi))
                    except Exception as e:
                        print(e)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd)))
                    result=result.all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}{ct}){Style.reset}: ")
                    if edit_which.lower() in ['q','quit']:
                        exit("user quit!")
                    elif edit_which.lower() in ['b','back','']:
                        return
                    else:
                        self.setValuePrompt(field,r,session)
        elif code and field == None and value == None:
            field=input(f"{Fore.green_yellow}Field(see help|?): {Style.reset}")
            if field.lower() in ['q','quit']:
                    exit("user quit!")
            elif field.lower() in ['back','b','']:
                return
            elif field.lower() in ['?','help']:
                self.helpTextPrint()
                return

            if field not in self.valid_field_names:
                raise Exception(f"InvalidField '{field}:{self.valid_field_names}'")
            if field in ['Timestamp',]:
                raise Exception(f"Field not supported for changes yet!")

            with Session(self.engine) as session:
                ext=code.lower().split('.')[0]
                cd=code.lower().split('.')[-1]
                print(code,cd,ext)
                #result=session.query()
                if ext in ['b']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}{ct}){Style.reset}: ")
                        if edit_which.lower() in ['q','quit']:
                            exit("user quit!")
                        elif edit_which.lower() in ['b','back','']:
                            return
                        else:
                            self.setValuePrompt(field,r,session)
                    except Exception as e:
                        raise e
                elif ext in ['c']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}{ct}){Style.reset}: ")
                        if edit_which.lower() in ['q','quit']:
                            exit("user quit!")
                        elif edit_which.lower() in ['b','back','']:
                            return
                        else:
                            self.setValuePrompt(field,r,session)
                    except Exception as e:
                        raise e
                elif ext in ['e']:
                    #entry id
                    try:
                        cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi)).first()
                        if result:
                            self.setValuePrompt(field,result,session)
                    except Exception as e:
                        raise e
                else:
                    result=session.query(Entry)
                    try:
                        try:
                            cdi=int(eval(cd))
                        except Exception as e:
                            print(e)
                            cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi))
                    except Exception as e:
                        print(e)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd)))
                    result=result.all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}{ct}){Style.reset}: ")
                    if edit_which.lower() in ['q','quit']:
                        exit("user quit!")
                    elif edit_which.lower() in ['b','back','']:
                        return
                    else:
                        self.setValuePrompt(field,r,session)
        elif code == None and field == None and value == None:
            code=input(f"{Fore.cyan}Barcode{Style.reset}|{Fore.green_yellow}Code{Style.reset}|{Fore.yellow}EntryId{Style.reset}: ")
            #get item next

            field=input(f"{Fore.green_yellow}Field(see help|?): {Style.reset}")
            if field.lower() in ['q','quit']:
                    exit("user quit!")
            elif field.lower() in ['back','b']:
                return
            elif field.lower() in ['?','help']:
                self.helpTextPrint()

            if field not in self.valid_field_names:
                raise Exception(f"InvalidField '{field}:{self.valid_field_names}'")
            if field in ['Timestamp',]:
                raise Exception(f"Field not supported for changes yet!")

            with Session(self.engine) as session:
                ext=code.lower().split('.')[0]
                cd=code.lower().split('.')[-1]
                if cd.lower() in ['q','quit']:
                    exit("user quit!")
                elif cd.lower() in ['back','b']:
                    return
                elif cd.lower() in ['?','help']:
                    self.helpTextPrint()
                #result=session.query()
                if ext in ['b']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}{ct}){Style.reset}: ")
                        if edit_which.lower() in ['q','quit']:
                            exit("user quit!")
                        elif edit_which.lower() in ['b','back','']:
                            return
                        else:
                            self.setValuePrompt(field,r,session)
                    except Exception as e:
                        raise e
                elif ext in ['c']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}{ct}){Style.reset}: ")
                        if edit_which.lower() in ['q','quit']:
                            exit("user quit!")
                        elif edit_which.lower() in ['b','back','']:
                            return
                        else:
                            self.setValuePrompt(field,r,session)
                    except Exception as e:
                        raise e
                elif ext in ['e']:
                    #entry id
                    try:
                        cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi)).first()
                        if result:
                            self.setValuePrompt(field,result,session)
                    except Exception as e:
                        raise e
                else:
                    result=session.query(Entry)
                    try:
                        try:
                            try:
                                cdi=int(eval(cd))
                            except Exception as e:
                                print(e)
                                cdi=int(cd)
                        except Exception as e:
                            print(e)
                            cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi))
                    except Exception as e:
                        print(e)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd)))
                    result=result.all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Fore.red}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}{ct}){Style.reset}: ")
                    if edit_which.lower() in ['q','quit']:
                        exit("user quit!")
                    elif edit_which.lower() in ['b','back','']:
                        return
                    else:
                        self.setValuePrompt(field,r,session)
        else:
            self.helpTextPrint()

    def setValuePrompt(self,field,entry,session,value=None):
        if not value:
            value=input(f"{Fore.green_yellow}Value {Fore.yellow}OLD{Style.reset}={Fore.tan}{getattr(entry,field)} {Style.reset}({Fore.green}{self.valid_fields[field]}{Style.reset}): ")
        if value.lower() in ['q','quit']:
            exit("user quit!")
        elif value.lower() in ['b','back']:
            return
        elif value.lower() in ['?','help']:
            self.helpTextPrint()

        if value not in ['']:
            t=self.valid_fields[field]
            if isinstance(t,String):
                value=str(value)
            elif isinstance(t,Integer):
                value=int(eval(value))
            elif isinstance(t,Float):
                value=float(eval(value))
            elif isinstance(t,Boolean):
                if value not in ['True','False','1','0']:
                    raise Exception(f"Not a Boolean: {['True','False','1','0']}")
                value=bool(eval(value))
            setattr(entry,field,value)
            #as item was changed, log it in InList==True
            if field != 'InList':
                setattr(entry,"InList",True)
            session.commit()
            session.flush()
            session.refresh(entry)
            print(entry)
        else:
            print(entry)
            print(f"{Fore.dark_goldenrod}{Style.underline}Nothing was changed!{Style.reset}")

def datePickerF(self):
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


def datetimePickerF(self,DATE=None,continue_replaced=False):
    while True:
        try:
            if DATE == None:
                DATE=datePickerF(None)
            if DATE == None:
                return
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
                if continue_replaced:
                    return
                else:
                    continue
            minute=Prompt.__init2__(None,func=mkint,ptext="Minute",helpText=f"minute to use for {self}",data="minute")
            if minute == None:
                if continue_replaced:
                    return
                else:
                    continue
            second=Prompt.__init2__(None,func=mkint,ptext="Second",helpText=f"second to use  for {self}",data="second")
            if second == None:
                if continue_replaced:
                    return
                else:
                    continue
            dt=datetime(year,month,day,hour,minute,second)

            return dt
        except Exception as e:
            print(e) 

class Shift(BASE):
    __tablename__="Shift"
    ShiftId=Column(Integer,primary_key=True)
    Date=Column(Date)
    start=Column(DateTime)
    end=Column(DateTime)
    break_start=Column(DateTime)
    break_end=Column(DateTime)

    def __str__(self):
        msg=f"{Fore.chartreuse_1}Shift({Style.reset}"
        for col in self.__table__.columns:
            color_val=''
            color_field=''
            field=col.name
            if field == 'start':
                color_field=Fore.green_yellow
                color_val=Fore.green+Style.bold
            elif field == 'end':
                color_field=Style.bold+Fore.light_red
                color_val=Fore.light_red
            elif field == 'break_start':
                color_field=Fore.cyan
                color_val=Fore.dark_goldenrod
            elif field == 'break_end':
                color_field=Fore.light_magenta
                color_val=Fore.light_yellow
            elif field == 'Date':
                color_field=Fore.pale_violet_red_1
                color_val=Fore.blue_violet
            elif field == 'ShiftId':
                color_field=Fore.red+Style.italic
                color_val=Fore.grey_35+Style.underline
            
            msg+=f"{color_field}{col.name}{Style.reset}={color_val}{getattr(self,col.name)}{Style.reset},\n"
        if msg.endswith(",\n"):
            msg=msg[:-2]
        msg+=f"{Fore.chartreuse_1}){Style.reset}"
        return msg

    def __repr__(self):
        return self.__str__()



    def estimatedPunches_8h(self,start_time=datetime.now()):
        shift={}
        shift['Start']=start_time
        shift['lunchStart']=start_time+timedelta(seconds=4*60*60)
        shift['lunchEnd']=shift['lunchStart']+timedelta(seconds=30*60)
        shift['end']=shift['lunchEnd']+timedelta(seconds=4*60*60)
        for I in shift:
            print(f"{Fore.light_yellow}{I}{Style.reset}",shift.get(I).ctime(),sep='-')
        return shift

    def manual_estimate_8(self):
        while True:
            dt=datetimePickerF(None,continue_replaced=True)
            if not dt:
                break
            self.estimatedPunches_8h(None,start_time=dt)

    def manual_estimate_7(self):
        while True:
            dt=datetimePickerF(None,continue_replaced=True)
            if not dt:
                break
            self.estimatedPunches_7h(None,start_time=dt)

    def manual_estimate_6(self):
        while True:
            dt=datetimePickerF(None,continue_replaced=True)
            if not dt:
                break
            self.estimatedPunches_6h(None,start_time=dt)

    def manual_estimate_5(self):
        while True:
            dt=datetimePickerF(None,continue_replaced=True)
            if not dt:
                break
            self.estimatedPunches_5h(None,start_time=dt)

    def manual_estimate_4(self):
        while True:
            dt=datetimePickerF(None,continue_replaced=True)
            if not dt:
                break
            self.estimatedPunches_4h(None,start_time=dt)
        
    def estimatedPunches_4h(self,start_time=datetime.now()):
        shift={}
        shift['Start']=start_time
        #shift['lunchStart']=start_time+timedelta(seconds=4*60*60)
        #shift['lunchEnd']=shift['lunchStart']+timedelta(seconds=30*60)
        shift['end']=shift['Start']+timedelta(seconds=4*60*60)
        for I in shift:
            print(f"{Fore.light_yellow}{I}{Style.reset}",shift.get(I).ctime(),sep='-')
        return shift

    def estimatedPunches_5h(self,start_time=datetime.now()):
        shift={}
        shift['Start']=start_time
        shift['lunchStart']=start_time+timedelta(seconds=4*60*60)
        shift['lunchEnd']=shift['lunchStart']+timedelta(seconds=30*60)
        shift['end']=shift['Start']+timedelta(seconds=0.5*60*60)
        shift['Stay 5H and Clock Out Exactly on the 5H Mark']=shift['Start']+timedelta(seconds=5*60*60)
        for I in shift:
            print(f"{Fore.light_yellow}{I}{Style.reset}",shift.get(I).ctime(),sep='-')
        return shift

    def estimatedPunches_6h(self,start_time=datetime.now()):
        shift={}
        shift['Start']=start_time
        shift['lunchStart']=start_time+timedelta(seconds=4*60*60)
        shift['lunchEnd']=shift['lunchStart']+timedelta(seconds=30*60)
        shift['end']=shift['Start']+timedelta(seconds=2*60*60)
        for I in shift:
            print(f"{Fore.light_yellow}{I}{Style.reset}",shift.get(I).ctime(),sep='-')
        return shift

    def estimatedPunches_7h(self,start_time=datetime.now()):
        shift={}
        shift['Start']=start_time
        shift['lunchStart']=start_time+timedelta(seconds=4*60*60)
        shift['lunchEnd']=shift['lunchStart']+timedelta(seconds=30*60)
        shift['end']=shift['Start']+timedelta(seconds=3*60*60)
        for I in shift:
            print(f"{Fore.light_yellow}{I}{Style.reset}",shift.get(I).ctime(),sep='-')
        return shift

    def gross(self,rate,unit="$"):
        try:
            total_duration=None
            if self.start and self.end:
                total_duration=self.end-self.start
            else:
                raise Exception(f"self.start={self.start},self.end={self.end}")
            break_duration=None
            if self.break_start and self.break_end:
                break_duration=self.break_end-self.break_start
            else:
                raise Exception(f"self.break_start={self.break_start},self.break_end={self.break_end}")
            if break_duration and total_duration:
                total_duration=total_duration-break_duration

            if isinstance(rate,float):
                ur=pint.UnitRegistry()
                dur=ur.convert(total_duration.total_seconds(),"seconds","hours")*rate
                dur=round(float(dur),2)
                print(f"{Fore.medium_purple_3b}{unit}{Fore.green}{dur}{Style.reset} @ {Fore.light_salmon_3a}{rate}{Style.reset}/Hr for {Fore.magenta}{total_duration}{Style.reset}")
                return dur
        except Exception as e:
            print(e)
        return 0

    def helpCard(self,start_arg=None):
        if self.start:
            start=self.start
        else:
            if start_arg:
                start=start_arg
            else:
                raise Exception("No valid start time!")
        print(f"{Fore.light_green}{'-'*15}\n|=| Estimated Punch Times |=|\n{Fore.light_yellow}{'-'*15}{Style.reset}")
        print(f"{Fore.light_blue} 4 Hr Shift{Style.reset}")
        print(f"{Fore.grey_70}{'*'*15}{Style.reset}")
        self.estimatedPunches_4h(start_time=start)
        print(f"{Fore.light_magenta} 5 Hr Shift{Style.reset}")
        print(f"{Fore.grey_70}{'*'*15}{Style.reset}")
        self.estimatedPunches_5h(start_time=start)
        print(f"{Fore.light_green} 6 Hr Shift{Style.reset}")
        print(f"{Fore.grey_70}{'*'*15}{Style.reset}")
        self.estimatedPunches_6h(start_time=start)
        print(f"{Fore.cyan} 7 Hr Shift{Style.reset}")
        print(f"{Fore.grey_70}{'*'*15}{Style.reset}")
        self.estimatedPunches_7h(start_time=start)
        print(f"{Fore.yellow} 8 Hr Shift{Style.reset}")
        print(f"{Fore.grey_70}{'*'*15}{Style.reset}")
        self.estimatedPunches_8h(start_time=start)
        print(f"{Fore.medium_violet_red}{'-'*15}\n{Fore.light_yellow}{'-'*15}{Style.reset}")

    def duration_completed(self):
        now=datetime.now()
        self.helpCard()
            
        if self.end:
            try:
                print(f"{Style.bold+Style.underline}{Fore.green_yellow}Shift{Style.reset} Has {Fore.light_red}Ended -> Total Duration{Style.reset}: {(self.end-self.start)-(self.break_end-self.break_start)}")
                print(f"{Style.bold+Style.underline}{Fore.green_yellow}Shift Break{Style.reset}{Fore.light_red} Duration{Style.reset}: {(self.break_end-self.break_start)}")
            except Exception as e:
                print(f"{Style.bold+Style.underline}{Fore.green_yellow}Shift{Style.reset} Has {Fore.light_red}Ended{Style.reset}: (start:{self.end}-end:{self.start})-(break_end:{self.break_end}-break_start:{self.break_start})")
                print(f"{Style.bold+Style.underline}{Fore.green_yellow}Shift{Style.reset} Has {Fore.light_red}Ended{Style.reset}: {(self.end-self.start)}")
        else:
            if self.break_start != None:
                if self.break_end != None:
                    #break is done
                    try:
                        print(f"{Style.bold+Style.underline}{Fore.green_yellow}Break{Style.reset} Is {Fore.medium_violet_red}Completed{Style.reset} Duration:{(now-self.start)-(self.break_end-self.break_start)}")
                    except Exception as e:
                        print(f"{Style.bold+Style.underline}{Fore.green_yellow}Break{Style.reset} Is {Fore.medium_violet_red}Completed{Style.reset} Duration:({now}-{self.start})-({self.break_end}-{self.break_start})")

                else:
                    #break is started but not ended
                    print(f"{Style.bold+Style.underline}{Fore.green_yellow}Break{Style.reset} Is {Fore.pale_green_1b}Started, But Not {Fore.light_red}Ended{Style.reset}: {now-self.break_start}")
            elif self.break_start == None:
                #break has not started
                print(f"{Style.bold+Style.underline}{Fore.green_yellow}Shift{Style.reset} has {Fore.pale_green_1b}Started, But Not {Style.bold+Style.underline}{Fore.green_yellow}Break{Style.reset} {now-self.start}")  

    def __init__(self,start,Date=date.today(),end=None,break_start=None,break_end=None,ShiftId=None):
        if ShiftId:
            self.ShiftId=ShiftId
        self.Date=Date
        self.start=start
        self.end=end
        self.break_end=break_end
        self.break_start=break_start
        

Shift.metadata.create_all(ENGINE)


class Template:
    def init(self,**kwargs):
        __tablename__=kwargs.get("__tablename__")
        fields=[i.name for i in self.__table__.columns]
        for i in fields:
            if i in list(kwargs.keys()):
                setattr(self,i,kwargs.get(i))

    def __str__(self,vc=Fore.light_yellow,fc=Fore.light_green,cc=Fore.light_magenta):
        m=[]
        m.append(f"{cc}{self.__tablename__}{Style.reset}(")
        fields=[i.name for i in self.__table__.columns]
        for i in fields:
            m.append(f"\t{fc}{i}{Style.reset}={vc}{getattr(self,i)}{Style.reset}")
        m.append(")")
        return '\n'.join(m)

class Billing(BASE,Template):
    __tablename__="Billing"
    default=Column(Boolean)
    sellerAddress=Column(String)
    sellerName=Column(String)
    sellerPhone=Column(String)
    sellerEmail=Column(String)
    purchaserEmail=Column(String)
    purchaserPhone=Column(String)
    purchaserName=Column(String)
    purchaserAddress=Column(String)
    BillingId=Column(Integer,primary_key=True)
    Date=Column(Date)
    RetailersPermitSerial=Column(String)
    CertofReg=Column(String)
    PaymentType=Column(String)
    def __init__(self,**kwargs):
        #kwargs['__tablename__']="Billing"
        kwargs['__tablename__']=self.__tablename__
        self.init(**kwargs,)

class RecieptEntry(BASE,Template):
    __tablename__="RecieptEntry"
    ReceiptEntryId=Column(Integer,primary_key=True)
    RecieptId=Column(Integer)
    Date=Column(Date)
    EntryCode=Column(String)
    EntryBarcode=Column(String)
    EntryName=Column(String)
    EntryId=Column(Integer)
    EntryPrice=Column(Float)
    QtySold=Column(Float)
    CRV=Column(Float)
    Tax=Column(Float)
    TaxNote=Column(String)
    def __init__(self,**kwargs):
        kwargs['__tablename__']=self.__tablename__
        self.init(**kwargs)

class AdditionalExpenseOrFee(BASE,Template):
    __tablename__="AdditionalExpenseOrFee"
    AdditionalExpenseId=Column(Integer,primary_key=True)
    RecieptId=Column(Integer)
    Value=Column(Integer)
    Name=Column(String)
    Comment=Column(String)
    DOE=Column(Date)#Date of Entry
    DD=Column(Date)#Due Date
    def __init__(self,**kwargs):
        kwargs['__tablename__']=self.__tablename__
        self.init(**kwargs)

Billing.metadata.create_all(ENGINE)
RecieptEntry.metadata.create_all(ENGINE)
AdditionalExpenseOrFee.metadata.create_all(ENGINE)

class Reciept(BASE,Template):
    __tablename__="Reciept"
    RecieptId=Column(Integer,primary_key=True)
    BillingId=Column(Integer)
    Date=Column(Date)
    
    def __init__(self,**kwargs):
        self.init(**kwargs)
        __tablename__="Reciept"

Reciept.metadata.create_all(ENGINE)
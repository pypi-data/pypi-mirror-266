from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.db import *
import MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.Unified.Unified as unified
import MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.possibleCode as pc
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.Prompt import *
from MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.Prompt import prefix_text
import random
from colored import Style,Fore
import json,sys

class TasksMode:
    def getTotalwithBreakDownForScan(self):
        while True:
            color1=Fore.red
            color2=Fore.yellow
            color3=Fore.cyan
            color4=Fore.green_yellow
            def mkT(text,self):
                return text
            scanned=Prompt.__init2__(None,func=mkT,ptext='barcode|code[help]?',helpText='',data=self)
            if not scanned:
                break
            else:
                with Session(self.engine) as session:
                    result=session.query(Entry).filter(or_(Entry.Barcode==scanned,Entry.Code==scanned),Entry.InList==True).first()
                    if result:
                        backroom=result.BackRoom
                        total=0
                        for f in self.valid_fields:
                            if f not in self.special:
                                if getattr(result,f) not in [None,'']:
                                    total+=float(getattr(result,f))
                        print(result)
                        print(f"{Fore.light_yellow}0 -> {color1}Amount Needed Total+BackRoom {Style.reset}{color2}{Style.bold}{total}{Style.reset}!")
                        print(f"{Fore.cyan}1 -> {color1}Amount Needed Total w/o BackRoom {Style.reset}{color2}{Style.bold}{total-backroom}{Style.reset}!")
                        print(f"{Fore.light_green}2 -> {color1}Amount Needed Total w/o BackRoom - BackRoom {Style.reset}{color2}{Style.bold}{(total-backroom)-backroom}{Style.reset}!")


                        
                    else:
                        print(f"{Fore.red}{Style.bold}No such Barcode|Code with InList==True:{scanned}{Style.reset}")

            

    def display_field(self,fieldname,load=False,above=None,below=None):
        color1=Fore.red
        color2=Fore.yellow
        color3=Fore.cyan
        color4=Fore.green_yellow
        m=f"Item Num |Name|Barcode|Code|{fieldname}|EID"
        hr='-'*len(m)
        print(f"{m}\n{hr}")
        if (fieldname in self.valid_fields) or (load == True and fieldname == 'ListQty'):
            with Session(self.engine) as session:
                query=session.query(Entry).filter(Entry.InList==True)
                if above == None:
                    def mkT(text,self):
                        try:
                            v=int(text)
                        except Exception as e:
                            print(e)
                            v=0
                        return v
                    above=Prompt.__init2__(None,func=mkT,ptext=f"Above [{Fore.light_green}0{Style.reset}]",helpText="anything below this will not be displayed!",data=self)
                if below == None:
                    def mkTBelow(text,self):
                        try:
                            v=int(text)
                        except Exception as e:
                            print(e)
                            v=sys.maxsize
                        return v
                    below=Prompt.__init2__(None,func=mkTBelow,ptext=f"Below [{Fore.light_green}{sys.maxsize}{Style.reset}]",helpText="anything above this will not be displayed!",data=self)
                if above != None:
                    print(type(above),above,fieldname)
                    query=query.filter(getattr(Entry,fieldname)>above)
                if below != None:
                    query=query.filter(getattr(Entry,fieldname)<below)
                results=query.all()
                if len(results) < 1:
                    print(f"{Fore.red}{Style.bold}Nothing is in List!{Style.reset}")
                for num,result in enumerate(results):
                    print(f"{Fore.red}{num}{Style.reset} -> {color1}{result.Name}{Style.reset}|{color2}{result.Barcode}{Style.reset}|{color3}{result.Code}{Style.reset}|{color4}{getattr(result,fieldname)}{Style.reset}|{Fore.yellow}{getattr(result,'EntryId')}{Style.reset}")
        print(f"{m}\n{hr}")

    def setFieldInList(self,fieldname,load=False):
        while True:
            if (fieldname not in self.special or fieldname in ['Facings'] )or (load==True and fieldname in ['ListQty',]):
                m=f"Item Num |Name|Barcode|Code|{fieldname}|EID"
                hr='-'*len(m)
                print(f"{m}\n{hr}")
                if (fieldname in self.valid_fields) or (load==True and fieldname in ['ListQty',]):
                    with Session(self.engine) as session:
                        code=''
                        
                        def mkT(text,self):
                            return str(text)
                        code=Prompt.__init2__(None,func=mkT,ptext="barcode|code",helpText=self.helpText_barcodes,data=self)
                        if code == None:
                            break
                        pc.PossibleCodes(scanned=code)
                        pc.PossibleCodesEAN13(scanned=code)
                            
                        value=0
                        def mkT(text,self):
                            try:
                                return float(eval(text)),text
                            except Exception as e:
                                return float(0),text

                        p=Prompt.__init2__(None,func=mkT,ptext="amount|+amount|-amount",helpText=self.helpText_barcodes,data=self)
                        if p:
                            value,text=p
                        else:
                            continue
                        try:
                            color1=Fore.red
                            color2=Fore.yellow
                            color3=Fore.cyan
                            color4=Fore.green_yellow 
                            if text.startswith("-") or text.startswith("+"):
                                result=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code)).first()
                                if result:
                                    setattr(result,fieldname,getattr(result,fieldname)+float(value))
                                    result.InList=True
                                    session.commit()
                                    session.flush()
                                    session.refresh(result)
                                    print(f"{Fore.red}0{Style.reset} -> {color1}{result.Name}{Style.reset}|{color2}{result.Barcode}{Style.reset}|{color3}{result.Code}{Style.reset}|{color4}{getattr(result,fieldname)}{Style.reset}|{color4}{getattr(result,'EntryId')}{Style.reset}")
                                    print(f"{m}\n{hr}")

                                else:
                                    n=Entry(Barcode=code,Code='',Name=code,InList=True,Note="New Item")
                                    setattr(n,fieldname,value)
                                    session.add(n)
                                    session.commit()
                                    session.flush()
                                    session.refresh(n)
                                    result=n
                                    print(f"{Fore.red}0{Style.reset} -> {color1}{result.Name}{Style.reset}|{color2}{result.Barcode}{Style.reset}|{color3}{result.Code}{Style.reset}|{color4}{getattr(result,fieldname)}{Style.reset}|{color4}{getattr(result,'EntryId')}{Style.reset}")

                                    print(f"{m}\n{hr}")
                            else:
                                result=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code)).first()
                                if result:
                                    setattr(result,fieldname,value)
                                    result.InList=True
                                    session.commit()
                                    session.flush()
                                    session.refresh(result)
                                    print(f"{Fore.red}0{Style.reset} -> {color1}{result.Name}{Style.reset}|{color2}{result.Barcode}{Style.reset}|{color3}{result.Code}{Style.reset}|{color4}{getattr(result,fieldname)}{Style.reset}|{color4}{getattr(result,'EntryId')}{Style.reset}")

                                    print(f"{m}\n{hr}")

                                else:
                                    n=Entry(Barcode=code,Code='',Name=code,InList=True,Note="New Item")
                                    setattr(n,fieldname,value)
                                    session.add(n)
                                    session.commit()
                                    session.flush()
                                    session.refresh(n)
                                    result=n
                                    print(f"{Fore.red}0{Style.reset} -> {color1}{result.Name}{Style.reset}|{color2}{result.Barcode}{Style.reset}|{color3}{result.Code}{Style.reset}|{color4}{getattr(result,fieldname)}{Style.reset}|{color4}{getattr(result,'EntryId')}{Style.reset}")

                                    print(f"{m}\n{hr}")

                                    #raise Exception(result)
                        except Exception as e:
                            print(e)
            else:
                #code for tags,caseId[br,6w,ld],
                self.processSpecial(fieldname)
                break
    helpText_barcodes=f"""
    1. Enter the EntryId into the prompt
    2. if an entry is found you will be prompted for a code to be saved
    """
    def setBarcodes(self,fieldname):
         while True:
            try:
                def mkT(text,self):
                    return text
                cmd=Prompt.__init2__(None,func=mkT,ptext='Do What[help/q/b/$EntryId]?',helpText=self.helpText_barcodes,data=self)
                if not cmd:
                    break
                else:
                    with Session(self.engine) as session:
                        r=session.query(Entry).filter(Entry.EntryId==int(cmd)).first()
                        if r:
                            def mkT(text,self):
                                return text
                            code=Prompt.__init2__(None,func=mkT,ptext=f'{fieldname}[help]?',helpText=self.helpText_barcodes,data=self)
                            if not code:
                                break
                            else:
                                setattr(r,fieldname,code)
                                session.commit()
                                session.flush()
                                session.refresh(r)
                                print(r)
            except Exception as e:
                print(e)



    def processSpecial(self,fieldname):
        if fieldname.lower() == "tags":
            self.editTags()
        elif 'Barcode' in fieldname:
            self.setBarcodes(fieldname)
        else:
            print("SpecialOPS Fields! {fieldname} Not Implemented Yet!")
            self.editCaseIds()


    helpText_caseIds=f'''
{Fore.green_yellow}$WHERE,$EntryId,exec()|$ID{Style.reset}
#[ld,6w,br,all],$EntryId,generate - create a synthetic id for case and save item to and save qrcode png of $case_id in $WHERE
#[ld,6w,br,all],$EntryId,$case_id - set case id for item in $WHERE
#[ld,6w,br,all],$EntryId - display item case id in $WHERE
[ld,6w,br,all],s|search,$case_id - display items associated with $case_id in $WHERE
#[ld,6w,br,all],$EntryId,clr_csid - set $case_id to '' in $WHERE
where:
 ld is for Load
 6w is 6-Wheeler or U-Boat
 br is BackRoom
 
 all will apply to all of the above fields
    '''
    def editCaseIds(self):
         while True:
            def mkT(text,self):
                return text
            cmd=Prompt.__init2__(None,func=mkT,ptext='Do What[help]?',helpText=self.helpText_tags,data=self)
            if not cmd:
                break
            else:
                print(cmd)
                split_cmd=cmd.split(",")
                if len(split_cmd)==3:
                    mode=split_cmd[0]
                    eid=split_cmd[1]
                    ex=split_cmd[2]
                    if eid.lower() in ['s','search']:
                        #search
                        with Session(self.engine) as session:
                            results=[]
                            if split_cmd[0].lower() == '6w':
                                results=session.query(Entry).filter(Entry.CaseID_6W==ex).all()
                            elif split_cmd[0].lower() == 'ld':
                                results=session.query(Entry).filter(Entry.CaseID_LD==ex).all()
                            elif split_cmd[0].lower() == 'br':
                                results=session.query(Entry).filter(Entry.CaseID_BR==ex).all()
                            elif split_cmd[0].lower() == 'all':
                                results=session.query(Entry).filter(or_(Entry.CaseID_BR==ex,Entry.CaseID_LD==ex,Entry.CaseID_6W==ex)).all()
                            if len(results) < 1:
                                print(f"{Fore.dark_goldenrod}No Items to display!{Style.reset}")
                            for num,r in enumerate(results):
                                print(f"{Fore.red}{num}{Style.reset} -> {r}")
                    else:
                        with Session(self.engine) as session:
                            query=session.query(Entry).filter(Entry.EntryId==int(eid)).first()
                            if query:
                                if ex.lower() in ['clr_csid',]:
                                    if split_cmd[0].lower() == '6w':
                                        query.CaseID_6W=''
                                    elif split_cmd[0].lower() == 'ld':
                                        query.CaseID_LD=''
                                    elif split_cmd[0].lower() == 'br':
                                        query.CaseID_BR=''
                                    elif split_cmd[0].lower() == 'all':
                                        query.CaseID_6W=''
                                        query.CaseID_LD=''
                                        query.CaseID_BR=''
                                elif ex.lower() in ['generate','gen','g']:
                                    if split_cmd[0].lower() == '6w':
                                        query.CaseID_6W=query.synthetic_field_str()
                                    elif split_cmd[0].lower() == 'ld':
                                        query.CaseID_LD=query.synthetic_field_str()
                                    elif split_cmd[0].lower() == 'br':
                                        query.CaseID_BR=query.synthetic_field_str()
                                    elif split_cmd[0].lower() == 'all':
                                        query.CaseID_6W=query.synthetic_field_str()
                                        query.CaseID_LD=query.synthetic_field_str()
                                        query.CaseID_BR=query.synthetic_field_str()
                                else:
                                    if split_cmd[0].lower() == '6w':
                                        query.CaseID_6W=ex
                                    elif split_cmd[0].lower() == 'ld':
                                        query.CaseID_LD=ex
                                    elif split_cmd[0].lower() == 'br':
                                        query.CaseID_BR=ex
                                    elif split_cmd[0].lower() == 'all':
                                        query.CaseID_6W=ex
                                        query.CaseID_LD=ex
                                        query.CaseID_BR=ex
                                session.commit()
                                session.flush()
                                session.refresh(query)
                                print(f"""
    Name: {query.Name}
    Barcode: {query.Barcode}
    Code: {query.Code}
    EntryId: {query.EntryId}
    CaseId 6W: {query.CaseID_6W}
    CaseId LD: {query.CaseID_LD}
    CaseId BR: {query.CaseID_BR}
    """)
                elif len(split_cmd)==2:
                    with Session(self.engine) as session:
                        query=session.query(Entry).filter(Entry.EntryId==int(split_cmd[1]))
                        r=query.first()
                        if r:
                            if split_cmd[0].lower() == '6w':
                                print(r.CaseID_6W)
                            elif split_cmd[0].lower() == 'ld':
                                print(r.CaseID_LD)
                            elif split_cmd[0].lower() == 'br':
                                print(r.CaseID_BR)
                                #self.CaseID_BR=CaseID_BR
                                #self.CaseID_LD=CaseID_LD
                                #self.CaseID_6W=CaseID_6W
                        else:
                            print(f"{Fore.dark_goldenrod}No Such Item!{Style.reset}")
                else:
                    print(self.helpText_caseIds)


    helpText_tags=f'''{prefix_text}
{Fore.green_yellow}$mode[=|R,+,-],$TAG_TEXT,$fieldname,$id|$code|$barcode|$fieldData_to_id{Style.reset}
{Fore.cyan}=|R{Style.reset} -> {Fore.yellow}{Style.bold}set Tag to $TAG_TEXT{Style.reset}
{Fore.cyan}+{Style.reset} -> {Fore.yellow}{Style.bold}add $TAG_TEXT to Tag{Style.reset}
{Fore.cyan}-{Style.reset} -> {Fore.yellow}{Style.bold}remove $TAG_TEXT from Tag{Style.reset}
{Fore.cyan}s|search{Style.reset} -> {Fore.yellow}{Style.bold}search for items containing Tag{Style.reset}
{Fore.cyan}l|list{Style.reset} -> {Fore.yellow}{Style.bold}List All Tags{Style.reset}
{Fore.light_red}{Style.bold}This performs operations on all results found without confirmation for mass tag-edits{Style.reset}
{Fore.cyan}ba|bta|bulk_tag_add{Style.reset} -> {Fore.yellow}{Style.bold}Bulk add Tags to {Fore.light_magenta}{Style.underline}#code{Style.reset}
{Fore.cyan}br|btr|bulk_tag_rem{Style.reset} -> {Fore.yellow}{Style.bold}Bulk remove Tags from {Fore.light_magenta}{Style.underline}#code{Style.reset}
{Fore.red}{Style.bold}reset_all_tags|clear_all_tags -> {Fore.yellow}{Style.underline} reset all tags to []{Style.reset}
    '''
    def editTags(self):
        while True:
            #cmd=input("Do What[help]?: ")
            #PROMPT
            def mkT(text,self):
                return text
            cmd=Prompt.__init2__(None,func=mkT,ptext='Do What[help]?',helpText=self.helpText_tags,data=self)
            if not cmd:
                break

            if cmd.lower() in ['l','list']:
                with Session(self.engine) as session:
                    tags=[]
                    allTags=session.query(Entry).all()
                    for i in allTags:
                        if i.Tags and i.Tags != '':
                            try:
                                tl=json.loads(i.Tags)
                                for t in tl:
                                    if t not in tags:
                                        tags.append(t)
                            except Exception as e:
                                print(e)
                    tagCt=len(tags)
                    for num,t in enumerate(tags):
                        print(f"{Fore.green}{num}{Style.reset}/{Fore.light_red}{tagCt-1}{Style.reset} -> {Fore.light_magenta}'{Style.reset}{Fore.grey_70}{t}{Style.reset}{Fore.light_magenta}'{Style.reset}")
            elif cmd.lower() in ['s','search']:
                def mkT(text,self):
                    return text
                tag=Prompt.__init2__(None,func=mkT,ptext='Tag[help]?',helpText=self.helpText_tags,data=self)
                if not tag:
                    break
               
                with Session(self.engine) as session:
                    results=session.query(Entry).all()
                    ct=len(results)
                    t=[]
                    for num,r in enumerate(results):
                        #print(r.Tags)
                        try:
                            if r.Tags not in ['',None]:

                                if tag in list(json.loads(r.Tags)):
                                    t.append(r)
                        except Exception as e:
                            pass
                    for num,rr in enumerate(t):
                        print(f"{Fore.green}{num}{Style.reset}/{Fore.light_red}{ct}{Style.reset} -> {rr}")
                    print(f"{Fore.light_yellow}there was/were {Style.reset}{Fore.light_blue}{len(t)} Results.{Style.reset}")
                    inlist=Prompt.__init2__(None,func=mkT,ptext='Set Results to Have InList=True[help]?',helpText=self.helpText_tags,data=self)
                    if not inlist:
                        break
                    if inlist.lower() in ['y','yes']:
                        ct2=len(t)
                        for num,x in enumerate(t):
                            x.InList=True
                            print(f"{Fore.light_green}{num}{r.EntryId}={Style.reset}{Fore.light_yellow}{r.InList}{Style.reset}/{Fore.light_red}{ct2}{Style.reset}")
                            if num%50 ==0:
                                session.commit()
                        session.commit()
            elif cmd.lower() in ['ba','bulk_tag_add']:
                while True:
                    try:
                        with Session(self.engine) as session:
                            query=session.query(Entry)
                            def mkT(text,self):
                                return text
                            tag=Prompt.__init2__(None,func=mkT,ptext="Tag",helpText="Tag to add to code")
                            while True:
                                try:
                                    #code=Prompt.__init2__(None,func=mkT,ptext="Code|Barcode",helpText=f"Code|Barcode to add Tag:'{tag}' to.")
                                    #if code in [None,]:
                                    #    break
                                    def addTag(session,entry,tag):
                                        try:
                                            old=list(json.loads(entry.Tags))
                                            if tag not in old:
                                                old.append(tag)
                                            entry.Tags=json.dumps(old)
                                        except Exception as e:
                                            print(e)
                                            entry.Tags=json.dumps([tag,])
                                        session.commit()
                                        session.flush()
                                        session.refresh(entry)
                                        
                                    def e_do(self,code,tag):
                                        with Session(self.engine) as session:
                                            try:
                                                code=int(code)
                                                query=session.query(Entry).filter(Entry.EntryId==code)
                                                results=query.all()
                                                ct=len(results)
                                                if len(results)==0:
                                                    print(f"{Fore.light_red}No Entry was found to match that code '{code}'{Style.reset}")
                                                for num,r in enumerate(results):
                                                    if num%2==0:
                                                        colorEntry=Style.bold
                                                    else:
                                                        colorEntry=Fore.grey_70+Style.underline
                                                    addTag(session,r,tag)
                                                    session.refresh(r)
                                                    compound=f'{colorEntry}{r.Name}|{r.Barcode}|{r.Code}|{r.EntryId}|{r.Tags}{Style.reset}'
                                                    if num == 0:
                                                        color1=Fore.light_green
                                                    elif num > 0 and num%2==0:
                                                        color1=Fore.green_yellow
                                                    elif num > 0 and num%2!=0:
                                                        color1=Fore.dark_goldenrod
                                                    elif num+1 == ct:
                                                        color1=Fore.light_red
                                                    print(f"{color1}{num}{Style.reset}/{Fore.red}{ct-1}{Style.reset} {compound}")
                                            except Exception as e:
                                                print(e)

                                    def b_do(self,code,tag):
                                        with Session(self.engine) as session:
                                            query=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Barcode.icontains(code)))
                                            results=query.all()
                                            ct=len(results)
                                            if len(results)==0:
                                                print(f"{Fore.light_red}No Entry was found to match that code '{code}'{Style.reset}")                                            
                                            for num,r in enumerate(results):
                                                if num%2==0:
                                                    colorEntry=Style.bold
                                                else:
                                                    colorEntry=Fore.grey_70+Style.underline
                                                addTag(session,r,tag)
                                                session.refresh(r)
                                                compound=f'{colorEntry}{r.Name}|{r.Barcode}|{r.Code}|{r.EntryId}|{r.Tags}{Style.reset}'
                                                if num == 0:
                                                    color1=Fore.light_green
                                                elif num > 0 and num%2==0:
                                                    color1=Fore.green_yellow
                                                elif num > 0 and num%2!=0:
                                                    color1=Fore.dark_goldenrod
                                                elif num+1 == ct:
                                                    color1=Fore.light_red
                                                print(f"{color1}{num}{Style.reset}/{Fore.red}{ct-1}{Style.reset} {compound}")

                                    def c_do(self,code,tag):
                                        with Session(self.engine) as session:
                                            query=session.query(Entry).filter(or_(Entry.Code==code,Entry.Code.icontains(code)))
                                            results=query.all()
                                            ct=len(results)
                                            if len(results)==0:
                                                print(f"{Fore.light_red}No Entry was found to match that code '{code}'{Style.reset}")
                                            for num,r in enumerate(results):
                                                if num%2==0:
                                                    colorEntry=Style.bold
                                                else:
                                                    colorEntry=Fore.grey_70+Style.underline
                                                addTag(session,r,tag)
                                                session.refresh(r)
                                                compound=f'{colorEntry}{r.Name}|{r.Barcode}|{r.Code}|{r.EntryId}|{r.Tags}{Style.reset}'
                                                if num == 0:
                                                    color1=Fore.light_green
                                                elif num > 0 and num%2==0:
                                                    color1=Fore.green_yellow
                                                elif num > 0 and num%2!=0:
                                                    color1=Fore.dark_goldenrod
                                                elif num+1 == ct:
                                                    color1=Fore.light_red
                                                print(f"{color1}{num}{Style.reset}/{Fore.red}{ct-1}{Style.reset} {compound}")
                                    def do(self,code,tag):
                                        with Session(self.engine) as session:
                                            query=session.query(Entry).filter(or_(Entry.Code==code,Entry.Barcode==code,Entry.Code.icontains(code),Entry.Barcode.icontains(code)))
                                            results=query.all()
                                            ct=len(results)
                                            if len(results)==0:
                                                print(f"{Fore.light_red}No Entry was found to match that code '{code}'{Style.reset}")
                                            for num,r in enumerate(results):
                                                if num%2==0:
                                                    colorEntry=Style.bold
                                                else:
                                                    colorEntry=Fore.grey_70+Style.underline
                                                addTag(session,r,tag)
                                                compound=f'{colorEntry}{r.Name}|{r.Barcode}|{r.Code}|{r.EntryId}|{r.Tags}{Style.reset}'
                                                if num == 0:
                                                    color1=Fore.light_green
                                                elif num > 0 and num%2==0:
                                                    color1=Fore.green_yellow
                                                elif num > 0 and num%2!=0:
                                                    color1=Fore.dark_goldenrod
                                                elif num+1 == ct:
                                                    color1=Fore.light_red
                                                print(f"{color1}{num}{Style.reset}/{Fore.red}{ct-1}{Style.reset} {compound}")
                                                    
                                    ex={
                                        'delim':'.',
                                        'e_do':lambda code,tag=tag,self=self:e_do(self,code,tag),
                                        'c_do':lambda code,tag=tag,self=self:c_do(self,code,tag),
                                        'b_do':lambda code,tag=tag,self=self:b_do(self,code,tag),
                                        'do':lambda code,tag=tag,self=self:do(self,code,tag)
                                    }
                                    status=Prompt(func=prefix_filter,ptext="Code|Barcode|(e|B|c).$code) ",helpText="Code|Barcode|EntryId to have tag applied to prefix will use the specified field e. == EntryID, c. == Code, B. == Barcode.",data=ex)
                                    if status.status == False:
                                        break   
                                except Exception as e:
                                    print(e)

                        break
                    except Exception as e:
                        print(e)
            elif cmd.lower() in ['br','btr','bulk_tag_rem']:
                while True:
                    try:
                        with Session(self.engine) as session:
                            query=session.query(Entry)
                            def mkT(text,self):
                                return text
                            tag=Prompt.__init2__(None,func=mkT,ptext="Tag",helpText="Tag to remove from code")
                            while True:
                                try:
                                    #code=Prompt.__init2__(None,func=mkT,ptext="Code|Barcode",helpText=f"Code|Barcode to add Tag:'{tag}' to.")
                                    #if code in [None,]:
                                    #    break
                                    def remTag(session,entry,tag):
                                        try:
                                            old=list(json.loads(entry.Tags))
                                            if tag not in old:
                                                return
                                            tmp=[]
                                            for t in old:
                                                if t != tag:
                                                    tmp.append(t)
                                            entry.Tags=json.dumps(tmp)
                                        except Exception as e:
                                            print(e)
                                            entry.Tags=json.dumps([])
                                        session.commit()
                                        session.flush()
                                        session.refresh(entry)

                                    def e_do(self,code,tag):
                                        with Session(self.engine) as session:
                                            try:
                                                code=int(code)
                                                query=session.query(Entry).filter(Entry.EntryId==code)
                                                results=query.all()
                                                ct=len(results)
                                                if len(results)==0:
                                                    print(f"{Fore.light_red}No Entry was found to match that code '{code}'{Style.reset}")
                                                for num,r in enumerate(results):
                                                    results=query.all()
                                                    if num%2==0:
                                                        colorEntry=Style.bold
                                                    else:
                                                        colorEntry=Fore.grey_70+Style.underline
                                                    remTag(session,r,tag)
                                                    session.refresh(r)
                                                    compound=f'{colorEntry}{r.Name}|{r.Barcode}|{r.Code}|{r.EntryId}|{r.Tags}{Style.reset}'
                                                    if num == 0:
                                                        color1=Fore.light_green
                                                    elif num > 0 and num%2==0:
                                                        color1=Fore.green_yellow
                                                    elif num > 0 and num%2!=0:
                                                        color1=Fore.dark_goldenrod
                                                    elif num+1 == ct:
                                                        color1=Fore.light_red
                                                    print(f"{color1}{num}{Style.reset}/{Fore.red}{ct-1}{Style.reset} {compound}")
                                                    
                                            except Exception as e:
                                                print(e)

                                    def b_do(self,code,tag):
                                        with Session(self.engine) as session:
                                            query=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Barcode.icontains(code)))
                                            results=query.all()
                                            ct=len(results)
                                            if len(results)==0:
                                                print(f"{Fore.light_red}No Entry was found to match that code '{code}'{Style.reset}")                                            
                                            for num,r in enumerate(results):
                                                if num%2==0:
                                                    colorEntry=Style.bold
                                                else:
                                                    colorEntry=Fore.grey_70+Style.underline
                                                remTag(session,r,tag)
                                                session.refresh(r)
                                                compound=f'{colorEntry}{r.Name}|{r.Barcode}|{r.Code}|{r.EntryId}|{r.Tags}{Style.reset}'
                                                if num == 0:
                                                    color1=Fore.light_green
                                                elif num > 0 and num%2==0:
                                                    color1=Fore.green_yellow
                                                elif num > 0 and num%2!=0:
                                                    color1=Fore.dark_goldenrod
                                                elif num+1 == ct:
                                                    color1=Fore.light_red
                                                print(f"{color1}{num}{Style.reset}/{Fore.red}{ct-1}{Style.reset} {compound}")
                                                    
                                                #print(f"{Fore.light_yellow}{num}{Style.reset}/{Fore.light_red}{ct}{Style.reset} -> {r}")
                                                #remTag(session,r,tag)

                                    def c_do(self,code,tag):
                                        with Session(self.engine) as session:
                                            query=session.query(Entry).filter(or_(Entry.Code==code,Entry.Code.icontains(code)))
                                            results=query.all()
                                            ct=len(results)
                                            if len(results)==0:
                                                print(f"{Fore.light_red}No Entry was found to match that code '{code}'{Style.reset}")
                                            for num,r in enumerate(results):
                                                if num%2==0:
                                                    colorEntry=Style.bold
                                                else:
                                                    colorEntry=Fore.grey_70+Style.underline
                                                remTag(session,r,tag)
                                                session.refresh(r)
                                                compound=f'{colorEntry}{r.Name}|{r.Barcode}|{r.Code}|{r.EntryId}|{r.Tags}{Style.reset}'
                                                if num == 0:
                                                    color1=Fore.light_green
                                                elif num > 0 and num%2==0:
                                                    color1=Fore.green_yellow
                                                elif num > 0 and num%2!=0:
                                                    color1=Fore.dark_goldenrod
                                                elif num+1 == ct:
                                                    color1=Fore.light_red
                                                print(f"{color1}{num}{Style.reset}/{Fore.red}{ct-1}{Style.reset} {compound}")
                                                    
                                    def do(self,code,tag):
                                        with Session(self.engine) as session:
                                            query=session.query(Entry).filter(or_(Entry.Code==code,Entry.Barcode==code,Entry.Code.icontains(code),Entry.Barcode.icontains(code)))
                                            results=query.all()
                                            ct=len(results)
                                            if len(results)==0:
                                                print(f"{Fore.light_red}No Entry was found to match that code '{code}'{Style.reset}")
                                            for num,r in enumerate(results):
                                                if num%2==0:
                                                    colorEntry=Style.bold
                                                else:
                                                    colorEntry=Fore.grey_70+Style.underline
                                                remTag(session,r,tag)
                                                session.refresh(r)
                                                compound=f'{colorEntry}{r.Name}|{r.Barcode}|{r.Code}|{r.EntryId}|{r.Tags}{Style.reset}'
                                                if num == 0:
                                                    color1=Fore.light_green
                                                elif num > 0 and num%2==0:
                                                    color1=Fore.green_yellow
                                                elif num > 0 and num%2!=0:
                                                    color1=Fore.dark_goldenrod
                                                elif num+1 == ct:
                                                    color1=Fore.light_red
                                                print(f"{color1}{num}{Style.reset}/{Fore.red}{ct-1}{Style.reset} {compound}")
                                                    
                                    ex={
                                        'delim':'.',
                                        'e_do':lambda code,tag=tag,self=self:e_do(self,code,tag),
                                        'c_do':lambda code,tag=tag,self=self:c_do(self,code,tag),
                                        'b_do':lambda code,tag=tag,self=self:b_do(self,code,tag),
                                        'do':lambda code,tag=tag,self=self:do(self,code,tag)
                                    }
                                    status=Prompt(func=prefix_filter,ptext="Code|Barcode|(e|B|c).$code) ",helpText="Code|Barcode|EntryId to have tag remove from (prefix will use the specified field e. == EntryID, c. == Code, B. == Barcode.)",data=ex)
                                    if status.status == False:
                                        break   
                                except Exception as e:
                                    print(e)

                        break
                    except Exception as e:
                        print(e)
            elif cmd.lower() in ['reset_all_tags','clear_all_tags',]:
                with Session(self.engine) as session:
                    query=session.query(Entry)
                    results=query.all()
                    ct=len(results)
                    if ct == 0:
                        print(f"{Fore.red}No Entry's with Tags to reset!{Style.reset}")
                    for num,r in enumerate(results):
                        if num%2==0:
                            colorEntry=Style.bold
                        else:
                            colorEntry=Fore.grey_70+Style.underline
                        compound=f'{colorEntry}{r.Name}|{r.Barcode}|{r.Code}|{r.EntryId}|{r.Tags}{Style.reset}'
                        if num == 0:
                            color1=Fore.light_green
                        elif num > 0 and num%2==0:
                            color1=Fore.green_yellow
                        elif num > 0 and num%2!=0:
                            color1=Fore.dark_goldenrod
                        elif num+1 == ct:
                            color1=Fore.light_red

                        print(f"{color1}{num}{Style.reset}/{Fore.red}{ct-1}{Style.reset} {compound}")
            else:
                split_cmd=cmd.split(",")
                if len(split_cmd) == 4:
                    #$mode,$search_fieldname,$EntryId,$tag
                    mode=split_cmd[0]
                    tag=[split_cmd[1],] 
                    search_fieldname=split_cmd[2]
                    eid=int(split_cmd[3])
                    with Session(self.engine) as session:
                        result=session.query(Entry).filter(Entry.__dict__.get(search_fieldname)==eid).all()
                        for num,r in enumerate(result):
                            msg=''
                            if r.Tags == '':
                                 r.Tags=json.dumps(list(tag))
                            
                            if mode in ['=','r','R']:
                                r.Tags=json.dumps(list(tag))
                            elif mode == '+':
                                try:
                                    old=json.loads(r.Tags)
                                    if tag[0] not in old:
                                        old.append(tag[0])
                                        r.Tags=json.dumps(old)
                                    else:
                                        msg=f"{Fore.light_yellow}Tag is Already Applied Nothing will be Done!{Style.reset}"
                                except Exception as e:
                                    print(e)
                            elif mode == '-':
                                try:
                                    old=json.loads(r.Tags)
                                    if tag[0] in old:
                                        i=old.index(tag[0])
                                        old.pop(i)
                                        r.Tags=json.dumps(old)
                                    else:
                                        msg=f"{Fore.light_red}No Such Tag in Item...{Fore.light_yellow} Nothing will be done!{Style.reset}"
                                except Exception as e:
                                    print(e)
                                

                            
                            session.commit()
                            session.flush()
                            session.refresh(r)
                            print(r)
                            print(msg)
                else:
                    print(self.helpText_tags)


    def setName(self):
        with Session(self.engine) as session:
            def mkT(text,self):
                    return text
            code=Prompt.__init2__(None,func=mkT,ptext='Code|Barcode[help]?',helpText='',data=self)
            if not code:
                return
            
            value=Prompt.__init2__(None,func=mkT,ptext='Name[help]?',helpText='',data=self)
            if not value:
                return
           
            result=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code)).first()
            if result:
                result.Name=value
                session.commit()
                session.flush()
                session.refresh(result)
                print(result)
            else:
                print(f"{Fore.red}{Style.bold}No Such Item Identified by '{code}'{Style.reset}")

    def list_total(self):
        with Session(self.engine) as session:
            results=session.query(Entry).filter(Entry.InList==True).all()
            ct=len(results)
            total=0
            total_case=0
            total_units=0
            total_units_br=0
            for num,r in enumerate(results):
                print(f"{Fore.green}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} -> {r}")
                total+=r.total_value(CaseMode=False)
                total_case+=r.total_value(CaseMode=True)
                total_units+=r.total_units()
                total_units_br+=r.total_units(BackRoom=False)
            #print(total_units,total_units_br)
            print(f"""
{Fore.light_green}Total By Units: ${Fore.light_red}{total}{Style.reset}{Fore.green_yellow} for{Fore.light_red} {total_units} w/BackRoom{Fore.light_green} | {total_units_br} {Fore.light_magenta}wo/BackRoom{Style.reset}
{Fore.light_green}Total By Case: ${Fore.light_red}{total_case}{Style.reset}{Fore.green_yellow} for{Fore.light_red} {total_units} w/BackRoom{Fore.light_green} | {total_units_br} {Fore.light_magenta}wo/BackRoom{Style.reset} 
""")

    def __init__(self,engine,parent):
        self.engine=engine
        self.parent=parent
        self.special=['Tags','ALT_Barcode','DUP_Barcode','CaseID_6W','CaseID_BR','CaseID_LD','Facings']
        self.valid_fields=['Shelf',
        'BackRoom',
        'Display_1',
        'Display_2',
        'Display_3',
        'Display_4',
        'Display_5',
        'Display_6',
        'ALT_Barcode',
        'DUP_Barcode',
        'CaseID_BR',
        'CaseID_LD',
        'CaseID_6W',
        'Tags',
        'Facings',
        'SBX_WTR_DSPLY',
        'SBX_CHP_DSPLY',
        'SBX_WTR_KLR',
        'FLRL_CHP_DSPLY',
        'FLRL_WTR_DSPLY',
        'WD_DSPLY',
        'CHKSTND_SPLY',
        ]
        '''
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
        '''
        #self.display_field("Shelf")
        self.options={
                '1':{
                    'cmds':['q','quit','#1'],
                    'desc':"quit program",
                    'exec':lambda: exit("user quit!"),
                    },
                '2':{
                    'cmds':['b','back','#2'],
                    'desc':'go back menu if any',
                    'exec':None
                    },
                }
        #autogenerate duplicate functionality for all valid fields for display
        count=3
        for entry in self.valid_fields:
            self.options[entry]={
                    'cmds':["#"+str(count),f"ls {entry}"],
                    'desc':f'list needed @ {entry}',
                    'exec':lambda self=self,entry=entry: self.display_field(f"{entry}"),
                    }
            count+=1
        #setoptions
        #self.setFieldInList("Shelf")
        for entry in self.valid_fields:
            self.options[entry+"_set"]={
                    'cmds':["#"+str(count),f"set {entry}"],
                    'desc':f'set needed @ {entry}',
                    'exec':lambda self=self,entry=entry: self.setFieldInList(f"{entry}"),
                    }
            count+=1
        self.options["lu"]={
                    'cmds':["#"+str(count),f"lookup","lu","check","ck"],
                    'desc':f'get total for valid fields',
                    'exec':lambda self=self,entry=entry: self.getTotalwithBreakDownForScan(),
                    }
        count+=1
        self.options["setName"]={
                    'cmds':["#"+str(count),f"setName","sn"],
                    'desc':f'set name for item by barcode!',
                    'exec':lambda self=self,entry=entry: self.setName(),
                    }
        count+=1
        self.options["setListQty"]={
                    'cmds':["#"+str(count),f"setListQty","slq"],
                    'desc':f'set ListQty for Values not wanted to be included in totals.',
                    'exec':lambda self=self: self.setFieldInList("ListQty",load=True),
                    }
        count+=1
        self.options["lsListQty"]={
                    'cmds':["#"+str(count),f"lsListQty","ls-lq"],
                    'desc':f'show ListQty for Values not wanted to be included in totals.',
                    'exec':lambda self=self: self.display_field("ListQty",load=True),
                    }
        count+=1
        self.options["listTotal"]={
                    'cmds':["#"+str(count),f"listTotal","list_total"],
                    'desc':f'show list total value.',
                    'exec':lambda self=self: self.list_total(),
                    }
        count+=1


        while True:
            def mkT(text,self):
                return text
            command=Prompt.__init2__(None,func=mkT,ptext='Do What[help/??/?]',helpText=self.parent.help(print_no=True),data=self)
            if not command:
                break
            #command=input(f"{Style.bold}{Fore.green}do what[??/?]:{Style.reset} ")
            if self.parent != None and self.parent.Unified(command):
                print("ran a Unified CMD")
            elif command == "??":
                for num,option in enumerate(self.options):
                    color=Fore.dark_goldenrod
                    color1=Fore.cyan
                    if (num%2)==0:
                        color=Fore.green_yellow
                        color1=Fore.magenta
                    print(f"{color}{self.options[option]['cmds']}{Style.reset} - {color1}{self.options[option]['desc']}{Style.reset}")
            else:
                for option in self.options:
                    if self.options[option]['exec'] != None and command.lower() in self.options[option]['cmds']:
                        self.options[option]['exec']()
                    elif self.options[option]['exec'] == None and command.lower() in self.options[option]['cmds']:
                        return
               



if __name__ == "__main__":
    TasksMode(parent=None,engine=ENGINE)

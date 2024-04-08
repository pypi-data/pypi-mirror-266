import os
import json
from urllib.parse import quote_plus

import requests

S_GOOGLEAPIS="translate.googleapis.com"
S_CLIENTS5="clients5.google.com"
S_GOOGLECOM="translate.google.com"
S_GOOGLECH="translate.google.ch"

def b(service,path):
    if path.startswith("/"):path=path[1:]
    if path.endswith("/"):path=path[:1]
    base=os.path.join(service,path)
    if not base.startswith("http"):
        base="https://"+base
    return base
def getitem(obj,indexs):
    for index in indexs:
        obj=obj[index]
    return obj
def setitem(obj,indexs,value):
    getitem(obj,indexs[:-1])[indexs[-1]]=value
class GoogleTrans:
    def __init__(self,service=S_GOOGLECH,client=["t","gtx","dict-chrome-ex"],path="translate_a/single",input_encoding="UTF-8",output_encoding="UTF-8"):
        self.service=service
        self.client=[client] if isinstance(client,str) else client
        self.path=path
        self.input_encoding=input_encoding
        self.output_encoding=output_encoding
    def _request(self,**params):
        base=b(self.service,self.path)
        params["ie"]=self.input_encoding
        params["oe"]=self.output_encoding
        params["dj"]="1"
        p="&".join(map(lambda i:(str(i[0])+"="+quote_plus(i[1])),params.items()))
        for c in self.client.copy():
            url=base+"?client="+c+"&"+p
            print(url)
            r=requests.get(url)
            try:
                r.raise_for_status()
            except Exception as err:
                error=err
                self.client.append(self.client.pop(0))
                continue
            j=json.loads(r.text.replace("\u200b",""))
            try:
                t=j[0]
            except:t=None
            if isinstance(t,str):return t
            return j
        raise error
    def translate(self,text,dest="en",src="auto",alternative=False):
        j=self._request(sl=src,tl=dest,dt=("at" if alternative else "t"),q=text)
        if isinstance(j,str):return j
        if alternative:
            tr=[]
            for e in j["alternative_translations"][0]["alternative"]:
                tr.append(e["word_postproc"])
            return tr
        return j["sentences"][0]["trans"]
    def transcription(self,word,src="auto"):
        j=self._request(sl=src,dt="rm",q=word)
        try:
            return j["sentences"][0]["src_translit"]
        except:return
    def dictionary(self,text,dest="en",src="auto"):
        j=self._request(sl=src,tl=dest,dt="bd",q=text)
        d={}
        for e in j["dict"][0]["entry"]:
            d[e["word"]]=e["reverse_translation"]
        return d
    def definitions(self,word,src="auto",hl="src",defs=True,syns=True,ex=True,seealso=True):
        global df,dr
        hl=src if hl=="src" else hl
        def add(id,**params):
            def rve(indexs,a,v):
                if a!=v:
                    raise ValueError("in add("+repr(id)+") indexs="+repr(indexs)+" "+repr(a)+"!="+repr(v))
            def _add(indexs=[]):
                pi=getitem(params,indexs)
                if not pi:return
                diex=True
                try:
                    di=getitem(d,indexs)
                    assert di!=None
                except:
                    di=None
                    diex=False
                if isinstance(pi,dict) and isinstance(di,dict):
                    for k in pi:
                        if k==None or k in ("gram_class","new"):continue
                        _add(indexs+[k])
                    return
                if isinstance(pi,tuple) and isinstance(di,tuple):
                    pi=di+pi
                    diex=False
                    
                if diex:
                    rve(indexs,pi,di)
                else:
                    setitem(d,indexs,pi)
            n="new" in params and params["new"]
            gc="gram_class" in params
            #print((id,params["gram_class"] if gc else "",len(dr)))
            dex=True
            try:
                d=df[id]
            except:
                d=df[id]=(len(dr)-(0 if n else 1),{})
                dex=False
                d=d[1]
                if n:
                    dd={"gram_class":None,"definitions":[d]}
                    if gc:
                        dd["gram_class"]=params["gram_class"]
                    else:
                        del dd["gram_class"]
                    dr.append(dd)
                elif dr:
                    dr[-1]["definitions"].append(d)
            else:
                #if gc:
                #    a=dr[d[0]]["gram_class"]
                #    if a!=params["gram_class"]:
                #        rve("gram_class",a,params["gram_class"])
                d=d[1]
            _add()
                

                
        def get_labels():
            
            la=[]
            ls=[]
            if "label_info" not in d:return la,ls
            l=d["label_info"]
            
            for label in l.get("register",[])+l.get("labels",[]):
                r=label=="rare"
                try:
                    i=df[id][1]
                except:
                    b=True
                    if r:print("WWW")
                else:
                    try:
                        l=i["labels"]
                    except:b=False
                    else:
                        if label in l:
                            if r:print("SSSS")
                            b=True
                        else:
                            b=False
                            if r:print("DDDDDD")
                if r:print((b,"EEEEEE"))
                if r and not b:print("TTTT")
                #print((b,id not in df))
                (la if b else ls).append(label)
            return la,ls
            #return []
        def notls():
            if ls:raise ValueError(repr(id)+" has a synonym label")
        df={}
        dr=[]
        if defs:
            j=self._request(sl=src,dt="md",q=word,hl=src)

            for e in j["definitions"]:
                g=e["pos"]
                new=1
                for d in e["entry"]:
                    id=d["definition_id"]
                    la,ls=get_labels()
                    
                    notls()
                
                    add(id,gram_class=g,labels=la,definition=d["gloss"],new=new)
                    new=0

        if syns:
            j=self._request(sl=src,dt="ss",q=word,hl=src)
            #mypkg.open_data(j)
            for e in j["synsets"] if "synsets" in j else []:
                g=e["pos"]

                new=1
                for d in e["entry"]:
                    id=d["definition_id"]
                    la,ls=get_labels()
                    a=[]
                    syns=d["synonym"]
                    

                    add(id,gram_class=g,labels=la,synonyms={",".join(ls):syns})
                            
                    new=0
                
        if ex:
            j=self._request(sl=src,dt="ex",q=word)
            #mypkg.open_data(j)
            if "examples" in j:
                for d in j["examples"]["example"]:
                    id=d["definition_id"]
                    la,ls=get_labels()
                    notls()
                    add(id,labels=la,examples=(d["text"].replace("<b>","").replace("</b>",""),),new=1)

        dr={"Word":word,"Definitions":dr}
        sa=None
        if seealso:
            j=self._request(sl=src,dt="rw",q=word)
            if "related_words" in j:
                sa=j["related_words"]["word"]

        if sa:
            dr["Seealso"]=sa
        return dr
            

t=GoogleTrans()
#df=t.definitions("salut","fr")
#mypkg.open_data(df)
#print(t.translate("Unité de mesure",alternative=True))
#print(t.translate("Bonjour"))


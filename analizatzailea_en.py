#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""

"""


import nltk,os,codecs,json,jsonrpclib,copy,sys
from nltk.tokenize.stanford import StanfordTokenizer
from pprint import pprint
#from corenlp import StanfordCoreNLP


class StanfordNLP:
    def __init__(self, port_number=9601):
        self.server = jsonrpclib.Server("http://158.227.106.115:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

   
class TermZerbitzaria:
    def __init__(self, port_number = 9602):
        self.server = jsonrpclib.Server("http://158.227.106.115:%d" % port_number)

    def deskribapenakJaso(self):
        return json.loads(self.server.deskribapenakJaso(),encoding="utf-8")

    def deskribapenArabera(self):
        return json.loads(self.server.deskribapenArabera(),encoding="utf-8")

    def sct2term(self,sctId):
        return json.loads(self.server.sct2term(sctId),encoding="utf-8")

    def sct2desc(self,sctId):
        return json.loads(self.server.sct2desc(sctId),encoding="utf-8")

    def sct2hierarkiak(self,sctId):
        return json.loads(self.server.sct2hierarkiak(sctId),encoding="utf-8")

    def desc2sct(self,desc,lemma):
        return json.loads(self.server.desc2sct(desc,lemma))

    def kontzeptuakJaso(self):
        return json.loads(self.server.kontzeptuakJaso(),encoding="utf-8")

def eponimoakIdentifikatu(tagged):
    epoFitx = '/ixadata/users/operezdevina001/Doktoretza/SintaxiMaila/Eponimoak/eponimoak.txt'
    aurrekaria = False
    lag = []
    lagForma = ''
    eponimoak = set()
    strOut = []
    parenthesis = ['-RSB-','-LSB-','-RRB-','-LRB-','AND/OR']
    with codecs.open(epoFitx,encoding='utf8') as fitx:
        for line in fitx:
            line = line.strip()
            eponimoak.add(line.lower())
    for token in tagged:
        forma,info = token
        if ',' in forma or '/' in forma or forma == "":
            strOut.append([forma,info])
            continue
        if not forma.isupper() and forma.lower() in ['van','von','de','den','der','del','la','le','di','da','du']:
            aurrekaria = True
            lag.append(token)
            lagForma += forma+'_'
            continue
        elif aurrekaria:
            fBerria = lagForma+forma
            if forma not in parenthesis and forma[0].isupper():
                forma = fBerria
                info["CharacterOffsetBegin"]=lag[0][1]["CharacterOffsetBegin"]
                info["Lemma"] = fBerria
                info["PartOfSpeech"]='NNP'
                info["NamedEntityTag"]='EPONYM'
            else:
                for el in lag:
                    strOut.append(el)
            aurrekaria = False
            lag = []
            lagForma = ''
        elif forma[0].isupper() and forma.lower() in eponimoak:
            info["NamedEntityTag"] = "EPONYM"
        elif forma.isupper() and forma not in parenthesis and len(forma) > 1:
            info["NamedEntityTag"] = "ABBRE"
        elif forma not in parenthesis and '-' in forma:
            asko = forma.split('-')
            for elem in asko: 
                if elem.lower() in eponimoak:
                    info["NamedEntityTag"] = "EPONYM"
                elif elem and elem[0].islower() or len(elem) <= 2 or elem.isdigit():
                    info["NamedEntityTag"] = "O"
                    break
        if info["NamedEntityTag"] in ["EPONYM","ABBRE"]:
            if info["NamedEntityTag"] == "EPONYM":
                lagMaius = forma.split('-')
                maius = False
                for lm in lagMaius:
                    #print(line,lm)
                    if lm[0].isupper():
                        maius = True
                if maius:
                    info["Lemma"] = forma
        if not aurrekaria:
            strOut.append([forma,info])
    if aurrekaria:
        for el in lag:
            strOut.append(el)
    return strOut

def errekOsatu(i,hInd,formak,hvalue,fAgertuak,multzoak,abstrakzioak,si):
    if i < len(formak):
        mulLagR = copy.deepcopy(multzoak[si])
        absLagR = copy.deepcopy(abstrakzioak[si])
        multzoak[si].append(formak[i])
        abstrakzioak[si].append(formak[i])
        sib = errekOsatu(i+1,hInd,formak,hvalue,fAgertuak,multzoak,abstrakzioak,si)
        #pprint(multzoak)
        # print('i',i,'sib',sib)
        for ml in hInd:
            if ml[0] == i:
                # print("BINGO",ml)
                # print(multzoak)
                mulLag = copy.deepcopy(mulLagR)
                absLag = copy.deepcopy(absLagR)
                ind = hInd.index(ml)
                # print('ind',ind)
                # print(sib)
                multzoak.append(mulLag)
                abstrakzioak.append(absLag)
                # print(multzoak)
                # print(abstrakzioak)
                multzoak[sib].append(fAgertuak[ind].replace(" ","_"))
                abstrakzioak[sib].append(hvalue[ind])
                # print(multzoak)
                # print(abstrakzioak)
                sib = errekOsatu(ml[1],hInd,formak,hvalue,fAgertuak,multzoak,abstrakzioak,sib)
        return sib
    else:
        # print(si+1)
        return si+1


def snomedIdentifikatu(tagged,des,luzeenaBool):
    formak = []
    fArray = []
    tArray = tagged[:]
    hInd = []
    hMultzokatzeko = {}
    hvalue = []
    cvalue = []
    fAgertuak = []
    eInd = []
    k = 0
    for token in tagged:
        forma,info = token
        formak.append(forma)
        llag = len(fArray)
        k += 1
        fArray.append(forma)
        for i in range(0,llag):
            if k == len(tagged) and i == 0:
                continue
            f  = fArray[i] + " " + forma
            fArray[i] = f
            kodT = des.desc2sct(f.lower(),'')

            hieT = des.sct2hierarkiak(kodT)
            # print('KodT',kodT,'hieT',hieT,'f',f)
            if hieT:
                #print(f,hieT)
                hInd.append((i,k))
                hMultzokatzeko[(i,k)] = hieT
                hvalue.append(hieT)
                cvalue.append(kodT)
                fAgertuak.append(f)
                
        kod1 = des.desc2sct(forma,info["Lemma"])
        hieT1 = des.sct2hierarkiak(kod1)
        if hieT1:
            #print(forma,hieT1)
            hvalue.append(hieT1)
            cvalue.append(kod1)
            hInd.append((k-1,k))
            hMultzokatzeko[(k-1,k)] = hieT1
            fAgertuak.append(forma)
        if info["NamedEntityTag"] in ["PERSON","EPONYM"]:
            if (k-1,k) in hMultzokatzeko:
                lagm = hMultzokatzeko[(k-1,k)]
                lagm.append("EPONYM")
                hMultzokatzeko[(k-1,k)]=lagm
            else:
                hMultzokatzeko[(k-1,k)]=["EPONYM"]
    #ZATI HAU, TERMINO LUZEENA BAKARRIK HARTZKEO ERABILTZEN DA
    if luzeenaBool:
        fOrdenatuak = fAgertuak[:]
        fOrdenatuak.sort(key=lambda x: len(x.split()))
        for i in range(0,len(fOrdenatuak)):
            unekoa = fOrdenatuak.pop(0)
            aurkitua = False 
            j = 0
            while not aurkitua and j< len(fOrdenatuak):
                if unekoa in fOrdenatuak[j]:
                    aurkitua = True
                j += 1
            if aurkitua:
                ind = fAgertuak.index(unekoa)
                hInd.pop(ind)
                fAgertuak.pop(ind)
                hvalue.pop(ind)
                cvalue.pop(ind)
    l = 0
    for inP in hInd:
        i = inP[0]
        j = inP[1]
        for k in range(i,j):
            lag = tArray[k]
            forma,info = lag
            etik = '#'.join(hvalue[l])+'-'+str(l)
            buk = ''
            if k == i and k != j-1:
                buk = '_HAS'
            elif k == j-1 and k != i:
                buk = '_BUK'
            elif i != j-1:
                buk = '_ERD'
            if "Hierarchy" in info :
                info["Hierarchy"] += '&' + etik + buk
            else:
                info["Hierarchy"] = etik + buk
            if "sctId" in info:
                info["sctId"] += '&' + '#'.join(cvalue[l]) + buk
            else:
                info["sctId"] = '#'.join(cvalue[l]) +buk
            tArray[k] = lag
        l += 1

    multzoak = [[]]
    abstrakzioak = [[]]
    sib = errekOsatu(0,hInd,formak,hvalue,fAgertuak,multzoak,abstrakzioak,0)

    return tArray,multzoak,abstrakzioak


def analizatu(term,luzeenaBool=False,multzokatu=False,abstrakzioak=False):
    """
    term: analizatzeko terminoa
    luzeenaBool: multzokatze luzeenak bakarrik hartzeko
    multzokatu: multzokatzeak jaso nahi baditugu
    abstrakzioak: abstrakzioak jaso nahi baditugu
    """
    
    nlp = StanfordNLP()
    result = nlp.parse(term)
    if type(result) != type({}):
        if multzokatu:
            if abstrakzioak:
                return None,None,None
            return None,None
        return None
    hitzak = result["sentences"][0]["words"]
    eponimoekin = eponimoakIdentifikatu(hitzak)
    des = TermZerbitzaria()
    analisia,multzoak,absak = snomedIdentifikatu(eponimoekin,des,luzeenaBool)
    if multzokatu:
        mulB = []
        for m in multzoak:
            if m not in mulB:
                mulB.append(m)
        if abstrakzioak:
            return analisia,mulB,absak
        else:
            return analisia,mulB
    elif abstrakzioak:
        return analisia,absak
    return analisia

def tokenizatu(term):
    return StanfordTokenizer().tokenize(term)

#Deskribapenena zerbitzu bezela jarri beharko litzateke
# print("Deskribapenak jasotzen...")
# deskribapenak = deskribapenakJaso()
# print("Eginda!")

if __name__ == "__main__":
    term = "methohexital sodium"
    term = "Refsum-Thiébaut disease".encode('utf-8')
    term = term.decode('utf-8')
    
    if len(sys.argv) >= 2:
        term = sys.argv[1]
    print(term)
    # analisia,multzoak = (analizatu(term,True,True,False))
    # pprint(analisia)
    # pprint(multzoak)
    #pprint(len(analisia))

    hie, mul, abst = (analizatu(term,True,True,True))
    pprint(hie)
    pprint(mul)
    pprint(abst)

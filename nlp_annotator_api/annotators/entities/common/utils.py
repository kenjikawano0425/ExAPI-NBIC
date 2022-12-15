import os
from unicodedata import unidata_version
from chemdataextractor import Document
import re
import json
from inflector import Inflector

import re
import nltk
from nltk.tokenize import WhitespaceTokenizer
from nltk import tokenize
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


resources_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../resources"
    )
)


def RegPropertiesAnnotator(paragraph):

    exlist = []
    dictionary_filename=os.path.join(resources_dir, "properties_resource.json")
    json_open = open(dictionary_filename, 'r')
    json_load = json.load(json_open)

    for jsondata in json_load:
        wordlist = []
        jsondata['_synonyms'].append(jsondata['_name'])
        words = jsondata['_synonyms']
        for word in words:
            wordlist.extend(Pattern_generation(word))
        pro_pattern = '|'.join(wordlist)
        parser = re.compile(pro_pattern)
        regex = parser.finditer(paragraph)
        for reg in regex:
            if not reg.group() == '':
                exlist.append([reg.start(), reg.end(), reg.group(), "properties", jsondata['_name']])
    exlist = sorted(exlist)
    return exlist

def RegAmineAnnotator(paragraph):

    exlist = []
    dictionary_filename=os.path.join(resources_dir, "amine_resource.json")
    json_open = open(dictionary_filename, 'r')
    json_load = json.load(json_open)
    for jsondata in json_load:
        wordlist = []
        words = jsondata['_synonyms']
        words.append(jsondata['_name'])
        for i, word in enumerate(words):
            if not matched(word):
                word = re.sub('[\(\)]', '', word)
            if len(word) >= 3:
                wordlist.extend(Pattern_generation(word))
        wordlist = list(set(wordlist))

        for word in wordlist:
            indexlist = list(find_all(paragraph, word))
            if not indexlist == []:
                for index in indexlist:
                    exlist.append([index, index+len(word), paragraph[index:index+len(word)], "amine", jsondata['_name']])
    return exlist

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)


def matched(str):
    count = 0
    for i in str:
        if i == "(":
            count += 1
        elif i == ")":
            count -= 1
        if count < 0:
            return False
    return count == 0    




def Pattern_generation(word):
    word = Inflector().singularize(word)
    wordlist = []
    wordlist.append(word.capitalize())
    wordlist.append(word.upper())
    wordlist.append(word.lower())
    wordlist.append(word.title())
    wordlist.append(Inflector().titleize(word))
    wordlist.append(Inflector().titleize(word, 'first'))

    wordlist.append(Inflector().pluralize(word.capitalize()))
    wordlist.append(Inflector().pluralize(word.upper()))
    wordlist.append(Inflector().pluralize(word.lower()))
    wordlist.append(Inflector().pluralize(word.title()))
    wordlist.append(Inflector().pluralize(Inflector().titleize(word)))
    wordlist.append(Inflector().pluralize(Inflector().titleize(word, 'first')))

    wordlist.append(Inflector().pluralize(word).capitalize())
    wordlist.append(Inflector().pluralize(word).upper())
    wordlist.append(Inflector().pluralize(word).lower())
    wordlist.append(Inflector().pluralize(word).title())
    wordlist.append(Inflector().titleize(Inflector().pluralize(word)))
    wordlist.append(Inflector().titleize(Inflector().pluralize(word), 'first'))

    wordlist = list(set(wordlist))
    return wordlist

def RegValueAnnotator(paragraph):
    value_pattern = '(([+\-]?)\s*(((10)\-?(\s+|(\$?\^))\s*(\$\^)?\{?\s*([+\-])?\s*(\$\^)?\{?\s*(\d+)\}?\$?)|(((\d+\.?\d*)|(\.\d+)|(?<![a-zA-Z])(e|E)\-?\^?(?![a-zA-Z]))(\s*(E|e|((\s|\*|X|x|×|((\$_{)?(GLYPH<[A-Z]+\d+>(}\$)?)))\s*10))\s*\-?\^?\s*(\$\^)?\{?\s*([+\-]?)\s*(\$\^)?\{?\s*(\d+)\}?\$?)?)))((( |to|and|\/|-|,)+(?=\d)))*'
    exlist = []
    pattern_re = re.compile(value_pattern)
    parser = pattern_re
    regex = parser.finditer(paragraph)
    for reg in regex:
        if not reg.group() == '':
            exlist.append([reg.start(), reg.end(), reg.group(), "value"])
    exlist = list(map(list, set(map(tuple, exlist))))
    exlist = sorted(exlist)
    connectlisttmp = connectlist(exlist)
    valuelist = revaluelist(connectlisttmp)
    return valuelist

def RegChemAnnotator(paragraph):
    exlist = []

    if len(paragraph) <= 10000:
        doc = Document(paragraph)
        for text in doc.cems:
            exlist.append([text.start, text.end, text.text, 1])
    else:
        texts = tokenize.sent_tokenize(paragraph)
        tmplist = []
        offsetlength = 0
        for text in texts:
            tmplist.append(text)
            tmptext = ".".join(tmplist)
            if len(tmptext) > 3000:
                doc = Document(tmptext)
                for resulttext in doc.cems:
                    exlist.append([offsetlength + resulttext.start, offsetlength + resulttext.end, resulttext.text, 1])
                tmplist = []
                offsetlength = offsetlength + len(tmptext)

        tmptext = ".".join(tmplist)
        doc = Document(tmptext)
        for resulttext in doc.cems:
            exlist.append([offsetlength + resulttext.start, offsetlength + resulttext.end, resulttext.text, 1])
            
    pattern = '((\$[_^]{[\d+-]{0,}}\$|[\[\]\=()\/\-\+])*((YSZ|NWs|@|He|Li|Be|Ne|Na|Mg|Al|Si|Cl|Ar|Ca|Sc|Ti|Cr|Mn|Fe|Co|Ni|Cu|Zn|Ga|Ge|As|Se|Br|Kr|Rb|Sr|Zr|Nb|Mo|Tc|Ru|Rh|Pd|Ag|Cd|In|Sn|Sb|Te|Xe|Cs|Ba|La|Ce|Pr|Nd|Pm|Sm|Eu|Gd|Tb|Dy|Ho|Er|Tm|Yb|Lu|Hf|Ta|Re|Os|Ir|Pt|Au|Hg|Tl|Pb|Bi|Po|At|Rn|Fr|Ra|Ac|Th|Pa|Np|Pu|Am|Cm|Bk|Cf|Es|Fm|Md|No|Lr|Rf|Db|Sg|Bh|Hs|Mt|Ds|Rg|Cn|Nh|Fl|Mc|Lv|Ts|Og|Hb|M|H|B|C|N|O|F|P|S|K|V|I|W|U|Y|X|x|λ)(\$[_^]\{([+-]|[a-z]|(\d\.*\d*))*\}\$|[\–\[\]()\/\-\+\.\d\: ])*)+)(?![a-z])'
    pattern_re = re.compile(pattern)
    regex = pattern_re.finditer(paragraph)
    for reg in regex:
        if not len(paragraph) == reg.end():
            if paragraph[reg.end()-2:reg.end()] == '/ ':
                exlist.append([reg.start(), reg.end()-2, reg.group()[0:-2], 1])
            elif paragraph[reg.end()-1] == ' ' or paragraph[reg.end()-1] == '/':
                exlist.append([reg.start(), reg.end()-1, reg.group()[0:-1], 1])
            elif re.search("(?<=[\(\/\$])[a-zø]", paragraph[reg.end()-1:reg.end()+1]):
                exlist.append([reg.start(), reg.end(), reg.group(), 1])
            elif not re.search("[a-zø]", paragraph[reg.end()]):
                exlist.append([reg.start(), reg.end(), reg.group(), 1])
        else:
            exlist.append([reg.start(), reg.end(), reg.group(), 1])


    pattern = '(Li|He),\s*[A-Z]\.|(([\d\.]{1,}(K|MPa|kPa)|([\d\.]{1,} (K|MPa|kPa))))|Re V\.*|J\.\s*(Mol|Am|Phys)\.|(\d{3,}C)|GC|As |In |At |TOF|SATP|STP|NTP|SMF|O\'Neill|CrossRef|PubMed|DI|II|XPS|ICP\-OES|QP\-5000|GC\-MS|F\-T|JEOL|DOI|S\/N|A\/F|(JP|US)\d{2,}[A-Z]|\d+\s*((k|M|m|n)*eV|C|° C|\$\^\{◦\}\$\s*C)|(B|C),*\s*[12][09]\d{2}|((F|f)igure(s)*|(F|f)ig|(T|t)able(s)*)[\,\.\s\dA-Z\-]*(and)*[\,\.\s\d\-]*[A-Z\d]*'
    pattern_re = re.compile(pattern)
    regex = pattern_re.finditer(paragraph)

    for reg in regex:
        exlist.append([reg.start(), reg.end(), reg.group(), 0])

    exlist = list(map(list, set(map(tuple, exlist))))
    exlist = sorted(exlist)

        
    def is_overlap(start1, end1, start2, end2):
        return start1 <= end2 and end1 >= start2
    

    tmplist = []
    newlist = []
    for i in range(0, len(exlist)):
        if not i == len(exlist)-1:
            if tmplist == []:
                lista = exlist[i]
                listb = exlist[i+1]
                if is_overlap(lista[0],lista[1], listb[0], listb[1]):
                    if lista[1]-lista[0] > listb[1]-listb[0]:
                        max = lista
                        min = listb
                    else:
                        max = listb
                        min = lista
                    
                    if max[3] == 0 or min[3] == 0:
                        max[3] = 0

                    if min[0] < max[0]:
                        gap = max[0] - min[0]
                        newword = min[2][0:gap] + max[2]
                        tmplist = [min[0], max[1], newword, max[3]]
                    elif min[0] >= max[0] and min[1] <= max[1]:
                            tmplist = [max[0], max[1], max[2], max[3]]
                    elif min[1] > max[1]:
                        gap = min[1] - max[1]
                        newword = max[2] + min[2][len(min[2])-gap:len(min[2])]
                        tmplist = [max[0], min[1], newword, max[3]]
                else:
                    if exlist[i][3] == 1:
                        newlist.append(exlist[i])
            else:
                lista = tmplist
                listb = exlist[i+1]
                if is_overlap(lista[0],lista[1], listb[0], listb[1]):
                    if lista[1]-lista[0] > listb[1]-listb[0]:
                        max = lista
                        min = listb
                    else:
                        max = listb
                        min = lista

                    if max[3] == 0 or min[3] == 0:
                        max[3] = 0


                    if min[0] < max[0]:
                        gap = max[0] - min[0]
                        newword = min[2][0:gap] + max[2]
                        tmplist = [min[0], max[1], newword, max[3]]
                    elif min[0] >= max[0] and min[1] <= max[1]:
                            tmplist = [max[0], max[1], max[2], max[3]]
                    elif min[1] > max[1]:
                        gap = min[1] - max[1]
                        newword = max[2] + min[2][len(min[2])-gap:len(min[2])]
                        tmplist = [max[0], min[1], newword, max[3]]
                else:
                    if tmplist[3] == 1:
                        newlist.append(tmplist)
                    tmplist = []
        else:
            if tmplist == [] and exlist[i][3] == 1:
                newlist.append(exlist[i])
            elif tmplist == [] and exlist[i][3] == 0:
                break
            elif tmplist[3] == 1:
                newlist.append(tmplist)
    

    for i, check in enumerate(newlist):
        if not bool(re.search('\(\)', check[2])):
            if check[2][-1] == ')' and not bool(re.search('\(',check[2])):
                newlist[i][1] = check[1]-1
                newlist[i][2] = check[2][0:len(check[2])-1]
            elif not check[2][-1] == ')' and check[2][0] == '(':
                newlist[i][0] = check[0]+1
                newlist[i][2] = check[2][1:len(check[2])]
            elif check[2][-1] == ')' and check[2][0] == '(':
                newlist[i][0] = check[0]+1
                newlist[i][1] = check[1]-1
                newlist[i][2] = check[2][1:len(check[2])-1]
            
            if check[2][-1] in ['(','/', '-', '.']:
                newlist[i][1] = check[1]-1
                newlist[i][2] = check[2][0:len(check[2])-1]
            if check[2][0] in ['/', '-', '.']:
                newlist[i][0] = check[0]+1
                newlist[i][2] = check[2][1:len(check[2])]
        else:
            print("this is not material {}".format(check[2]))

         
    return newlist

def RegValueUnitAnnotator(paragraph):
    value_pattern = '(([+\-]?)\s*(((10)\-?(\s+|(\$?\^))\s*(\$\^)?\{?\s*([+\-])?\s*(\$\^)?\{?\s*(\d+)\}?\$?)|(((\d+\.?\d*)|(\.\d+)|(?<![a-zA-Z])(e|E)\-?\^?(?![a-zA-Z]))(\s*(E|e|((\s|\*|X|x|×|((\$_{)?(GLYPH<[A-Z]+\d+>(}\$)?)))\s*10))\s*\-?\^?\s*(\$\^)?\{?\s*([+\-]?)\s*(\$\^)?\{?\s*(\d+)\}?\$?)?)))((( |to|and|\/|-|,)+(?=\d)))*'
    unit_pattern = '((?<=[\d\$])\s?((f|p|n|(u|μ)|m|c|d|k|M|G|P)?(mol\s*CO2|mol\s*N|t\s*i\s*m\s*e\s*s|p\s*e\s*r\s*c\s*e\s*n\s*t\s*a\s*g\s*e|w\s*e\s*i\s*g\s*h\s*t|v\s*o\s*l\s*u\s*m\s*e|a\s*t\s*o\s*m|h\s*o\s*u\s*r|m\s*i\s*n|s\s*e\s*c|v\s*o\s*l|p\s*p\s*m|m\s*o\s*l|c\s*p\s*s|c\s*a\s*t|(o\s*h\s*m|Ω)|w\s*t|P\s*a|e\s*V|h|H|s|d|C|K|cP|W|m|l|L|J|g|Å|θ|%|°|℃|V|A|S)+([\^\/\_\-\+\d\s\$\{\}\·\(\)])*)+((?=to)|(?![a-z])))|((pH\s*\=\s*)|(pH))(?=[\s\d])'
    pattern_re = re.compile(unit_pattern)
    parser = pattern_re
    regex = parser.finditer(paragraph)
    exlist = []
    for reg in regex:
        if not reg.group() == '':
            if "pH" in reg.group():
                exlist.append([reg.start(), reg.end(), reg.group(), 'forwardunit', reg.group(), False, None])
            else:
                exlist.append([reg.start(), reg.end(), reg.group(), 'unit', reg.group(), False, None])

    exlist = list(map(list, set(map(tuple, exlist))))
    unitlist = sorted(exlist)


    exlist = []
    pattern_re = re.compile(value_pattern)
    parser = pattern_re
    regex = parser.finditer(paragraph)
    for reg in regex:
        if not reg.group() == '':
            exlist.append([reg.start(), reg.end(), reg.group(), "value"])
    exlist = list(map(list, set(map(tuple, exlist))))
    exlist = sorted(exlist)
    valuelist = revaluelist(connectlist(exlist))

    exlist = []
    exlist.extend(valuelist)
    exlist.extend(unitlist)
    valueunitlist = valueunit(exlist)
    return valueunitlist


def is_overlap(start1, end1, start2, end2):
    return start1 <= end2 and end1 >= start2

def connectlist(exlist):
    exlist = list(map(list, set(map(tuple, exlist))))
    exlist = sorted(exlist)
        
    tmplist = []
    newlist = []
    for i in range(0, len(exlist)):
        if not i == len(exlist)-1:
            if tmplist == []:
                lista = exlist[i]
                listb = exlist[i+1]
                if is_overlap(lista[0],lista[1], listb[0], listb[1]):
                    if lista[1]-lista[0] > listb[1]-listb[0]:
                        max = lista
                        min = listb
                    else:
                        max = listb
                        min = lista
                    
                    unit = max[3]


                    if min[0] < max[0]:
                        gap = max[0] - min[0]
                        newword = min[2][0:gap] + max[2]
                        tmplist = [min[0], max[1], newword, unit]
                    elif min[0] >= max[0] and min[1] <= max[1]:
                            tmplist = [max[0], max[1], max[2], unit]
                    elif min[1] > max[1]:
                        gap = min[1] - max[1]
                        newword = max[2] + min[2][len(min[2])-gap:len(min[2])]
                        tmplist = [max[0], min[1], newword, unit]
                else:
                    newlist.append(exlist[i])
            else:
                lista = tmplist
                listb = exlist[i+1]
                if is_overlap(lista[0],lista[1], listb[0], listb[1]):
                    if lista[1]-lista[0] > listb[1]-listb[0]:
                        max = lista
                        min = listb
                    else:
                        max = listb
                        min = lista

                    unit = max[3]

                    if min[0] < max[0]:
                        gap = max[0] - min[0]
                        newword = min[2][0:gap] + max[2]
                        tmplist = [min[0], max[1], newword, unit]
                    elif min[0] >= max[0] and min[1] <= max[1]:
                        tmplist = [max[0], max[1], max[2], unit]
                    elif min[1] > max[1]:
                        gap = min[1] - max[1]
                        newword = max[2] + min[2][len(min[2])-gap:len(min[2])]
                        tmplist = [max[0], min[1], newword, unit]
                else:
                    newlist.append(tmplist)
                    tmplist = []
        else:
            if tmplist == []:
                newlist.append(exlist[i])
            else:
                newlist.append(tmplist)
    return newlist


def valueunit(exlist):
    
    print("process valueunit : ", exlist)
    exlist = list(map(list, set(map(tuple, exlist))))
    exlist = sorted(exlist)

    newlist = []
    for i in range(0, len(exlist)):
        if not i == len(exlist)-1:
            lista = exlist[i]
            listb = exlist[i+1]
            if lista[3]=="value" and listb[3]=="unit":
                if lista[1]+1 == listb[0]:
                    newword = lista[2] + ' ' + listb[2]
                    valueunit = [lista[0], listb[1], newword, "value + unit", re.sub(' ', '', listb[4]), lista[5], lista[6]]
                    newlist.append(valueunit)
                elif lista[1] == listb[0]:
                    newword = lista[2] + listb[2]
                    valueunit = [lista[0], listb[1], newword, "value + unit", re.sub(' ', '', listb[4]), lista[5], lista[6]]
                    newlist.append(valueunit)
                
                if exlist[i][5] == True:
                    for num in range(i-1,-1,-1):
                        if exlist[num][3] == "value":
                            if exlist[num][5] == True:
                                lista = exlist[num]
                                if lista[1]+1 == listb[0]:
                                    newword = lista[2] + ' ' + listb[2]
                                    valueunit = [lista[0], listb[1], newword, "value + unit", re.sub(' ', '', listb[4]), lista[5], lista[6]]
                                    newlist.append(valueunit)
                                elif lista[1] == listb[0]:
                                    newword = lista[2] + listb[2]
                                    valueunit = [lista[0], listb[1], newword, "value + unit", re.sub(' ', '', listb[4]), lista[5], lista[6]]
                                    newlist.append(valueunit)
                            elif exlist[num][5] == False:
                                break
                        else:
                            continue


            elif lista[3] == "forwardunit" and listb[3] == "value":
                if lista[1]+1 == listb[0]:
                    newword = lista[2] + ' ' + listb[2]
                    valueunit = [lista[0], listb[1], newword, "value + unit", re.sub('[\s=]', '', lista[4]), listb[5], listb[6]]
                    newlist.append(valueunit)
                elif lista[1] == listb[0]:
                    newword = lista[2] + listb[2]
                    valueunit = [lista[0], listb[1], newword, "value + unit", re.sub('[\s=]', '', lista[4]), listb[5], listb[6]]
                    newlist.append(valueunit)

                if listb[5] == True:
                    for num in range(i+2,len(exlist)):
                        if exlist[num][3] == "value":
                            if exlist[num][5] == True:
                                listb = exlist[num]
                                if lista[1]+1 == listb[0]:
                                    newword = lista[2] + ' ' + listb[2]
                                    valueunit = [lista[0], listb[1], newword, "value + unit", re.sub('[\s=]', '', lista[4]), listb[5], listb[6]]
                                    newlist.append(valueunit)
                                elif lista[1] == listb[0]:
                                    newword = lista[2] + listb[2]
                                    valueunit = [lista[0], listb[1], newword, "value + unit", re.sub('[\s=]', '', lista[4]), listb[5], listb[6]]
                                    newlist.append(valueunit)
                            elif exlist[num][5] == False:
                                break
                        else:
                            continue


            elif lista[3] == "value" and not listb[3] == "unit":
                pass
        else:
            pass

    print("process valueunit done : ", newlist)
    return newlist

def uniformvalue(value):
    print("start process uniformvalue : ", value)
    if bool(re.search('(\*|X|x|×|GLYPH<[A-Z]+\d+>)', value)):
        print("process uniformvalue 1 : ", value)
        if bool(re.search('(E|e|10)\s*((?=\-)|(?=\^)|(?=\+)|(?=\$))', value)):
            print("process uniformvalue 1-1 : ", value)
            tmplist = re.split('(\*|X|x|×|GLYPH<[A-Z]+\d+>)', value)
            tmpvalue = int(re.sub('[\s\$\_\^\{\}]', '', re.split('E|E|e|10',tmplist[-1])[-1]))
            if tmpvalue > 300:
                tmpvalue = 300
            revalue = float(re.sub('[\s\$\_\^\{\}]', '', tmplist[0])) * 10 ** tmpvalue
            print("process uniformvalue 1-1 done : ", revalue)
        else:
            print("process uniformvalue 1-2 : ", value)
            tmplist = re.split('(\*|X|x|×|GLYPH<[A-Z]+\d+>)', value)
            revalue = float(re.sub('[\s\$\_\^\{\}]', '', tmplist[0])) * float(re.sub('[\s\$\_\^\{\}]', '', tmplist[-1]))
            print("process uniformvalue 1-2 done : ", revalue)
    else:
        print("process uniformvalue 2 : ", value)
        if bool(re.search('((E|E|e|10)\s*)((?=\-)|(?=\+)|(?=\$)|(?=\^))', value)):
            print("process uniformvalue 2-1 : ", value)
            tmplist = re.split('E|E|e|10', value, 1)
            if not bool(re.search('\d', tmplist[0])):
                print("process uniformvalue 2-1-1 : ", value)
                tmpvalue = int(re.sub('[\s\$\^\{\}\_]', '', tmplist[-1]))
                if tmpvalue > 300:
                    tmpvalue = 300
                revalue = 10 ** tmpvalue
                print("process uniformvalue 2-1-1 done : ", revalue)
            else:
                print("process uniformvalue 2-1-2 : ", value)
                tmpvalue = float(re.sub('[\s\$\^\{\}\_]', '', tmplist[-1]))
                if tmpvalue > 300:
                    tmpvalue = 300
                revalue = float(tmplist[0]) * 10 ** tmpvalue
                print("process uniformvalue 2-1-2 done : ", revalue)
        else:
            print("process uniformvalue 2-2 : ", value)
            if bool(re.search('E|E|e', value)):
                tmplist = re.split('E|E|e', value)
                if not tmplist[0] == '':
                    print("process uniformvalue 2-2-1 : ", value)
                    revalue = float(re.sub(' ', '', tmplist[0])) * 10
                    print("process uniformvalue 2-2-1 done : ", revalue)
                elif not tmplist[1] == '':
                    print("process uniformvalue 2-2-2 : ", value)
                    tmpvalue = float(re.sub(' ', '', tmplist[1]))
                    if tmpvalue > 300:
                        tmpvalue = 300
                    revalue = 10 ** tmpvalue
                    print("process uniformvalue 2-2-2 done : ", revalue)
                else:
                    print("process uniformvalue 2-2-3 : ", value)
                    tmpvalue = float(re.sub(' ', '', tmplist[1]))
                    if tmpvalue > 300:
                        tmpvalue = 300
                    revalue = float(re.sub(' ', '', tmplist[0])) * 10 ** tmpvalue
                    print("process uniformvalue 2-2-3 done : ", revalue)
            else:
                print("process uniformvalue 2-2-4 : ", value)
                revalue = float(re.sub(' ', '', value))
                print("process uniformvalue 2-2-4 done : ", revalue)
    
    #solve MongoDB can only handle up to 8-byte ints
    if revalue >= 2 ** 63 - 1 :
        revalue = 2 ** 62
    elif revalue <=-(2 ** 63 - 1):
        revalue = -(2 ** 62)

    print("process uniformvalue done : value ", value, " to revalue ", revalue)
    return revalue


def revaluelist(valuelist):
    print("start process revaluelist : ", valuelist)
    exlist = []
    for value in valuelist:
        if value[2][0] == ' ':
            value[0] = value[0]+1
            value[2] = value[2][1:len(value[2])]
        if len(re.findall('\-', value[2])) >= 2:
            continue
        if len(value[2]) == 1:
            if bool(re.search('[eE]', value[2])):
                continue
            
        try:
            if bool(re.search('(?<=\d)\s6\s(?=\d)', value[2])):
                revalue = value[2].split(" 6 ")[0]
                tmplist = [value[0], value[1], value[2], 'value', 'no unit', True, revalue]
                exlist.append(tmplist)
            elif bool(re.search('and|to|&|,|\/', value[2])):
                splitvalue = value[2]
                regex = re.finditer(',', splitvalue)
                offset = 0
                for reg in regex:
                    if not splitvalue[reg.start()-offset+1]==' ':
                        if bool(re.search('(?<=\,)\d{3}', splitvalue[reg.start()-offset:reg.start()-offset+4])):
                            replace_tmp = list(splitvalue)
                            replace_tmp[reg.start()-offset] = ''
                            splitvalue = ''.join(replace_tmp)
                            offset = offset + 1
                tmpvalues = re.split('and|to|&|,|\/', splitvalue)
                for i, tmpvalue in enumerate(tmpvalues):
                    tmpvalue = re.sub(' ', '', tmpvalue)
                    if bool(re.search('\d', tmpvalue)):
                        if bool(re.search('((?<![Ee])(?<!10)(?<!\^)(?<!\{)(?<![Ee]\s)(?<!10\s)(?<!\^\s)(?<!\{\s))[\-\+]\s*(?=\d)', tmpvalue)):
                            if bool(re.search('[\-\+]', tmpvalue[0])):
                                revalue = uniformvalue(tmpvalue)
                            else:
                                revalue1 = uniformvalue(re.sub(' ', '', re.split('[\-\+]', tmpvalue)[0]))
                                tmplist = [value[0], value[1], value[2], 'value', 'no unit', True, revalue1]
                                exlist.append(tmplist)
                                revalue2 = uniformvalue(re.sub(' ', '', re.split('[\-\+]', tmpvalue)[1]))
                                tmplist = [value[0], value[1], value[2], 'value', 'no unit', True, revalue2]
                                exlist.append(tmplist)
                                continue
                        else:
                            revalue = uniformvalue(tmpvalue)
                        tmplist = [value[0], value[1], value[2], 'value', 'no unit', True, revalue]
                        exlist.append(tmplist)
                        continue

            elif bool(re.search('((?<![Ee])(?<!10)(?<!\^)(?<!\{)(?<![Ee]\s)(?<!10\s)(?<!\^\s)(?<!\{\s))[\-\+]\s*(?=\d)', value[2])):
                if bool(re.search('[\-\+]', re.sub(' ', '', value[2][0]))):
                    revalue = uniformvalue(value[2])
                    tmplist = [value[0], value[1], value[2], 'value', 'no unit', False, revalue]
                else:
                    revalue1 = uniformvalue(re.sub(' ', '', re.split('[\-\+]', value[2])[0]))
                    tmplist = [value[0], value[1], value[2], 'value', 'no unit', True, revalue1]
                    exlist.append(tmplist)
                    revalue2 = uniformvalue(re.sub(' ', '', re.split('[\-\+]', value[2])[1]))
                    tmplist = [value[0], value[1], value[2], 'value', 'no unit', True, revalue2]
                    exlist.append(tmplist)
                    continue
            else:
                revalue = uniformvalue(value[2])
                tmplist = [value[0], value[1], value[2], 'value', 'no unit', False, revalue]
                exlist.append(tmplist)
        
        except Exception as e:
            print("warning:{0}\nthis is not value:{1}".format(e, value[2]))
            continue

    print("done process revaluelist : ", exlist)

    return exlist


def ChemDataAnnotator(paragraph):
    exlist = []

    if len(paragraph) <= 10000:
        doc = Document(paragraph)
        for text in doc.cems:
            exlist.append([text.start, text.end, text.text])
    else:
        texts = tokenize.sent_tokenize(paragraph)
        tmplist = []
        offsetlength = 0
        for text in texts:
            tmplist.append(text)
            tmptext = ".".join(tmplist)
            if len(tmptext) > 3000:
                doc = Document(tmptext)
                for resulttext in doc.cems:
                    exlist.append([offsetlength + resulttext.start, offsetlength + resulttext.end, resulttext.text])
                tmplist = []
                offsetlength = offsetlength + len(tmptext)

        tmptext = ".".join(tmplist)
        doc = Document(tmptext)
        for resulttext in doc.cems:
            exlist.append([offsetlength + resulttext.start, offsetlength + resulttext.end, resulttext.text])

    exlist = sorted(exlist)

    return exlist

def RegUnitAnnotator(paragraph):
    unit_pattern = '(?<=[\d\$])\s?((f|p|n|(u|μ)|m|c|d|k|M|G|P)?(mol\s*CO2|mol\s*N|t\s*i\s*m\s*e\s*s|p\s*e\s*r\s*c\s*e\s*n\s*t\s*a\s*g\s*e|w\s*e\s*i\s*g\s*h\s*t|v\s*o\s*l\s*u\s*m\s*e|a\s*t\s*o\s*m|h\s*o\s*u\s*r|m\s*i\s*n|s\s*e\s*c|v\s*o\s*l|p\s*p\s*m|m\s*o\s*l|c\s*p\s*s|c\s*a\s*t|(o\s*h\s*m|Ω)|w\s*t|P\s*a|e\s*V|h|H|s|d|C|K|cP|W|m|l|L|J|g|Å|θ|%|°|℃|V|A|S)+([\^\/\_\-\+\d\s\$\{\}\·\(\)])*)+((?=to)|(?![a-z]))'
    pattern_re = re.compile(unit_pattern)
    parser = pattern_re
    regex = parser.finditer(paragraph)
    exlist = []
    for reg in regex:
        if not reg.group() == '':
            exlist.append([reg.start(), reg.end(), reg.group(), 'unit'])

    exlist = list(map(list, set(map(tuple, exlist))))
    return sorted(exlist)


def RegInhibitorAnnotator(paragraph):
    startnum = 0
    exlist = []
    for sent in tokenize.sent_tokenize(paragraph):
        if "inhibitor" in sent:
            try:
                words = sent.split(" ")
                spans = list(WhitespaceTokenizer().span_tokenize(sent))
                for i, span in enumerate(spans):
                    if span[0] == sent.find("inhibitor"):
                        inhibitor_index = i
                        word_index = -inhibitor_index
                        break
                if len(nltk.pos_tag(words)) == len(spans):
                    for t in zip(nltk.pos_tag(words), spans):
                        tag, span = t
                        if "NN" in tag[1]:
                            if not "inhibitor" in tag[0]:
                                exlist.append([span[0]+startnum, span[1]+startnum, tag[0], word_index, "inhibitor"])
                        word_index = word_index + 1
                else:
                    print(f"warning:len(tokenize) not equal len(span)")
            except Exception as e:
                print(f"warning:{e}")

        startnum = startnum + len(sent) + 1


    return exlist
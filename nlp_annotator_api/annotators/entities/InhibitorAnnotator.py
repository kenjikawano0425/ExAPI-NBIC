from .common.utils import RegInhibitorAnnotator

class InhibitorAnnotator:
    
    def key(self) -> str:
        return "inhibitor"

    def description(self) -> str:
        return "finding pre-suf words of inhibitor, word_index -(prefix), +(suffix)"

    def __init__(self):

        # init CDE
        self.parser = RegInhibitorAnnotator

    def annotate_entities_text(self, text:str):


        ents=[]

        #implement CDE
        doc = self.parser(text)

        for cem in doc:

            t0 = cem[0]
            t1 = cem[1]
            name = cem[2]

            ent = {
                "match": name,
                "range": [t0,t1],
                "original": text[t0:t1],
                "type":"inhibitor",
                "word_index":cem[3]
            }
            ents.append(ent)

        return ents
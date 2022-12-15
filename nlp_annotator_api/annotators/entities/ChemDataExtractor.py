from .common.utils import ChemDataAnnotator

class ChemDataExtractor:
    
    def key(self) -> str:
        return "chemdataextractor"

    def description(self) -> str:
        return "finding materials with only ChemDataExtractor"

    def __init__(self):

        # init CDE
        self.parser = ChemDataAnnotator

    def annotate_entities_text(self, text:str):

        ents=[]

        #implement CDE
        doc = self.parser(text)

        for cem in doc:

            name = cem[2]

            t0 = cem[0]
            t1 = cem[1]

            ent = {
                "match": name,
                "range": [t0,t1],
                "original": text[t0:t1],
                "type":"chemdataextractor",
            }
            ents.append(ent)


        return ents
    
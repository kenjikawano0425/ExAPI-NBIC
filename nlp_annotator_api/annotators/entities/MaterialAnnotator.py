from .common.utils import RegChemAnnotator

class MaterialAnnotator:
    
    def key(self) -> str:
        return "materials"

    def description(self) -> str:
        return "finding materials with ChemDataExtractor+Regex"

    def __init__(self):

        # init CDE
        self.parser = RegChemAnnotator

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
                "type":"materials",
            }
            ents.append(ent)

        return ents
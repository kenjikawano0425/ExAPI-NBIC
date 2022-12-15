from .common.utils import RegUnitAnnotator

class UnitAnnotator:
    
    def key(self) -> str:
        return "units"

    def description(self) -> str:
        return "finding unit."

    def __init__(self):

        # init CDE
        self.parser = RegUnitAnnotator

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
                "type":"units",
            }
            ents.append(ent)

        return ents
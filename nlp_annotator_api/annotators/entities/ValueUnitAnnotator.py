from .common.utils import RegValueUnitAnnotator

class ValueUnitAnnotator:
    
    def key(self) -> str:
        return "value+units"

    def description(self) -> str:
        return "finding value+units, which can search float_value(500, 0.05) by filter node in query."

    def __init__(self):

        # init CDE
        self.parser = RegValueUnitAnnotator

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
                "type":"value+units",
                "unit":cem[4],
                "range_bool":cem[5],
                "float_value":cem[6]
            }
            ents.append(ent)

        return ents
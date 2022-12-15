from .common.utils import RegPropertiesAnnotator

class PropertiesAnnotator:
    
    def key(self) -> str:
        return "properties"

    def description(self) -> str:
        return "Names of properties"

    def __init__(self):

        # init CDE
        self.parser = RegPropertiesAnnotator

    def annotate_entities_text(self, text:str):

        ents=[]

        #implement CDE
        doc = self.parser(text)

        for cem in doc:

            name = cem[4]

            t0 = cem[0]
            t1 = cem[1]

            typename = cem[3]


            ent = {
                "match": name,
                "range": [t0,t1],
                "original": text[t0:t1],
                "type": typename
            }
            ents.append(ent)

        return ents

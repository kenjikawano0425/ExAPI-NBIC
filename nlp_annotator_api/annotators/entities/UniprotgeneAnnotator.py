from .common.DictionaryAnnotator import DawgMatchingAnnotator


class UniprotgeneAnnotator:
    
    def key(self) -> str:
        return "uniprot_genes"

    def description(self) -> str:
        return "Names of genes name from uniprot about 20,000 names."

    def __init__(self):

        # init CDE
        self.parser = DawgMatchingAnnotator
        self.name = "uniprot_gene"

    def annotate_entities_text(self, text:str):

        ents=[]

        #implement CDE
        doc = self.parser(text, self.name)

        for cem in doc:


            t0 = cem[0]
            t1 = cem[1]

            entityname = self.name
            originalname = cem[3]


            ent = {
                "match": originalname,
                "range": [t0,t1],
                "original": text[t0:t1],
                "type": entityname
            }
            ents.append(ent)

        return ents

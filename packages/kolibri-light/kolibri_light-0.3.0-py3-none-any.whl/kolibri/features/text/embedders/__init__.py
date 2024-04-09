from kolibri.features.text.embedders.glove_embedder import GloVeEmbedding
from kolibri.features.text.embedders.fasttext_embedder import FasttextEmbedding

def get_embedder(embedder, configs):
    if embedder=="glove":
        return GloVeEmbedding(configs)
    elif embedder=="fasttext":
        return FasttextEmbedding(configs)

    return None
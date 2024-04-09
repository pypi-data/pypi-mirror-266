from kolibri.backend.bn.inference import inference


def predict(model, variables, evidence, verbose=3):

    return inference.fit(model, variables=variables, evidence=evidence, verbose=verbose)
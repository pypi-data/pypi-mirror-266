from kolibri.core.component import Component
from kolibri.registry import register


@register("PandasColumnRemover")
class PandasColumnRemover(Component):

    defaults = {
        "fixed":{
            "columns-to-remove":[]
        },

    }

    component_type = "transformer"
    def __init__(self, params={}):
        super().__init__(params)

        self.columns_to_remove = self.get_parameter("columns-to-remove")
    def fit(self, dataset, y=None):  #
        return self


    def transform(self, dataset, y=None):
        data=dataset
        # actual computation:

        return data.drop(columns=self.columns_to_remove, errors="ignore")

    def fit_transform(self, dataset, y=None):

        data = dataset
        self.fit(data)
        return self.transform(data)


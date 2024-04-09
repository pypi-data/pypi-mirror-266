from kolibri.core.component import Component
from kolibri.registry import register

@register('PandasColumnTransformer')
class PandasColumnTransformer(Component):

    defaults = {
        "fixed":{
            "formulas": None,
            "new-column-names": None
        },
        "tuneable":{
            "drop-source-columns":{
                "value": False,
                "type": "boolean",
                "values": [
                    True,
                    False
                ]
            }
        }

    }

    component_type = "transformer"

    def __init__(self, params={}):
        super().__init__(params)

        self.fromulas = self.get_parameter("formulas")
        self.new_col_names = self.get_parameter("new-column-names")

        if self.fromulas is None or self.new_col_names is None:
            raise Exception('Column Names or Formulas cannot be None')
        elif len(self.fromulas) != len(self.new_col_names):
            raise Exception('The number of names shoould be equal to the number of formulas')

    def fit(self, dataset, y=None):  #
        return self


    def transform(self, dataset, y=None):
        data=dataset
        # actual computation

        for formula, col_name  in zip(self.fromulas, self.new_col_names):
            try:
                data[col_name]=data.eval(formula)
            except Exception as e:
                raise e

        return data

    def fit_transform(self, dataset, y=None):

        data = dataset
        self.fit(data)
        return self.transform(data)


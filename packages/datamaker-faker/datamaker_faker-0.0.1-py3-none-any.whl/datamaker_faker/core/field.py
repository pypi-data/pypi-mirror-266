from ..utils.data_folder import data_folder
import numpy as np
import pandas as pd


class Field:
    def __init__(
        self,
        name: str,
        seed: int | None = None,
        mapper: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize a Field object to be used for data generation.

        ## Args

        name (str): The name of the field.
        seed (int | None, optional): The seed value for random number generation. Defaults to None.
        mapper (dict[str, str] | None, optional): A dictionary to map the values of the field. Defaults to None.


        ## Example

        You can generate a single value from the field by calling the `generate` method.

        ```python
        sex = Field("sex", seed=42)
        sex.generate()
        ```

        Optionally, you can generate multiple values by passing the number of values you want to generate.

        ```python
        sex.generate(10)
        ```
        """
        self.name = name
        self.path = data_folder / name
        self.seed = seed
        self.random_state = np.random.RandomState(seed)
        self.mapper = mapper

    def __sample(self, arr: np.array, n: int = 1):
        return self.random_state.choice(arr, n, replace=True)

    def generate(self, n=1):
        """
        Generates n random data values.
        """
        data = pd.read_csv(f"{self.path}.csv")[self.name].to_numpy()

        res = self.__sample(data, n).tolist()

        if self.mapper is not None:
            res = [self.mapper[item] if item in self.mapper else item for item in res]

        return res

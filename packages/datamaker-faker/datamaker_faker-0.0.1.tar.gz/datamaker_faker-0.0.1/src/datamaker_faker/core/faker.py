from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd

from ..utils.data_folder import data_folder
from ..utils.helpers import model_to_fields, sample_from_df


class Faker:
    def __init__(
        self,
        model: dict[str, str] | None = None,
        seed: int | None = None,
    ):
        self.seed = seed
        self.model = model_to_fields(model, self.seed)
        self.random_state = np.random.RandomState(self.seed)

    def __sample(self, arr: np.array, n: int = 1):
        return self.random_state.choice(arr, n, replace=True)

    def __get_dataset(self, path: str | Path, field: str, full: bool = False):
        df = pd.read_csv(f"{path}.csv")

        if full:
            return df
        else:
            return df[field].to_numpy()

    def __determine_relations(self, path: str | Path, name: str):
        df = pd.read_csv(f"{path}.csv")
        return [col for col in df.columns if col not in [name, "id"]]

    def __enforce_relations(self, generated: dict[str, list[Any]]) -> pd.DataFrame:
        fields = [(field.name, field.path) for field in self.model.values()]
        generated_df = pd.DataFrame(generated)

        og_cols = generated_df.columns
        columns = [field[0] for field in fields]
        generated_df.columns = columns

        relations_enforced = set()
        reverse_lookup = {}

        for name, path in fields:
            relations = self.__determine_relations(path, name)

            for relation in relations:
                if relation in relations_enforced:
                    relations.remove(relation)
                    reverse_lookup[name] = relation

            if relations != []:
                if name in relations_enforced:
                    continue

                df = self.__get_dataset(path, name, True)

                # filter df on relation
                vals_to_keep = generated_df[name].unique()
                df = df[df[name].isin(vals_to_keep)]

                # determine sampling weights
                sampling_dict = generated_df[name].value_counts().to_dict()
                samples = sample_from_df(df, sampling_dict, name, self.random_state)

                generated_df = pd.merge(
                    generated_df.set_index(name),
                    samples.set_index(name),
                    on=name,
                    how="left",
                    suffixes=("_drop", ""),
                ).reset_index()[columns]

                relations_enforced = set(relations_enforced) | set(relations)

        # perform reverse lookups for relations that couldn't be enforced
        for name, relation in reverse_lookup.items():
            df = self.__get_dataset(data_folder / name, name, True)

            # filter df on relation
            df = df[df[relation].isin(generated_df[relation])]

            sampling_dict = generated_df[relation].value_counts().to_dict()
            samples = sample_from_df(df, sampling_dict, relation, self.random_state)

            # replace the values in the generated_df.name with the values in df.relation
            tmp = pd.merge(
                generated_df.set_index(relation),
                samples.set_index(relation),
                on=relation,
                how="left",
                suffixes=("_drop", ""),
            ).reset_index()
            generated_df = tmp[columns]

        generated_df.columns = og_cols
        return generated_df

    def generate(self, n=1):
        generated = {}
        for k, v in self.model.items():
            data = self.__get_dataset(v.path, v.name)
            generated[k] = self.__sample(data, n).tolist()

        with_relations = self.__enforce_relations(generated)

        return with_relations

    # TODO: This is generation from csv, but we should also support generation from functions

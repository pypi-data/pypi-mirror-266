from ..core.field import Field
import pandas as pd


def model_to_fields(
    model: dict[str, str],
    seed,
):
    if model is None:
        return None
    else:
        updated_model = {}
        for k, v in model.items():
            if isinstance(v, dict):
                updated_model[k] = v

            updated_model[k] = Field(name=v, seed=seed)

        return updated_model


def sample_from_df(df, sampling_dict, sampling_key, random_state):
    # sample from df
    samples = pd.DataFrame()

    # add a random sample of v rows from df where name == k
    for k, v in sampling_dict.items():
        samples = pd.concat(
            [
                samples,
                df[df[sampling_key] == k].sample(
                    n=v,
                    replace=True,
                    random_state=random_state,
                ),
            ]
        )

    # drop duplicates and reset the index
    samples = samples.drop_duplicates(subset=[sampling_key]).reset_index(drop=True)

    # return the samples
    return samples

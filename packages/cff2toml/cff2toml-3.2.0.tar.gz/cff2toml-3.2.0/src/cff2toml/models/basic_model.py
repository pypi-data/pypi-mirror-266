from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_snake


def to_kebab(s: str) -> str:
    return s.replace("_", "-")


class BasicModel(BaseModel):

    # configure all models to convert their keys to kebab case
    # when they serialize, but to validate keys using snake case
    # Both the CFF format and the Pyproject TOML format seem to use
    # kebab case for their keys.
    # So this configuration is needed when we try to .dump_model
    # Also, when dumping models, use .model_dump(mode="json", by_alias=True)
    # you might also want to use the exclude_defaults parameter when dumping, which
    # will exclude keys that do not differ from
    # their defaults, but this mainly makes sense when you have
    # a datastructure which has empty strings defaults;
    # it would not make sense for those involving useful defaults

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_kebab,
            serialization_alias=to_kebab,
        )
    )

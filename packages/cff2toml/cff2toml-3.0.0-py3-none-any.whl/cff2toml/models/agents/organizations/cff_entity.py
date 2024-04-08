from cff2toml.models.basic_model import BasicModel


class CffEntity(BasicModel):
    # CFF definitions.entity
    # https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md#definitionsentity

    address: str = ''
    alias: str = ''
    city: str = ''
    country: str = ''
    date_end: str = ''
    date_start: str = ''
    email: str = ''
    fax: str = ''
    location: str = ''
    name: str = ''
    orcid: str = ''
    post_code: str = ''
    region: str = ''
    tel: str = ''
    website: str = ''

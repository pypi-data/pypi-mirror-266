from dataclasses import dataclass


@dataclass(slots=True)
class NaceCodeTypesense:
    country: str
    level: int
    code: str
    section_label: str
    section_code: str
    label_en: str
    label_en_embedding: list[float] | None = None
    label_fr: str | None = None
    label_fr_embedding: list[float] | None = None
    label_nl: str | None = None
    label_nl_embedding: list[float] | None = None



@dataclass
class EntityName:
    name: str | None = None
    name_fr: str | None = None
    name_nl: str | None = None
    name_de: str | None = None
    website: str | None = None


@dataclass(init=False)
class CompanyNameTypesense(EntityName):
    _id: str
    establishments: list[EntityName] | None = None

    # We have to manually define the __init__ method here because of the way dataclasses work with inheritance
    def __init__(self, _id: str, establishments: list[EntityName] | None = None, **kwargs):
        super().__init__(**kwargs)
        self._id = _id
        self.establishments = establishments


@dataclass(slots=True)
class OnlineContentTypesense:
    companies_id: list[str] | None = None
    facebook_page_url: str | None = None
    facebook_page_text: str | None = None
    facebook_page_embedding: list[float] | None = None
    google_my_business_url: str | None = None
    google_my_business_text: str | None = None
    google_my_business_embedding: list[float] | None = None
    website_base_url: str | None = None
    website_home_page_url: str | None = None
    website_home_page_status_code: int | None = None
    website_home_page_text: str | None = None
    website_home_page_embedding: list[float] | None = None
    website_about_page_url: str | None = None
    website_about_page_status_code: int | None = None
    website_about_page_text: str | None = None
    website_about_page_embedding: list[float] | None = None
    website_contact_page_url: str | None = None
    website_contact_page_status_code: int | None = None
    website_contact_page_text: str | None = None
    website_contact_page_embedding: list[float] | None = None

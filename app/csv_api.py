from pydantic import BaseModel, ConfigDict, Field


class OrtCbdIntCsv(BaseModel):
    published_on: str = Field(alias="Published on")
    url: str = Field(alias="url")
    unique_id: str = Field(alias="Unique Id")
    government: str = Field(alias="Government")
    national_target_title: str = Field(alias="National target title")
    description: str = Field(alias="Description")
    main_policy_measures: str = Field(default="", alias="Main policy measures")
    global_goals: str = Field(default="", alias="Global Goals")
    global_targets: str = Field(default="", alias="Global targets")
    degree_of_alignment_by_target: str = Field(
        default="", alias="Degree of Alignment by target"
    )
    aspects_covered: str = Field(
        default="", alias="Aspects of the goal or target are covered"
    )
    implementation_considerations: str = Field(
        default="", alias="Considerations for implementation from Section C"
    )
    explain_considerations: str = Field(default="", alias="Explain considerations")
    headline_indicators: str = Field(default="", alias="Headline indicators")
    binary_indicators: str = Field(default="", alias="Binary indicators")
    component_indicators: str = Field(default="", alias="Component indicators")
    complementary_indicators: str = Field(default="", alias="Complementary indicators")
    other_national_indicators: str = Field(default="", alias="otherNationalIndicators")
    non_state_commitments: str = Field(default="", alias="Non-state commitments")
    overlaps_or_links: str = Field(default="", alias="Overlaps or links")
    commitments_and_actors: str = Field(default="", alias="Commitment(s) and actor(s)")
    means_of_implementation: str = Field(default="", alias="Means of implementation")
    explain_means_of_implementation: str = Field(
        default="", alias="Please explain (means of implementation)"
    )
    additional_explanation: str = Field(default="", alias="additionalExplanation")
    any_other_information: str = Field(default="", alias="Any other information")

    model_config = ConfigDict(validate_by_name=True)

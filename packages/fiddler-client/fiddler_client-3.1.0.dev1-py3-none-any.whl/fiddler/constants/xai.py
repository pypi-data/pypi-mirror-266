import enum


@enum.unique
class ExplainMethod(str, enum.Enum):
    SHAP = 'SHAP'
    FIDDLER_SHAP = 'FIDDLER_SHAP'
    IG = 'IG'
    PERMUTE = 'PERMUTE'
    ZERO_RESET = 'ZERO_RESET'
    MEAN_RESET = 'MEAN_RESET'

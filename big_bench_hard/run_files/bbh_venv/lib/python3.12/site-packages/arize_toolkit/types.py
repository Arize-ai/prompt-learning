from enum import Enum


class InputValidationEnum(Enum):
    @classmethod
    def _missing_(cls, value):
        # Search through all enum members and their aliases
        for member in cls:
            # Check if the value matches any of the values in the member's value tuple
            if isinstance(member.value, tuple) and value in member.value:
                return member
        return None

    @classmethod
    def from_input(cls, user_input):
        for operator in cls:
            if user_input in operator.value:
                return operator.name
        raise ValueError(f"{user_input} is not a valid {cls.__name__}")


class PerformanceMetric(InputValidationEnum):
    accuracy = "accuracy", "Accuracy"
    precision = "precision", "Precision"
    recall = "recall", "Recall"
    f_1 = "f_1", "F1 Score"
    sensitivity = "sensitivity", "Sensitivity"
    specificity = "specificity", "Specificity"
    falsePositiveRate = "falsePositiveRate", "False Positive Rate"
    falseNegativeRate = "falseNegativeRate", "False Negative Rate"
    falseNegativeDensity = "falseNegativeDensity", "False Negative Density"
    mse = "mse", "Mean Squared Error", "MSE"
    rmse = "rmse", "Root Mean Squared Error", "RMSE"
    mae = "mae", "Mean Absolute Error", "MAE"
    mape = "mape", "Mean Absolute Percentage Error", "MAPE"
    predictionAverage = "predictionAverage", "Prediction Average"
    actualsAverage = "actualsAverage", "Actual Average"
    auc = "auc", "Area Under Curve", "AUC"
    logLoss = (
        "logLoss",
        "Log Loss",
    )
    rSquared = (
        "rSquared",
        "R-Squared",
    )
    prAuc = "prAuc", "Precision Recall Curve", "PR AUC"
    meanError = "meanError", "Mean Error"
    calibration = "calibration", "Calibration"
    ndcg = "ndcg", "Normalized Discounted Cumulative Gain", "NDCG"
    recallParity = "recallParity", "Recall Parity"
    falsePositiveRateParity = "falsePositiveRateParity", "False Positive Rate Parity"
    disparateImpact = "disparateImpact", "Disparate Impact"
    wape = "wape", "Weighted Absolute Percentage Error", "WAPE"
    smape = "smape", "Symmetric Mean Absolute Percentage Error", "SMAPE"
    mase = "mase", "Mean Absolute Scaled Error", "MASE"
    udf = "udf", "User-Defined Function", "UDF"
    groupAuc = "groupAuc", "Group Area Under Curve", "Group AUC"
    mrr = "mrr", "Mean Reciprocal Rank", "MRR"
    rankingMap = "rankingMap", "Ranking Mean Average Precision", "Ranking MAP"
    rankingRecall = "rankingRecall", "Ranking Recall"
    rankingPrecision = "rankingPrecision", "Ranking Precision"
    microAveragedPrecision = "microAveragedPrecision", "Micro-Averaged Precision"
    microAveragedRecall = "microAveragedRecall", "Micro-Averaged Recall"
    multiClassPrecision = "multiClassPrecision", "Multi-Class Precision"
    multiClassRecall = "multiClassRecall", "Multi-Class Recall"
    macroAveragedPrecision = "macroAveragedPrecision", "Macro-Averaged Precision"
    macroAveragedRecall = "macroAveragedRecall", "Macro-Averaged Recall"


class DriftMetric(InputValidationEnum):
    psi = "psi", "Population Stability Index", "population_stability_index"
    js = (
        "js",
        "js_distance",
        "Jensen Shannon Distance",
        "Jensen-Shannon Distance",
        "jensen_shannon_distance",
    )
    kl = (
        "kl",
        "kl_divergence",
        "Kullback-Leibler",
        "KL Divergence",
        "kullback_leibler_divergence",
    )
    ks = (
        "ks",
        "ks_statistic",
        "Kolmogorov-Smirnov",
        "KS Statistic",
        "kolmogorov_smirnov_statistic",
    )
    euclideanDistance = (
        "euclideanDistance",
        "euclidean",
        "euclidean_distance",
        "Euclidean Distance",
    )
    cosineSimilarity = (
        "cosineSimilarity",
        "cosine",
        "cosine_similarity",
        "Cosine Similarity",
    )


class DataQualityMetric(InputValidationEnum):
    avg = "avg", "average", "mean"
    count = "count", "total", "n"
    sum = "sum", "total_sum"
    percentEmpty = "percentEmpty", "percent_empty", "empty_rate"
    cardinality = "cardinality", "unique_count", "n_unique"
    standardDeviation = "standardDeviation", "std_dev", "std", "standard_deviation"
    p50 = "p50", "median", "50th_percentile"
    p95 = "p95", "95th_percentile"
    p99 = "p99", "99th_percentile"
    p99_9 = "p99_9", "p999", "99.9th_percentile"
    newValues = "newValues", "new_values", "new_categories"
    missingValues = "missingValues", "missing_values", "dropped_categories"
    averageStringListLength = (
        "averageStringListLength",
        "avg_string_list_length",
        "mean_list_length",
    )


class ComparisonOperator(InputValidationEnum):
    greaterThan = "greaterThan", "Greater Than", ">"
    lessThan = "lessThan", "Less Than", "<"
    equals = "equals", "Equals", "="
    notEquals = "notEquals", "Not Equal", "!="
    greaterThanOrEqual = "greaterThanOrEqual", "Greater Than or Equal", ">="
    lessThanOrEqual = "lessThanOrEqual", "Less Than or Equal", "<="


class MonitorCategory(InputValidationEnum):
    performance = "performance", "Performance"
    drift = "drift", "Drift"
    dataQuality = "dataQuality", "Data Quality"


class ModelType(InputValidationEnum):
    score_categorical = (
        "score_categorical",
        "Score Categorical",
        "classification",
        "Classification",
    )
    numeric = "numeric", "Numeric", "regression", "Regression"
    ranking = "ranking", "Ranking"
    multi_class = "multi_class", "Multi-Class", "multiclass"
    object_detection = "object_detection", "Object Detection", "CV", "Computer Vision"
    generative_llm = "generative_llm", "Generative LLM", "LLM", "tracing", "Tracing"


class FilterRowType(InputValidationEnum):
    featureLabel = "featureLabel", "Feature Label"
    tagLabel = "tagLabel", "Tag Label"
    predictionValue = "predictionValue", "Prediction Value"
    actuals = "actuals", "Actuals"
    modelVersion = "modelVersion", "Model Version"
    batchId = "batchId", "Batch ID"
    spanProperty = "spanProperty", "Span Property"
    llmEval = "llmEval", "LLM Eval"
    annotation = "annotation", "Annotation"
    userAnnotation = "userAnnotation", "User Annotation"
    actualScore = "actualScore", "Actual Score"
    actualLabel = "actualLabel", "Actual Label"
    predictionClass = "predictionClass", "Prediction Class"
    predictionScore = "predictionScore", "Prediction Score"


class DimensionCategory(InputValidationEnum):
    featureLabel = "featureLabel", "Feature Label"
    prediction = "prediction", "Prediction"
    actuals = "actuals", "Actuals"
    actualScore = "actualScore", "Actual Score"
    actualLabel = "actualLabel", "Actual Label"
    actualClass = "actualClass", "Actual Class"
    predictionClass = "predictionClass", "Prediction Class"
    predictionLabel = "predictionLabel", "Prediction Label"
    predictionScore = "predictionScore", "Prediction Score"
    tag = "tag", "Tag"
    spanProperty = "spanProperty", "Span Property"
    llmEval = "llmEval", "LLM Eval"
    annotation = "annotation", "Annotation"
    userAnnotation = "userAnnotation", "User Annotation"
    modelVersion = "modelVersion", "Model Version"
    batchId = "batchId", "Batch ID"


class ModelEnvironment(InputValidationEnum):
    production = "production", "Production"
    validation = "validation", "Validation"
    training = "training", "Training"
    tracing = "tracing", "Tracing"


class DimensionDataType(InputValidationEnum):
    STRING = "STRING", "String", "string", "str"
    LONG = "LONG", "Long", "long", "int"
    FLOAT = "FLOAT", "Float", "float", "float32"
    DOUBLE = "DOUBLE", "Double", "double", "float64"
    EMBEDDING = "EMBEDDING", "Embedding", "embedding"
    STRING_LIST = "STRING_LIST", "String List", "string_list", "str_list"
    DICTIONARY = "DICTIONARY", "Dictionary", "dictionary", "dict"


class DataGranularity(InputValidationEnum):
    hour = "hour", "Hour"
    day = "day", "Day"
    week = "week", "Week"
    month = "month", "Month"


class PromptVersionInputVariableFormatEnum(InputValidationEnum):
    """The input variable format for determining prompt variables in the messages"""

    NONE = "NONE", "None", "none"
    F_STRING = "F_STRING", "F String", "f_string", "{}"
    MUSTACHE = "MUSTACHE", "Mustache", "mustache", "{{}}"


class LLMIntegrationProvider(InputValidationEnum):
    """The LLM provider used for execution with the prompt"""

    openAI = "openAI", "OpenAI", "openai", "OPENAI"
    awsBedrock = "awsBedrock", "AWS Bedrock", "aws_bedrock", "AWS_BEDROCK"
    azureOpenAI = "azureOpenAI", "Azure OpenAI", "azure_openai", "AZURE_OPENAI"
    vertexAI = "vertexAI", "Vertex AI", "vertex_ai", "VERTEX_AI"
    custom = "custom", "Custom", "custom", "CUSTOM"


class ExternalLLMProviderModel(InputValidationEnum):
    # OpenAI models
    GPT_4o_MINI = "GPT_4o_MINI", "gpt-4o-mini", "GPT-4o-mini"
    GPT_4o_MINI_2024_07_18 = (
        "GPT_4o_MINI_2024_07_18",
        "gpt-4o-mini-2024-07-18",
        "GPT-4o-mini-2024-07-18",
    )
    GPT_4o = "GPT_4o", "gpt-4o", "GPT-4o"
    GPT_4o_2024_05_13 = "GPT_4o_2024_05_13", "gpt-4o-2024-05-13", "GPT-4o-2024-05-13"
    GPT_4o_2024_08_06 = "GPT_4o_2024_08_06", "gpt-4o-2024-08-06", "GPT-4o-2024-08-06"
    CHATGPT_4o_LATEST = "CHATGPT_4o_LATEST", "chatgpt-4o-latest", "ChatGPT-4o-latest"
    O1_PREVIEW = "O1_PREVIEW", "o1-preview", "o1-preview"
    O1_PREVIEW_2024_09_12 = (
        "O1_PREVIEW_2024_09_12",
        "o1-preview-2024-09-12",
        "o1-preview-2024-09-12",
    )
    O1_MINI = "O1_MINI", "o1-mini", "o1-mini"
    O1_MINI_2024_09_12 = (
        "O1_MINI_2024_09_12",
        "o1-mini-2024-09-12",
        "o1-mini-2024-09-12",
    )
    GPT_4_TURBO = "GPT_4_TURBO", "gpt-4-turbo", "GPT-4 Turbo"
    GPT_4_TURBO_2024_04_09 = (
        "GPT_4_TURBO_2024_04_09",
        "gpt-4-turbo-2024-04-09",
        "GPT-4 Turbo 2024-04-09",
    )
    GPT_4_TURBO_PREVIEW = (
        "GPT_4_TURBO_PREVIEW",
        "gpt-4-turbo-preview",
        "GPT-4 Turbo Preview",
    )
    GPT_4_0125_PREVIEW = (
        "GPT_4_0125_PREVIEW",
        "gpt-4-0125-preview",
        "GPT-4 0125 Preview",
    )
    GPT_4_1106_PREVIEW = (
        "GPT_4_1106_PREVIEW",
        "gpt-4-1106-preview",
        "GPT-4 1106 Preview",
    )
    GPT_4 = "GPT_4", "gpt-4", "GPT-4"
    GPT_4_32k = "GPT_4_32k", "gpt-4-32k", "GPT-4 32k"
    GPT_4_0613 = "GPT_4_0613", "gpt-4-0613", "GPT-4 0613"
    GPT_4_0314 = "GPT_4_0314", "gpt-4-0314", "GPT-4 0314"
    GPT_4_VISION_PREVIEW = (
        "GPT_4_VISION_PREVIEW",
        "gpt-4-vision-preview",
        "GPT-4 Vision Preview",
    )
    GPT_3_5_TURBO = "GPT_3_5_TURBO", "gpt-3.5-turbo", "GPT-3.5 Turbo"
    GPT_3_5_TURBO_1106 = (
        "GPT_3_5_TURBO_1106",
        "gpt-3.5-turbo-1106",
        "GPT-3.5 Turbo 1106",
    )
    GPT_3_5_TURBO_0125 = (
        "GPT_3_5_TURBO_0125",
        "gpt-3.5-turbo-0125",
        "GPT-3.5 Turbo 0125",
    )
    O1_2024_12_17 = "O1_2024_12_17", "o1-2024-12-17", "o1-2024-12-17"
    O1 = "O1", "o1", "o1"
    O3_MINI = "O3_MINI", "o3-mini", "o3-mini"
    O3_MINI_2025_01_31 = (
        "O3_MINI_2025_01_31",
        "o3-mini-2025-01-31",
        "o3-mini-2025-01-31",
    )

    # Google/Gemini models
    GEMINI_PRO = "GEMINI_PRO", "gemini-pro", "Gemini Pro"
    GEMINI_1_0_PRO = "GEMINI_1_0_PRO", "gemini-1.0-pro", "Gemini 1.0 Pro"
    GEMINI_1_0_PRO_VISION = (
        "GEMINI_1_0_PRO_VISION",
        "gemini-1.0-pro-vision",
        "Gemini 1.0 Pro Vision",
    )
    GEMINI_1_0_PRO_VISION_002 = (
        "GEMINI_1_0_PRO_VISION_002",
        "gemini-1.0-pro-vision-002",
        "Gemini 1.0 Pro Vision 002",
    )
    GEMINI_1_5_PRO = "GEMINI_1_5_PRO", "gemini-1.5-pro", "Gemini 1.5 Pro"
    GEMINI_1_5_PRO_002 = (
        "GEMINI_1_5_PRO_002",
        "gemini-1.5-pro-002",
        "Gemini 1.5 Pro 002",
    )
    GEMINI_1_5_FLASH = "GEMINI_1_5_FLASH", "gemini-1.5-flash", "Gemini 1.5 Flash"
    GEMINI_1_5_FLASH_002 = (
        "GEMINI_1_5_FLASH_002",
        "gemini-1.5-flash-002",
        "Gemini 1.5 Flash 002",
    )
    GEMINI_1_5_FLASH_8B = (
        "GEMINI_1_5_FLASH_8B",
        "gemini-1.5-flash-8b",
        "Gemini 1.5 Flash 8B",
    )
    GEMINI_2_0_FLASH_EXP = (
        "GEMINI_2_0_FLASH_EXP",
        "gemini-2.0-flash-exp",
        "Gemini 2.0 Flash Exp",
    )
    GEMINI_2_0_FLASH_001 = (
        "GEMINI_2_0_FLASH_001",
        "gemini-2.0-flash-001",
        "Gemini 2.0 Flash 001",
    )
    GEMINI_2_0_FLASH_LITE_PREVIEW_02_05 = (
        "GEMINI_2_0_FLASH_LITE_PREVIEW_02_05",
        "gemini-2.0-flash-lite-preview-02-05",
        "Gemini 2.0 Flash Lite Preview 02-05",
    )
    GEMINI_1_5_FLASH_LATEST = (
        "GEMINI_1_5_FLASH_LATEST",
        "gemini-1.5-flash-latest",
        "Gemini 1.5 Flash Latest",
    )
    GEMINI_1_5_FLASH_8B_LATEST = (
        "GEMINI_1_5_FLASH_8B_LATEST",
        "gemini-1.5-flash-8b-latest",
        "Gemini 1.5 Flash 8B Latest",
    )
    GEMINI_1_5_PRO_LATEST = (
        "GEMINI_1_5_PRO_LATEST",
        "gemini-1.5-pro-latest",
        "Gemini 1.5 Pro Latest",
    )
    GEMINI_2_0_FLASH = "GEMINI_2_0_FLASH", "gemini-2.0-flash", "Gemini 2.0 Flash"
    GEMINI_1_5_PRO_001 = (
        "GEMINI_1_5_PRO_001",
        "gemini-1.5-pro-001",
        "Gemini 1.5 Pro 001",
    )

    # Anthropic Claude models
    CLAUDE_3_5_HAIKU = (
        "CLAUDE_3_5_HAIKU",
        "claude-3-5-haiku",
        "Claude 3.5 Haiku",
        "haiku_3_5",
    )
    CLAUDE_3_5_HAIKU_20241022 = (
        "CLAUDE_3_5_HAIKU_20241022",
        "claude-3-5-haiku-20241022",
        "Claude 3.5 Haiku 20241022",
    )
    CLAUDE_3_5_SONNET = (
        "CLAUDE_3_5_SONNET",
        "claude-3-5-sonnet",
        "Claude 3.5 Sonnet",
        "sonnet_3_5",
    )
    CLAUDE_3_5_SONNET_20240620 = (
        "CLAUDE_3_5_SONNET_20240620",
        "claude-3-5-sonnet-20240620",
        "Claude 3.5 Sonnet 20240620",
    )
    CLAUDE_3_5_SONNET_V2 = (
        "CLAUDE_3_5_SONNET_V2",
        "claude-3-5-sonnet-v2",
        "Claude 3.5 Sonnet V2",
    )
    CLAUDE_3_5_SONNET_V2_20241022 = (
        "CLAUDE_3_5_SONNET_V2_20241022",
        "claude-3-5-sonnet-v2-20241022",
        "Claude 3.5 Sonnet V2 20241022",
    )
    CLAUDE_3_7_SONNET = (
        "CLAUDE_3_7_SONNET",
        "claude-3-7-sonnet",
        "Claude 3.7 Sonnet",
        "sonnet_3_7",
    )
    CLAUDE_3_7_SONNET_20250219 = (
        "CLAUDE_3_7_SONNET_20250219",
        "claude-3-7-sonnet-20250219",
        "Claude 3.7 Sonnet 20250219",
    )
    CLAUDE_3_HAIKU = "CLAUDE_3_HAIKU", "claude-3-haiku", "Claude 3 Haiku", "haiku_3"
    CLAUDE_3_HAIKU_20240307 = (
        "CLAUDE_3_HAIKU_20240307",
        "claude-3-haiku-20240307",
        "Claude 3 Haiku 20240307",
    )
    CLAUDE_3_OPUS = "CLAUDE_3_OPUS", "claude-3-opus", "Claude 3 Opus", "opus_3"
    CLAUDE_3_OPUS_20240229 = (
        "CLAUDE_3_OPUS_20240229",
        "claude-3-opus-20240229",
        "Claude 3 Opus 20240229",
    )
    ANTHROPIC_CLAUDE_V2 = (
        "ANTHROPIC_CLAUDE_V2",
        "anthropic-claude-v2",
        "Anthropic Claude V2",
    )
    ANTHROPIC_CLAUDE_3_SONNET = (
        "ANTHROPIC_CLAUDE_3_SONNET",
        "anthropic-claude-3-sonnet",
        "Anthropic Claude 3 Sonnet",
    )
    ANTHROPIC_CLAUDE_3_5_SONNET = (
        "ANTHROPIC_CLAUDE_3_5_SONNET",
        "anthropic-claude-3-5-sonnet",
        "Anthropic Claude 3.5 Sonnet",
    )
    ANTHROPIC_CLAUDE_3_HAIKU = (
        "ANTHROPIC_CLAUDE_3_HAIKU",
        "anthropic-claude-3-haiku",
        "Anthropic Claude 3 Haiku",
    )
    ANTHROPIC_CLAUDE_3_5_HAIKU = (
        "ANTHROPIC_CLAUDE_3_5_HAIKU",
        "anthropic-claude-3-5-haiku",
        "Anthropic Claude 3.5 Haiku",
    )
    ANTHROPIC_CLAUDE_INSTANT_V1 = (
        "ANTHROPIC_CLAUDE_INSTANT_V1",
        "anthropic-claude-instant-v1",
        "Anthropic Claude Instant V1",
    )
    ANTHROPIC_CLAUDE_V2_1 = (
        "ANTHROPIC_CLAUDE_V2_1",
        "anthropic-claude-v2-1",
        "Anthropic Claude V2.1",
    )
    ANTHROPIC_CLAUDE_3_OPUS = (
        "ANTHROPIC_CLAUDE_3_OPUS",
        "anthropic-claude-3-opus",
        "Anthropic Claude 3 Opus",
    )
    ANTHROPIC_CLAUDE_3_5_SONNET_V2 = (
        "ANTHROPIC_CLAUDE_3_5_SONNET_V2",
        "anthropic-claude-3-5-sonnet-v2",
        "Anthropic Claude 3.5 Sonnet V2",
    )

    # Amazon models
    AMAZON_NOVA_PRO = (
        "AMAZON_NOVA_PRO",
        "amazon-nova-pro",
        "Amazon Nova Pro",
    )  # Amazon's Nova Pro
    AMAZON_NOVA_LITE = (
        "AMAZON_NOVA_LITE",
        "amazon-nova-lite",
        "Amazon Nova Lite",
    )  # Amazon's Nova Lite
    AMAZON_NOVA_MICRO = (
        "AMAZON_NOVA_MICRO",
        "amazon-nova-micro",
        "Amazon Nova Micro",
    )  # Amazon's Nova Micro
    AMAZON_TITAN_TEXT = (
        "AMAZON_TITAN_TEXT",
        "amazon-titan-text",
        "Amazon Titan Text",
    )  # Amazon's Titan Text
    AMAZON_TITAN_TEXT_EXPRESS = (
        "AMAZON_TITAN_TEXT_EXPRESS",
        "amazon-titan-text-express",
        "Amazon Titan Text Express",
    )  # Amazon's Titan Text Express
    AMAZON_TITAN_TEXT_LITE = (
        "AMAZON_TITAN_TEXT_LITE",
        "amazon-titan-text-lite",
        "Amazon Titan Text Lite",
    )  # Amazon's Titan Text Lite

    # Meta Llama models
    META_LLAMA_3_0_8B_INSTRUCT = (
        "META_LLAMA_3_0_8B_INSTRUCT",
        "meta-llama-3-0-8b-instruct",
        "Meta Llama 3.0 8B Instruct",
    )  # Meta's Llama 3.0 8B Instruct
    META_LLAMA_3_0_70B_INSTRUCT = (
        "META_LLAMA_3_0_70B_INSTRUCT",
        "meta-llama-3-0-70b-instruct",
        "Meta Llama 3.0 70B Instruct",
    )  # Meta's Llama 3.0 70B Instruct
    META_LLAMA_3_1_8B_INSTRUCT = (
        "META_LLAMA_3_1_8B_INSTRUCT",
        "meta-llama-3-1-8b-instruct",
        "Meta Llama 3.1 8B Instruct",
    )  # Meta's Llama 3.1 8B Instruct
    META_LLAMA_3_1_70B_INSTRUCT = (
        "META_LLAMA_3_1_70B_INSTRUCT",
        "meta-llama-3-1-70b-instruct",
        "Meta Llama 3.1 70B Instruct",
    )  # Meta's Llama 3.1 70B Instruct
    META_LLAMA_3_1_405B_INSTRUCT = (
        "META_LLAMA_3_1_405B_INSTRUCT",
        "meta-llama-3-1-405b-instruct",
        "Meta Llama 3.1 405B Instruct",
    )  # Meta's Llama 3.1 405B Instruct
    META_LLAMA_3_2_1B_INSTRUCT = (
        "META_LLAMA_3_2_1B_INSTRUCT",
        "meta-llama-3-2-1b-instruct",
        "Meta Llama 3.2 1B Instruct",
    )  # Meta's Llama 3.2 1B Instruct
    META_LLAMA_3_2_3B_INSTRUCT = (
        "META_LLAMA_3_2_3B_INSTRUCT",
        "meta-llama-3-2-3b-instruct",
        "Meta Llama 3.2 3B Instruct",
    )  # Meta's Llama 3.2 3B Instruct
    META_LLAMA_3_2_11B_INSTRUCT = (
        "META_LLAMA_3_2_11B_INSTRUCT",
        "meta-llama-3-2-11b-instruct",
        "Meta Llama 3.2 11B Instruct",
    )  # Meta's Llama 3.2 11B Instruct
    META_LLAMA_3_2_90B_INSTRUCT = (
        "META_LLAMA_3_2_90B_INSTRUCT",
        "meta-llama-3-2-90b-instruct",
        "Meta Llama 3.2 90B Instruct",
    )  # Meta's Llama 3.2 90B Instruct
    META_LLAMA_3_3_70B_INSTRUCT = (
        "META_LLAMA_3_3_70B_INSTRUCT",
        "meta-llama-3-3-70b-instruct",
        "Meta Llama 3.3 70B Instruct",
    )  # Meta's Llama 3.3 70B Instruct


class BlobStore(InputValidationEnum):
    S3 = "S3", "s3"
    GCS = "GCS", "gcs"
    Azure = "Azure", "azure", "AZURE"


class TableStore(InputValidationEnum):
    BigQuery = "BigQuery", "bigquery", "BIGQUERY"
    Snowflake = "Snowflake", "snowflake", "SNOWFLAKE"
    Databricks = "Databricks", "databricks", "DATABRICKS"


class TimeSeriesMetricCategory(InputValidationEnum):
    modelDataMetric = "modelDataMetric", "Model Data Metric"
    evaluationMetric = "evaluationMetric", "Evaluation Metric"


class WidgetCreationStatus(InputValidationEnum):
    needsInit = "needsInit", "Needs Init"
    pending = "pending", "Pending"
    created = "created", "Created"
    published = "published", "Published"
    unpublished = "unpublished", "Unpublished"


class BarChartWidgetDataValueObjectType(InputValidationEnum):
    number = ("number", "Number")
    string = ("string", "String")
    range = ("range", "Range")
    total = ("total", "Total")


class DashboardStatus(InputValidationEnum):
    active = "active", "Active"
    inactive = "inactive", "Inactive"
    deleted = "deleted", "Deleted"

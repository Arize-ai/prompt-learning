CREATE_QUERY_HOP1_PROMPT = "Given the fields {claim}, produce the field 'query_1'."

SUMMARIZE1_PROMPT = (
    "Given the fields {claim}, {passages_1}, produce the field 'summary_1'."
)

CREATE_QUERY_HOP2_PROMPT = (
    "Given the fields {claim}, {summary_1}, produce the field 'query_2'."
)

SUMMARIZE2_PROMPT = (
    "Given the fields {claim}, {summary_1}, {passages_2}, produce the field 'summary_2'."
)

CREATE_QUERY_HOP3_PROMPT = (
    "Given the fields {claim}, {summary_1}, {summary_2}, produce the field 'query_3'."
)

SUMMARIZE3_PROMPT = (
    "Given the fields {claim}, {summary_1}, {summary_2}, {passages_3}, produce the field 'summary_3'."
)

GENERATE_ANSWER_PROMPT = (
    "Given the fields {claim}, {summary_1}, {summary_2}, {summary_3}, return either 'SUPPORTED', 'REFUTED', or 'NOT ENOUGH INFO'."
)



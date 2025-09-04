Replace any email address with [EMAIL].
Replace any Social Security–like number (###-##-####) with [SSN].
If a person’s full name (two capitalized words) appears, replace with [NAME].
Normalize percentages (e.g., 15%, 15 percent) → 0.15.
If a number is over 1000, and contains commas, remove the commas (10,000 → 10000).
Remove extra whitespace and replace with a single space.
Replace slang like u → you, thx → thanks, pls → please.
If a message contains one of the 3 banned words (e.g., refund, lawsuit, fraud), replace them with [FLAGGED].
Append a compliance footer: -- Company Confidential -- at the end of every message.
Replace any phone number with [PHONE].
Redact any credit card number (16 digits, grouped as ####-####-####-####) with [CARD].
Convert all dollar amounts ($123.45) into USD 123.45.
All dollar amounts should have 2 decimal places, rounded. 
Standardize dates to ISO format YYYY-MM-DD.
Round all decimals to 2 places.
Expand common abbreviations: ASAP → as soon as possible, ETA → estimated time of arrival.
Remove repeated punctuation (e.g. !!! → !, ??? -> ?).
If an address is detected, redact with [ADDRESS].
If the message contains both [EMAIL] and [PHONE], prepend a warning: [PII ALERT].
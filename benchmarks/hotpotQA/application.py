from numpy.matlib import test
import openai
from search import search
import os
import pandas as pd
import random
import json
from phoenix.evals import OpenAIModel, llm_generate
from hotpot_evaluate_v1 import eval
import time

def generate_output(dataset, system_prompt):
    output_model = OpenAIModel(
        model="gpt-4.1-mini",
        temperature=1
    )
    outputs = llm_generate(
        dataframe=dataset,
        template=system_prompt,
        model=output_model,
        concurrency=40,
        verbose=True
    )
    return outputs["output"]

def answer_dataset(dataset, client, create_query_1_prompt, summarize_1_prompt, create_query_2_prompt, summarize_2_prompt, final_answer_prompt):
    predictions = {
        "answer": {},
        "sp": {}
        }

    questions = pd.DataFrame({"question": dataset["question"], "question_id": dataset["_id"], "gold_answer": dataset["answer"], "supporting_facts": dataset["supporting_facts"]})
    questions.set_index("question_id", inplace=True, drop=False)
    
    # Generate query 1 for all questions
    questions["query_1"] = generate_output(questions, create_query_1_prompt)
    
    # Search for each query individually
    questions["passages_1"] = questions["query_1"].apply(lambda q: search(q, 5))
    
    # Generate summary 1
    questions["summary_1"] = generate_output(questions, summarize_1_prompt)
    
    # Generate query 2
    questions["query_2"] = generate_output(questions, create_query_2_prompt)
    
    # Search for each query 2 individually
    questions["passages_2"] = questions["query_2"].apply(lambda q: search(q, 5))
    
    # Generate summary 2
    questions["summary_2"] = generate_output(questions, summarize_2_prompt)
    
    # Generate final answer
    questions["final_answer"] = generate_output(questions, final_answer_prompt)
    
    for question_id, row in questions.iterrows():
        predictions["answer"][question_id] = row["final_answer"]
        predictions["sp"][question_id] = row["passages_2"]
    
    return questions, predictions

def main():

    start_time = time.time()

    # train_data = pd.read_json("data/hotpot_train_v1.json")
    # test_data = pd.read_json("data/hotpot_dev_fullwiki_v1.json")
    # test_data = pd.read_json("data/hotpot_test_fullwiki_v1.json")

    # Sample 300 rows from dev_data
    dev_data = pd.read_json("data/hotpot_dev_fullwiki_v1.json")
    dataset = dev_data.sample(300, random_state=42)

    # sample 150 rows from train_data
    # dataset = train_data.sample(150, random_state=42)
    
    # Save the sampled gold data for evaluation
    dataset.to_json("data/hotpot_dev_sample_300.json", orient="records")
    # dataset.to_json("data/hotpot_train_sample_150.json", orient="records")
    # train_data = pd.read_json("data/hotpot_train_v1.json")
    # test_data = pd.read_json("data/hotpot_dev_fullwiki_v1.json")
    # train_dataset = train_data.sample(150, random_state=42)
    # dev_dataset = train_data.drop(train_dataset.index).sample(150, random_state=42)
    # test_dataset = test_data.sample(300, random_state=42)
    # train_dataset.to_json("data/hotpot_train_sample_150.json", orient="records")
    # dev_dataset.to_json("data/hotpot_dev_sample_150.json", orient="records")
    # test_dataset.to_json("data/hotpot_test_sample_300.json", orient="records")

    # create_query_1_prompt = "Given the fields {question}, produce a query."
    # summarize_1_prompt = "Given the fields {question}, {passages_1}, produce a summary."
    # create_query_2_prompt = "Given the fields {question}, {summary_1}, produce a query."
    # summarize_2_prompt = "Given the fields {question}, {summary_1}, {passages_2}, produce a summary."
    # # final_answer_prompt = "Given the fields {question}, {summary_1}, {summary_2}, produce an answer."
    # final_answer_prompt = """
    # Given the fields {question}, {summary_1}, {summary_2}, produce a concise and precise answer that directly and minimally responds to the question.  
    # - Provide the shortest possible answer that fully addresses the question.  
    # - If the question expects a specific name, date, number, phrase, or list, output only that without any additional explanation, context, or full sentences.  
    # - For yes/no questions, answer with "yes" or "no" only, without elaboration.  
    # - Avoid adding extra context, background information, or verbose sentences.  
    # - If the information is not available or cannot be determined from the summaries, respond with "No information available."  

    # # # Answer:
    # # # """

    create_query_1_prompt = "Given the fields {question}, produce a single, precise search query that maximizes the chance of retrieving the exact fact needed. Output only the final query string (no quotes, no analysis, no extra words).  - Parse the question: identify core entities, relations, constraints (dates/locations/roles), and the requested answer type (name, date, number, yes/no, title). If the task is multi-hop (e.g., person → team → championships), note the steps and target the first missing link.  - Include the key slot word(s) from the question to focus retrieval on the exact field: e.g., platforms/devices/systems/OS; birth date/DOB/age; creator/created by; continent; exact day month year; list/count/number.  - Disambiguate titles, names, and mediums with context: add qualifiers like (TV series), (film), (short film), (documentary), (song), (album), (magazine), (album vs single), character vs actor, publisher/network (BBC, ITV, Nickelodeon), location (city/country), and year. Include ordinal→name mapping (e.g., 'tenth Governor General of Canada' → Prince Arthur) when relevant.  - Include critical qualifiers: exact dates when required ('day month year'), specific years, 'studio album' vs 'compilation/promotional', 'created by' vs 'produced by', 'revived in YEAR', 'exact location name' (e.g., 'Royal Observatory'), 'short film' vs 'feature film', 'song' vs 'album', 'second by release date'.  - Prefer exact phrasings from the question; add likely synonyms/aliases, alternate spellings, and regional variations. Include both specific and broader terms if helpful. Add clarifiers for slot terms (e.g., platforms OR devices OR systems OR OS; birth date OR born OR DOB).  - Add clarifiers/negative terms to avoid common confusions (e.g., 'The Ring (magazine) not Lord of the Rings'; 'The Other Side (song) by Pendulum not 1927 album'; 'Return of the Jedi (1983) not documentary'; 'Walt Disney 2003 sequel The Jungle Book 2; exclude 1997 live-action').  - If the question implies a comparison or count without explicit numbers, include terms that help qualitative comparison (e.g., 'list of subsidiaries', 'acquisitions', 'number of subsidiaries') for each entity.  - If the question asks for a specific field (exact formation date, creator names, exact location), explicitly request that detail ('exact day month year', 'creator(s) name(s)', 'exact location name').  - Avoid generic or unrelated concepts; don’t anchor on the first plausible entity—cover alternate candidates in the query if ambiguity is high.  - Use search-friendly formulations: put exact titles and mediums, add years where known, and include the slot keyword.  Examples:  - Q: 'Who was the widow affected by the Sixth Circuit's same-sex marriage decision from Ohio?'  Query: 'female surviving spouse widow Ohio Sixth Circuit same-sex marriage decision Obergefell v. Hodges name'  - Q: 'Rowland Barnes was murdered by a man on trial for what crime?'  Query: 'Brian Nichols on trial for what charge when he murdered Judge Rowland W. Barnes 2005 Atlanta courtroom'  - Q: 'What continent were both The Ring and Shonen Jump published in?'  Query: 'The Ring (magazine) publication continent and Shonen Jump North America publication'  - Q: 'Who created the British soap opera in which Rebecca Egan had the guest role of Kendra Hills-Smythe?'  Query: 'EastEnders (BBC TV series) creator created by Julia Smith Tony Holland Kendra Hills-Smythe Rebecca Egan'  - Q: 'Who appeared as a DC Comic book hero in a title revived in 2007?'  Query: 'The Brave and the Bold revived 2007 DC Comics which hero appeared Donna Troy'  - Q: 'What was the name of Red Hot Chili Peppers 1989 album released by EMI Records?'  Query: 'Red Hot Chili Peppers 1989 studio album released by EMI Records Mother’s Milk (not Sock-Cess compilation)'  - Q: 'Shepherd Gate Clock was probably the first to display the solar time at which location in London?'  Query: 'Shepherd Gate Clock first to display Greenwich Mean Time exact location name Royal Observatory Greenwich'  - Q: 'Silliman University was named after a businessman from the town added to the National Register in what year?'  Query: 'Horace Brinsmade Silliman Cohoes New York National Register of Historic Places Downtown Cohoes Historic District added year'  - Q: 'Which actor born May 17, 1955 starred in Tombstone?'  Query: 'actor born May 17, 1955 starred in Tombstone (1993 film) cast Bill Paxton birthdate'  - Q: 'The Other Side was released by the band founded in what year?'  Query: 'The Other Side song Pendulum (drum and bass band) founding year (exclude Shalamar 1983 album and 1927 album)'  - Q: 'When was the second movie featuring Baloo produced?'  Query: 'second movie featuring Baloo chronological list The Jungle Book films Disney The Jungle Book 2 2003 production year (exclude 1997 live-action Mowgli & Baloo)'  - Q: 'Which city is about 80 km northeast of Chartres Cathedral?'  Query: 'Chartres Cathedral located about 80 km southwest of Paris identify city Paris'  - Q: 'The Japanese action role-playing game, Rise of Mana, was developed for Sony Interactive Entertainment's PlayStation Vita and what other devices?'  Query: 'Rise of Mana platforms devices systems iOS Android (PlayStation Vita already known)'  - Q: 'Who is older, Patty Fendick or Manuela Maleeva?'  Query: 'Patty Fendick birth date DOB and Manuela Maleeva birth date DOB who older'"

    summarize_1_prompt = "Given the fields {question}, {passages_1}, produce a faithful, compact summary that directly supports answering the question.  - Extract only facts explicitly stated in the passages; do not infer beyond the text. Simple deterministic derivations directly implied by the text (e.g., comparing two explicit birthdates to identify who is older) are allowed.  - Capture key entities, relations, constraints, and the required answer type (e.g., gender/role distinctions, exact charge, direct sequel vs spin-off, publication continent, exact dates/numbers, exact location names, birthdates, team affiliations).  - Disambiguate closely related concepts (e.g., studio album vs compilation; song vs album; short film vs feature; creator vs producer; nationality vs profession; revived vs rebooted).  - If multiple candidates/entities share a name, list the candidates and the disambiguating details present.  - If multiple conflicting facts appear, note the conflict.  - If critical details are missing (e.g., only a year is given but a full date is asked; the relevant filmography link is absent; ‘second’ requires a chronological list not present), explicitly state what is missing and what the next retrieval should target (e.g., 'need actor’s name born on DATE', 'need team championships count', 'need list of all adaptations and years to pick the second').  - Prefer precise wording from the passages; avoid verbosity.  - For slot-like questions, enumerate the slot values plainly (e.g., platforms: iOS; Android).  - Output format: use 'Findings:', 'Missing:', 'Conflicts:' headings only.  - Example style: 'Findings: … Missing: … Conflicts: …'"

    create_query_2_prompt = "Given the fields {question}, {summary_1}, produce a refined single query that fills remaining gaps or resolves ambiguities identified in the first summary. Output only the final query string (no quotes, no analysis, no extra words).  - Target the exact missing detail(s) or disambiguation (e.g., 'exact day month year', 'direct sequel vs spin-off', 'female widow', 'The Ring (magazine)', 'creator(s) name(s)', 'studio album', 'short film', 'revived in 2007', 'exact location Royal Observatory', 'actor born May 17, 1955', 'list all Baloo films and years (select second by date)').  - Incorporate best-known entity names, roles, dates, ordinals→names, and qualifiers from summary_1.  - Add synonyms/aliases and clarifying context; add geographic qualifiers to avoid homonyms (e.g., River Thames England not Connecticut).  - Include the slot keyword(s) to sharpen retrieval (e.g., platforms OR devices OR systems OR OS; birth date OR born OR DOB; creator OR created by).  - Use exclusion/clarification terms to avoid traps (e.g., 'not compilation', 'not Connecticut', 'BBC TV series', 'DC Comics title', 'song not album', '2003 Disney sequel not 1997 live-action').  - For multi-hop questions, explicitly query the next hop (e.g., first retrieve the player’s team, then the team’s World Series wins; first retrieve the actor’s identity, then their film credit).  - For comparative/counted results lacking explicit numbers, query for lists or counts for both entities to enable a reasoned comparison (e.g., 'list of Cisco Systems subsidiaries acquisitions vs American Water subsidiaries').  - Examples:  - If summary lacks exact date: 'Led Zeppelin exact formation date day month year'  - If entity ambiguous: 'The Ring (magazine) publication continent (not The Lord of the Rings)'  - If hierarchy needed: 'Coldstream Guards broader classification Guards Division Foot Guards'  - If creator missing: 'EastEnders (BBC TV series) created by creator names'  - If revived-title hero missing: 'The Brave and the Bold revived 2007 DC Comics character appearances Donna Troy'  - If album type unclear: 'Red Hot Chili Peppers 1989 studio album EMI Records Mother’s Milk exact title (exclude compilation Sock-Cess)'  - If location too broad: 'Shepherd Gate Clock exact location name Royal Observatory Greenwich London'  - If town/year missing: 'Downtown Cohoes Historic District National Register year Cohoes New York'  - If filmography link missing: 'actor born May 17, 1955 starred in Tombstone cast list verify Bill Paxton'  - If 'second movie' unresolved: 'complete list of films featuring Baloo with release years (identify second chronologically)'  - If devices/platforms remain: 'Rise of Mana platforms devices systems iOS Android (exclude PlayStation Vita already mentioned)'  - If age comparison unclear: 'Patty Fendick birth date and Manuela Maleeva birth date DOB which earlier'"

    summarize_2_prompt = "Given the fields {question}, {summary_1}, {passages_2}, produce an improved, concise summary that integrates new evidence.  - Confirm or correct facts from summary_1; resolve conflicts when possible.  - Extract the specific detail(s) needed to answer at the requested granularity (e.g., exact date, specific crime, direct sequel title, continent, studio album title, creator names, short vs feature film, exact location name, regiment/division).  - Prefer the most specific, properly named entity that directly answers (e.g., 'Royal Observatory' rather than 'Greenwich'; 'Bill Paxton' rather than describing his roles).  - For ordinal references (e.g., 'tenth Governor General'), map to the proper name if present and link to the resulting entity/action.  - Simple deterministic derivations directly implied by the text are allowed (e.g., identify who is older from two birthdates).  - Clearly note any remaining missing information that prevents a definitive answer and what a final retrieval would need (if any).  - Keep it strictly evidence-based and minimal, while preserving key qualifiers.  - Output format: use 'Findings:', 'Missing:', 'Resolved:' headings only.  - Example style: 'Findings: … Missing: … Resolved: …'"

    final_answer_prompt = """
    Given the fields {question}, {summary_1}, {summary_2}, produce a concise and precise answer that directly and minimally responds to the question.  
    - Provide the shortest possible answer that fully addresses the question.  
    - If the question expects a specific name, date, number, phrase, or list, output only that without any additional explanation, context, or full sentences.  
    - For yes/no questions, answer with \"yes\" or \"no\" only, without elaboration.  
    - When a comparative judgment is required but explicit counts are missing, prefer the best-supported conclusion from the summaries (e.g., one entity has 'numerous named subsidiaries' vs a single example), and output only the winning entity.  
    - Avoid adding extra context, background information, or verbose sentences.  
    ...
    - Keep answers minimal (e.g., for 'Where is X located about 80 km southwest of ?', answer 'Paris' only).  

    Answer:
    """
    

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    questions, predictions = answer_dataset(dataset, client, create_query_1_prompt, summarize_1_prompt, create_query_2_prompt, summarize_2_prompt, final_answer_prompt)

    # questions.to_json("questions/questions_dev_300.json")
    questions.to_json("questions/questions_dev_300.json")
    # questions.to_json("questions/questions_train_150.json", orient="records")
    with open("predictions/predictions_dev_300.json", "w") as f:
        json.dump(predictions, f, indent=2)
    # with open("predictions/predictions_train_150.json", "w") as f:
    #     json.dump(predictions, f, indent=2)

    # Evaluate on the same 300 sample
    eval("predictions/predictions_dev_300.json", "data/hotpot_dev_sample_300.json")
    # eval("predictions/predictions_train_150.json", "data/hotpot_train_sample_150.json")

    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()

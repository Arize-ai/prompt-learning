import pandas as pd


train_data = pd.read_json("data/hotpot_train_v1.json")
test_data = pd.read_json("data/hotpot_dev_fullwiki_v1.json")
train_dataset = train_data.sample(150, random_state=42)
dev_dataset = train_data.drop(train_dataset.index).sample(150, random_state=42)
test_dataset = test_data.sample(300, random_state=42)
train_dataset.to_json("data/hotpot_train_sample_150.json", orient="records")
dev_dataset.to_json("data/hotpot_dev_sample_150.json", orient="records")
test_dataset.to_json("data/hotpot_test_sample_300.json", orient="records")
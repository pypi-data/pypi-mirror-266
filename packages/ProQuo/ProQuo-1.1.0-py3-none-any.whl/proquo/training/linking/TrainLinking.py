from os.path import join
from pathlib import Path
from proquo.model.linking import LinkingModelTrainer
from proquo.model.linking.LinkingVectorizer import LinkingVectorizer
import json


def train(train_file_path, val_file_path, batch_size, num_epochs, lower_case, model_name, output_folder_path):
    config = {
        'base model name': model_name,
        'lower case': lower_case,
        'num epochs': num_epochs,
        'batch size': batch_size,
    }

    with open(join(output_folder_path, 'config.json'), 'w', encoding='utf-8') as config_file:
        content = json.dumps(config)
        config_file.write(content)

    x_train = []
    y_train = []

    with open(train_file_path, 'r', encoding='utf-8') as train_file:
        for line in train_file:

            if not line.strip():
                continue

            parts = line.split('\t')

            if len(parts) >= 3:
                x_train.append((parts[0], parts[1]))
                y_train.append(int(parts[2]))
            else:
                print(f'wrong count: {line}')

    x_val = []
    y_val = []

    with open(val_file_path, 'r', encoding='utf-8') as val_file:
        for line in val_file:

            if not line.strip():
                continue

            parts = line.split('\t')

            if len(parts) >= 3:
                x_val.append((parts[0], parts[1]))
                y_val.append(int(parts[2]))
            else:
                print(f'wrong count: {line}')

    linking_vectorizer = LinkingVectorizer.from_raw(model_name,512, lower_case)

    tokenizer_dir = join(output_folder_path, 'tokenizer')
    Path(tokenizer_dir).mkdir(parents=True, exist_ok=True)
    linking_vectorizer.tokenizer.save_pretrained(tokenizer_dir)

    LinkingModelTrainer.train_model(linking_vectorizer, model_name, batch_size, num_epochs, x_train, y_train, x_val,
                                    y_val, output_folder_path)

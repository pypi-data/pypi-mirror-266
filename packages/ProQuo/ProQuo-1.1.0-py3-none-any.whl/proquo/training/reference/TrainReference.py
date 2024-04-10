from os.path import isfile
from proquo.model.reference.ReferenceModelTrainer import ReferenceModelTrainer


def train(train_file_path, val_file_path, output_folder_path):
    if (not (isfile(train_file_path) and train_file_path.endswith(".txt")) or
            not (isfile(val_file_path) and val_file_path.endswith(".txt"))):
        # TODO: log warning
        pass

    x_train = []
    y_train = []

    with open(train_file_path, 'r', encoding='utf-8') as train_file:
        for line in train_file:

            if not line.strip():
                continue

            parts = line.split('\t')

            if len(parts) == 3:
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

            if len(parts) == 3:
                x_val.append((parts[0], parts[1]))
                y_val.append(int(parts[2]))
            else:
                print(f'wrong count: {line}')

    model = ReferenceModelTrainer(25, True, 32, 32, 0.2, 512, 10)
    model.train_model(x_train, y_train, x_val, y_val, output_folder_path)

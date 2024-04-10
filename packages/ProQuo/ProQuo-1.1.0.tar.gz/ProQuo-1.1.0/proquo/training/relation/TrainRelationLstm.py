from proquo.model.relation.RelationModelLstmTrainer import RelationModelLstmTrainer


def train(train_file_path, val_file_path, output_folder_path):

    x_train = []
    y_train = []

    with open(train_file_path, 'r', encoding='utf-8') as train_file:
        for line in train_file:

            if not line.strip():
                continue

            parts = line.split('\t')

            if len(parts) == 2:
                x_train.append(parts[0])
                y_train.append(int(parts[1]))
            else:
                print(f'wrong count: {line}')

    x_val = []
    y_val = []

    with open(val_file_path, 'r', encoding='utf-8') as val_file:
        for line in val_file:

            if not line.strip():
                continue

            parts = line.split('\t')

            if len(parts) == 2:
                x_val.append(parts[0])
                y_val.append(int(parts[1]))
            else:
                print(f'wrong count: {line}')

    model = RelationModelLstmTrainer(200, True, 64, 64, 0.3, 128, 5)
    model.train_model(x_train, y_train, x_val, y_val, output_folder_path)

from proquo.model.reference.ReferenceModelTrainer import ReferenceModelTrainer
from proquo.model.reference.ReferenceVectorizer import ReferenceVectorizer


def test(input_path, vocab_path, model_path):
    vectorizer = ReferenceVectorizer.from_vocab_file(vocab_path, 25, True)

    sentences_1 = []
    sentences_2 = []
    gold_preds = []

    with open(input_path, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            if not line.strip():
                continue

            parts = line.split('\t')

            if len(parts) == 3:
                sentences_1.append(parts[0])
                sentences_2.append(parts[1])
                gold_preds.append(int(parts[2]))

    test_data_x_1 = vectorizer.vectorize(sentences_1)
    test_data_x_2 = vectorizer.vectorize(sentences_2)

    reference_vectorizer = ReferenceVectorizer.from_vocab_file(vocab_path, 25, True)
    reference_model_trainer = ReferenceModelTrainer(25, True, 32, 32, 0.2, 512, 10)
    reference_model = reference_model_trainer.get_model(reference_vectorizer.max_id)
    reference_model.load_weights(model_path)

    print(reference_model.summary())

    preds = list(reference_model.predict([test_data_x_1, test_data_x_2], verbose=1).ravel())

    tp_cnt = 0
    fp_cnt = 0
    tn_cnt = 0
    fn_cnt = 0

    for s1, s2, pred, gold_pred in zip(sentences_1, sentences_2, preds, gold_preds):
        if pred > 0.5:
            if gold_pred == 1:
                tp_cnt += 1
            else:
                fp_cnt += 1
                print(f'FP: {s1}, {s2}, {pred}')
        else:
            if gold_pred == 0:
                tn_cnt += 1
            else:
                fn_cnt += 1
                print(f'FN: {s1}, {s2}, {pred}')

    precision = tp_cnt / (tp_cnt + fp_cnt)
    recall = tp_cnt / (tp_cnt + fn_cnt)

    print(f'TP: {tp_cnt}, FP: {fp_cnt}, TN: {tn_cnt}, FN: {fn_cnt}, Precision: {precision}, Recall: {recall}')

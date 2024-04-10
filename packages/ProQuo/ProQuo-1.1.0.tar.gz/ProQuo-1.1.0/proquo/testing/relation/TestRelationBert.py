import tensorflow as tf
from proquo.model.relation.RelationVectorizerBert import RelationVectorizerBert
import transformers


def test(test_file_path, tokenizer_folder_path, model_folder_path):
    examples = []
    gold_preds = []

    with open(test_file_path, 'r', encoding='utf-8') as input_file:
        for line in input_file:

            if not line.strip():
                continue

            parts = line.split('\t')

            if len(parts) == 2:
                examples.append(parts[0])
                gold_preds.append(int(parts[1]))

    vectorizer = RelationVectorizerBert.from_saved(200, tokenizer_folder_path, True)

    test_data = vectorizer.vectorize(examples)
    model = transformers.TFBertForSequenceClassification.from_pretrained(model_folder_path, num_labels=2)
    prediction = model.predict(test_data)
    prediction_logits = prediction.logits
    probs = tf.nn.softmax(prediction_logits, axis=1).numpy()

    preds = [row[1] for row in probs]

    tp_cnt = 0
    fp_cnt = 0
    tn_cnt = 0
    fn_cnt = 0

    for example, pred, gold_pred in zip(examples, preds, gold_preds):

        if pred > 0.5:
            if gold_pred == 1:
                tp_cnt += 1
            else:
                fp_cnt += 1
                print(f'FP: {example}, {pred}')
        else:
            if gold_pred == 0:
                tn_cnt += 1
            else:
                fn_cnt += 1
                print(f'FN: {example}, {pred}')

    precision = 0

    if tp_cnt + fp_cnt > 0:
        precision = tp_cnt / (tp_cnt + fp_cnt)

    recall = tp_cnt / (tp_cnt + fn_cnt)

    f_score = 0
    if precision + recall > 0:
        f_score = (2 * precision * recall) / (precision + recall)

    print(f'TP: {tp_cnt}, FP: {fp_cnt}, TN: {tn_cnt}, FN: {fn_cnt}, Precision: {precision}, Recall: {recall},'
          f' F-Score: {f_score}')

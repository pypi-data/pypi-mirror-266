import tensorflow as tf
import transformers
from proquo.model.linking.LinkingVectorizer import LinkingVectorizer


def test(input_path, tokenizer_path, model_path, lower_case):
    names = []
    examples = []
    gold_preds = []
    quotes = []

    with open(input_path, 'r', encoding='utf-8') as input_file:
        for line in input_file:

            if not line.strip():
                continue

            parts = line.strip().split('\t')

            if len(parts) >= 3:
                examples.append((parts[0], parts[1]))
                gold_preds.append(int(parts[2]))

                if len(parts) >= 6:
                    names.append(parts[3])
                    quotes.append(f'{parts[4]} - {parts[5]}')
                else:
                    names.append('NN')
                    quotes.append('NN')

    link_bert_vectorizer = LinkingVectorizer.from_saved(512, tokenizer_path, lower_case)
    link_bert_model = transformers.TFBertForSequenceClassification.from_pretrained(model_path, num_labels=2)

    test_data = link_bert_vectorizer.vectorize(examples)

    prediction = link_bert_model.predict(test_data)
    prediction_logits = prediction.logits
    probs = tf.nn.softmax(prediction_logits, axis=1).numpy()
    preds = [row[1] for row in probs]

    tp_cnt = 0
    fp_cnt = 0
    tn_cnt = 0
    fn_cnt = 0

    for name, example, quote, pred, gold_pred in zip(names, examples, quotes, preds, gold_preds):

        if pred > 0.5:
            if gold_pred == 1:
                tp_cnt += 1
            else:
                fp_cnt += 1
                print(f'FP: {example}, {pred}, {name}, {quote}')
        else:
            if gold_pred == 0:
                tn_cnt += 1
            else:
                fn_cnt += 1
                print(f'FN: {example}, {pred}, {name}, {quote}')

    precision = tp_cnt / (tp_cnt + fp_cnt)
    recall = tp_cnt / (tp_cnt + fn_cnt)

    f_score = 0
    if precision + recall > 0:
        f_score = (2 * precision * recall) / (precision + recall)

    print(f'TP: {tp_cnt}, FP: {fp_cnt}, TN: {tn_cnt}, FN: {fn_cnt}, Precision: {precision}, Recall: {recall},'
          f' F-Score: {f_score}')

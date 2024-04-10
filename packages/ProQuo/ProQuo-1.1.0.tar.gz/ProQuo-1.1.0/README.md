# Readme
`ProQuo` and `ProQuoLM` are a tools for the detection of short quotations (<= 4 words) between two texts, a source text and
a target text. The target text is the text quoting the source text. Quotations in the target text need to be clearly
marked with quotations marks. For more information, see below.

## Overview
The main purpose of this tool is to use the pretrained models for the detection of short quotations.
Both approaches, `ProQuo` and `ProQuoLM` are separate. In our evaluation (see citation below) we found both approaches
to perform at the same level while `ProQuoLm` is less complex as it is mainly a fine-tuned language model.
The library also supports training and testing of custom models for reference classification, relation classification
and linking classification.

**Note**: `ProQuoLM` is easier to use, faster, better documented, better maintained, better tested and the recommended
approach to use.

## Quotation marks
By default, the 'best', i.e. most common combination of opening and closing quotation mark in the specific text is used.
The following combinations are automatically tried:

1. " and "
2. „ and “
3. „ and "
4. “ and “
5. » and «
6. « and »
7. ‘ and ’

If this is not the desired behaviour, quotations marks can be manually defined, using the command line options
`--open-quote` and `--close-quote` to define which opening and closing quotation marks to use.

## Pretrained models and training data

The pretrained models and training data are made available and can be downloaded from [here](https://scm.cms.hu-berlin.de/schluesselstellen/proquodata).

For `ProQuoLm`, we also provide a model on [Hugging Face](https://huggingface.co/Fredr0id/proquolm). This is used by default.

## Installation

### From PyPi

**Note**: Both tools are part of the same PyPi package. So the following command installs both.

~~~
pip install ProQuo
~~~

### From source
Checkout this repository and then run:

~~~
python -m pip install .
~~~

This installs `ProQuo` and all dependencies except `tensorflow` which needs to be installed manually depending on
the individual needs, see [Tensorflow installation](https://www.tensorflow.org/install). The latest version that was
tested is 2.14.1.

For `RelationModelLstmTrainer`, `tensorflow-text` is needed. `RelationModelLstmTrainer` should normally not be needed as
`RelationModelBertTrainer` performs better and is the default in the pipeline.

## Usage
There are two ways to use the tool: in code and from the command line. Both are described in the following sections.

### Quotation detection
There are two approaches which can be used for quotation detection: A specialized pipeline and a general language model based approach.
To run the (recommended) language model approach with the default model, use the following command:

~~~
proquolm compare
path_to_source_text
path_to_target_text
--text
--output-type text
~~~

To run the specialized pipeline, use the following command:

~~~
proquo compare
path_to_source_text
path_to_target_text
path_to_the_reference_vocab_file
path_to_the_reference_model_file
path_to_the_relation_tokenizer_folder
path_to_the_relation_model_folder
--text
--output-type text
~~~

`--output-type text` prints the results to the command line. To save the results to a file, use `--output-type csv` or
`--output-type json`. `--text` includes the quotation text in the output.

The output will look something like this:
~~~
10	15	500	505	quote	quote
1000	1016	20	36	some other quote	some other quote
~~~
The first two numbers are the character start and end positions in the source text and the other two numbers are the
character start and end positions in the target text.

#### Note
There are a number of command line arguments to configure the output format, for example, to save the result to a csv
file. For all options, use the following commands:

~~~
proquo compare -h
~~~

~~~
proquolm compare -h
~~~

### Training and testing a model

#### Reference model
The following command can be used to train a reference model:

~~~
proquo train reference
path_to_train_set.txt
path_to_val_set.txt
path_to_the_output_folder
~~~

`path_to_train_set.txt` and `path_to_val_set.txt` contain one example per line in the form of two strings and a class,
tab separated, for example:

~~~
S. 47   S. 35	1
63	DKV III, 17	0
~~~

To test the model, run:

~~~
proquo test reference
path_to_test_set.txt
path_to_the_reference_vocab_file
path_to_the_reference_model_file
~~~

#### Relation model
The following command can be used to train a bert relation model:

~~~
proquo train relation
path_to_train_set.txt
path_to_val_set.txt
path_to_the_output_folder
--arch
"bert"
~~~

`path_to_train_set.txt` and `path_to_val_set.txt` contain one example per line in the form of a string and a class,
tab separated, for example:

~~~
some context, some text <Q> some quote </Q> ( <OREF> ). some more text ( <REF> )   0
~~~

To test the model, run:

~~~
proquo test relation bert
path_to_test_set.txt
path_to_the_tokenizer_folder
path_to_the_model_folder
~~~

#### Linking model
The following command can be used to train a linking model:

~~~
proquolm train
path_to_train_set.txt
path_to_val_set.txt
path_to_the_output_folder
~~~

`path_to_train_set.txt` and `path_to_val_set.txt` contain one example per line in the form of two strings and a class,
tab separated, for example:

~~~
some text for context, <S> candidate </S> some more text  start of second text, some context <T> candidate </T> text text text  0
~~~

To test the model, run:

~~~
proquolm test
path_to_test_set.txt
path_to_the_tokenizer_folder
path_to_the_model_folder
~~~

## Citation
If you use ProQuo or ProQuoLM or base your work on our code, please cite our paper:
~~~
@article{arnold2023,
  author = {Frederik Arnold, Robert Jäschke},
  title = {A Novel Approach for Identification and Linking of Short Quotations in Scholarly Texts and Literary Works},
  volume = {2},
  year = {2023},
  url = {https://jcls.io/article/id/3590/},
  issue = {1},
  doi = {10.48694/jcls.3590},
  month = {1},
  publisher={Universitäts- und Landesbibliothek Darmstadt},
  journal = {Journal of Computational Literary Studies}
}
~~~
#!/usr/bin/env python
import sys
import os
import os.path
from scipy.stats import sem
import numpy as np
from ast import literal_eval

def f1(predictions, gold):
    """
    F1 (a.k.a. DICE) operating on two lists of offsets (e.g., character).
    >>> assert f1([0, 1, 4, 5], [0, 1, 6]) == 0.5714285714285714
    :param predictions: a list of predicted offsets
    :param gold: a list of offsets serving as the ground truth
    :return: a score between 0 and 1
    """
    if len(gold) == 0:
        return 1 if len(predictions)==0 else 0
    nom = 2*len(set(predictions).intersection(set(gold)))
    denom = len(set(predictions))+len(set(gold))
    return nom/denom


def evaluate(pred, gold):
    """
    Based on https://github.com/felipebravom/EmoInt/blob/master/codalab/scoring_program/evaluation.py
    :param pred: file with predictions
    :param gold: file with ground truth
    :return:
    """
    # read the predictions
    f = open(pred, "rb")
    pred_lines = f.readlines()
    f.close()
    # read the ground truth
    f = open(gold, "rb")
    gold_lines = f.readlines()
    f.close()

    # only when the same number of lines exists
    if (len(pred_lines) == len(gold_lines)):
        data_dic = {}
        for line in gold_lines:
            parts = line.split('\t')
            if len(parts) == 2:
                data_dic[int(parts[0])] = [literal_eval(parts[1])]
            else:
                sys.exit('Format problem.')

        for line in pred_lines:
            parts = line.split('\t')
            if len(parts) == 2:
                if int(parts[0]) in data_dic:
                    try:
                        data_dic[int(parts[0])].append(literal_eval(parts[1]))
                    except ValueError:
                        # Invalid predictions are replaced by a default value
                        data_dic[int(parts[0])].append([])
                else:
                    sys.exit('Invalid text id.')
            else:
                sys.exit('Format problem.')

        # lists storing gold and prediction scores
        scores = []
        for id in data_dic:
            if len(data_dic[id]) == 2:
                gold_spans = data_dic[id][0]
                pred_spans = data_dic[id][1]
                scores.append(f1(pred_spans, gold_spans))
            else:
                sys.exit('Repeated id in test data.')

        return (np.mean(scores), sem(scores))

    else:
        sys.exit('Predictions and gold data have different number of lines.')


def main(argv):
    # https://github.com/Tivix/competition-examples/blob/master/compute_pi/program/evaluate.py
    # as per the metadata file, input and output directories are the arguments
    [input_dir, output_dir] = argv

    # unzipped submission data is always in the 'res' subdirectory
    # https://github.com/codalab/codalab-competitions/wiki/User_Building-a-Scoring-Program-for-a-Competition#directory-structure-for-submissions
    truth_path = os.path.join(input_dir, 'ref', 'spans-gold.txt')
    submission_path = os.path.join(input_dir, 'res', 'spans-pred.txt')
    if not os.path.exists(submission_path):
        sys.exit('Could not find submission file {0}'.format(submission_path))
    scores = evaluate(submission_path, truth_path)

    # the scores for the leaderboard must be in a file named "scores.txt"
    # https://github.com/codalab/codalab-competitions/wiki/User_Building-a-Scoring-Program-for-a-Competition#directory-structure-for-submissions
    output_file = open(os.path.join(output_dir, 'scores.txt'), "w")
    output_file.write("spans_F1:{0}\n".format(scores[0]))
    output_file.close()


if __name__ == "__main__":
    main(sys.argv[1:])
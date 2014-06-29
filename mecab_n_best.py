# -*- coding: utf-8 -*-

import MeCab
try:
    import cPickle as pkl
except:
    import pickle as pkl



class MeCabNBest:

    @classmethod
    def serialize(cls, matrix_path, serialize_path):
        trans_costs_and_context_n = cls._read_trans_costs(matrix_path)

        with open(serialize_path, "w") as serialize_f:
            pkl.dump(trans_costs_and_context_n, serialize_f)


    # (i, j)'s index is transfered to i * context_n + j
    @classmethod
    def _read_trans_costs(cls, matrix_path):
        matrix_f = open(matrix_path, "r")

        first_line = matrix_f.readline().rstrip("\n\r")
        context_n = int(first_line.split(" ")[0])

        trans_costs = range(context_n ** 2)
        for i in xrange(context_n):
            for j in xrange(context_n):
                line = matrix_f.readline().rstrip("\n\r")
                cost = int(line.split(" ")[2])
                trans_costs[i * context_n + j] = cost

        return [trans_costs, context_n]


    def __init__(self, serialized_path):
        with open(serialized_path, "r") as serialized_f:
            self.trans_costs, self.context_n = pkl.load(serialized_f)

        self.tagger = MeCab.Tagger("-Odump")


    # sentence's type must be String not Unicode.
    def parseNBest(self, sentence, n_best):
        parsed_string = self.tagger.parseNBest(n_best, sentence).decode('utf-8').rstrip(u"\n\r")
        sentences = self._partition_n_best(parsed_string)

        transed_sentences = []
        for sentence in sentences:
            transed_sentences.append(self._analyse_sentence(sentence))

        return transed_sentences


    def _partition_n_best(self, parsed_string):
        parsed_lines = parsed_string.split(u"\n")

        n_best_sentences = []
        sentence = []
        for line in parsed_lines:
            columns = line.split(u" ")
            if columns[1] == u"EOS" and columns[2].find(u"EOS") != -1:
                sentence.append(line)
                n_best_sentences.append(sentence)
                sentence = []
            else:
                sentence.append(line)

        return n_best_sentences


    # sentence is list of morphological line of MeCab
    def _analyse_sentence(self, sentence):
        transed_sent = []
        cost = 0

        bos_morph = sentence[0]
        bos_columns = bos_morph.split(u" ")
        left_context = int(bos_columns[6])
        cost += int(bos_columns[14])

        for morph in sentence[1:-1]:
            morph_columns = morph.split(u" ")
            right_context = int(morph_columns[5])
            cost += self.get_trans_cost(left_context, right_context)
            left_context = int(morph_columns[6])
            cost += int(morph_columns[14])

            transed_sent.append(morph_columns[1] + u"\t" + morph_columns[2])

        eos_morph = sentence[-1]
        eos_columns = eos_morph.split(u" ")
        right_context = int(eos_columns[6])
        cost += self.get_trans_cost(left_context, right_context)
        cost += int(eos_columns[14])

        return {"sent": transed_sent, "cost": cost}


    def get_trans_cost(self, left_context, right_context):
        return self.trans_costs[left_context * self.context_n + right_context]

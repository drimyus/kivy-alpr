import json
import os

END_TWO_ALPHA = "end_2_alpha"
END_THREE_ALPHA = "end_3_alpha"

FST_ALPHA = "fst_alpha"
FST_DIGIT = "fst_digit"


rules = {
    "8": {
        FST_ALPHA: "AAX11XAA",
        FST_DIGIT: "11A111AA"
    },
    "7": {
        FST_ALPHA: "AAX1XAA",
        FST_DIGIT: "11A11AA"
    }
}


class RegularUtils:
    """
    ..................................
    e.g.    "AAA123BC"
    e.g.    "AA123BCD"
    e.g.    "52L155FG"

    e.g.    "AAA12BC"
    e.g.    "AA12ABC"
    e.g.    "52L38FG"
    .................................."""

    def __init__(self, candidates):
        self.candidates = candidates

    def determine(self):
        avg_len, rate = self.determine_length(candidates=self.candidates)
        print("average length: {},   confidence: {}".format(avg_len, round(rate * 100, 2)))
        mode, rate = self.determine_fst_character(candidates=self.candidates)
        print("first character: {},   confidence: {}".format(mode, round(rate * 100, 2)))

        if avg_len in [7, 8]:
            return self.clear_plate(avg_len, mode, self.candidates)
        else:
            return ""

    @staticmethod
    def determine_fst_character(candidates):
        # avg_score
        n_alpha = 0
        n_digit = 0
        for candidate in candidates:
            plate = candidate['plate']
            if plate[:2].isalpha():
                n_alpha += 1
            elif plate[:2].isdigit():
                n_digit += 1
            elif plate[2].isdigit() and plate[3].isalpha() and plate[4:6].isalpha():
                n_digit += 1

        if n_alpha > n_digit:
            return FST_ALPHA, n_alpha / len(candidates)
        else:
            return FST_DIGIT, n_digit / len(candidates)

    def determine_length(self, candidates):
        # avg_score
        avg_score = 0.0
        for candidate in candidates:
            confidence = candidate['confidence']
            avg_score += confidence
        avg_score /= len(candidates)
        avg_len = 0.0
        for candidate in self.candidates:
            plate = candidate['plate']
            print(plate)
            confidence = candidate['confidence']
            avg_len += len(plate) * confidence
        avg_len /= avg_score * len(candidates)
        avg_len = round(avg_len)

        new_candis = [candidate for candidate in candidates if len(candidate['plate']) == avg_len]
        return avg_len, len(new_candis) / len(candidates)

    @staticmethod
    def clear_plate(avg_len, fst_mode, candidates):
        new_candis = []
        for candidate in candidates:
            plate = candidate['plate']
            if len(plate) == avg_len:
                if fst_mode == FST_ALPHA and plate[:2].isalpha():
                    new_candis.append(plate)
                elif fst_mode == FST_DIGIT and plate[:2].isdigit():
                    new_candis.append(plate)

        rule = rules[str(avg_len)][fst_mode]

        buf_list = []
        for i in range(avg_len):
            buf_list.append([])

        for plate in new_candis:
            for i in range(avg_len):
                if rule[i] == "X":
                    buf_list[i].append(plate[i])
                elif plate[i].isalpha() and rule[i].isalpha():
                    buf_list[i].append(plate[i])
                elif plate[i].isdigit() and rule[i].isdigit():
                    buf_list[i].append(plate[i])

        res = ""
        from collections import Counter

        for i in range(avg_len):
            most_common, num_most_common = Counter(buf_list[i]).most_common(1)[0]
            res += most_common

        return res


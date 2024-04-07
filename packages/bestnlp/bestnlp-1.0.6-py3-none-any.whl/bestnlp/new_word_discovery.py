import random
import math
import pandas as pd
import jieba.posseg as jieba
import re
import os
import bestnlp.utils as utils

_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))


class NewWordDiscovery():

    def __init__(self):
        self.jieba_dict = self._read_jieba_dict()


    def _read_jieba_dict(self):
        di = dict()
        with open(_get_module_path("dict.txt"), "r") as f:
            for line in f:
                temp = line.strip().split()
                word, freq = temp[0], int(temp[1])
                di[word] = freq
        return di


    def calculate_idf(self, idf_list):
        idf_di = dict()
        for sentence_word_set in idf_list:
            for word in sentence_word_set:
                if word not in idf_di:
                    idf_di[word] = 0
                idf_di[word] += 1
        l = len(idf_list)
        for word in idf_di:
            idf_di[word] = math.log(l/(idf_di[word] + 1))
        return idf_di


    def get_filter_word(self, freq_di, threshold=500):
        jieba_dict = self._read_jieba_dict()
        filter_words = set()
        for word in freq_di:
            word = "".join(word)
            if jieba_dict.get(word, 0) > threshold:
                filter_words.add(word)
        return filter_words


    def calculate_frequency(self, sentences, k_min=1, k_max=4, mode="word"):
        word_num = 0
        freq_di = dict()
        idf_list = []
        print(len(sentences))
        for ii, sentence in enumerate(sentences):
            if ii % 100000 == 0:
                print(ii)
            sentence_set = set()
            if mode == "word":
                res = jieba.lcut(sentence)
                words = [elem.word for elem in res]
                flags = [elem.flag for elem in res]
            elif mode == "char":
                words = list(sentence)
                flags = ["n" for i in words]
            l = len(words)
            word_num = word_num + l
            for i in range(l):
                sentence_set.add(words[i])
                for j in [1] + list(range(k_min, k_max + 1 if i + k_max + 1 <= l else l - i)):
                    word = tuple(words[i: i + j])
                    if word not in freq_di:
                        freq_di[word] = {"freq": 0, "left": dict(), "right": dict(), "pos": []}
                    freq_di[word]["freq"] += 1
                    left_tmp = words[i - 1] if i - 1 >= 0 else ""
                    freq_di[word]["left"][left_tmp] = freq_di[word]["left"].get(left_tmp, 0) + 1
                    right_tmp = words[i + j] if i + j < l else ""
                    freq_di[word]["right"][right_tmp] = freq_di[word]["right"].get(right_tmp, 0) + 1
                    freq_di[word]["pos"] = flags[i: i + j]
            idf_list.append(sentence_set)
        idf_di = self.calculate_idf(idf_list)
        return freq_di, word_num, idf_di


    def ami(self, freq_di, word_num, threshold=0, percent=10):
        di = dict()
        for word in freq_di:
            if len(word) > 1:
                val = freq_di[word]["freq"]/word_num
                for single_word in word:
                    val = val / (freq_di[tuple([single_word])]["freq"]/word_num)
                val = math.log2(val)
                #val *= freq_di[word]["freq"]/word_num/len(word)
                val /= len(word)
                if val > threshold:
                    di[word] = val
        di = sorted(di.items(), key=lambda x: x[1], reverse=True)
        di = di[:int(len(freq_di) * percent / 100)]
        di = {key: value for key, value in di}
        return di


    def structure(self, freq_di, threshold=1.9):
        di = dict()
        for word in freq_di:
            if len(word) > 1:
                val = 1
                flags = freq_di[word]["pos"]
                for flag in flags:
                    if flag.startswith("n"):
                        val += 1
                    elif flag.startswith("u"):
                        val *= 0.5
                    elif flag.startswith("w"):
                        val *= 0.01
                if not flags[-1].startswith("n"):
                    val *= 0.1

                if val > threshold:
                    di[word] = val
        return di


    def entropy(self, di):
       num = sum(di.values())
       res = 0
       for word, freq in di.items():
           if word == "":
               res -= freq/num * math.log2(freq/num)
           else:
               res -= freq/num * math.log2(freq/num)
       return res


    def L_entropy(self, freq_di, threshold=0, percent=10):
        di = dict()
        for word in freq_di:
            if len(word) > 1:
                l_e = self.entropy(freq_di[word]["left"])
                r_e = self.entropy(freq_di[word]["right"])
                final_entropy = min(l_e, r_e) * math.log(max(l_e, r_e) + math.e, math.e)
                if final_entropy > threshold:
                    di[word] = [final_entropy, l_e, r_e]
        di = sorted(di.items(), key=lambda x: x[1][0], reverse=True)
        di = di[:int(len(freq_di) * percent / 100)]
        di = {key: value for key, value in di}
        return di


    def extract_keyword(self, filename, sentences=None, k_min=2, k_max=5, mode="word", min_freq=5, entropy_percent=20, ami_percent=20, write_mode=True, write_name="details.csv"):
        if sentences is None:
            sentences = utils.read_txt(filename)
        write_df = {"word":[], "ami":[], "entropy":[], "l_e":[], "r_e":[], "pos":[], "freq":[], "idf":[], "score":[]}
        freq_di, word_num, idf_di = self.calculate_frequency(sentences, k_min, k_max, mode)
        entropy_di = self.L_entropy(freq_di, percent=entropy_percent)
        print(len(entropy_di))
        ami_di = self.ami(freq_di, word_num, percent=ami_percent)
        print(len(ami_di))
        structure_di = self.structure(freq_di)
        filter_words = self.get_filter_word(freq_di)
        final_di = dict()
        for name in entropy_di:
            complete_name = "".join(name)
            if (complete_name not in filter_words) and (name in ami_di) and (name in structure_di) and (freq_di[name]["freq"] >= min_freq):
                idf = [idf_di[w] for w in name]
                idf = sum(idf)/len(idf)
                final_di[name] = entropy_di[name][0] * ami_di[name] * structure_di[name] * idf * math.sqrt(freq_di[name]["freq"])
                write_df["word"].append(complete_name)
                write_df["ami"].append(ami_di[name])
                write_df["entropy"].append(entropy_di[name][0])
                write_df["l_e"].append(entropy_di[name][1])
                write_df["r_e"].append(entropy_di[name][2])
                write_df["pos"].append("_".join(freq_di[name]["pos"]))
                write_df["freq"].append(freq_di[name]["freq"])
                write_df["idf"].append(idf)
                write_df["score"].append(final_di[name])
        if write_mode:
            write_df = pd.DataFrame.from_dict(write_df).sort_values("score", ascending=False)
            write_df.to_csv(write_name)




# nwd = NewWordDiscovery()
# nwd.extract_keyword("三体.txt", k_min=2, k_max=7, mode="char", min_freq=7, entropy_percent=20, ami_percent=20, write_name="char.csv", write_mode=True)











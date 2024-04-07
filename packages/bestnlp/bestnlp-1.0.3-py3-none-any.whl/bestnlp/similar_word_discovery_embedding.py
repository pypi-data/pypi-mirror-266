# import jieba
# import numpy as np
# import gensim
# import utils
# from scipy.spatial.distance import cosine
# from collections import OrderedDict
#
#
#
# class SimilarWordDiscovery():
#
#     def is_similar(self, elem1, elem2, wv):
#         common_char = ["的"]
#         elem1_set, elem2_set = set(elem1), set(elem2)
#         for char in common_char:
#             elem1_set.add(char)
#             elem2_set.add(char)
#         cut1 = set(jieba.lcut(elem1))
#         cut2 = set(jieba.lcut(elem2))
#         cut1.discard(" ")
#         cut2.discard(" ")
#         elem1_set.discard(" ")
#         elem2_set.discard(" ")
#         non_match1 = set()
#         non_match2 = set()
#
#         if utils.is_same_set(cut1, cut2) or utils.is_same_set(elem1_set, elem2_set):
#             return True
#
#         arr1, arr2 = np.zeros(100), np.zeros(100)
#         count1, count2 = 0, 0
#         for c in cut1:
#             if c in wv:
#                 arr1 = np.add(arr1, wv[c])
#                 count1 += 1
#             else:
#                 non_match1.add(c)
#         for c in cut2:
#             if c in wv:
#                 arr2 = np.add(arr2, wv[c])
#                 count2 += 1
#             else:
#                 non_match2.add(c)
#         if (count1 == 0 and count2 != 0) or (count1 != 0 and count2 == 0):
#             return False
#         if count1 == 0 and count2 == 0:
#             return utils.is_same_set(non_match1, non_match2)
#         if count1 != 0 and count2 != 0:
#             if cosine(arr1 / count1, arr2 / count2) < 0.08:
#                 return utils.is_same_set(non_match1, non_match2)
#             else:
#                 return False
#
#
#     def get_vec(self, word, wv):
#         words = jieba.lcut(word)
#         vector = np.zeros((100,), dtype='float32')
#         count = 0
#         for word in words:
#             if word in wv:
#                 vector += wv[word]
#                 count += 1
#         if count == 0: return None
#         return vector / count
#
#
#     def get_similar_words(self, target_words, candidate_words=None, threshold=0.6, k=3):
#         tw = list(OrderedDict.fromkeys(target_words))
#         cw = list(OrderedDict.fromkeys(candidate_words)) if candidate_words is not None else None
#         wv = gensim.models.KeyedVectors.load(r'embedding.bin', mmap='r')
#         res = []
#         for word in tw:
#             if cw is None or len(cw) == 0:
#                 if word not in wv:
#                     vec = self.get_vec(word, wv)
#                     if vec is not None:
#                         for elem in wv.most_similar(positive=vec):
#                             if elem[1] > threshold:
#                                 res.append((word, elem[0], "extra_word", elem[1]))
#                 else:
#                     for elem in wv.most_similar(word, k):
#                         if elem[1] > threshold:
#                             res.append((word, elem[0], "extra_word"))
#             else:
#                 # word_vec = get_vec(word, wv)
#                 # if word_vec:
#                 #     for cw in candidate_words:
#                 #         cw_vec = get_vec(cw, wv)
#                 #         if cw_vec:
#                 #             cos = cosine(word_vec, cw_vec)
#                 #             if cos < 1-threshold: res.append((word, cw, "original_word", cos))
#                 for c in cw:
#                     if c == word: continue
#                     if self.is_similar(word, c, wv):
#                         res.append((word, c, "original_word"))
#         return res


# swd = SimilarWordDiscovery()
# #target_words = ["新闻", "新闻联播是什么", "小鸡", "达观数据", "母鸡", "新闻数据", "什么是新闻联播"]
# with open("words", "r") as f:
#     all_lines = []
#     for line in f:
#         line = line.strip()
#         all_lines.append(line)
#
# for line in all_lines:
#     res = swd.get_similar_words([line])
#     print(line, res)






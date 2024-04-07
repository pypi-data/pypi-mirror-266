# import pandas as pd
import bestnlp.utils as utils


class SimilarWordDiscovery():
    """
    search dataframe
    time  keyword  user_id

    click dataframe
    time  keyword  user_id  item_id
    """
    def process_search(self, search_df, threshold=10, time_name="time", user_id_name="user_id", keyword_name="keyword",):
        #搜索行为
        di = dict()
        df = search_df.sort_values(time_name)
        df = df.groupby(user_id_name)[keyword_name].agg(list).reset_index()
        for keyword in df[keyword_name].tolist():
            if len(keyword) >= 2:
                for i in range(len(keyword) - 1):
                    if keyword[i] == keyword[i + 1]: continue
                    key = frozenset([keyword[i], keyword[i + 1]])
                    di[key] = di.get(key, 0) + 1
        res = dict()
        for key, value in di.items():
            if value >= threshold:
                res[key] = value
        return res


    def process_click(self, click_df, threshold=10, time_name="time", user_id_name="user_id", keyword_name="keyword", item_id_name="item_id"):
        #点击行为
        #同一个商品点击等行为对应的搜索词
        act_df = click_df.sort_values(time_name).drop_duplicates([user_id_name, keyword_name, item_id_name])
        df = act_df.groupby(item_id_name)[keyword_name].agg(list).reset_index()
        di = dict()
        for keyword in df[keyword_name].tolist():
            if len(keyword) >= 2:
                for key1 in keyword:
                    for key2 in keyword:
                        if key1 == key2: continue
                        key = frozenset([key1, key2])
                        di[key] = di.get(key, 0) + 1
        res = dict()
        for key, value in di.items():
            if value >= threshold:
                res[key] = value
        return res


    def find_similar(self, search_df, click_df=None, search_weight=1, click_weight=1, both=False, search_threshod=10, click_threshold=10, threshold=20, max_num=1000, time_name="time", user_id_name="user_id", keyword_name="keyword", item_id_name="item_id"):
        search_res = self.process_search(search_df, search_threshod, time_name=time_name, user_id_name=user_id_name, keyword_name=keyword_name) if search_df is not None else dict()
        click_res = self.process_click(click_df, click_threshold, time_name=time_name, user_id_name=user_id_name, keyword_name=keyword_name, item_id_name=item_id_name) if click_df is not None else dict()
        res = dict()
        if both:
            keys = set(search_res.keys()).intersection(set(click_res.keys()))
        else:
            keys = set(search_res.keys()).union(set(click_res.keys()))
        for key in keys:
            score = search_res.get(key, 0) * search_weight + click_res.get(key, 0) * click_weight
            if score >= threshold:
                res[key] = score
        res = list(sorted(res.items(), key=lambda x: x[1], reverse=True))
        res = res[:max_num if len(res) > max_num else len(res)]
        return res


# df = pd.read_excel("df_details.xlsx")
# search_df = df[df["action_type"]=="search"][["timestamp", "query", "userid"]]
# search_df.rename(columns={"timestamp":"time", "query":"keyword", "userid":"user_id"}, inplace=True)
# click_df = df[df["action_type"]=="click"][["timestamp", "query", "userid", "itemid"]]
# click_df.rename(columns={"timestamp":"time", "query":"keyword", "userid":"user_id", "itemid":"item_id"}, inplace=True)
# swd = SimilarWordDiscovery()
# res = swd.find_similar(search_df, click_df, threshold=100)
# print(res)
# print(len(res))
# for elem in res:
#     print(elem)



# search_df = pd.read_excel("search.xlsx")
# click_df = pd.read_excel("click.xlsx")
# print(search_df)
# print(click_df)
#
# search_df.rename(columns={"search_term":"keyword", "distinct_id":"user_id"}, inplace=True)
# click_df["keyword"] = click_df["url"].apply(lambda x: str(x)[6:])
# click_df.rename(columns={"distinct_id":"user_id", "article_number":"item_id"}, inplace=True)
#
# swd = SimilarWordDiscovery()
# res = swd.find_similar(search_df, click_df, threshold=100)
# print(res)
# print(len(res))
# for elem in res:
#     print(elem)






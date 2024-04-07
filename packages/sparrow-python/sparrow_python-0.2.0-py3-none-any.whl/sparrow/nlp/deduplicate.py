import abc
import pandas as pd
# from ..extras.packages import is_nltk_available, is_rouge_available, is_jieba_available, is_levenshtein_available
from sparrow.extras.packages import is_nltk_available, is_rouge_available, is_jieba_available, is_levenshtein_available

if is_jieba_available():
    import jieba

if is_levenshtein_available():
    from Levenshtein import ratio as edit_distance_ratio

if is_rouge_available():
    from rouge_chinese import Rouge

if is_nltk_available():
    from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu


class Similarity:

    def __init__(self, use_jieba=False):
        self.data = []
        if use_jieba:
            assert is_jieba_available(), "jieba is not available, please install it with: `pip install jieba`"

    def load_data(self, filename: str, target_col: str = 'data'):
        if filename.endswith('.csv'):
            df = pd.read_csv(filename)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filename)
        else:
            raise Exception(f"{filename} is not a csv or excel file")
        df[target_col] = df[target_col].astype(str)
        df.drop_duplicates(subset=[target_col], inplace=True)
        self.data = df[target_col].to_list()

    def deduplicate(self, chunk_size: int = 200, save_to_file: str = None, threshold=0.7, **kwargs):
        # 将原始数据列表分割为每份chunk_size个的小数据集，然后对每个数据集进行去重，最后合并
        sub_data_list = []
        for i in range(0, len(self.data), chunk_size):
            sub_data_list.append(self.data[i:i + chunk_size])

        # 对每个小数据集进行去重，去重逻辑是利用 is_similar 方法判断是否相似
        new_data_list = [self.deduplicate_sub_data(sub_data, threshold=threshold, **kwargs) for sub_data in sub_data_list]

        new_data = [i for sub_data in new_data_list for i in sub_data]
        if save_to_file:
            df = pd.DataFrame({'data': new_data})
            if save_to_file.endswith('.csv'):
                df.to_csv(save_to_file)
            elif save_to_file.endswith('.xlsx'):
                df.to_excel(save_to_file)
            else:
                raise Exception(f"{save_to_file} is not a csv or excel file")
        return new_data

    def deduplicate_sub_data(self, sub_data: list, threshold=0.7, **kwargs):
        for i in range(len(sub_data)):
            for j in range(i + 1, len(sub_data)):
                if sub_data[i] is None or sub_data[j] is None:
                    continue
                if self.is_similar([sub_data[i]], [sub_data[j]], threshold=threshold, **kwargs)[0]:
                    # print(f"{sub_data[i]} and {sub_data[j]} are similar")
                    sub_data[j] = None

        dedup_sub_data = [i for i in sub_data if i is not None]
        print(f"{len(sub_data)} -> {len(dedup_sub_data)}")
        return dedup_sub_data

    @abc.abstractmethod
    def get_similarity(self, hypothesis_list: list, reference_list: list, use_jieba=False) -> list:
        ...

    def is_similar(self, hypothesis_list: list, reference_list: list, threshold=0.7, **kwargs):
        is_similar_list = []
        for score in self.get_similarity(hypothesis_list, reference_list, **kwargs):
            if score >= threshold:
                is_similar_list.append(1)
            else:
                is_similar_list.append(0)
        return is_similar_list


class RougeSimilarity(Similarity):
    from rouge_chinese import Rouge
    rouge = Rouge()

    def __init__(self, use_jieba=False):
        super().__init__(use_jieba=use_jieba)

    def get_similarity(self, hypothesis_list: list, reference_list: list, use_jieba=False):
        if use_jieba:
            hypothesis = [' '.join(jieba.cut(i.strip())) for i in hypothesis_list]
            reference = [' '.join(jieba.cut(i.strip())) for i in reference_list]
        else:
            # 打散: 将每个字符后面加一个空格
            hypothesis = [' '.join(list(i.strip())) for i in hypothesis_list]
            reference = [' '.join(list(i.strip())) for i in reference_list]
        scores = self.rouge.get_scores(hypothesis, reference)
        return [i['rouge-l']['f'] for i in scores]


class BleuSimilarity(Similarity):
    assert is_nltk_available(), "nltk is not available, please install it with: `pip install nltk`"
    smoothie = SmoothingFunction().method3

    def __init__(self, use_jieba=False):
        super().__init__(use_jieba=use_jieba)

    def get_similarity(self, hypothesis_list: list, reference_list: list, use_jieba=False):
        if use_jieba:
            hypothesis = [list(jieba.cut(i.strip())) for i in hypothesis_list]
            reference = [list(jieba.cut(i.strip())) for i in reference_list]
        else:
            hypothesis = [list(i.strip()) for i in hypothesis_list]
            reference = [list(i.strip()) for i in reference_list]

        scores = [sentence_bleu(reference, hypo, smoothing_function=self.smoothie) for hypo in hypothesis]
        return scores


class EditSimilarity(Similarity):
    assert is_levenshtein_available(), "Levenshtein is not available, please install it with: `pip install levenshtein`"
    def __init__(self):
        super().__init__()

    def get_similarity(self, hypothesis_list: list, reference_list: list, **kwargs):
        assert len(hypothesis_list) == len(reference_list)
        hypothesis = [i.strip() for i in hypothesis_list]
        reference = [i.strip() for i in reference_list]
        scores = [edit_distance_ratio(hypo, ref) for hypo, ref in zip(hypothesis, reference)]
        return scores

if __name__ == "__main__":
    hypothesis = "啦啦啦哈哈哈桌子上有个苹果  "
    reference =  "啦啦啦哈哈哈桌上有一个苹果。"
    edit_simi = EditSimilarity()
    print(edit_simi.get_similarity([hypothesis], [reference]),)

    edit_simi.load_data('./data/测试去重.xlsx', 'data')
    edit_simi.deduplicate(100, save_to_file="./data/edit测试去重后.xlsx", threshold=0.5)
    exit()

    rouge_simi = RougeSimilarity()
    # 一般使用rouge-l: 最长公共子串
    print(rouge_simi.get_similarity([hypothesis], [reference]),)
    bleu_simi = BleuSimilarity()
    print(bleu_simi.get_similarity([hypothesis], [reference]),)

    # simi = BleuSimilarity()
    # simi.load_data('./data/测试去重.xlsx', 'data')
    # simi.deduplicate(50, save_to_file="./data/bleu测试去重后.xlsx", threshold=0.5)

    r_simi = RougeSimilarity()
    r_simi.load_data('./data/测试去重.xlsx', 'data')
    r_simi.deduplicate(50, save_to_file="./data/rouge_测试去重后.xlsx", threshold=0.4)


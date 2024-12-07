from konlpy.tag import Kkma
from collections import Counter
import re

def extract_summary(text, top_n=4):
    kkma = Kkma()

    KOREAN_STOPWORDS = {
        "수", "것", "들", "및", "의", "가", "이", "에", "을", "는", "로", "도", "다", 
        "으로", "그리고", "하지만", "더", "있습니다", "아래", "명이", "일간", "같은", 
        "주제", "명"
    }

    text = re.sub(r'\d+', '', text) 
    text = re.sub(r'[^\w\s]', '', text) 

    nouns = kkma.nouns(text)
    filtered_nouns = [noun for noun in nouns if noun not in KOREAN_STOPWORDS and len(noun) > 1]
    noun_counts = Counter(filtered_nouns)

    keywords = [word for word, freq in noun_counts.most_common(top_n)]
    return " ".join(keywords)


'''
영어까지 있다면:
from konlpy.tag import Kkma
from collections import Counter
import re

def extract_summary_with_english(text, top_n=4):
    kkma = Kkma()

    KOREAN_STOPWORDS = {
        "수", "것", "들", "및", "의", "가", "이", "에", "을", "는", "로", "도", "다", 
        "으로", "그리고", "하지만", "더", "있습니다", "아래", "명이", "일간", "같은", 
        "주제", "명"
    }

    text = re.sub(r'\d+', '', text) 
    text = re.sub(r'[^\w\s]', '', text)

    nouns = kkma.nouns(text)

    english_words = re.findall(r'[a-zA-Z]+', text)

    filtered_nouns = [noun for noun in nouns if noun not in KOREAN_STOPWORDS and len(noun) > 1]

    all_words = filtered_nouns + english_words

    word_counts = Counter(all_words)

    keywords = [word for word, freq in word_counts.most_common(top_n)]
    return " ".join(keywords)

'''

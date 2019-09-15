import pandas as pd
import csv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import json



class NewsIndex():
    def __init__(self, basePath='inputs'):
        nltk.download('vader_lexicon')

        self.sia = SentimentIntensityAnalyzer()

        # stock market lexicon
        stock_lex = pd.read_csv(
            f'{basePath}/lexicon_data/stock_lex.csv')
        stock_lex['sentiment'] = (
            stock_lex['Aff_Score'] + stock_lex['Neg_Score'])/2
        stock_lex = dict(zip(stock_lex.Item, stock_lex.sentiment))
        stock_lex = {k: v for k, v in stock_lex.items()
                     if len(k.split(' ')) == 1}
        stock_lex_scaled = {}
        for k, v in stock_lex.items():
            if v > 0:
                stock_lex_scaled[k] = v / max(stock_lex.values()) * 4
            else:
                stock_lex_scaled[k] = v / min(stock_lex.values()) * -4

        # Loughran and McDonald
        positive = []
        with open(f'{basePath}/lexicon_data/lm_positive.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                positive.append(row[0].strip())

        negative = []
        with open(f'{basePath}/lexicon_data/lm_negative.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                entry = row[0].strip().split(" ")
                if len(entry) > 1:
                    negative.extend(entry)
                else:
                    negative.append(entry[0])

        final_lex = {}
        final_lex.update({word: 5.0 for word in positive})
        final_lex.update({word: -5.0 for word in negative})
        final_lex.update(stock_lex_scaled)
        final_lex.update(self.sia.lexicon)
        self.sia.lexicon = final_lex

    def getIndex(self, text):
        return (self.sia.polarity_scores(text)['compound'])/5


if __name__ == '__main__':
    ni = NewsIndex()
    fp = open('data.json', 'r')
    d = json.load(fp)
    csvFile = open('newsIndex.csv', 'w')
    writer = csv.writer(csvFile)
    writer.writerow(['Date', 'NewsIndex'])
    for i in d:
        i['time'] = i['time'].split('T')[0]
        title = i['title'].encode('ascii', 'ignore').decode("utf-8")
        text = i['text'].encode('ascii', 'ignore').decode("utf-8")
        title_len = len(title.split(' '))
        text_len = len(text.split(' '))
        total_words = title_len + text_len
        i['index'] = (title_len/total_words) * ni.getIndex(title) + \
            (text_len/total_words) * ni.getIndex(text)
        writer.writerow([i['time'], i['index']])
    fp.close()
    csvFile.close()
    fp = open('data.json', 'w')
    json.dump(d, fp)

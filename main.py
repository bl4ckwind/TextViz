from collections import defaultdict
from gensim import corpora, models, similarities
#import logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from nltk.tokenize import sent_tokenize, word_tokenize
from bokeh.plotting import show, output_file
from bokeh.io import gridplot
import math
import os

import plots




def createDictionary(textTokens, excludeMostCommon=True, excludeTypes=[]):
    if excludeMostCommon:
        stoplist = '. , - -- : ; ( ) [ ] ! ? " / & \'\' \' ´´ ``'.split()
        stoplist += "be to of and a in that have it for on with as do at this but by is has from say an will one all would there what or the had was did were 's 'nt".split()  # most common english words /pronouns
        stoplist += "i you he she it they them me my not your his her him its their".split() #  pronouns
    frequency = defaultdict(int)
    for text in textTokens:
        for token in text:
            frequency[token] += 1
    dictionary = corpora.Dictionary([[token for token in text if token not in stoplist + excludeTypes and frequency[token] > 1] for text in textTokens])
    return dictionary


def tokenizer(documents):
    stoplist = []  # set("for a of the and to in".split())
    textsTokens = []
    for document in documents:
        textTokens = []
        with open(document, encoding='utf-8') as doc:
            for line in doc:
                line = line.strip('"')
                new = word_tokenize(line.lower())
                textTokens += new
        textsTokens.append(textTokens)
    return textsTokens


def createBow(dictionary, textTokens):
    #print(textTokens)
    bow = [dictionary.doc2bow(text) for text in textTokens]  # frequency
    return bow


def sentenceizer(documents):
    sentences = []
    for document in documents:
        with open(document, 'r', encoding='utf-8') as doc:
            data = doc.read().replace('\n', '')
        sentences += sent_tokenize(data)
    #print(sentences)
    return sentences


def detAvgSentLength(sentences):
    charLength, wordLength = [], []
    for sentence in sentences:
        tokens = word_tokenize(sentence)
        wordLength.append(len(tokens))
        #print(tokens)
        length = 0
        for token in tokens:
            length += len(token)
        charLength.append(length)
    avgCharLength = sum(charLength) / len(charLength)
    avgWordLength = sum(wordLength) / len(wordLength)
    return [avgCharLength, avgWordLength]


def detAvgWordLength(textTokens):
    stoplist = '. , - -- : ; ( ) [ ] ! ? " /'.split()
    summa, length = 0, 0
    wordLength = [[len(token) for token in text if token not in stoplist] for text in textTokens]
    for l in wordLength:
        summa += sum(l)
        length += len(l)
    return [summa / length]


def mostCommonTypes(dictionary, bow, excludeTypes=[], n=30):
    allbow = []
    for b in bow:
        allbow += b
    ranks = sorted(allbow, key=lambda item: item[1], reverse=True)
    mapped = []
    for rank in ranks:
        if dictionary[rank[0]] not in excludeTypes and dictionary[rank[0]] not in [t[0] for t in mapped]:
            mapped.append((dictionary[rank[0]], rank[1]))
    #Prepare data for plot
    x , y = [t[0] for t in mapped[0:n]], [t[1] for t in mapped[0:n]]
    return x, y


def createLsiModel(bow, dictionary, df=False):
    model = bow
    if df:
        tfidfmodel = models.TfidfModel(bow)
        model = tfidfmodel[bow]
    lsimodel = models.LsiModel(model, id2word=dictionary, num_topics=3)
    return lsimodel


def prepLsiData(lsimodel):
    topics = lsimodel.show_topics(log=False, formatted=True)
    listTopics = []
    for i in range(len(topics)):
        listTopics.append([])
        topic = lsimodel.show_topic(i)
        #print(topic)
        for t in topic:
            d = {}
            d['type'] = t[0]
            d['contr'] = math.fabs(t[1])
            d['nr'] = i
            listTopics[i].append(d)
    #print(listTopics)
    return listTopics


def docContrLsi(lsi):
    docValues = []
    for j in range(len(lsi[0])):
        docValues.append([])
        for i in range(len(lsi)):
            v = math.fabs(lsi[i][j][1])
            docValues[j].append(v)
    return docValues


def similarityReq(document, dictionary, lsimodel, lsi):
    new_doc = tokenizer(document)
    #print(new_doc)
    new_bow = createBow(dictionary, new_doc)
    new_lsi = lsimodel[new_bow]
    index = similarities.MatrixSimilarity(lsi)
    sims = index[new_lsi]  # sim request against indexed corpus
    x, y = [], []
    for doc in sorted(enumerate(sims[0]), reverse=True):
        x.append(str(doc[0]))
        y.append(doc[1] * 100)
    x.append('corpus')
    y.append(sum(y) / len(y))
    return(x, y)

def wordHistory(textsTokens, typ, granularity):
    history = []
    for text in textsTokens:
        h = []
        length = len(text)
        for i in range(text.count(typ)):
            index = text.index(typ)
            text.pop(index)
            h.append(index)
        d = {}
        stop = 0
        position = 0
        while stop <= length:
            stop += granularity
            d[stop] = []
            while position <= stop:
                if len(h) == 0:
                    break
                position = h[0]
                d[stop].append(position)
                h.pop(0)
        history.append(d)
    # Prepare data for plot
    x = []
    y = []
    for doc in history:
        dat1 = []
        dat2 = []
        for k in sorted(doc.keys()):
            dat1.append(k)
            dat2.append(len(doc[k]))
        x.append(dat1)
        y.append(dat2)
    print(x, y)
    return(x, y, typ)


def showPlots(data_MCT, data_avg, data_lsi, data_contr, data_sims, data_hist):
    output_file('standard.html')
    p = plots.hbarMCT(data_MCT[0], data_MCT[1])
    q = plots.hbarLength(data_avg)
    donutList = []
    for topic in data_lsi:
        donutList.append(plots.donutLsi(topic))
    barList = []
    for topic in data_contr:
        barList.append(plots.barDocLsi(topic))
    lsiList = []
    for i in range(len(donutList)):
        lsiList.append(barList[i])
        lsiList.append(donutList[i])
    g = gridplot([[p, q], [d for d in lsiList]])
    show(g)

    output_file('sim.html')
    b = plots.barSim(data_sims)
    show(b)

    output_file('hist.html')
    b = plots.lineHistory(data_hist)
    show(b)


def docReader(path_add):
    fn = os.path.join(os.path.dirname(__file__), path_add)
    return [fn+file for file in os.listdir(fn)]
        


docs = docReader('docs\\')
compare = docReader('compare\\')
print(type(docs[0]))
textTokens = tokenizer(docs)
sentences = sentenceizer(docs)
dictionary = createDictionary(textTokens)
bow = createBow(dictionary, textTokens)
lsimodel = createLsiModel(bow, dictionary)
lsi = lsimodel[bow]

avgSentLength = detAvgSentLength(sentences)
avgWordLength = detAvgWordLength(textTokens)
avg = avgSentLength + avgWordLength

mct = mostCommonTypes(dictionary, bow)

lsiData = prepLsiData(lsimodel)
docLsi = docContrLsi(lsi)

sims = similarityReq(compare, dictionary, lsimodel, lsi)

hist = wordHistory(textTokens, 'old', 500)

showPlots(mct, avg, lsiData, docLsi, sims, hist)


def main():
    pass


if __name__ == '__main__':
    main()
















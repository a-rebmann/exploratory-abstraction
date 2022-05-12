import gensim
import os
import re
import numpy as np
from nltk.tokenize import RegexpTokenizer
#from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim.models.doc2vec import TaggedDocument

def get_doc_list(folder_name,walks_name):
    doc_list = []
    file_list = ['input/'+folder_name+'/'+walks_name+'/'+name for name in os.listdir('input/'+folder_name+'/'+walks_name) if name.endswith('txt')]

    print ('Found %s documents under the dir %s .....'%(len(file_list),folder_name))
    return file_list

def get_doc(folder_name,walks_name):

    doc_list = get_doc_list(folder_name,walks_name)
    tokenizer = RegexpTokenizer(r'\w+')
    #en_stop = get_stop_words('en')
    #p_stemmer = PorterStemmer()

    taggeddoc = []

    for index,i in enumerate(doc_list):
        file = open(i,'r')

            # for tagged doc
        wordslist = []
        tagslist = []

        # clean and tokenize document string
        #raw = i.lower()
        #tokens = tokenizer.tokenize(i)

        # remove gateway number info from walk
        for line in file.readlines():
            cleanwalk= []
            for word in line.split(' '):
                #if ('%GWC%' in word):
                #    splitword= word.split('%GWC%')
                #    cleanwalk.append(splitword[0])
                if '+' in word:
                    cleanwalk.append(word.replace("+",""))
                else:
                    cleanwalk.append(word)

            #print(cleanwalk)
        #stopped_tokens = [i for i in tokens]

        # remove numbers
        #number_tokens = [re.sub(r'[\d]', ' ', i) for i in tokens]
        #number_tokens = ' '.join(number_tokens).split()

        # stem tokens
        #stemmed_tokens = [p_stemmer.stem(i) for i in number_tokens]
        # remove empty
        #length_tokens = [i for i in i if len(i) > 1]
        # add tokens to list


            # remove stop words from tokens
        #    stopped_tokens = [i for i in tokens if not i in en_stop]


            td = TaggedDocument(gensim.utils.to_unicode(str.encode(' '.join(cleanwalk))).split(),[index])
        # for later versions, you may want to use: td = TaggedDocument(gensim.utils.to_unicode(str.encode(' '.join(stemmed_tokens))).split(),[str(index)])
            taggeddoc.append(td)

    return taggeddoc

def get_doc_stats(folder_name,walks_name):

    doc_list = get_doc_list(folder_name,walks_name)
    tokenizer = RegexpTokenizer(r'\w+')
    #en_stop = get_stop_words('en')
    #p_stemmer = PorterStemmer()
    length_array=[]

    for index,i in enumerate(doc_list):
        file = open(i,'r')

            # for tagged doc
        wordslist = []
        tagslist = []


        # clean and tokenize document string
        #raw = i.lower()
        #tokens = tokenizer.tokenize(i)

        # remove gateway number info from walk
        for line in file.readlines():
            cleanwalk= []
            for word in line.split(' '):
                if ('%GWC%' in word):
                    splitword= word.split('%GWC%')
                    cleanwalk.append(splitword[0])
                elif '+' in word:
                    cleanwalk.append(word.replace("+",""))
                else:
                    cleanwalk.append(word)
            length_array.append(len(cleanwalk))
    length_np= np.array(length_array)
    print('Average: ',str(length_np.mean()), ' St_dev: ', str(np.std(length_np)))
            #print(cleanwalk)
        #stopped_tokens = [i for i in tokens]

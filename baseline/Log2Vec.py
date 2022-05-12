import gensim
import loadXES


def learn(folderName,vectorsize):
    documents = loadXES.get_doc_multiple_XES_tagged(folderName)
    print ('Data Loading finished')

    model = gensim.models.Doc2Vec(documents, dm = 0, alpha=0.025, size= vectorsize, window=3, min_alpha=0.025, min_count=0)
    nrEpochs= 10
    for epoch in range(nrEpochs):
        if epoch % 2 == 0:
            print ('Now training epoch %s'%epoch)
        model.train(documents,len(documents), epochs=nrEpochs)
        model.alpha -= 0.002  # decrease the learning rate
        model.min_alpha = model.alpha  # fix the learning rate, no decay

    model.save('output/'+folderName+'L2VVS'+str(vectorsize) +'.model')
    model.save_word2vec_format('output/'+folderName+ 'L2VVS'+str(vectorsize) + '.word2vec')

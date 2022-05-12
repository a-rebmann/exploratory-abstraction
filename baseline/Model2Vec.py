import gensim
import loadRandomWalks


def learn(folderName, walksName, vectorsize):
    documents = loadRandomWalks.get_doc(folderName, walksName)
    print ('Data Loading finished. ')


# build the model
    model = gensim.models.Doc2Vec(documents, dm = 0, alpha=0.025, size= vectorsize, window=8, min_alpha=0.025, min_count=0)

# start training
    nrEpochs=10
    for epoch in range(nrEpochs):
        if epoch % 2 == 0:
            print ('Now training epoch %s'%epoch)
        model.train(documents,len(documents), epochs=nrEpochs)
        model.alpha -= 0.002  # decrease the learning rate
        model.min_alpha = model.alpha  # fix the learning rate, no decay

    model.save('output/'+folderName+walksName+'M2VVS'+ str(vectorsize)+'.model')
    model.save_word2vec_format('output/'+folderName+ walksName+'M2VVS'+ str(vectorsize)+'.word2vec')

import gensim
import loadXES

def learn(folderName,vectorsize):
    #load .xes-file from input folder
    sentences = loadXES.get_sentences_XES(folderName + '.xes')
    print ('Data Loading finished')
    #train model
    model = gensim.models.Word2Vec(sentences, vector_size=vectorsize, window=3,  min_count=0)
    nrEpochs= 10
    for epoch in range(nrEpochs):
        if epoch % 2 == 0:
            print ('Now training epoch %s'%epoch)
        model.train(sentences, total_examples=len(sentences), start_alpha=0.025, epochs=nrEpochs)
        model.alpha -= 0.002  # decrease the learning rate
        model.min_alpha = model.alpha  # fix the learning rate, no decay



    model.save('output/'+folderName+'A2VVS'+str(vectorsize) +'.model')

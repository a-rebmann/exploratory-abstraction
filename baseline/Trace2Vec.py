import gensim
import loadXES
import nltk
from nltk.cluster.kmeans import KMeansClusterer
from sklearn.cluster import AgglomerativeClustering

def learn(folderName,vectorsize):
    documents = loadXES.get_doc_XES_tagged(folderName + '.xes')
    print ('Data Loading finished, ', str(len(documents)), ' traces found.')

# build the model
    model = gensim.models.Doc2Vec(documents, dm = 0, alpha=0.025, size= vectorsize, window=3, min_alpha=0.025, min_count=0)

# start training
    nrEpochs= 10
    for epoch in range(nrEpochs):
        if epoch % 2 == 0:
            print ('Now training epoch %s'%epoch)
        model.train(documents,len(documents), epochs=nrEpochs)
        model.alpha -= 0.002  # decrease the learning rate
        model.min_alpha = model.alpha  # fix the learning rate, no decay


    model.save('output/'+folderName+'T2VVS'+str(vectorsize) +'.model')
    model.save_word2vec_format('output/'+folderName+ 'T2VVS'+str(vectorsize) + '.word2vec')


def cluster(folderName, vectorsize, clusterType):
    corpus = loadXES.get_doc_XES_tagged(folderName + '.xes')
    print ('Data Loading finished, ', str(len(corpus)), ' traces found.')


    model= gensim.models.Doc2Vec.load('output/'+folderName+'T2VVS'+str(vectorsize) +'.model')

    vectors = []
    NUM_CLUSTERS= 5
    print("inferring vectors")
    for doc_id in range(len(corpus)):
        inferred_vector = model.infer_vector(corpus[doc_id].words)
        vectors.append(inferred_vector)
    print("done")


    if(clusterType=="KMeans"):
        kclusterer = KMeansClusterer(NUM_CLUSTERS, distance=nltk.cluster.util.cosine_distance, repeats=25)
        assigned_clusters = kclusterer.cluster(vectors, assign_clusters=True)
    elif(clusterType=="HierWard"):
        ward = AgglomerativeClustering(n_clusters=NUM_CLUSTERS, linkage='ward').fit(vectors)
        assigned_clusters = ward.labels_
    else:
        print(clusterType, " is not a predefined cluster type. Please use 'KMeans' or 'HierWard', or create a definition for ", clusterType)
        return
    trace_list = loadXES.get_trace_names(folderName + ".xes")
    clusterResult= {}
    for doc_id in range(len(corpus)):
        clusterResult[trace_list[doc_id]]=assigned_clusters[doc_id]


    resultFile= open('output/'+folderName+'T2VVS'+str(vectorsize)+clusterType+'.csv','w')
    for doc_id in range(len(corpus)):
        resultFile.write(trace_list[doc_id]+','+str(assigned_clusters[doc_id])+"\n")

    resultFile.close()
    print("done with " , clusterType , " on event log ", folderName)



def get_titles_by_cluster(id):
    list = []
    for x in range(0, len(assigned_clusters)):
        if (assigned_clusters[x] == id):
            list.append(used_lines[x])
    return list

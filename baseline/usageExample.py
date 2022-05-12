from baseline import Act2Vec

'''
This is an example script you can use to run the learning algorithms.
For input, please download dataRepLearnForBP.zip from processmining.be/dataRepLearnForBP
and unzip it in the 'input' folder.
Act2Vec and Trace2Vec require the name of an event log (.xes file) and a vectorsize.
Log2Vec requires a folderName that contains all event logs.
Model2Vec requires a folderName and the name of a subfolder with random walk results per model.

Output is written to the 'output' folder.
You can remove the comments around a block to test it.

'''



#  Act2Vec example

logName='BPIC15GroundTruth'
vectorsize=16
Act2Vec.learn(logName, vectorsize)


'''
#  Trace2vec example
logName='BPIC15GroundTruth'
vectorsize=16
Trace2Vec.learn(logName,vectorsize)
### After learning a representation, you can use it to create clustering
#Example clustertypes: "Kmeans" and "HierWard"
Trace2Vec.cluster(logName,vectorsize,"KMeans")

'''
'''
# Log2Vec Example
vectorsize=16
folderName="PLG2"
Log2Vec.learn(folderName,vectorsize)
'''


#  Model2vec example
# vectorsize=16
# folderName="PLG2"
# walksName="WalksResults"
# Model2Vec.learn(folderName,walksName,16)

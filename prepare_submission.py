from sklearn import linear_model
from sklearn.svm import SVR
from sklearn import ensemble
from sklearn.metrics import mean_squared_error
from sklearn import preprocessing
import cPickle as cp

models=cp.load(open('./predictor_model.pkl'))
locals().update(cp.load(open('test_features.pkl')))
allkeys = ['extraversion','neuroticism','agreeableness',\
'conscientiousness','interview','openness']

# Preprocess features
X = models['min_max_scaler'].fit_transform(X)

# predict all the variables
output={}
for alabel in allkeys:
    output[alabel]={v:p for v,p in zip(V,models['model'+alabel].predict(X))}

cp.dump(output,open('predictions.pkl','wb'))



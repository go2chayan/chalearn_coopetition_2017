from sklearn import linear_model
from sklearn.svm import SVR
from sklearn import ensemble
from sklearn.metrics import mean_squared_error
from sklearn import preprocessing
import cPickle as cp
import numpy as np

def main():
    # parameters
    method = "gb"    

    # Model file to save
    model_dict={}

    # Read features and annotations
    data = cp.load(open('./training_features.pkl'))
    annot = cp.load(open('./annotation_training.pkl'))
    X = data['X']
    v = data['V']
    print 'feature shape:',np.shape(X)

    # Normalize the features and save normalizer
    min_max_scaler = preprocessing.MinMaxScaler()
    X = min_max_scaler.fit_transform(X)
    model_dict['min_max_scaler']=min_max_scaler

    for label in annot:
        # variable to predict
        y = [annot[label][vid] for vid in v]        
        print 'training '+label
        print  'label shape:',np.shape(y)        

        # Model selection
        if method == "lasso":
            print 'using LASSO'
            model = linear_model.Lasso(alpha=0.001, fit_intercept=True,
                                       normalize=False, precompute='auto',
                                       copy_X=True, max_iter=1000, tol=0.0001,
                                       warm_start=False, positive=False)
            model.fit(X, y)
            # yp = lasso.predict(xtest)
        elif method == "svm":
            print 'using Support Vector Regression'
            model = SVR(C=0.010, kernel='linear', epsilon=0.00001, tol=0.00001, verbose=True,
                      max_iter=100000)
            model.fit(X, y)
            # yp = svr.predict(xtest)

        elif method == "logreg":
            print 'Using logistic regression'
            model = linear_model.LogisticRegression(penalty='l1', dual=False,
                                                       tol=0.0001, C=10.0,
                                                       fit_intercept=False,
                                                       intercept_scaling=1,
                                                       class_weight=None,
                                                       random_state=None)
            model.fit(X, y)
            # yp = logistic.predict(xtest)
        elif method == "gb":
            print 'Using Gradient Boosting Regressor'
            params = {'n_estimators': 500, 'max_depth': 4, 'min_samples_split': 2,
                  'learning_rate': 0.01, 'loss': 'ls'}
            model = ensemble.GradientBoostingRegressor(**params)
            model.fit(X, y)
            # yp = clf.predict(xtest)
        elif method == "gp":
            print 'Using Gaussian Process'
            gp = gaussian_process.GaussianProcess(theta0=1e-2, thetaL=1e-4,
                                                  thetaU=1e-1)
            gp.fit(X, y)
            # yp, sigma2_p = gp.predict(xtest, eval_MSE=True)
        print
        # save model for current label
        model_dict['model'+label]=model
    
    # Save all the models
    cp.dump(model_dict,open('predictor_model.pkl','wb'))

if __name__=='__main__':
    main()
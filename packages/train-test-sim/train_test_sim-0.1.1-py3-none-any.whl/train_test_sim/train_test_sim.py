# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 15:55:23 2024

@author: Marcel Tino
"""

# Import necessary libraries
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, auc
from sklearn.metrics import confusion_matrix,precision_score,accuracy_score,recall_score,f1_score


def get_simulation(X,Y,model):
    test_size=[0.2,0.25,0.3,0.35,0.4,0.45,0.5]
    columns=['accuracy','precision','recall','f1score']
    
    data=[]
    for elem in test_size:
    # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
        	X, Y, test_size=elem, random_state=42)
        list1=[]
        # Train the Logistic Regression model
        
        model.fit(X_train, y_train)
        ypred=model.predict(X_test)
        #print("\n,Test Size",elem)
        #cm=confusion_matrix(y_test,ypred)
        accuracy= round(accuracy_score(y_test, ypred),3)
        precision=round(precision_score(y_test, ypred),3)
        recall=round(recall_score(y_test, ypred),3)
        f1score=round(f1_score(y_test, ypred),3)
        raw_data=[accuracy,precision,recall,f1score]
        data.append(raw_data)
    df=pd.DataFrame(data,columns=columns)
    df['Test Size'] =test_size
    df= df.reset_index(drop=True)
    df.set_index('Test Size')
    df=df[['Test Size','accuracy','precision','recall','f1score']]
    return print(f"{df.to_string(index=False)}")



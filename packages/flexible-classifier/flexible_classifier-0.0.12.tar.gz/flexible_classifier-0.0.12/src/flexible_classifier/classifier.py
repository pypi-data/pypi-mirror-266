import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn import svm
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureMerger(BaseEstimator, TransformerMixin):
  def fit(self, X, y=None):
    return self
  
  def transform(self, X):
    df = pd.DataFrame()
    df['result'] = X.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    return df['result']


numerical_transformer = Pipeline(steps=[
  ('imputer', SimpleImputer(strategy='median')),
  ('scaler', StandardScaler())
]) 

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

vectorized_transformer = Pipeline(steps=[
  ('merge', FeatureMerger()),
  ('vectorize', TfidfVectorizer(max_features=2000))
])

def process_data(df, target_column, big_size_dataset = 100000):
  if type(df) == str:
    df = pd.read_csv(df)
  y = df[target_column]
  X = df.drop([target_column], axis=1)
  categorical_cols = [cname for cname in X.columns if X[cname].nunique() < 10 and  X[cname].dtype == "object"]
  vectorized_cols = [cname for cname in X.columns if X[cname].nunique() >= 10 and  X[cname].dtype == "object"]
  numerical_cols = [cname for cname in X.columns if X[cname].dtype in ['int64', 'float64']]
  preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_cols),
        ('cat', categorical_transformer, categorical_cols),
        ('vect', vectorized_transformer, vectorized_cols)
    ])
  cv = 5
  if (len(vectorized_cols) > 1):
    cv = 3
  logistic_param_grid = {"max_iter": [1000]}
  if df.shape[0] < big_size_dataset:
    logistic_param_grid["C"] = [0.5, 1, 1.5]
  logistic_regression  = GridSearchCV(
    LogisticRegression(max_iter=1000),
    logistic_param_grid,
    cv = 2,
    refit=True
  )
  models_to_test = [
    ('Logistic Regression', logistic_regression, cv),
  ]
  if df.shape[0] < big_size_dataset:
    random_forest = GridSearchCV(
         RandomForestClassifier(),
         {'n_estimators': [200], 'max_depth' : [4, 8]},
         cv = 2,
         refit=True
         )
    models_to_test.append(('Random Forest', random_forest, cv))
    svm_model = GridSearchCV(
         svm.SVC(),
         {'C': [1, 10]},
         cv = 2,
         refit=True)
    models_to_test.append(('SVM', svm_model, cv))
  results = []
  for name, model, cv in models_to_test:
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                ('model', model)
                              ])
    score = cross_val_score(pipeline, X, y, cv=cv, scoring='accuracy').mean()
    pipeline.fit(X, y)
    results.append((score, name, pipeline))
  results.sort()
  best_result = results[0]
  print(f"Model is {best_result[1]}. With average accuracy {best_result[0]}")
  return best_result[2]

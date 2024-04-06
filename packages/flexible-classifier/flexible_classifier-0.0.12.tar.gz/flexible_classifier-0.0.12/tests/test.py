from flexible_classifier import classifier
import pandas as pd

salaries = pd.read_csv('./data/ds_salaries.csv')
model = classifier.process_data('./data/ds_salaries.csv', 'experience_level')
X = salaries.drop('experience_level', axis='columns').iloc[:100]
print(X)
# customers1 = pd.read_csv('./data/Train.csv', index_col='ID')
# customers2 = pd.read_csv('./data/Test.csv', index_col='ID')
# customers = pd.concat([customers1, customers2])
# classifier.process_data(customers, 'Segmentation')

# to use in classifier file 
# salaries = pd.read_csv('../../tests/data/ds_salaries.csv')
# process_data('../../tests/data/ds_salaries.csv', 'experience_level')
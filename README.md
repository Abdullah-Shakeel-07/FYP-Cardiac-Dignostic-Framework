# FYP
This repo contains the code of our final year project  which comes under the domain of computer vision and healthcare
with primary focus on cardiac MRI. The main goal of the project is the automated diagnosis of
cardiac issues using cardiac MRI. The diagnosis will be made on the basis of detection of end
systolic, end diastolic volume and ejection fraction i.e the measure of percentage of blood
pumped out of the heart chamber with each contraction. A skilled cardiologist usually takes
about 20 minutes to measure the volume of the ejection fraction. The suggested diagnostic
system can help reduce this time which can lead to fast and accurate prediction of heart failure.
For this purpose, the proposed method is designed on publicly available cardiac MRI datasets
such as ACDC and 2015 data science bowl challenge which contains hundreds of cardiac MRI
images of multiple patients. This work will be based on already tested UNet for segmentation of
our ROIs (Region of Interests) in the MRI images and a type of neural network for the
classification purpose i.e whether the patient is healthy or not, or if there are any concerns for
him in the future regarding cardiac. The model will be tested on combination of well reputed
publicly available cardiac MRI datasets.

Dataset Links
Data Science Bowl: https://www.kaggle.com/competitions/second-annual-data-science-bowl/data
Sunnybrook 2009: http://www.cardiacatlas.org/studies/sunnybrook-cardiac-data/
ACDC 2017: https://www.creatis.insa-lyon.fr/Challenge/acdc/databases.html

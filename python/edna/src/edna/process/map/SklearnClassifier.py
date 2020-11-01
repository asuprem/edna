from os import PathLike
from edna.process import BaseProcess
from edna.process.map import Map
import warnings


sklearn = None
try:
    import sklearn
    import joblib
    import numpy
except ImportError:
    warnings.warn("scikit-learn module is not installed. edna.process.map.SklearnClassifier might not work properly.", category=ImportWarning)



class SklearnClassifier(Map):
    process_name : str = "SklearnClassifier"
    classifier : sklearn.base.BaseEstimator
    def __init__(self, process: BaseProcess = None, 
        classifier_path: PathLike = None, 
        *args, **kwargs) -> BaseProcess:
        if classifier_path is None:
            raise ValueError("Must provide valid `classifier_path` for SklearnClassifier, got None")
        self.classifier_path = classifier_path
        self.classifier = joblib.load(classifier_path)
        super().__init__(process=process, *args, **kwargs)

    def map(self,message : object):
        return self.classifier.predict(message)


        

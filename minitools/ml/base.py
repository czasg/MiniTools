__all__ = (
    'MachineLearning',
    'Classification',
    'Regression',
    'SupervisedLearning',
    'UnsupervisedLearning'
)


class MetaClassBase(type):

    def __new__(cls, className, bases, attrs):
        if not attrs.get('machine_learning_type'):
            attrs['machine_learning_type'] = \
                "|".join([base.machine_learning_type for base in bases if base.machine_learning_type])
        return super(MetaClassBase, cls).__new__(cls, className, bases, attrs)


class MachineLearning(metaclass=MetaClassBase):
    """Machine Learning Base"""

    def collect_data(self, *args, **kwargs):
        """Collect data"""

    def analyze_data(self, *args, **kwargs):
        """Analyze data"""

    def training_algorithm(self, *args, **kwargs):
        """Training algorithm"""

    def test_algorithm(self, *args, **kwargs):
        """Test algorithm"""

    def result(self, *args, **kwargs):
        """Using the algorithm"""


class Classification(MachineLearning):
    """Machine Learning of classification"""

    machine_learning_type = "classification"


class Regression(MachineLearning):
    """Machine Learning of regression"""

    machine_learning_type = "regression"


class SupervisedLearning(MachineLearning):
    """Machine Learning of supervised"""

    machine_learning_type = "supervised"


class UnsupervisedLearning(MachineLearning):
    """Machine Learning of unsupervised"""

    machine_learning_type = "unsupervised"

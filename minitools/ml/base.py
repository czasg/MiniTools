__all__ = ('MachineLearning',
           'classification',
           'regression',
           'supervised',
           'unsupervised')


class MetaClassBase(type):
    machine_learning_type = None

    def __new__(cls, className, bases, attrs):
        machine_learning_type = attrs.get('machine_learning_type')

        if machine_learning_type:
            if cls.machine_learning_type:
                attrs['machine_learning_type'] = cls.machine_learning_type = \
                    '|'.join((cls.machine_learning_type, machine_learning_type))
            else:
                attrs['machine_learning_type'] = cls.machine_learning_type = \
                    machine_learning_type
        else:
            attrs['machine_learning_type'] = cls.machine_learning_type

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


def classification():
    class Classification(MachineLearning):
        """Machine Learning of classification"""

        machine_learning_type = "classification"

    return Classification


def regression():
    class Regression(MachineLearning):
        """Machine Learning of regression"""

        machine_learning_type = "regression"

    return Regression


def supervised():
    class SupervisedLearning(MachineLearning):
        """Machine Learning of supervised"""

        machine_learning_type = "supervised"

    return SupervisedLearning


def unsupervised():
    class UnsupervisedLearning(MachineLearning):
        """Machine Learning of unsupervised"""

        machine_learning_type = "unsupervised"

    return UnsupervisedLearning

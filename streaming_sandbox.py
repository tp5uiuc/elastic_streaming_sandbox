from typing import Dict
import numpy as np


class ElasticStreamingSolution:
    def __init__(self, w: float, c: float):
        self.womerseley = w
        self.cauchy = c
        self.epsilon = 0.05

    def process(self, x: np.ndarray, y: np.ndarray):
        """
        Assume circle is of radius 1
        """
        X, Y = np.meshgrid(x, y)
        Z = (self.womerseley + self.cauchy) * np.cos(np.pi * X) * np.sin(np.pi * Y)

        return X, Y, Z

    def __call__(self, xy):
        # thin converter to
        to_py = map(lambda x: np.asarray(x.to_py()), xy)
        # only return z
        return self.process(*to_py)[2]


def simulator(config: Dict[str, str]):
    pyconfig = config.to_py()
    # def generate_data(x, y):

    #     py_x = np.asarray(x.to_py())
    #     py_y = np.asarray(y.to_py())

    #     X, Y = np.meshgrid(py_x, py_y)

    #     Z = (womerseley + cauchy) * np.cos(np.pi * X) * np.sin(np.pi * Y)

    #     return Z

    return ElasticStreamingSolution(
        float(pyconfig["womerseley"]), float(pyconfig["cauchy"])
    )


# DON'T CALL FROM JAVASCRIPT side
def test_code():
    solution = ElasticStreamingSolution(0.2, 0.001)
    x = np.linspace(-4.0, 4.0, 51)
    y = np.linspace(-4.0, 4.0, 51)
    X, Y, Z = solution.process(x, y)

    from matplotlib import pyplot as plt

    plt.contourf(X, Y, Z)
    plt.show()


if __name__ == "__main__":
    test_code()

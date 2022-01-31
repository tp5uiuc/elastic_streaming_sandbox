from typing import Dict
import numpy as np


class ElasticStreamingSolution:
    def __init__(self, w: float, c: float, z: float):
        self.womerseley = w
        self.cauchy = c
        self.zeta = z
        self.epsilon = 0.1
        # we need to add a note to user somewhere that
        # self.kappa has to be Order(1).
        self.kappa = self.cauchy / self.epsilon
        self.generate_lambda_for_psi_radial_variation()
        self.generate_lambda_for_psi_angular_variation()

    def generate_lambda_for_psi_radial_variation(self):
        """
        Generates lambda functions for radial decay of
        streamfunction (psi), based on womerseley, cauchy
        and zeta, and into which directly the cylindrical
        coordinates (r, theta) can be input.

        For details on defined symbols, formulae refer to
        Holtsmark et al., 1954 and
        TODO: Add PRL arxiv link, (later paper).
        """
        from sympy import hankel1, conjugate, lambdify, symbols, simplify
        import numpy as np
        import scipy.integrate as integrate

        # symbols defined as per Holtsmark et al., 1954.
        r = symbols("r", real=True)
        e = self.womerseley * 1j ** 0.5
        X = hankel1(0, e * r) / hankel1(0, e)
        Z = hankel1(2, e * r) / hankel1(0, e)
        C = Z.subs(r, 1)

        # Rigid body streaming psi computation
        # time-averaged Reynolds stress term, Holtsmark et al., 1954
        steady_reynolds_stress = Z - conjugate(Z)
        steady_reynolds_stress += C * conjugate(X) / r ** 2 - conjugate(C) * X / r ** 2
        steady_reynolds_stress += 2 * X * conjugate(Z) - 2 * conjugate(X) * Z
        steady_reynolds_stress *= -1j * (self.womerseley ** 4) / 4
        steady_reynolds_stress = simplify(steady_reynolds_stress)

        # For terms and coefficients below, refer to Holtsmark et al., 1954
        f1 = lambdify(r, steady_reynolds_stress / r)
        f2 = lambdify(r, steady_reynolds_stress * r)
        f3 = lambdify(r, steady_reynolds_stress * (r ** 3))
        f4 = lambdify(r, steady_reynolds_stress * (r ** 5))
        arg1 = lambda x: integrate.quad(f1, 1, x)[0]
        arg2 = lambda x: integrate.quad(f2, 1, x)[0]
        arg3 = lambda x: integrate.quad(f3, 1, x)[0]
        arg4 = lambda x: integrate.quad(f4, 1, x)[0]
        c_1 = -arg1(np.inf) / 48
        c_2 = arg2(np.inf) / 16
        c_3 = arg1(np.inf) / 16 - arg2(np.inf) / 8
        c_4 = -arg1(np.inf) / 24 + arg2(np.inf) / 16
        self.rigid_body_psi_radial_decay = np.vectorize(
            lambda y: (
                y ** 4 * (arg1(y) / 48 + c_1)
                + y ** 2 * (-arg2(y) / 16 + c_2)
                + (arg3(y) / 16 + c_3)
                + (-arg4(y) / 48 + c_4) / y ** 2
            )
        )

        # Elasticity effects streaming psi computation
        zeta_effect = 0.5 * (
            (self.zeta ** 2 + 1) * np.log(self.zeta) / (self.zeta ** 2 - 1) - 1
        )
        womerseley_effect = (-e * hankel1(1, e) / hankel1(0, e)).evalf()
        self.elasticity_effect_psi_radial_decay = lambda y: (
            0.5
            * zeta_effect
            * np.abs(womerseley_effect) ** 2
            * (1 - y ** (-2))
            / self.womerseley ** 2
        )

    def generate_lambda_for_psi_angular_variation(self):
        """
        Generates lambda for psi angular variation, sin(2 theta)
        directly from X and Y, skipping theta computation.
        """
        self.psi_angular_variation = lambda x, y: 2 * x * y / (x ** 2 + y ** 2)

    def process(self, x: np.ndarray, y: np.ndarray):
        """
        Assume circle is of radius 1
        """
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X ** 2 + Y ** 2)
        Z = (
            self.epsilon
            * (
                self.rigid_body_psi_radial_decay(R)
                + self.kappa * self.elasticity_effect_psi_radial_decay(R)
            )
            * self.psi_angular_variation(X, Y)
        ) * (R >= 1).astype(
            float
        )  # mask inside cylinder

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
        float(pyconfig["womerseley"]),
        float(pyconfig["cauchy"], float(pyconfig["pinned_zone_radius"])),
    )


# DON'T CALL FROM JAVASCRIPT side
def test_code():
    womerseley = 8
    cauchy = 0.05
    zeta = 0.2
    solution = ElasticStreamingSolution(w=womerseley, c=cauchy, z=zeta)
    x = np.linspace(-3.0, 3.0, 50)
    y = np.linspace(-3.0, 3.0, 50)
    X, Y, Z = solution.process(x, y)

    from matplotlib import pyplot as plt

    plt.contourf(X, Y, Z, levels=50)
    plt.contour(X, Y, Z, levels=11, colors="k", linewidths=2)
    plt.show()


if __name__ == "__main__":
    test_code()

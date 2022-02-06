from typing import Dict
import numpy as np
from functools import lru_cache

# from timeit import default_timer as timer


def compute_factors(womerseley):
    from sympy import hankel1, conjugate, lambdify, symbols, simplify
    import numpy as np
    import scipy.integrate as integrate

    # symbols defined as per Holtsmark et al., 1954.
    r = symbols("r", real=True)
    e = womerseley * 1j**0.5
    X = hankel1(0, e * r) / hankel1(0, e)
    Z = hankel1(2, e * r) / hankel1(0, e)
    C = Z.subs(r, 1)

    # Rigid body streaming psi computation
    # time-averaged Reynolds stress term, Holtsmark et al., 1954
    steady_reynolds_stress = Z - conjugate(Z)
    steady_reynolds_stress += C * conjugate(X) / r**2 - conjugate(C) * X / r**2
    steady_reynolds_stress += 2 * X * conjugate(Z) - 2 * conjugate(X) * Z
    steady_reynolds_stress *= -1j * (womerseley**4) / 4
    steady_reynolds_stress = simplify(steady_reynolds_stress)

    # For terms and coefficients below, refer to Holtsmark et al., 1954
    f1 = lambdify(r, steady_reynolds_stress / r)
    f2 = lambdify(r, steady_reynolds_stress * r)
    f3 = lambdify(r, steady_reynolds_stress * (r**3))
    f4 = lambdify(r, steady_reynolds_stress * (r**5))
    arg1 = lru_cache(maxsize=50)(lambda x: integrate.quad(f1, 1, x)[0])
    arg2 = lru_cache(maxsize=50)(lambda x: integrate.quad(f2, 1, x)[0])
    arg3 = lru_cache(maxsize=50)(lambda x: integrate.quad(f3, 1, x)[0])
    arg4 = lru_cache(maxsize=50)(lambda x: integrate.quad(f4, 1, x)[0])
    inf = np.inf
    c_1 = -arg1(inf) / 48
    c_2 = arg2(inf) / 16
    c_3 = arg1(inf) / 16 - arg2(inf) / 8
    c_4 = -arg1(inf) / 24 + arg2(inf) / 16

    womerseley_effect = np.cdouble((-e * hankel1(1, e) / hankel1(0, e)).evalf())

    def rigid_effects(zeta):
        return np.vectorize(
            lambda y: (
                y**4 * (arg1(y) / 48 + c_1)
                + y**2 * (-arg2(y) / 16 + c_2)
                + (arg3(y) / 16 + c_3)
                + (-arg4(y) / 48 + c_4) / y**2
            )
        )

    def elastic_effects(zeta):
        # Elasticity effects streaming psi computation
        zeta_effect = 0.5 * ((zeta**2 + 1) * np.log(zeta) / (zeta**2 - 1) - 1)
        return lambda y: (
            0.5
            * zeta_effect
            * np.abs(womerseley_effect) ** 2
            * (1 - y ** (-2))
            / womerseley**2
        )

    return (rigid_effects, elastic_effects)


class ElasticStreamingSolution:
    simulator_cache = []

    def __init__(self, w: float, c: float, z: float):
        self.womerseley = w
        self.cauchy = c
        self.zeta = z
        self.epsilon = 0.1
        # we need to add a note to user somewhere that
        # self.kappa has to be Order(1).
        self.kappa = self.cauchy / self.epsilon
        # start = timer()

        r, e = compute_factors(self.womerseley)
        # end = timer()
        # print("compute_factors ", end - start)
        # cheap
        # start = timer()
        self.rigid_body_psi_radial_decay = r(self.zeta)
        self.elasticity_effect_psi_radial_decay = e(self.zeta)
        # end = timer()

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
        e = self.womerseley * 1j**0.5
        X = hankel1(0, e * r) / hankel1(0, e)
        Z = hankel1(2, e * r) / hankel1(0, e)
        C = Z.subs(r, 1)

        # Rigid body streaming psi computation
        # time-averaged Reynolds stress term, Holtsmark et al., 1954
        steady_reynolds_stress = Z - conjugate(Z)
        steady_reynolds_stress += C * conjugate(X) / r**2 - conjugate(C) * X / r**2
        steady_reynolds_stress += 2 * X * conjugate(Z) - 2 * conjugate(X) * Z
        steady_reynolds_stress *= -1j * (self.womerseley**4) / 4
        steady_reynolds_stress = simplify(steady_reynolds_stress)

        # For terms and coefficients below, refer to Holtsmark et al., 1954
        f1 = lambdify(r, steady_reynolds_stress / r)
        f2 = lambdify(r, steady_reynolds_stress * r)
        f3 = lambdify(r, steady_reynolds_stress * (r**3))
        f4 = lambdify(r, steady_reynolds_stress * (r**5))
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
                y**4 * (arg1(y) / 48 + c_1)
                + y**2 * (-arg2(y) / 16 + c_2)
                + (arg3(y) / 16 + c_3)
                + (-arg4(y) / 48 + c_4) / y**2
            )
        )

        # Elasticity effects streaming psi computation
        zeta_effect = 0.5 * (
            (self.zeta**2 + 1) * np.log(self.zeta) / (self.zeta**2 - 1) - 1
        )
        womerseley_effect = (-e * hankel1(1, e) / hankel1(0, e)).evalf()
        self.elasticity_effect_psi_radial_decay = lambda y: (
            0.5
            * zeta_effect
            * np.abs(womerseley_effect) ** 2
            * (1 - y ** (-2))
            / self.womerseley**2
        )

    @staticmethod
    def generate_lambda_for_psi_angular_variation():
        """
        Generates lambda for psi angular variation, sin(2 theta)
        directly from X and Y, skipping theta computation.
        """
        return lambda x, y: 2 * x * y / (x**2 + y**2)

    def process(self, x: np.ndarray, y: np.ndarray):
        """
        Assume circle is of radius 1
        """
        from scipy.interpolate import griddata

        # R = np.sqrt(X ** 2 + Y ** 2)
        # r = np.sqrt(x ** 2 + y ** 2)
        r_max = np.sqrt(np.amax(np.abs(x)) ** 2 + np.amax(np.abs(y)) ** 2)

        n_grid_samples = 81
        r = np.hstack(
            (
                np.linspace(1.0, 1.5, 31, endpoint=False),
                np.linspace(1.5, np.ceil(r_max), n_grid_samples - 21),
            )
        )
        idx = r > 1.0
        theta = np.linspace(0.0, 2.0 * np.pi, n_grid_samples - 1, endpoint=False)

        psi_rad_variation = 0.0 * r

        psi_rad_variation[idx] = self.rigid_body_psi_radial_decay(
            r[idx]
        ) + self.kappa * self.elasticity_effect_psi_radial_decay(r[idx])
        psi_theta_variation = np.sin(2.0 * theta)

        PSI_THETA = (
            self.epsilon
            * psi_rad_variation.reshape(1, -1)
            * psi_theta_variation.reshape(-1, 1)
        )
        R, THETA = np.meshgrid(r, theta)

        # PSI_THETA = R  # r.reshape(1, -1) + 0.0 * theta_variation.reshape(-1, 1)

        NX = R * np.cos(THETA)
        NY = R * np.sin(THETA)

        X, Y = np.meshgrid(x, y)
        Z = griddata(
            (NX.flatten(), NY.flatten()), PSI_THETA.flatten(), (X, Y), method="linear"
        )

        return X, Y, Z

    def DC_layer_thickness(self):
        from scipy.optimize import root_scalar

        def f(r):
            return self.rigid_body_psi_radial_decay(
                r
            ) + self.kappa * self.elasticity_effect_psi_radial_decay(r)

        root_lower_bracket = 1.1
        root_upper_bracket = 3.0
        root_initial_guess = 2.0
        # Below we check if a finite DC layer exists within said limits
        if f(root_lower_bracket) * f(root_upper_bracket) < 0:
            return (
                root_scalar(
                    f,
                    bracket=(root_lower_bracket, root_upper_bracket),
                    x0=root_initial_guess,
                ).root
                - 1.0
            )
        else:
            # refactor on JS side as you feel apt
            return "DC layer diverging!"

    def __call__(self, xy):
        # thin converter to
        to_py = map(lambda x: np.asarray(x.to_py()), xy)
        # only return z
        return self.process(*to_py)[2]

        # X, Y = np.meshgrid(x, y)
        # x = next(to_py)
        # y = next(to_py)
        # R = np.sqrt(X ** 2 + Y ** 2)
        # return R


def simulator(config: Dict[str, str]):
    pyconfig = config.to_py()
    print(pyconfig)
    return ElasticStreamingSolution(
        float(pyconfig["womersley"]),
        float(pyconfig["cauchy"]),
        float(pyconfig["pinned_zone_radius"]),
    )

import numpy as np
from streaming_sandbox import ElasticStreamingSolution

# DON'T CALL FROM JAVASCRIPT side
def test_code():
    womerseley = 8
    cauchy = 0.05
    zeta = 0.2
    solution = ElasticStreamingSolution(w=womerseley, c=cauchy, z=zeta)
    print(solution.DC_layer_thickness())
    r = np.linspace(1.1, 2.0, 501)

    v = np.abs(
        solution.rigid_body_psi_radial_decay(r)
        + solution.kappa * solution.elasticity_effect_psi_radial_decay(r)
    )
    idx = np.argmin(v)
    print(idx, r[idx], v[idx])

    x = np.linspace(-3.0, 3.0, 50)
    y = np.linspace(-3.0, 3.0, 50)
    # for _ in range(10):
    from timeit import default_timer as timer

    start = timer()
    X, Y, Z = solution.process(x, y)
    end = timer()
    print("process ", end - start)

    from matplotlib import pyplot as plt

    contr = plt.contourf(X, Y, Z, levels=50)
    plt.colorbar(contr)
    plt.contour(X, Y, Z, levels=11, colors="k", linewidths=2)
    plt.show()


# no longer works with latest pyodide
if __name__ == "__main__":
    test_code()

import numpy as np
import casadi as ca
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class RectangleRegion:
    """[Rectangle shape]
    """

    def __init__(self, left, right, down, up):
        self.left = left
        self.right = right
        self.down = down
        self.up = up

    def get_convex_rep(self):
        mat_A = np.array([[-1, 0], [0, -1], [1, 0], [0, 1]])
        vec_b = np.array([[-self.left], [-self.down], [self.right], [self.up]])
        return mat_A, vec_b

    def get_plot_patch(self):
        return patches.Rectangle(
            (self.left, self.down),
            self.right - self.left,
            self.up - self.down,
            linewidth=1,
            edgecolor="r",
            facecolor="r",
        )


class ConvexRegion2D:
    pass


def get_dist_point_to_region(point, mat_A, vec_b):
    """Return distance between a point and a convex region
    """
    opti = ca.Opti()
    # variables and cost
    point_in_region = opti.variable(mat_A.shape[-1], 1)
    cost = 0
    # constraints
    opti.subject_to(ca.mtimes(mat_A, point_in_region) <= vec_b)
    dist_vec = point - point_in_region
    cost += ca.mtimes(dist_vec.T, dist_vec)
    # solve optimization
    opti.minimize(cost)
    option = {"verbose": False, "ipopt.print_level": 0, "print_time": 0}
    opti.solver("ipopt", option)
    opt_sol = opti.solve()
    return opt_sol.value(ca.norm_2(dist_vec))


def get_dist_region_to_region(mat_A1, vec_b1, mat_A2, vec_b2):
    opti = ca.Opti()
    # variables and cost
    point1 = opti.variable(mat_A1.shape[-1], 1)
    point2 = opti.variable(mat_A2.shape[-1], 1)
    cost = 0
    # constraints
    opti.subject_to(ca.mtimes(mat_A1, point1) <= vec_b1)
    opti.subject_to(ca.mtimes(mat_A2, point2) <= vec_b2)
    dist_vec = point1 - point2
    cost += ca.mtimes(dist_vec.T, dist_vec)
    # solve optimization
    opti.minimize(cost)
    option = {"verbose": False, "ipopt.print_level": 0, "print_time": 0}
    opti.solver("ipopt", option)
    opt_sol = opti.solve()
    return opt_sol.value(ca.norm_2(dist_vec))
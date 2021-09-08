import math

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib import animation

from control.dcbf_controller import NmpcDcbfController
from models.dubin_car import (
    DubinCarDynamics,
    DubinCarGeometry,
    DubinCarStates,
    DubinCarSystem,
)
from models.geometry_utils import *
from models.kinematic_car import (
    KinematicCarDynamics,
    KinematicCarRectangleGeometry,
    KinematicCarTriangleGeometry,
    KinematicCarPentagonGeometry,
    KinematicCarStates,
    KinematicCarSystem,
)
from planning.path_generator.search_path_generator import (
    AstarLoSPathGenerator,
    AstarPathGenerator,
    ThetaStarPathGenerator,
)
from planning.trajectory_generator.constant_speed_generator import (
    ConstantSpeedTrajectoryGenerator,
)
from sim.simulation import Robot, SingleAgentSimulation


def plot_world(simulation, indexes, figure_name="world"):
    # TODO: make this plotting function general applicable to different systems
    fig, ax = plt.subplots()
    plt.axis("equal")
    global_paths = simulation._robot._global_planner_logger._paths
    global_path = global_paths[0]
    ax.plot(global_path[:, 0], global_path[:, 1], "bo--", linewidth=1, markersize=4)
    closedloop_traj = np.vstack(simulation._robot._system_logger._xs)
    ax.plot(closedloop_traj[:, 0], closedloop_traj[:, 1], "k-", linewidth=2, markersize=4)
    for obs in simulation._obstacles:
        obs_patch = obs.get_plot_patch()
        ax.add_patch(obs_patch)
    for index in indexes:
        polygon_patch = simulation._robot._system._geometry.get_plot_patch(closedloop_traj[index, :])
        ax.add_patch(polygon_patch)
    plt.savefig("figures/" + figure_name + ".eps", format="eps", dpi=1000, pad_inches=0)
    plt.savefig("figures/" + figure_name + ".png", format="png", dpi=1000, pad_inches=0)


def animate_world(simulation, animation_name="world"):
    # TODO: make this plotting function general applicable to different systems
    fig, ax = plt.subplots()
    plt.axis("equal")
    global_paths = simulation._robot._global_planner_logger._paths
    global_path = global_paths[0]
    ax.plot(global_path[:, 0], global_path[:, 1], "bo--", linewidth=1, markersize=4)

    local_paths = simulation._robot._local_planner_logger._trajs
    local_path = local_paths[0]
    (reference_traj_line,) = ax.plot(local_path[:, 0], local_path[:, 1])

    optimized_trajs = simulation._robot._controller_logger._xtrajs
    optimized_traj = optimized_trajs[0]
    (optimized_traj_line,) = ax.plot(optimized_traj[:, 0], optimized_traj[:, 1])

    closedloop_traj = np.vstack(simulation._robot._system_logger._xs)
    ax.plot(closedloop_traj[:, 0], closedloop_traj[:, 1], "k-", linewidth=2, markersize=4)
    for obs in simulation._obstacles:
        obs_patch = obs.get_plot_patch()
        ax.add_patch(obs_patch)

    robot_patch = patches.Polygon(np.zeros((1, 2)), alpha=1.0, closed=True, fc="None", ec="tab:brown")
    ax.add_patch(robot_patch)

    def update(index):
        local_path = local_paths[index]
        reference_traj_line.set_data(local_path[:, 0], local_path[:, 1])
        optimized_traj = optimized_trajs[index]
        optimized_traj_line.set_data(optimized_traj[:, 0], optimized_traj[:, 1])
        polygon_patch_next = simulation._robot._system._geometry.get_plot_patch(closedloop_traj[index, :])
        robot_patch.set_xy(polygon_patch_next.get_xy())

    anim = animation.FuncAnimation(fig, update, frames=len(closedloop_traj), interval=1000 * 0.1)
    anim.save("animation/" + animation_name + ".mp4", dpi=300, writer=animation.writers["ffmpeg"](fps=10))


def dubin_car_simulation_test():
    start_pos, goal_pos, grid, obstacles = create_env("maze")
    robot = Robot(
        DubinCarSystem(
            state=DubinCarStates(x=np.block([start_pos[:2], np.array([0.0, start_pos[2]])])),
            geometry=DubinCarGeometry(0.14, 0.08),
            dynamics=DubinCarDynamics(),
        )
    )
    # Reduce margin (radius) for tighter corners
    global_path_margin = 0.07
    robot.set_global_planner(ThetaStarPathGenerator(grid, quad=False, margin=global_path_margin))
    robot.set_local_planner(ConstantSpeedTrajectoryGenerator())
    robot.set_controller(NmpcDcbfController(dynamics=DubinCarDynamics()))
    sim = SingleAgentSimulation(robot, obstacles, goal_pos)
    sim.run_navigation(20.0)
    plot_world(sim, np.arange(0, 200, 5))
    animate_world(sim)


def kinematic_car_triangle_simulation_test():
    start_pos, goal_pos, grid, obstacles = create_env("maze")
    robot = Robot(
        KinematicCarSystem(
            state=KinematicCarStates(x=np.block([start_pos[:2], np.array([0.0, start_pos[2]])])),
            geometry=KinematicCarTriangleGeometry(np.array([[0.14, 0.00], [-0.03, 0.05], [-0.03, -0.05]])),
            dynamics=KinematicCarDynamics(),
        )
    )
    global_path_margin = 0.07
    robot.set_global_planner(ThetaStarPathGenerator(grid, quad=False, margin=global_path_margin))
    robot.set_local_planner(ConstantSpeedTrajectoryGenerator())
    robot.set_controller(NmpcDcbfController(dynamics=KinematicCarDynamics()))
    sim = SingleAgentSimulation(robot, obstacles, goal_pos)
    sim.run_navigation(20.0)
    plot_world(sim, np.arange(0, 200, 5), figure_name="triangle")
    animate_world(sim, animation_name="triangle")


def kinematic_car_rectangle_simulation_test():
    start_pos, goal_pos, grid, obstacles = create_env("maze")
    robot = Robot(
        KinematicCarSystem(
            state=KinematicCarStates(x=np.block([start_pos[:2], np.array([0.0, start_pos[2]])])),
            geometry=KinematicCarRectangleGeometry(0.15, 0.06, 0.1),
            dynamics=KinematicCarDynamics(),
        )
    )
    global_path_margin = 0.07
    robot.set_global_planner(ThetaStarPathGenerator(grid, quad=False, margin=global_path_margin))
    robot.set_local_planner(ConstantSpeedTrajectoryGenerator())
    robot.set_controller(NmpcDcbfController(dynamics=KinematicCarDynamics()))
    sim = SingleAgentSimulation(robot, obstacles, goal_pos)
    sim.run_navigation(20.0)
    plot_world(sim, np.arange(0, 200, 5), figure_name="rectangle")
    animate_world(sim, animation_name="rectangle")


def kinematic_car_pentagon_simulation_test():
    start_pos, goal_pos, grid, obstacles = create_env("maze")
    robot = Robot(
        KinematicCarSystem(
            state=KinematicCarStates(x=np.block([start_pos[:2], np.array([0.0, start_pos[2]])])),
            geometry=KinematicCarPentagonGeometry(
                np.array([[0.15, 0.00], [0.03, 0.05], [-0.01, 0.02], [-0.01, -0.02], [0.03, -0.05]])
            ),
            dynamics=KinematicCarDynamics(),
        )
    )
    global_path_margin = 0.07
    robot.set_global_planner(ThetaStarPathGenerator(grid, quad=False, margin=global_path_margin))
    robot.set_local_planner(ConstantSpeedTrajectoryGenerator())
    robot.set_controller(NmpcDcbfController(dynamics=KinematicCarDynamics()))
    sim = SingleAgentSimulation(robot, obstacles, goal_pos)
    sim.run_navigation(20.0)
    plot_world(sim, np.arange(0, 200, 5), figure_name="pentagon")
    animate_world(sim, animation_name="pentagon")


def create_env(env_type):
    if env_type == "s_path":
        s = 1.0  # scale of environment
        start = np.array([0.0 * s, 0.2 * s, 0.0])
        goal = np.array([1.0 * s, 0.8 * s])
        bounds = ((-0.2 * s, 0.0 * s), (1.2 * s, 1.2 * s))
        cell_size = 0.05 * s
        grid = (bounds, cell_size)
        obstacles = []
        obstacles.append(RectangleRegion(0.0 * s, 1.0 * s, 0.9 * s, 1.0 * s))
        obstacles.append(RectangleRegion(0.0 * s, 0.4 * s, 0.4 * s, 1.0 * s))
        obstacles.append(RectangleRegion(0.6 * s, 1.0 * s, 0.0 * s, 0.7 * s))
        return start, goal, grid, obstacles
    elif env_type == "maze":
        s = 0.2  # scale of environment
        start = np.array([0.5 * s, 5.5 * s, -math.pi / 2.0])
        goal = np.array([12.5 * s, 0.5 * s])
        bounds = ((0.0 * s, 0.0 * s), (13.0 * s, 6.0 * s))
        cell_size = 0.25 * s
        grid = (bounds, cell_size)
        obstacles = []
        obstacles.append(RectangleRegion(0.0 * s, 3.0 * s, 0.0 * s, 3.0 * s))
        obstacles.append(RectangleRegion(1.0 * s, 2.0 * s, 4.0 * s, 6.0 * s))
        obstacles.append(RectangleRegion(2.0 * s, 6.0 * s, 5.0 * s, 6.0 * s))
        obstacles.append(RectangleRegion(6.0 * s, 7.0 * s, 4.0 * s, 6.0 * s))
        obstacles.append(RectangleRegion(4.0 * s, 5.0 * s, 0.0 * s, 4.0 * s))
        obstacles.append(RectangleRegion(5.0 * s, 7.0 * s, 2.0 * s, 3.0 * s))
        obstacles.append(RectangleRegion(6.0 * s, 9.0 * s, 1.0 * s, 2.0 * s))
        obstacles.append(RectangleRegion(8.0 * s, 9.0 * s, 2.0 * s, 4.0 * s))
        obstacles.append(RectangleRegion(9.0 * s, 12.0 * s, 3.0 * s, 4.0 * s))
        obstacles.append(RectangleRegion(11.0 * s, 12.0 * s, 4.0 * s, 5.0 * s))
        obstacles.append(RectangleRegion(8.0 * s, 10.0 * s, 5.0 * s, 6.0 * s))
        obstacles.append(RectangleRegion(10.0 * s, 11.0 * s, 0.0 * s, 2.0 * s))
        obstacles.append(RectangleRegion(12.0 * s, 13.0 * s, 1.0 * s, 2.0 * s))
        obstacles.append(RectangleRegion(0.0 * s, 13.0 * s, 6.0 * s, 7.0 * s))
        obstacles.append(RectangleRegion(-1.0 * s, 0.0 * s, 0.0 * s, 6.0 * s))
        obstacles.append(RectangleRegion(0.0 * s, 13.0 * s, -1.0 * s, 0.0 * s))
        obstacles.append(RectangleRegion(13.0 * s, 14.0 * s, 0.0 * s, 6.0 * s))
        return start, goal, grid, obstacles


if __name__ == "__main__":
    kinematic_car_triangle_simulation_test()
    kinematic_car_rectangle_simulation_test()
    kinematic_car_pentagon_simulation_test()
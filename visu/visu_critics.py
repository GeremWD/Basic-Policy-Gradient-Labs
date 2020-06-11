import os
import numpy as np
import matplotlib.pyplot as plt
import random
from policies import GenericNet, PolicyWrapper
from visu.visu_policies import final_show
from environment import make_env


def plot_critic_from_name(folder, file_name, policy):
    complete_name = folder + file_name
    pw = PolicyWrapper(GenericNet(), "", "")
    critic = pw.load(complete_name)
    env_name = pw.env_name
    env, discrete = make_env(env_name, ["x", "y"])
    obs_size = env.observation_space.shape[0]
    picture_name = file_name + '_portrait.pdf'
    if not discrete:
        if obs_size == 1:
            plot_qfunction_1D(critic, env, plot=False, save_figure=True, figname=picture_name, foldername='/critics/')
        else:
            plot_qfunction_ND(critic, policy, env, plot=False, save_figure=True, figname=picture_name, foldername='/critics/')
    else:
        if obs_size == 2:
            plot_vfunction_2D(critic, env, plot=False, save_figure=True, figname=picture_name, foldername='/critics/')
        else:
            plot_vfunction_ND(critic, env, plot=False, save_figure=True, figname=picture_name, foldername='/critics/')


def plot_critics_from_directory(folder, policy):
    listdir = os.listdir(folder)
    for critic_file in listdir:
        plot_critic_from_name(folder, critic_file, policy)


def plot_critic(simu, critic, policy, study, default_string, num):
    picturename = str(num) + '_critic_' + study + default_string + simu.name + '.pdf'
    env = simu.env
    obs_size = simu.obs_size
    if not simu.discrete:
        if obs_size == 1:
            plot_qfunction_1D(critic, env, plot=False, save_figure=True, figname=picturename, foldername='/plots/')
        elif obs_size == 2:
            plot_qfunction_2D(critic, policy, env, plot=False, save_figure=True, figname=picturename, foldername='/plots/')
        else:
            plot_qfunction_ND(critic, policy, env, plot=False, save_figure=True, figname=picturename, foldername='/plots/')
    else:
        if obs_size == 2:
            plot_vfunction_2D(critic, env, plot=False, save_figure=True, figname=picturename, foldername='/plots/')
        else:
            plot_vfunction_ND(critic, env, plot=False, save_figure=True, figname=picturename, foldername='/plots/')


# visualization of the V function for a 2D environment like continuous mountain car. The action does not matter.
def plot_vfunction_2D(vfunction, env, plot=True, figname="vfunction.pdf", foldername='/plots/', save_figure=True, definition=50):
    if env.observation_space.shape[0] != 2:
        raise(ValueError("Observation space dimension {}, should be 2".format(env.observation_space.shape[0])))

    portrait = np.zeros((definition, definition))
    x_min, y_min = env.observation_space.low
    x_max, y_max = env.observation_space.high

    for index_x, x in enumerate(np.linspace(x_min, x_max, num=definition)):
        for index_y, y in enumerate(np.linspace(y_min, y_max, num=definition)):
            # Be careful to fill the matrix in the right order
            portrait[definition - (1 + index_y), index_x] = vfunction.evaluate(np.array([[x, y]]))

    plt.figure(figsize=(10, 10))
    plt.imshow(portrait, cmap="inferno", extent=[x_min, x_max, y_min, y_max], aspect='auto')
    plt.colorbar(label="critic value")
    # Add a point at the center
    plt.scatter([0], [0])
    x_label, y_label = getattr(env.observation_space, "names", ["x", "y"])
    final_show(save_figure, plot, figname, x_label, y_label, "V Function", foldername)


# visualization of the V function for a ND environment like cartpole. The action does not matter.
def plot_vfunction_ND(vfunction, env, plot=True, figname="vfunction.pdf", foldername='/plots/', save_figure=True, definition=50):
    if env.observation_space.shape[0] <= 2:
        raise(ValueError("Observation space dimension {}, should be > 2".format(env.observation_space.shape[0])))

    portrait = np.zeros((definition, definition))
    state_min = env.observation_space.low
    state_max = env.observation_space.high

    for index_x, x in enumerate(np.linspace(state_min[0], state_max[0], num=definition)):
        for index_y, y in enumerate(np.linspace(state_min[1], state_max[1], num=definition)):
            state = np.array([[x, y]])
            for i in range(2, len(state_min)):
                z = random.random() - 0.5
                state = np.append(state, z)
            portrait[definition - (1 + index_y), index_x] = vfunction.evaluate(state)

    plt.figure(figsize=(10, 10))
    plt.imshow(portrait, cmap="inferno", extent=[state_min[0], state_max[0], state_min[1], state_max[1]], aspect='auto')
    plt.colorbar(label="critic value")
    # Add a point at the center
    plt.scatter([0], [0])
    x_label, y_label = getattr(env.observation_space, "names", ["x", "y"])
    final_show(save_figure, plot, figname, x_label, y_label, "V Function", foldername)


# visualization of the Q function for a 1D environment like 1D Toy with continuous actions
def plot_qfunction_1D(qfunction, env, plot=True, figname="qfunction_1D.pdf", foldername='/plots/', save_figure=True, definition=50):
    if env.observation_space.shape[0] != 1:
        raise(ValueError("The observation space dimension is {}, should be 1".format(env.observation_space.shape[0])))

    portrait = np.zeros((definition, definition))
    x_min = env.observation_space.low[0]
    x_max = env.observation_space.high[0]
    y_min = env.action_space.low[0]
    y_max = env.action_space.high[0]

    for index_x, x in enumerate(np.linspace(x_min, x_max, num=definition)):
        for index_y, y in enumerate(np.linspace(y_min, y_max, num=definition)):
            # Be careful to fill the matrix in the right order
            portrait[definition - (1 + index_y), index_x] = qfunction.evaluate(np.array([x]), [y])

    plt.figure(figsize=(10, 10))
    plt.imshow(portrait, cmap="inferno", extent=[x_min, x_max, y_min, y_max], aspect='auto')
    plt.colorbar(label="critic value")
    # Add a point at the center
    plt.scatter([0], [0])
    x_label, y_label = getattr(env.observation_space, "names", ["x", "y"])
    final_show(save_figure, plot, figname, x_label, y_label, "Q Function", foldername)


# visualization of the Q function for a 2D environment like continuous mountain car.
# The action is the one from the policy sent as parameter
def plot_qfunction_2D(qfunction, policy, env, plot=True, figname="qfunction_cont.pdf", foldername='/plots/', save_figure=True, definition=50):
    if env.observation_space.shape[0] != 2:
        raise(ValueError("The observation space dimension is {}, whereas it should be 2".format(env.observation_space.shape[0])))

    portrait = np.zeros((definition, definition))
    x_min, y_min = env.observation_space.low
    x_max, y_max = env.observation_space.high

    for index_x, x in enumerate(np.linspace(x_min, x_max, num=definition)):
        for index_y, y in enumerate(np.linspace(y_min, y_max, num=definition)):
            state = np.array([x, y])
            action = policy.select_action(state)
            portrait[definition - (1 + index_y), index_x] = qfunction.evaluate(state, action)

    plt.figure(figsize=(10, 10))
    plt.imshow(portrait, cmap="inferno", extent=[x_min, x_max, y_min, y_max], aspect='auto')
    plt.colorbar(label="critic value")
    # Add a point at the center
    plt.scatter([0], [0])
    x_label, y_label = getattr(env.observation_space, "names", ["x", "y"])
    final_show(save_figure, plot, figname, x_label, y_label, "Q Function or current policy", foldername)


# visualization of the Q function for a ND environment like continuous cart pole.
# The action is the one from the policy sent as parameter
def plot_qfunction_ND(qfunction, policy, env, plot=True, figname="qfunction_cont.pdf", foldername='/plots/', save_figure=True, definition=50):
    if env.observation_space.shape[0] <= 2:
        raise(ValueError("Observation space dimension {}, should be > 2".format(env.observation_space.shape[0])))

    portrait = np.zeros((definition, definition))
    state_min = env.observation_space.low
    state_max = env.observation_space.high

    for index_x, x in enumerate(np.linspace(state_min[0], state_max[0], num=definition)):
        for index_y, y in enumerate(np.linspace(state_min[1], state_max[1], num=definition)):
            state = np.array([[x, y]])
            for i in range(2, len(state_min)):
                z = random.random() - 0.5
                state = np.append(state, z)
            action = policy.select_action(state)
            portrait[definition - (1 + index_y), index_x] = qfunction.evaluate(state, action)

    plt.figure(figsize=(10, 10))
    plt.imshow(portrait, cmap="inferno", extent=[state_min[0], state_max[0], state_min[1], state_max[1]], aspect='auto')
    plt.colorbar(label="critic value")
    # Add a point at the center
    plt.scatter([0], [0])
    x_label, y_label = getattr(env.observation_space, "names", ["x", "y"])
    final_show(save_figure, plot, figname, x_label, y_label, "Q Function or current policy", foldername)


# visualization of the Q function for a 2D environment like continuous mountain car.
# The action is given as parameter
def plot_qfunction_cont_act(qfunction, action, env, plot=True, figname="qfunction_cont.pdf", foldername='/plots/', save_figure=True, definition=50):
    if env.observation_space.shape[0] < 2:
        raise(ValueError("The observation space dimension is {}, whereas it should be 2".format(env.observation_space.shape[0])))

    portrait = np.zeros((definition, definition))
    x_min, y_min = env.observation_space.low
    x_max, y_max = env.observation_space.high

    for index_x, x in enumerate(np.linspace(x_min, x_max, num=definition)):
        for index_y, y in enumerate(np.linspace(y_min, y_max, num=definition)):
            state = np.array([x, y])
            portrait[definition - (1 + index_y), index_x] = qfunction.evaluate(state, action)

    plt.figure(figsize=(10, 10))
    plt.imshow(portrait, cmap="inferno", extent=[x_min, x_max, y_min, y_max], aspect='auto')
    plt.colorbar(label="critic value")
    # Add a point at the center
    plt.scatter([0], [0])
    x_label, y_label = getattr(env.observation_space, "names", ["x", "y"])
    final_show(save_figure, plot, figname, x_label, y_label, "Q Function or current policy", foldername)

if __name__ == '__main__':
    directory = os.getcwd() + '/policies/'
    pw = PolicyWrapper(GenericNet(), "", "")
    pol = pw.load(directory + "CartPole-v0#top1_198.6#198.6.pt")
    plot_critics_from_directory('./critics/', pol)
    if False:
        plot_critic_from_name('./critics/', 'CartPole-v0#moi#244.26543.pt', pol)




import matplotlib.pyplot as plt
import numpy as np

from matplotlib import cm
from matplotlib.ticker import LinearLocator
from matplotlib.animation import FuncAnimation
from time import time

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

# Make data.
X = np.arange(-5, 5, 0.1)
Y = np.arange(-5, 5, 0.1)
X, Y = np.meshgrid(X, Y)
R = np.sqrt(X**2 + Y**2)
Z = np.sin(R)


# Plot the surface.
cmap = cm.coolwarm
surf = ax.plot_surface(X, Y, Z, cmap=cmap,
                       linewidth=0, antialiased=False)

# Customize the z axis.
ax.set_zlim(-1.01, 1.01)
cbar = fig.colorbar(surf)

def func(frame, fig, ax, surf, cbar):
    start = time()
    Z = (-1)**frame*frame*np.sin(R)
    ax.set_zlim(Z.min(), Z.max())

    # surf._vec[2] = (-1)**frame*frame*heights
    # if frame % 2 == 0:
    #     surf.set_cmap(cm.coolwarm)
    # else:
    #     surf.set_cmap(cm.viridis)

    # cbar.set_ticks(np.arange(0, frame + 1))
    # cbar.ax.set_title(frame)
    # cbar.ax.set_ylim(0, frame + 1)

    # cbar.ax.set_ylim(-frame - 1, frame + 1)
    # surf.set_alpha(frame/10)
    if frame % 2 == 1:
        cmap = cm.viridis
    else:
        cmap = cm.coolwarm
    surf[0].remove()
    surf[0] = ax.plot_surface(X, Y, Z, cmap=cmap,
                       linewidth=0, antialiased=False)

    cbar = fig.colorbar(surf[0], cax=cbar.ax)
    print(time() - start)
    return [[surf], cbar]

from functools import partial
# ani = FuncAnimation(
#         fig, func, frames=10,
#         fargs=(fig, ax, [surf], cbar))
ani = FuncAnimation(
        fig, partial(func, fig=fig, ax=ax, surf=[surf], cbar=cbar),
        frames=10)

ani.save('funcanimation.gif')
plt.show()

############################################################################
############################################################################
############################################################################
############################################################################
############################################################################
############################################################################

# from matplotlib.animation import ArtistAnimation
# 
# X = np.arange(-5, 5, 0.1)
# Y = np.arange(-5, 5, 0.1)
# X, Y = np.meshgrid(X, Y)
# R = np.sqrt(X**2 + Y**2)
# Z = np.sin(R)
# 
# fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
# 
# artists = []
# cbar = None
# for i in range(5):
#     start = time()
#     Z = (-1)**i*i*np.sin(R)
#     surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis,
#                        linewidth=0, antialiased=False)
#     #ax.set_zlim(Z.min(), Z.max())
# 
#     # if cbar is None:
#     cbar = fig.colorbar(surf)
#     cax = cbar.ax
# 
#     artists.append([surf, cax])
# 
#     print(id(surf))
#     print(dir(cax))
# 
# ani = ArtistAnimation(fig=fig, artists=artists, interval=400)
# plt.show()

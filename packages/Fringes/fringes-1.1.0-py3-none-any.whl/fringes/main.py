# import numpy as np
#
# import pyqtgraph as pg
# import matplotlib.pyplot as plt
#
# import fringes
# from fringes import Fringes
#
# x = np.linspace(0, 1, 1000)
# y = 2 / np.pi * (np.arccos(x) - x * np.sqrt(1 - x**2))
# plt.figure()
# plt.plot(x, y)
# plt.grid(True)
# plt.xlabel(r"$\nu$ / $\nu_c$", fontsize=13)
# plt.ylabel("MTF", fontsize=13)
# plt.xticks(np.linspace(0, 1, 11), fontsize=13)
# plt.yticks(np.linspace(0, 1, 11), fontsize=13)
# plt.xlim(0, 1)
# plt.ylim(0, 1)
# plt.savefig("MTF.svg")
# plt.show()
#
# f = Fringes()
#
# fringes.documentation()
#
# # I = np.ones(shape=(1000, 1000)) * 230
# # In = f._simulate(I)
# # std = np.std(In)
#
# xi = np.random.uniform(0, 1, (f.D, f.X, f.Y))  # % 1
# xi[0] *= f.X
# xi[1] *= f.Y
# if f.indexing == "ij":
#     xi = xi[::-1]
#
# f.X = f.Y = 600  # 899
# f.N = 16
#
# f.l = 29, 31  # perfect
# f.l = 9.1, 10  # perfect
# f.l = 9, 10, 11  # perfect
# f.v = 9, 10  # perfect
# f.l = 9.1, 10.1  # perfect
# f.v = 9.1, 10.1  # perfect
# f.v = 9, 10, 11  # bad todo
# # f.v = 1, 10 todo
# # f.v = 21, 35  # bad todo
# # f.l = 99, 110  # perfect
# # f.v = 13, 7, 89  # bad todo
# # f.l = 13, 7, 89  # perfect
# # f.l = 9.1, 10.1, 11.1  # perfect
# # f.l = 90, 100, 110  # perfect
# f.v = 50.5, 20.2, 30.3
# f.l = 9, 10, 11
#
# f.dtype = float
# I = f.encode()
# dec = f.decode(I)
#
# # a = np.arange(100)
# # b = np.arange(1000)
# # c = np.meshgrid(a, b)
# # I = f.encode(c)
#
# # I = f.encode()
# # I_ = f._simulate(I)
#
# # import pyqtgraph as pg
# # pg.setConfigOptions(imageAxisOrder="row-major", useNumba=True)  # useCupy
# # pg.image(I)

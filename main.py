import math
import matplotlib.pyplot as plt
import numpy as np
import taichi as ti

ti.init(arch=ti.cpu)

vec2i = ti.types.vector(2, ti.i32)
vec3i = ti.types.vector(3, ti.i32)

vec2f = ti.types.vector(2, ti.f32)
vec3f = ti.types.vector(3, ti.f32)

# We evaluate on a PIxPI domain size, but sample it more dense
original_domain_size = (math.pi, math.pi)
sampling_size = (10, 10)
dim = 2
velocity_sample_field = ti.Vector.field(n=dim, dtype=ti.f32, shape=sampling_size)

@ti.func
# def phi(k: vec2i, p: vec2f) -> vec2f:
def phi(k, p):
    k_1, k_2, x, y = k[0], k[1], p[0], p[1]
    const = 1 / (k_1**2 + k_2**2)
    k_1x, k_2y = k_1*x, k_2*y
    x = +const * (k_2 * ti.sin(k_1x) * ti.cos(k_2y))
    y = -const * (k_1 * ti.cos(k_1x) * ti.sin(k_2y))
    return vec2f(x, y)

# Laplacian eigenfunctions on a P, IxPI square domain.
# - k = (k_1, k_2) are integers ("vector wave number")
# - p = (p_1, p_2, ...) is the point to be sampled in R^(dim)
@ti.kernel
def get_phi(k: vec2i, p: vec2f) -> vec2f:
    return phi(k, p)

@ti.kernel
def fill_values(k: vec2i):
    for x, y in velocity_sample_field:
        # 0..200 -> 0..pi
        p = vec2f(x, y) / sampling_size * original_domain_size
        value = phi(k, p)
        for k in ti.static(range(dim)):
            velocity_sample_field[x, y][k] = value[k]

fill_values(vec2i(1,1))
print(velocity_sample_field)

X, Y = np.mgrid[0:sampling_size[0], 0:sampling_size[1]]
X = Y = np.linspace(0, original_domain_size[0], sampling_size[0]) #square domain
U = velocity_sample_field[:, :][0].to_numpy()
V = velocity_sample_field[:, :][1].to_numpy()

plt.quiver(X, Y, U, V)
plt.show()
# gui = ti.GUI("laplacian eigenfunctions test", sampling_size)
# while gui.running:
    # gui.set_image(velocity_sample_field)
    # gui.show()

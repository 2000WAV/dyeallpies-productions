"""moderngl on the RTX 2060 for the renderers: a standalone context, meshes for MuJoCo's geoms, the
pinhole clip matrix that reproduces the scripts' own `project()` (x right, y = depth, z up; pixel
u = cx + f X/Y, v = cy - f Z/Y), a geometry pass that writes linear depth + body id, and the
2x -> 1x area-average accumulate pass for supersampling and motion blur.

Written 2026-09-12 to move the puppet bake off the CPU (8.7 s a frame in NumPy: 8 motion-blur
sub-samples of a 0.57 s shade + 0.30 s MuJoCo read-back + 0.15 s strings). MuJoCo now supplies the
poses only (mj_forward, microseconds); the rasterising happens here. Conventions:

- The framebuffer row 0 is the IMAGE TOP: the clip matrix flips y so `fbo.read()` returns the image
  in row order and texelFetch(ivec2(u, v)) addresses image pixel (u, v) directly.
- Depth is the camera-forward distance in metres (the same quantity MuJoCo's depth read-back gives),
  written as a colour channel (RG32F: depth, id; id = -1 where nothing was drawn) so the shading
  pass reads it exactly, not the non-linear z-buffer.
- Everything is single-sampled at the caller's scale (2x for the puppet); anti-aliasing is the area
  downsample in `accumulate()`.
"""
import numpy as np
import moderngl

GEOM_VS = """
#version 330
uniform mat4 P;          // clip = P * (X, Y_depth, Z_up, 1) in the camera-world frame
uniform mat4 M;          // local -> camera-world (rotation * size for ellipsoids, translation)
in vec3 in_pos;
out float v_depth;
void main() {
    vec4 w = M * vec4(in_pos, 1.0);
    v_depth = w.y;
    gl_Position = P * w;
}
"""

GEOM_FS = """
#version 330
uniform float body_id;
in float v_depth;
out vec2 o_g;            // (depth m, body id)
void main() { o_g = vec2(v_depth, body_id); }
"""

FULLSCREEN_VS = """
#version 330
in vec2 in_pos;
void main() { gl_Position = vec4(in_pos, 0.0, 1.0); }
"""

# 2x2 area average of (E * a, a): premultiplied at the high resolution, then averaged (INTER_AREA at
# scale 2), weighted by `w` (1/n for n motion-blur sub-samples) and added into the accumulation buffer.
# Optional string coverage `s` (R32F) is blended UNDER the premultiply, as the CPU path did:
# E' = E (1 - s) + col_s s, a' = max(a, s).
ACC_FS = """
#version 330
uniform sampler2D shaded;      // RGBA32F at 2x: E (linear light), a
uniform sampler2D strings;     // R32F at 2x: coverage (0 if unused)
uniform vec3 string_col;
uniform float w;
uniform int use_strings;
out vec4 o;
void main() {
    ivec2 p = ivec2(gl_FragCoord.xy) * 2;
    vec4 acc = vec4(0.0);
    for (int dy = 0; dy < 2; dy++) for (int dx = 0; dx < 2; dx++) {
        vec4 t = texelFetch(shaded, p + ivec2(dx, dy), 0);
        vec3 E = t.rgb; float a = t.a;
        if (use_strings == 1) {
            float s = texelFetch(strings, p + ivec2(dx, dy), 0).r;
            E = E * (1.0 - s) + string_col * s;
            a = max(a, s);
        }
        acc += vec4(E * a, a);
    }
    o = acc * (0.25 * w);
}
"""

# Jump-flood distance field (Rong & Tan 2006) on the g-buffer's ID channel: every figure pixel gets the
# position of the nearest pixel whose body ID differs from a 4-neighbour (a silhouette or a body-to-body
# edge). Feeds the neon style's "lit from inside" thickness gradient (item 06 section 1.4), which the
# CPU path computed with cv2.distanceTransform per body (0.19 s a frame). Passes start at `max_step`
# (the largest thickness of interest in px); farther pixels get an undefined seed, which is fine
# because every figure pixel is closer than that to its own edge.
JFA_INIT_FS = """
#version 330
uniform sampler2D g;
uniform ivec2 size;
out vec2 o;                    // the seed's own coordinates, or (-1, -1)
void main() {
    ivec2 p = ivec2(gl_FragCoord.xy);
    float id = texelFetch(g, p, 0).g;
    bool edge = false;
    for (int k = 0; k < 4; k++) {
        ivec2 d = (k == 0) ? ivec2(1, 0) : (k == 1) ? ivec2(-1, 0) : (k == 2) ? ivec2(0, 1) : ivec2(0, -1);
        ivec2 q = p + d;
        float idq = (q.x < 0 || q.y < 0 || q.x >= size.x || q.y >= size.y) ? -1.0 : texelFetch(g, q, 0).g;
        if (idq != id) edge = true;
    }
    o = edge ? vec2(p) + 0.5 : vec2(-1.0);
}
"""

JFA_STEP_FS = """
#version 330
uniform sampler2D src;
uniform ivec2 size;
uniform int step;
out vec2 o;
void main() {
    ivec2 p = ivec2(gl_FragCoord.xy); vec2 pc = vec2(p) + 0.5;
    vec2 best = texelFetch(src, p, 0).rg; float bd = (best.x < 0.0) ? 1e20 : dot(pc - best, pc - best);
    for (int dy = -1; dy <= 1; dy++) for (int dx = -1; dx <= 1; dx++) {
        ivec2 q = p + ivec2(dx, dy) * step;
        if (q.x < 0 || q.y < 0 || q.x >= size.x || q.y >= size.y) continue;
        vec2 s = texelFetch(src, q, 0).rg;
        if (s.x < 0.0) continue;
        float d = dot(pc - s, pc - s);
        if (d < bd) { bd = d; best = s; }
    }
    o = best;
}
"""


def pinhole_clip_matrix(f, cx, cy, W, H, near=0.05, far=2.0, half_pixel=True):
    """4x4 P with clip = P (X, Y, Z, 1), X right, Y depth (forward), Z up, so that the NDC lands on
    pixel u = cx + f X/Y, v = cy - f Z/Y with the framebuffer's row 0 at the image TOP (y flipped).
    half_pixel: integer pixel coordinates are pixel CENTRES (the OpenCV / NumPy convention the CPU
    shaders use: u = index - cx), so a point projecting to u = 790.0 must land at window x = 790.5."""
    if half_pixel: cx = cx + 0.5; cy = cy + 0.5
    A = (far + near) / (far - near); B = -2 * far * near / (far - near)
    P = np.array([[2 * f / W, 2 * cx / W - 1, 0, 0],
                  [0, -(1 - 2 * cy / H), -2 * f / H, 0],
                  [0, A, 0, B],
                  [0, 1, 0, 0]], np.float32)
    return P


def capsule_vertices(r, half_len, n_around=32, n_cap=12):
    """Triangle soup of a capsule along local z from -half_len to +half_len, radius r (MuJoCo's convention)."""
    return _revolve(lambda: _capsule_profile(r, half_len, n_cap), n_around)


def ellipsoid_vertices(a, b, c, n_around=32, n_lat=24):
    """Triangle soup of an ellipsoid with semi-axes a, b, c along local x, y, z."""
    v = _revolve(lambda: _sphere_profile(n_lat), n_around)
    return (v * np.array([a, b, c], np.float32)).astype(np.float32)


def _capsule_profile(r, hl, n_cap):
    # (radius, z) points from the bottom pole to the top pole
    t = np.linspace(-np.pi / 2, 0, n_cap + 1)
    bottom = np.stack([r * np.cos(t), -hl + r * np.sin(t)], 1)
    t = np.linspace(0, np.pi / 2, n_cap + 1)
    top = np.stack([r * np.cos(t), hl + r * np.sin(t)], 1)
    return np.concatenate([bottom, top], 0)


def _sphere_profile(n_lat):
    t = np.linspace(-np.pi / 2, np.pi / 2, n_lat + 1)
    return np.stack([np.cos(t), np.sin(t)], 1)


def _revolve(profile_fn, n_around):
    prof = profile_fn()                                   # (m, 2): radius, z
    ang = np.linspace(0, 2 * np.pi, n_around + 1)
    ca, sa = np.cos(ang), np.sin(ang)
    ring = lambda k: np.stack([prof[k, 0] * ca, prof[k, 0] * sa, np.full_like(ca, prof[k, 1])], 1)   # (n+1, 3)
    tris = []
    for k in range(len(prof) - 1):
        r0, r1 = ring(k), ring(k + 1)
        for j in range(n_around):
            tris += [r0[j], r1[j], r1[j + 1], r0[j], r1[j + 1], r0[j + 1]]
    return np.array(tris, np.float32)


def mujoco_geom_meshes(model):
    """One vertex array per geom: (geom id, body id, vertices (N,3) float32). Capsules and ellipsoids
    (the puppet's shapes); spheres and boxes are easy to add when a format needs them."""
    import mujoco
    out = []
    for g in range(model.ngeom):
        t = int(model.geom_type[g]); s = model.geom_size[g]
        if t == int(mujoco.mjtGeom.mjGEOM_CAPSULE):
            v = capsule_vertices(float(s[0]), float(s[1]))
        elif t == int(mujoco.mjtGeom.mjGEOM_ELLIPSOID):
            v = ellipsoid_vertices(float(s[0]), float(s[1]), float(s[2]))
        elif t == int(mujoco.mjtGeom.mjGEOM_SPHERE):
            v = ellipsoid_vertices(float(s[0]), float(s[0]), float(s[0]))
        else:
            raise NotImplementedError(f"geom type {t} (geom {g})")
        out.append((g, int(model.geom_bodyid[g]), v))
    return out


def geom_model_matrix(data, g):
    """local -> world 4x4 from MuJoCo's geom_xpos / geom_xmat (row-major 3x3)."""
    M = np.eye(4, dtype=np.float32)
    M[:3, :3] = np.asarray(data.geom_xmat[g], np.float32).reshape(3, 3)
    M[:3, 3] = data.geom_xpos[g]
    return M


class GL:
    """A standalone context and the helpers every renderer uses."""

    def __init__(self):
        self.ctx = moderngl.create_standalone_context()
        self._fs_vbo = self.ctx.buffer(np.array([-1, -1, 3, -1, -1, 3], np.float32).tobytes())
        self.geom_prog = self.program(GEOM_VS, GEOM_FS)
        self.acc_prog = self.program(FULLSCREEN_VS, ACC_FS)
        self._acc_vao = self.fullscreen_vao(self.acc_prog)
        self.jfa_init = self.program(FULLSCREEN_VS, JFA_INIT_FS); self._jfa_init_vao = self.fullscreen_vao(self.jfa_init)
        self.jfa_step = self.program(FULLSCREEN_VS, JFA_STEP_FS); self._jfa_step_vao = self.fullscreen_vao(self.jfa_step)
        self._jfa = {}

    def make_current(self):
        """Re-assert this context. Another GL user in the process (mujoco.Renderer's GLFW context, for
        the CPU-vs-GPU check) makes its own current whenever it renders; every pass here starts with this."""
        self.ctx.__enter__()

    def program(self, vs, fs):
        return self.ctx.program(vertex_shader=vs, fragment_shader=fs)

    def fullscreen_vao(self, prog):
        return self.ctx.simple_vertex_array(prog, self._fs_vbo, "in_pos")

    def tex(self, W, H, components, dtype="f4"):
        t = self.ctx.texture((W, H), components, dtype=dtype); t.filter = (moderngl.NEAREST, moderngl.NEAREST); return t

    def fbo(self, textures, depth=False):
        W, H = textures[0].size
        return self.ctx.framebuffer(color_attachments=list(textures), depth_attachment=self.ctx.depth_renderbuffer((W, H)) if depth else None)

    def mesh_vao(self, vertices, prog=None):
        vbo = self.ctx.buffer(np.ascontiguousarray(vertices, np.float32).tobytes())
        return self.ctx.simple_vertex_array(prog or self.geom_prog, vbo, "in_pos")

    def upload_mat4(self, prog, name, M):
        prog[name].write(np.ascontiguousarray(M.T, np.float32).tobytes())   # GLSL mat4 is column-major

    def geometry_pass(self, fbo, P, draws):
        """draws: iterable of (vao, model 4x4, body id). Writes (depth, id) into `fbo` (RG32F, cleared to (0, -1))."""
        self.make_current(); fbo.use(); fbo.clear(0.0, -1.0, 0.0, 0.0, depth=1.0)
        self.ctx.enable(moderngl.DEPTH_TEST); self.ctx.disable(moderngl.BLEND); self.ctx.disable(moderngl.CULL_FACE)
        self.upload_mat4(self.geom_prog, "P", P)
        for vao, M, bid in draws:
            self.upload_mat4(self.geom_prog, "M", M); self.geom_prog["body_id"].value = float(bid)
            vao.render(moderngl.TRIANGLES)

    def accumulate(self, acc_fbo, shaded_tex, w, strings_tex=None, string_col=(0, 0, 0)):
        """Add w * area-downsampled premultiplied (E a, a) of `shaded_tex` (2x) into acc_fbo (1x)."""
        self.make_current(); acc_fbo.use(); self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND); self.ctx.blend_func = (moderngl.ONE, moderngl.ONE); self.ctx.blend_equation = moderngl.FUNC_ADD
        shaded_tex.use(0); self.acc_prog["shaded"].value = 0
        if strings_tex is not None:
            strings_tex.use(1); self.acc_prog["strings"].value = 1; self.acc_prog["use_strings"].value = 1
            self.acc_prog["string_col"].value = tuple(float(c) for c in string_col)
        else:
            shaded_tex.use(1); self.acc_prog["strings"].value = 1; self.acc_prog["use_strings"].value = 0
        self.acc_prog["w"].value = float(w)
        self._acc_vao.render(moderngl.TRIANGLES)
        self.ctx.disable(moderngl.BLEND)

    def distance_field(self, g_tex, max_step=128):
        """Jump flood on the g-buffer's ID channel -> an RG32F texture holding, per pixel, the coordinates
        (pixel centres) of the nearest ID-edge pixel; distance = length(p + 0.5 - value). max_step: the
        first jump (a power of two >= the largest thickness that must be exact)."""
        self.make_current()
        W, H = g_tex.size
        if (W, H) not in self._jfa:
            t = [self.tex(W, H, 2), self.tex(W, H, 2)]
            self._jfa[(W, H)] = (t, [self.fbo([t[0]]), self.fbo([t[1]])])
        texs, fbos = self._jfa[(W, H)]
        self.ctx.disable(moderngl.DEPTH_TEST); self.ctx.disable(moderngl.BLEND)
        fbos[0].use(); g_tex.use(0); self.jfa_init["g"].value = 0; self.jfa_init["size"].value = (W, H); self._jfa_init_vao.render(moderngl.TRIANGLES)
        cur = 0; step = max_step
        self.jfa_step["size"].value = (W, H)
        while step >= 1:
            fbos[1 - cur].use(); texs[cur].use(0); self.jfa_step["src"].value = 0; self.jfa_step["step"].value = int(step)
            self._jfa_step_vao.render(moderngl.TRIANGLES)
            cur = 1 - cur; step //= 2
        return texs[cur]

    def read(self, fbo, components=4, dtype="f2"):
        """Read a framebuffer back as (H, W, components), image row order (row 0 = top, see the module doc)."""
        W, H = fbo.size
        self.make_current(); buf = fbo.read(components=components, dtype=dtype)
        return np.frombuffer(buf, dtype=np.float16 if dtype == "f2" else np.float32).reshape(H, W, components)

#!/usr/bin/env python3
"""
QHO Cheat Sheet — matplotlib mathtext only (no LaTeX install needed).
Uses only commands supported by matplotlib's built-in mathtext parser.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

# ── Colours ───────────────────────────────────────────────────────────────────
BG       = "#0d0d1a"
COL_BG   = "#11112a"
HDR_BG   = "#2e1065"
HDR_FG   = "#c4b5fd"
BOX_V    = "#1a1040"
BOX_G    = "#062a1e"
BOX_B    = "#061a2e"
BOX_Y    = "#221a00"
BDR_V    = "#7c3aed"
BDR_G    = "#059669"
BDR_B    = "#0284c7"
BDR_Y    = "#d97706"
TEXT     = "#e2e8f0"
DIM      = "#94a3b8"
ACCENT   = "#a78bfa"

# ── Primitives ────────────────────────────────────────────────────────────────
def rrect(ax, x, y, w, h, fc, ec, lw=0.8, r=0.008, zorder=1):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0.003,rounding_size={r}",
                       transform=ax.transAxes,
                       facecolor=fc, edgecolor=ec, linewidth=lw,
                       clip_on=False, zorder=zorder)
    ax.add_patch(p)

def hdr(ax, y, text):
    rrect(ax, 0, y - 0.002, 1.0, 0.038, HDR_BG, BDR_V, lw=0, zorder=2)
    ax.text(0.5, y + 0.015, text, transform=ax.transAxes,
            ha='center', va='center', fontsize=6.6, fontweight='bold',
            color=HDR_FG, zorder=3)

def sub(ax, x, y, text, c=ACCENT):
    ax.text(x, y, f"\u25b8  {text}", transform=ax.transAxes,
            ha='left', va='top', fontsize=5.9, fontweight='bold', color=c, zorder=3)

def tx(ax, x, y, s, sz=6.0, c=TEXT, ha='left'):
    ax.text(x, y, s, transform=ax.transAxes,
            ha=ha, va='top', fontsize=sz, color=c, zorder=3)

def mt(ax, x, y, s, sz=6.0, c=TEXT, ha='left'):
    """Render a mathtext string."""
    ax.text(x, y, s, transform=ax.transAxes,
            ha=ha, va='top', fontsize=sz, color=c, zorder=3, usetex=False)

def box(ax, x, y, w, h, lines, fc, ec, lw=0.9, sz=5.9, pad=0.011):
    rrect(ax, x, y - h, w, h, fc, ec, lw=lw, zorder=2)
    cy = y - pad
    for ln in lines:
        ax.text(x + pad * 0.8, cy, ln, transform=ax.transAxes,
                ha='left', va='top', fontsize=sz, color=TEXT, zorder=4, usetex=False)
        cy -= 0.021
    return cy

def note(ax, x, y, s, sz=5.6, c=DIM):
    ax.text(x, y, s, transform=ax.transAxes,
            ha='left', va='top', fontsize=sz, color=c, zorder=3)

def col_ax(fig, idx, xs, cw, y0, ch):
    a = fig.add_axes([xs[idx], y0, cw, ch])
    a.set_xlim(0, 1); a.set_ylim(0, 1)
    a.set_axis_off()
    rrect(a, 0, 0, 1, 1, COL_BG, "#1e2040", lw=0.4, r=0.004)
    return a

# ─────────────────────────────────────────────────────────────────────────────
# PAGE  (A4 landscape)
# ─────────────────────────────────────────────────────────────────────────────
FW, FH = 29.7 / 2.54, 21.0 / 2.54
fig = plt.figure(figsize=(FW, FH), facecolor=BG)

# Global title bar
ta = fig.add_axes([0, 0.93, 1, 0.07])
ta.set_axis_off()
ta.set_facecolor(HDR_BG)
ta.text(0.5, 0.65,
        "Quantum Harmonic Oscillator — Complete Cheat Sheet",
        transform=ta.transAxes, ha='center', va='center',
        fontsize=11, fontweight='bold', color=HDR_FG)
ta.text(0.5, 0.18,
        "Physics Voyage  \u00b7  Aditya Kumar  \u00b7  Shankar | Cohen-Tannoudji | Griffiths",
        transform=ta.transAxes, ha='center', va='center',
        fontsize=6.0, color=DIM)

# Four columns
CW = 0.235; GAP = 0.010; Y0 = 0.01; Y1 = 0.92; CH = Y1 - Y0
XS = [0.005 + i * (CW + GAP) for i in range(4)]
a1 = col_ax(fig, 0, XS, CW, Y0, CH)
a2 = col_ax(fig, 1, XS, CW, Y0, CH)
a3 = col_ax(fig, 2, XS, CW, Y0, CH)
a4 = col_ax(fig, 3, XS, CW, Y0, CH)

P = 0.03   # left text padding

# ═════════════════════════════════════════════════════════════════════════════
# COL 1 — Fundamentals + Ladder Operators
# ═════════════════════════════════════════════════════════════════════════════
ax = a1; y = 0.99

hdr(ax, y - 0.038, "\u2776  FUNDAMENTALS"); y -= 0.052

sub(ax, P, y, "Canonical Quantization"); y -= 0.022
mt(ax, P+.02, y, r"$[\hat{x},\,\hat{p}] = i\hbar$"); y -= 0.020
mt(ax, P+.02, y, r"Position rep: $\hat{p} = -i\hbar\,\partial/\partial x$"); y -= 0.026

sub(ax, P, y, "The QHO Hamiltonian"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.078,
        [r"$\hat{H} = \hat{p}^2/(2m) + m\omega^2\hat{x}^2/2$",
         r"$\quad = \hbar\omega(\hat{N} + 1/2)$",
         r"$\quad = \hbar\omega(\hat{a}^{\dagger}\hat{a} + 1/2)$"],
        BOX_V, BDR_V, sz=6.2); y -= 0.006

sub(ax, P, y, "Energy Eigenvalues"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.074,
        [r"$E_n = \hbar\omega(n + 1/2), \quad n=0,1,2,\ldots$",
         r"Zero-point: $E_0 = \hbar\omega/2$",
         r"Level spacing: $\Delta E = \hbar\omega$"],
        BOX_V, BDR_V); y -= 0.006

sub(ax, P, y, "Natural Length Scale"); y -= 0.022
mt(ax, P+.02, y, r"$x_0 = \sqrt{\hbar / m\omega}$   (oscillator length)"); y -= 0.020
mt(ax, P+.02, y, r"$\xi = x/x_0$   (dimensionless)"); y -= 0.022
y = box(ax, 0, y, 1.0, 0.030,
        [r"Virial:  $\langle T\rangle_n = \langle V\rangle_n = E_n/2$"],
        BOX_Y, BDR_Y); y -= 0.008

hdr(ax, y - 0.038, "\u2777  LADDER OPERATORS"); y -= 0.052

sub(ax, P, y, "Definitions"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.060,
        [r"$\hat{a} = \sqrt{m\omega/2\hbar}\,(\hat{x} + i\hat{p}/m\omega)$",
         r"$\hat{a}^{\dagger} = \sqrt{m\omega/2\hbar}\,(\hat{x} - i\hat{p}/m\omega)$"],
        BOX_V, BDR_V, sz=6.1); y -= 0.006

sub(ax, P, y, "Inverse Relations"); y -= 0.022
mt(ax, P+.02, y, r"$\hat{x} = (x_0/\sqrt{2})(\hat{a}+\hat{a}^{\dagger})$"); y -= 0.020
mt(ax, P+.02, y, r"$\hat{p} = i\hbar/(\sqrt{2}\,x_0)(\hat{a}^{\dagger}-\hat{a})$"); y -= 0.022
mt(ax, P+.02, y, r"Number op: $\hat{N}=\hat{a}^{\dagger}\hat{a},\; \hat{N}|n\rangle=n|n\rangle$"); y -= 0.026

sub(ax, P, y, "Commutators"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.074,
        [r"$[\hat{a},\,\hat{a}^{\dagger}] = 1$",
         r"$[\hat{N},\hat{a}]=-\hat{a},\quad [\hat{N},\hat{a}^{\dagger}]=+\hat{a}^{\dagger}$",
         r"$[\hat{H},\hat{a}]=-\hbar\omega\hat{a}$",
         r"$[\hat{H},\hat{a}^{\dagger}]=+\hbar\omega\hat{a}^{\dagger}$"],
        BOX_V, BDR_V); y -= 0.006

sub(ax, P, y, "Action on Fock States"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.094,
        [r"$\hat{a}|n\rangle = \sqrt{n}\;|n-1\rangle$",
         r"$\hat{a}^{\dagger}|n\rangle = \sqrt{n+1}\;|n+1\rangle$",
         r"$|n\rangle = (\hat{a}^{\dagger})^n / \sqrt{n!}\;|0\rangle$",
         r"$\hat{a}|0\rangle = 0$   (ground state)"],
        BOX_V, BDR_V); y -= 0.006

sub(ax, P, y, "Matrix Elements"); y -= 0.022
mt(ax, P+.01, y,
   r"$\langle m|\hat{x}|n\rangle = (x_0/\sqrt{2})[\sqrt{n}\,\delta_{m,n-1}+\sqrt{n+1}\,\delta_{m,n+1}]$",
   sz=5.5); y -= 0.020
mt(ax, P+.02, y, r"$\langle n|\hat{x}^2|n\rangle = x_0^2(n+1/2)$"); y -= 0.020
mt(ax, P+.02, y, r"$\langle n|\hat{p}^2|n\rangle = (\hbar^2/x_0^2)(n+1/2)$")

# ═════════════════════════════════════════════════════════════════════════════
# COL 2 — Wavefunctions + Time Evolution
# ═════════════════════════════════════════════════════════════════════════════
ax = a2; y = 0.99

hdr(ax, y - 0.038, "\u2778  WAVEFUNCTIONS"); y -= 0.052

sub(ax, P, y, "General Formula"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.058,
        [r"$\psi_n(x) = (m\omega/\pi\hbar)^{1/4}$",
         r"$\quad\quad \times H_n(\xi)/\sqrt{2^n n!}\cdot e^{-\xi^2/2}$"],
        BOX_V, BDR_V, sz=6.1); y -= 0.006

sub(ax, P, y, "Ground State (Gaussian)"); y -= 0.022
mt(ax, P+.02, y, r"$\psi_0(x) = (\pi x_0^2)^{-1/4}\exp(-x^2/2x_0^2)$", sz=5.9); y -= 0.020
note(ax, P+.02, y, "(Minimum uncertainty \u2014 no nodes)"); y -= 0.026

sub(ax, P, y, r"Hermite Polynomials $H_n(\xi)$"); y -= 0.022
for hn in [r"$H_0=1$", r"$H_1=2\xi$", r"$H_2=4\xi^2-2$",
           r"$H_3=8\xi^3-12\xi$", r"$H_4=16\xi^4-48\xi^2+12$"]:
    mt(ax, P+.06, y, hn, sz=5.9); y -= 0.018
mt(ax, P+.02, y, r"Recurrence: $H_{n+1}=2\xi H_n - 2nH_{n-1}$", sz=5.8); y -= 0.018
mt(ax, P+.02, y, r"Derivative:  $H_n' = 2nH_{n-1}$", sz=5.8); y -= 0.026

sub(ax, P, y, r"Key Properties of $\psi_n$"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.072,
        [r"Parity:  $\psi_n(-x) = (-1)^n\psi_n(x)$",
         r"Nodes:  $\psi_n$ has exactly $n$ zeros",
         r"Ortho: $\int\psi_m^*\psi_n\,dx = \delta_{mn}$"],
        BOX_Y, BDR_Y); y -= 0.006

sub(ax, P, y, r"Expectation Values in $|n\rangle$"); y -= 0.022
for ex in [r"$\langle\hat{x}\rangle=0,\quad\langle\hat{p}\rangle=0$",
           r"$\langle\hat{x}^2\rangle=x_0^2(n+1/2)$",
           r"$\Delta x = x_0\sqrt{n+1/2}$",
           r"$\Delta x\,\Delta p = (n+1/2)\hbar \geq \hbar/2$"]:
    mt(ax, P+.02, y, ex, sz=5.9); y -= 0.020
mt(ax, P+.02, y, r"Turning pts: $x_{\pm}=\pm\sqrt{2n+1}\;x_0$", sz=5.8); y -= 0.020
note(ax, P+.02, y, "Tunneling prob. for n=0: ~15.7%"); y -= 0.028

hdr(ax, y - 0.038, "\u2779  TIME EVOLUTION"); y -= 0.052

sub(ax, P, y, r"Schr\"{o}dinger Picture"); y -= 0.022
mt(ax, P+.02, y, r"$|n,t\rangle = e^{-i\omega(n+1/2)t}|n\rangle$"); y -= 0.020
mt(ax, P+.02, y, r"$|\Psi(t)\rangle=\sum_n c_n e^{-i\omega(n+1/2)t}|n\rangle$", sz=5.8); y -= 0.020
y = box(ax, 0, y, 1.0, 0.030,
        [r"Period of full revival:  $T = 2\pi/\omega$"],
        BOX_Y, BDR_Y); y -= 0.008

sub(ax, P, y, "Heisenberg Picture"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.074,
        [r"$\hat{a}(t) = e^{-i\omega t}\hat{a}(0)$",
         r"$\hat{a}^{\dagger}(t) = e^{+i\omega t}\hat{a}^{\dagger}(0)$",
         r"$\hat{x}(t)=x_0\cos\omega t\,\hat{x}(0)$",
         r"$\quad\quad + \sin(\omega t)/(m\omega)\,\hat{p}(0)$"],
        BOX_V, BDR_V); y -= 0.006

sub(ax, P, y, "Ehrenfest's Theorem"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.094,
        [r"$d\langle\hat{x}\rangle/dt = \langle\hat{p}\rangle/m$",
         r"$d\langle\hat{p}\rangle/dt = -m\omega^2\langle\hat{x}\rangle$",
         r"$\Rightarrow\; d^2\langle\hat{x}\rangle/dt^2 = -\omega^2\langle\hat{x}\rangle$",
         "Valid for ANY quantum state!"],
        BOX_G, BDR_G); y -= 0.006

sub(ax, P, y, "Wigner Function"); y -= 0.022
mt(ax, P+.01, y,
   r"$W(x,p) = \frac{1}{\pi\hbar}\int\psi^*(x{+}y)\psi(x{-}y)e^{2ipy/\hbar}dy$",
   sz=5.5); y -= 0.020
mt(ax, P+.02, y, r"$\int W\,dp=|\psi(x)|^2,\;\int W\,dx=|\phi(p)|^2$", sz=5.8); y -= 0.020
mt(ax, P+.02, y, r"$W_0 = \frac{1}{\pi\hbar}e^{-x^2/x_0^2-p^2x_0^2/\hbar^2}$", sz=5.8); y -= 0.018
note(ax, P+.02, y, "W < 0 possible \u2192 non-classical signature")

# ═════════════════════════════════════════════════════════════════════════════
# COL 3 — Coherent States
# ═════════════════════════════════════════════════════════════════════════════
ax = a3; y = 0.99

hdr(ax, y - 0.038, "\u277a  COHERENT STATES"); y -= 0.052

sub(ax, P, y, "Definition"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.050,
        [r"$\hat{a}|\alpha\rangle = \alpha|\alpha\rangle,\quad \alpha\in\mathbb{C}$",
         "(eigenstate of annihilation operator)"],
        BOX_G, BDR_G, sz=6.2); y -= 0.006

sub(ax, P, y, "Fock-State Expansion"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.040,
        [r"$|\alpha\rangle = e^{-|\alpha|^2/2}\sum_{n=0}^{\infty}\frac{\alpha^n}{\sqrt{n!}}|n\rangle$"],
        BOX_G, BDR_G, sz=6.4); y -= 0.006

sub(ax, P, y, "Displacement Operator"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.094,
        [r"$\hat{D}(\alpha)=e^{\alpha\hat{a}^{\dagger}-\alpha^*\hat{a}}$",
         r"$= e^{-|\alpha|^2/2}e^{\alpha\hat{a}^{\dagger}}e^{-\alpha^*\hat{a}}$  (BCH)",
         r"$|\alpha\rangle = \hat{D}(\alpha)|0\rangle$",
         r"$\hat{D}^{\dagger}\hat{a}\hat{D} = \hat{a}+\alpha$"],
        BOX_G, BDR_G, sz=6.1); y -= 0.006

sub(ax, P, y, "BCH Lemma"); y -= 0.022
mt(ax, P+.02, y, r"If $[A,[A,B]]=[B,[A,B]]=0$:"); y -= 0.020
mt(ax, P+.02, y, r"$e^{A+B}=e^A e^B e^{-[A,B]/2}$"); y -= 0.026

sub(ax, P, y, "Expectation Values"); y -= 0.022
mt(ax, P+.02, y, r"$\langle\hat{x}\rangle = \sqrt{2}\,x_0\,\mathrm{Re}(\alpha)$"); y -= 0.020
mt(ax, P+.02, y, r"$\langle\hat{p}\rangle = (\sqrt{2}\,\hbar/x_0)\,\mathrm{Im}(\alpha)$"); y -= 0.022
y = box(ax, 0, y, 1.0, 0.074,
        [r"$\Delta x = x_0/\sqrt{2}$   (independent of $\alpha$!)",
         r"$\Delta p = \hbar/(\sqrt{2}\,x_0)$   (independent of $\alpha$!)",
         r"$\Delta x\,\Delta p = \hbar/2$   \u2190 MINIMUM"],
        BOX_G, BDR_G); y -= 0.006

sub(ax, P, y, "Photon Number"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.074,
        [r"$P(n) = e^{-|\alpha|^2}|\alpha|^{2n}/n!$  [Poisson]",
         r"$\langle\hat{N}\rangle = |\alpha|^2,\quad \Delta N = |\alpha|$",
         "Mandel Q = 0   (classical boundary)"],
        BOX_G, BDR_G); y -= 0.006

sub(ax, P, y, "Time Evolution"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.060,
        [r"$\hat{U}(t)|\alpha\rangle = e^{-i\omega t/2}|\alpha e^{-i\omega t}\rangle$",
         r"Stays coherent!  $\alpha\to\alpha e^{-i\omega t}$",
         r"$\langle\hat{x}\rangle(t)=\sqrt{2}\,x_0|\alpha|\cos(\omega t-\phi)$"],
        BOX_G, BDR_G); y -= 0.006

sub(ax, P, y, "Overlaps & Over-Completeness"); y -= 0.022
mt(ax, P+.02, y, r"$|\langle\beta|\alpha\rangle|^2 = e^{-|\alpha-\beta|^2}$"); y -= 0.020
mt(ax, P+.02, y, r"$(1/\pi)\int|\alpha\rangle\langle\alpha|\,d^2\alpha = \hat{I}$  (over-complete)"); y -= 0.028

hdr(ax, y - 0.038, "\u277d  QUICK COMPARISON"); y -= 0.050

cols_x = [0.0, 0.27, 0.52, 0.76]
cols_w = [0.27, 0.25, 0.24, 0.24]
headers = ["State", r"$\Delta x$", r"$\Delta p$", r"$\Delta x\Delta p$"]
rows_data = [
    [r"Fock $|n\rangle$",          r"$x_0\sqrt{n+\frac{1}{2}}$",
     r"$\frac{\hbar}{x_0}\sqrt{n+\frac{1}{2}}$",  r"$\hbar(n+\frac{1}{2})$"],
    [r"Coherent $|\alpha\rangle$",  r"$x_0/\sqrt{2}$",
     r"$\hbar/\sqrt{2}\,x_0$",                      r"$\hbar/2$"],
    [r"Squeezed",                   r"$x_0 e^{-r}/\sqrt{2}$",
     r"$\hbar e^{r}/\sqrt{2}\,x_0$",                r"$\hbar/2$"],
]
# header row
rrect(ax, 0, y - 0.027, 1.0, 0.027, HDR_BG, BDR_V, lw=0.5, zorder=2)
for i, h in enumerate(headers):
    ax.text(cols_x[i] + cols_w[i]/2, y - 0.009, h, transform=ax.transAxes,
            ha='center', va='center', fontsize=5.2, color=HDR_FG,
            fontweight='bold', zorder=3)
y -= 0.029
for ri, row in enumerate(rows_data):
    rc = BOX_V if ri % 2 == 0 else "#161630"
    rrect(ax, 0, y - 0.026, 1.0, 0.026, rc, "#2a2a5a", lw=0.3, zorder=2)
    for i, cell in enumerate(row):
        ax.text(cols_x[i] + cols_w[i]/2, y - 0.009, cell,
                transform=ax.transAxes, ha='center', va='center',
                fontsize=5.0, color=TEXT, zorder=3)
    y -= 0.028

# ═════════════════════════════════════════════════════════════════════════════
# COL 4 — Squeezed States + Identities + LIGO
# ═════════════════════════════════════════════════════════════════════════════
ax = a4; y = 0.99

hdr(ax, y - 0.038, "\u277b  SQUEEZED STATES"); y -= 0.052

sub(ax, P, y, "Quadrature Operators"); y -= 0.022
mt(ax, P+.01, y, r"$\hat{X}_1=(\hat{a}+\hat{a}^{\dagger})/2,\quad\hat{X}_2=(\hat{a}-\hat{a}^{\dagger})/2i$", sz=5.7); y -= 0.020
mt(ax, P+.02, y, r"$[\hat{X}_1,\hat{X}_2]=i/2,\quad\Delta X_1\Delta X_2\geq 1/4$", sz=5.8); y -= 0.020
mt(ax, P+.02, y, r"Coherent: $\Delta X_1=\Delta X_2=1/2$", sz=5.8); y -= 0.026

sub(ax, P, y, "Squeeze Operator"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.050,
        [r"$\hat{S}(\xi)=\exp(\xi^*\hat{a}^2/2 - \xi\hat{a}^{\dagger 2}/2),\;\xi=re^{i\theta}$",
         r"$\hat{S}^{\dagger}=\hat{S}^{-1}=\hat{S}(-\xi)$  [unitary]"],
        BOX_B, BDR_B, sz=5.9); y -= 0.006

sub(ax, P, y, "Bogoliubov Transformation"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.074,
        [r"$\hat{S}^{\dagger}(r)\hat{a}\hat{S}(r)=\hat{a}\cosh r-\hat{a}^{\dagger}\sinh r$",
         r"$\hat{S}^{\dagger}(r)\hat{a}^{\dagger}\hat{S}(r)=\hat{a}^{\dagger}\cosh r-\hat{a}\sinh r$",
         r"New ops: $[\hat{b},\hat{b}^{\dagger}]=1$ \u2713"],
        BOX_B, BDR_B); y -= 0.006

sub(ax, P, y, r"Squeezed Vacuum $|0,r\rangle=\hat{S}(r)|0\rangle$"); y -= 0.024
y = box(ax, 0, y, 1.0, 0.094,
        [r"$\Delta x = x_0\,e^{-r}/\sqrt{2}$   \u2190 below SQL!",
         r"$\Delta p = \hbar\,e^{+r}/(\sqrt{2}\,x_0)$   \u2190 above SQL",
         r"$\Delta x\,\Delta p = \hbar/2$   \u2190 still minimum!",
         r"$\langle\hat{N}\rangle = \sinh^2 r$   (photons in vacuum!)"],
        BOX_B, BDR_B); y -= 0.006

sub(ax, P, y, "Fock expansion (even n only)"); y -= 0.022
mt(ax, P+.01, y,
   r"$|0,r\rangle = \frac{1}{\sqrt{\cosh r}}\sum_n \frac{(-\tanh r)^n\sqrt{(2n)!}}{2^n n!}|2n\rangle$",
   sz=5.4); y -= 0.022

sub(ax, P, y, "Squeezed Coherent State"); y -= 0.022
mt(ax, P+.02, y, r"$|\alpha,\xi\rangle = \hat{D}(\alpha)\hat{S}(\xi)|0\rangle$"); y -= 0.020
mt(ax, P+.02, y, "Mandel Q < 0  \u2192 sub-Poissonian (non-classical)"); y -= 0.028

hdr(ax, y - 0.038, "\u277c  LIGO & APPLICATIONS"); y -= 0.052

y = box(ax, 0, y, 1.0, 0.148,
        [r"LIGO measures phase quadrature $\hat{X}_2$",
         r"Shot noise (SQL): $\Delta X_2 = 1/2$",
         r"Phase-squeezed input: $\Delta X_2 \to \Delta X_2\,e^{-r}$",
         r"SNR improvement factor: $e^r$",
         r"LIGO O3 (2019): $r\approx 0.5$\u20131.0  (4\u20139 dB)",
         "\u2192 50% improvement in detection range",
         "Applications: CV-QKD, quantum teleportation,",
         "Gaussian boson sampling, spin squeezing"],
        BOX_B, BDR_B); y -= 0.006

hdr(ax, y - 0.038, "\u277e  KEY IDENTITIES"); y -= 0.052

sub(ax, P, y, "Gaussian Integrals"); y -= 0.022
mt(ax, P+.02, y, r"$\int_{-\infty}^{\infty}e^{-\alpha x^2}dx = \sqrt{\pi/\alpha}$"); y -= 0.020
mt(ax, P+.02, y, r"$\int_{-\infty}^{\infty}x^{2n}e^{-x^2}dx = (2n-1)!!/(2^n)\sqrt{\pi}$", sz=5.7); y -= 0.026

sub(ax, P, y, "Hermite Orthogonality"); y -= 0.022
mt(ax, P+.02, y, r"$\int H_m H_n e^{-\xi^2}d\xi = 2^n n!\sqrt{\pi}\,\delta_{mn}$", sz=5.7); y -= 0.026

sub(ax, P, y, "Uncertainty Relations"); y -= 0.022
mt(ax, P+.02, y, r"Heisenberg: $\Delta x\,\Delta p\geq\hbar/2$"); y -= 0.020
mt(ax, P+.02, y, r"Number-phase: $\Delta N\,\Delta\phi\geq 1/2$"); y -= 0.020
mt(ax, P+.02, y, r"Time-energy: $\Delta E\,\Delta t\geq\hbar/2$"); y -= 0.026

sub(ax, P, y, "Commutator Rules"); y -= 0.022
mt(ax, P+.02, y, r"$[\hat{A},\hat{B}\hat{C}]=[\hat{A},\hat{B}]\hat{C}+\hat{B}[\hat{A},\hat{C}]$", sz=5.7); y -= 0.020
mt(ax, P+.02, y, r"$[\hat{a},f(\hat{a}^{\dagger})]=f'(\hat{a}^{\dagger})$  for analytic $f$", sz=5.8); y -= 0.024

y = box(ax, 0, y, 1.0, 0.074,
        ["Shankar \u2014 Ch. 7   |   Griffiths \u2014 \u00a72.3",
         "Cohen-Tannoudji Vol. 1 Ch. V + Compl. GV",
         "Walls & Milburn \u2014 Quantum Optics",
         "PhysicsVoyage \u2192 Courses \u2192 QHO"],
        BOX_Y, BDR_Y)

# Footer
fa = fig.add_axes([0, 0.0, 1, 0.012])
fa.set_axis_off()
fa.text(0.5, 0.5,
        "Physics Voyage  \u00b7  adityakumarphy.github.io/PhysicsVoyage.github.io"
        "  \u00b7  Aditya Kumar  \u00b7  CC BY 4.0",
        transform=fa.transAxes, ha='center', va='center',
        fontsize=5.2, color=DIM)

# Save
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qho_cheatsheet.pdf')
fig.savefig(OUT, dpi=200, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
print(f"\u2705  Saved \u2192 {OUT}")
plt.close(fig)

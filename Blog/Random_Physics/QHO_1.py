# ============================================================
# QUANTUM HARMONIC OSCILLATOR
# FULL COMPUTATIONAL SOLUTION
# ============================================================

# ============================================================
# IMPORT LIBRARIES
# ============================================================

import os
import matplotlib

# Detect if running inside a Jupyter notebook
def is_jupyter():
    try:
        shell = get_ipython().__class__.__name__
        return shell == 'ZMQInteractiveShell'
    except NameError:
        return False

# Prevent Tkinter errors in headless environments, but allow Jupyter's inline backend
if not is_jupyter() and not ('DISPLAY' in os.environ and os.environ['DISPLAY']):
    matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt

from scipy.integrate import simpson
from scipy.special import eval_hermite
from scipy.special import factorial
from tabulate import tabulate
import matplotlib.animation as animation

# ============================================================
# USER INPUTS
# ============================================================

print("\n========== USER INPUT SECTION ==========\n")

# Initial wavefunction parameters/coefficients
A = float(input("Enter value of A : "))
B = float(input("Enter value of B : "))

# Physical parameters
m = float(input("Enter mass m (kg) : "))
omega = float(input("Enter angular frequency omega (rad/s) : "))

# Time input
t = float(input("Enter time t (seconds) : "))

# Number of energy eigenstates
n_max = int(input("Enter number of eigenstates : "))

# ============================================================
# PHYSICAL CONSTANT
# ============================================================

hbar = 1.0545718e-34  # J.s

# ============================================================
# NORMALIZATION CONSTANT
# From our Analytical Result
# ============================================================

N = (np.sqrt(15) * (B**0.25)) / (4 * (A**1.25))

print("\n========================================")
print("Normalization Constant")
print("========================================")

print(f"N = {N:.6e}")

# ============================================================
# HARMONIC OSCILLATOR NATURAL LENGTH SCALE
# ============================================================

# Characteristic quantum length scale
l = np.sqrt(hbar / (m * omega))

print(f"\nOscillator length scale l = {l:.6e} m")

# ============================================================
# SPATIAL GRID
# ============================================================

# Choose large enough region
x_max = 8 * l

# Spatial points
x = np.linspace(-x_max, x_max, 5000)

# Grid spacing
dx = x[1] - x[0]

# ============================================================
# INITIAL WAVEFUNCTION
# ============================================================

# Initialize with zeros
psi0 = np.zeros_like(x)

# Region where wavefunction exists
mask = x**2 <= (A / B)

# Define wavefunction
psi0[mask] = N * (A - B * x[mask]**2)

# ============================================================
# CHECK NORMALIZATION NUMERICALLY
# ============================================================

norm_initial = simpson(np.abs(psi0)**2, x)

print(f"\nInitial normalization check = {norm_initial:.6f}")

# ============================================================
# HARMONIC OSCILLATOR PARAMETER
# ============================================================

alpha = np.sqrt(m * omega / hbar)

# ============================================================
# FUNCTION : HARMONIC OSCILLATOR EIGENFUNCTION
# ============================================================

def psi_n(n, x):

    """
    Harmonic oscillator eigenfunction
    """

    # Normalization factor
    norm = (
        (alpha**2 / np.pi)**0.25
        /
        np.sqrt((2.0**n) * factorial(n))
    )

    # Hermite polynomial evaluation
    Hn = eval_hermite(n, alpha * x)

    # Eigenfunction
    return norm * Hn * np.exp(-0.5 * (alpha * x)**2)

# ============================================================
# COMPUTE EXPANSION COEFFICIENTS
# ============================================================

coefficients = []
probabilities = []
energies = []

table_data = []

for n in range(n_max):

    # nth eigenfunction
    psiN = psi_n(n, x)

    # Overlap integral
    cn = simpson(psiN * psi0, x)

    # Probability
    Pn = np.abs(cn)**2

    # Energy eigenvalue
    En = (n + 0.5) * hbar * omega

    # Store values
    coefficients.append(cn)
    probabilities.append(Pn)
    energies.append(En)

    # Store for table output
    table_data.append([n, En, cn, Pn])

# Print results in table format using tabulate
headers = ["State (n)", "Energy E_n (J)", "Coefficient c_n", "Probability P_n"]
print("\n======================================================================")
print("ENERGY EIGENSTATE INFORMATION")
print("======================================================================")
print(tabulate(table_data, headers=headers, tablefmt="fancy_grid", floatfmt=(".0f", ".6e", ".6e", ".6e")))
print("======================================================================\n")

# Convert lists to arrays
coefficients = np.array(coefficients)
probabilities = np.array(probabilities)
energies = np.array(energies)

# ============================================================
# CHECK TOTAL PROBABILITY
# ============================================================

total_probability = np.sum(probabilities)

print("\n========================================")
print("TOTAL PROBABILITY CHECK")
print("========================================")

print(f"Sum of probabilities = {total_probability:.6f}")

# ============================================================
# TIME EVOLUTION
# ============================================================

# Complex wavefunction
psi_t = np.zeros_like(x, dtype=complex)

for n in range(n_max):

    # Energy
    En = (n + 0.5) * hbar * omega

    # Time phase factor
    phase = np.exp(-1j * En * t / hbar)

    # Add contribution
    psi_t += coefficients[n] * psi_n(n, x) * phase

# ============================================================
# PROBABILITY DENSITY
# ============================================================

prob_density = np.abs(psi_t)**2

# ============================================================
# NORMALIZATION CHECK AFTER EVOLUTION
# ============================================================

norm_t = simpson(prob_density, x)

print("\n========================================")
print("TIME EVOLUTION NORMALIZATION CHECK")
print("========================================")

print(f"∫|ψ(x,t)|² dx = {norm_t:.6f}")

# ============================================================
# FINAL PROFESSIONAL PLOTTING SECTION
# ============================================================

# Natural time period
T = 2 * np.pi / omega

# Scale factor for physical coordinates:
# Coordinate u = x/l, wavefunction phi(u) = psi(x) * sqrt(l), probability |phi(u)|^2 = |psi(x)|^2 * l
phi0_scaled = psi0 * np.sqrt(l)
phit_scaled = psi_t * np.sqrt(l)
prob0_scaled = np.abs(phi0_scaled)**2
probt_scaled = np.abs(phit_scaled)**2
u = x / l

# Create a professional 2-panel static figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), layout="constrained")

# Clean, professional aesthetics settings
plot_colors = {
    'potential': '#64748b',       # Slate gray
    'initial_wf': '#94a3b8',      # Light slate
    'initial_prob': '#cbd5e1',    # Very light gray
    'evolved_wf_real': '#3b82f6', # Blue
    'evolved_wf_imag': '#f43f5e', # Rose/Coral
    'evolved_prob': '#8b5cf6',    # Violet
    'grid': '#e2e8f0'
}

# ------------------------------------------------------------
# PANEL 1: WAVEFUNCTIONS AND POTENTIAL WELL
# ------------------------------------------------------------

# Dimensionless potential well V(u) = 0.5 * u**2
V_u = 0.5 * u**2
ax1.plot(u, V_u, color=plot_colors['potential'], ls='--', lw=1.5, label='Potential $V(u) = 0.5 u^2$')

# Initial probability density (shaded)
ax1.fill_between(u, prob0_scaled, color=plot_colors['initial_wf'], alpha=0.2, label=r'$|\psi(u,0)|^2$ (Initial)')

# Evolved wavefunction & probability density at t
ax1.plot(u, np.real(phit_scaled), color=plot_colors['evolved_wf_real'], lw=1.5, label=r'$\mathrm{Re}[\psi(u,t)]$')
ax1.plot(u, np.imag(phit_scaled), color=plot_colors['evolved_wf_imag'], lw=1.5, ls=':', label=r'$\mathrm{Im}[\psi(u,t)]$')
ax1.fill_between(u, probt_scaled, color=plot_colors['evolved_prob'], alpha=0.3, label=r'$|\psi(u,t)|^2$ (Evolved)')

# Axis formatting
ax1.set_xlim(-5, 5)
ax1.set_ylim(-1.2, 1.8)
ax1.set_title("Wavefunction Dynamics & Potential Well", fontsize=12, fontweight='semibold', pad=12)
ax1.set_xlabel(r"Dimensionless Coordinate $u = x/l$", fontsize=10)
ax1.set_ylabel("Amplitude / Probability Density", fontsize=10)
ax1.grid(True, linestyle=':', alpha=0.6, color=plot_colors['grid'])
ax1.legend(loc='upper right', frameon=True, framealpha=0.9, facecolor='white', edgecolor='#cbd5e1')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# ------------------------------------------------------------
# PANEL 2: ENERGY SPECTRUM (|c_n|^2)
# ------------------------------------------------------------

n_vals = np.arange(n_max)
bars = ax2.bar(n_vals, probabilities, color=plot_colors['evolved_prob'], edgecolor='#7c3aed', alpha=0.8, width=0.5)

# Axis formatting
ax2.set_title("Energy Spectrum $|c_n|^2$", fontsize=12, fontweight='semibold', pad=12)
ax2.set_xlabel("Quantum Number $n$", fontsize=10)
ax2.set_ylabel("Probability $P_n$", fontsize=10)
ax2.set_xticks(n_vals)
ax2.grid(True, linestyle=':', alpha=0.6, color=plot_colors['grid'], axis='y')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Label probability values on top of bars
for bar in bars:
    height = bar.get_height()
    if height > 0.005:
        ax2.text(
            bar.get_x() + bar.get_width()/2.0, 
            height + 0.01, 
            f"{height:.3f}", 
            ha='center', 
            va='bottom', 
            fontsize=9, 
            color='#475569', 
            fontweight='medium'
        )

static_plot_path = os.path.join(os.path.dirname(__file__), "qho_static_plots.png")
plt.savefig(static_plot_path, dpi=300)
print(f"Static plots successfully saved to: {static_plot_path}")

# ============================================================
# ANIMATION: CONTINUOUS TIME EVOLUTION
# ============================================================

print("\nGenerating continuous time evolution animation...")

fig_anim, ax_anim = plt.subplots(figsize=(8, 5.5), layout="constrained")

# Setup axis and styling for animation
ax_anim.set_xlim(-5, 5)
ax_anim.set_ylim(-1.2, 1.8)
ax_anim.set_title(r"Wavefunction Time Evolution $\psi(u, t)$", fontsize=12, fontweight='semibold', pad=12)
ax_anim.set_xlabel(r"Dimensionless Coordinate $u = x/l$", fontsize=10)
ax_anim.set_ylabel("Amplitude / Probability Density", fontsize=10)
ax_anim.grid(True, linestyle=':', alpha=0.6, color=plot_colors['grid'])
ax_anim.spines['top'].set_visible(False)
ax_anim.spines['right'].set_visible(False)

# Plot the potential well in the background
ax_anim.plot(u, V_u, color=plot_colors['potential'], ls='--', lw=1.5, label='Potential $V(u)$')

# Initialize plots to be updated
line_prob, = ax_anim.plot([], [], color=plot_colors['evolved_prob'], lw=2.5, label=r'$|\psi(u, t)|^2$')
line_real, = ax_anim.plot([], [], color=plot_colors['evolved_wf_real'], lw=1.5, label=r'$\mathrm{Re}[\psi(u, t)]$')
line_imag, = ax_anim.plot([], [], color=plot_colors['evolved_wf_imag'], lw=1.5, ls=':', label=r'$\mathrm{Im}[\psi(u, t)]$')

# List-wrapped reference to permit updating inside the animation loop
fill_coll = [ax_anim.fill_between([], [], color=plot_colors['evolved_prob'], alpha=0.2)]

# Time text indicator
time_text = ax_anim.text(
    0.05, 0.93, '', 
    transform=ax_anim.transAxes, 
    fontsize=10, 
    fontweight='bold', 
    bbox=dict(facecolor='white', alpha=0.9, edgecolor='#e2e8f0', boxstyle='round,pad=0.5')
)

ax_anim.legend(loc='upper right', frameon=True, framealpha=0.9, facecolor='white', edgecolor='#cbd5e1')

# Configure animation frames (120 frames covering 2 full classical periods)
num_frames = 120
t_fracs = np.linspace(0, 2, num_frames)

def init():
    line_prob.set_data([], [])
    line_real.set_data([], [])
    line_imag.set_data([], [])
    time_text.set_text('')
    return line_prob, line_real, line_imag, time_text

def update(frame):
    t_frac = t_fracs[frame]
    t_val = t_frac * T
    
    # Calculate time-evolved wavefunction
    psi_t_anim = np.zeros_like(x, dtype=complex)
    for n in range(n_max):
        phase = np.exp(-1j * (n + 0.5) * omega * t_val)
        psi_t_anim += coefficients[n] * psi_n(n, x) * phase
        
    phi_t_anim = psi_t_anim * np.sqrt(l)
    prob_t_anim = np.abs(phi_t_anim)**2
    real_t_anim = np.real(phi_t_anim)
    imag_t_anim = np.imag(phi_t_anim)
    
    # Update line data
    line_prob.set_data(u, prob_t_anim)
    line_real.set_data(u, real_t_anim)
    line_imag.set_data(u, imag_t_anim)
    
    # Re-draw transparent filled area
    fill_coll[0].remove()
    fill_coll[0] = ax_anim.fill_between(u, prob_t_anim, color=plot_colors['evolved_prob'], alpha=0.2)
    
    # Update time text
    time_text.set_text(rf"$t = {t_frac:.2f}\,T$")
    
    return line_prob, line_real, line_imag, time_text

ani = animation.FuncAnimation(
    fig_anim, update, frames=num_frames, init_func=init, blit=False, interval=50
)

# Export the animation to a GIF
gif_path = os.path.join(os.path.dirname(__file__), "qho_evolution.gif")
print("Saving evolution animation to GIF... (this may take a few seconds)")
try:
    ani.save(gif_path, writer='pillow', fps=20)
    print(f"Animation successfully saved to: {gif_path}")
except Exception as e:
    print(f"Failed to save animation as GIF: {e}")

# Display animation inline inside Jupyter Notebooks
if is_jupyter():
    from IPython.display import HTML, display
    print("\nDisplaying interactive animation inline...")
    display(HTML(ani.to_jshtml()))
    # Close figures to avoid rendering static duplicate images in Jupyter output
    plt.close('all')
# Display GUI if available locally
elif ('DISPLAY' in os.environ and os.environ['DISPLAY']):
    plt.show()
# Headless run: close and save memory
else:
    plt.close('all')

print("\n========================================")
print("PROGRAM COMPLETED SUCCESSFULLY")
print("========================================")
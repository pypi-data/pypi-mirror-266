import numpy as np
import scipy.optimize
import pylab as plt

def fit_sin(tt, yy):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
    tt = np.array(tt)
    yy = np.array(yy)
    ff = np.fft.fftfreq(len(tt), (tt[1]-tt[0]))   # assume uniform spacing
    Fyy = abs(np.fft.fft(yy))
    guess_freq = abs(ff[np.argmax(Fyy[1:])+1])   # excluding the zero frequency "peak", which is related to offset
    guess_amp = 2*np.std(yy) * 2.**0.5
    guess_offset = np.mean(yy)
    guess = np.array([guess_amp, np.pi*guess_freq, 0., guess_offset])
    print("guess:" + str(guess))

    def sinfunc(t, A, w, p, c):
        return A * np.sin(w*t + p)**2 + c
    
    popt, pcov = scipy.optimize.curve_fit(sinfunc, tt, yy, p0=guess)
    A, w, p, c = popt
    # f = w/(2.*np.pi)
    f = w/(np.pi)
    fitfunc = lambda t: A * np.sin(w*t + p)**2 + c
    return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1./f, "fitfunc": fitfunc, "maxcov": np.max(pcov), "rawres": (guess,popt,pcov)}

##########################################################################################

#N, amp, omega, phase, offset, noise = 500, 1., 2., .5, 4., 0.1
#N, amp, omega, phase, offset, noise = 50, 1., .4, .5, 4., .2
#N, amp, omega, phase, offset, noise = 200, 1., 20, .5, 4., 0
#tt = np.linspace(0, 10, N)
#tt2 = np.linspace(0, 10, 10*N)
#yy = amp*np.sin(omega*tt + phase)**2 + offset
#yynoise = yy + noise*(np.random.random(len(tt))-0.5)

# res = fit_sin(tt, yynoise)
# print( "Amplitude=%(amp)s, Angular freq.=%(omega)s, phase=%(phase)s, offset=%(offset)s, Max. Cov.=%(maxcov)s" % res )
# 
# plt.plot(tt, yy, "-k", label="y", linewidth=2)
# plt.plot(tt, yynoise, "ok", label="y with noise")
# plt.plot(tt2, res["fitfunc"](tt2), color="blue", label="y fit curve", linewidth=2)
# plt.plot(tt, yy - res["fitfunc"](tt) + offset, label="y - fit", color='red')
# plt.legend(loc="best")
# plt.show()

import hiperwalk as hpw

# ##########################################################################################
# ### complete graph ###
# num_vert = 225
# g = hpw.Complete(num_vert)
# qw = hpw.Coined(g, marked={'-G' : [0]})
# psi0 = qw.uniform_state()
# states = qw.simulate((num_vert, 1), psi0)
# prob_dist = qw.success_probability(states)
# 
# timestamps = np.arange(num_vert + 1)
# 
# res = fit_sin(timestamps, prob_dist)
# t_opt = int(np.pi/4 * np.sqrt(num_vert))
# p_succ = 0.5


# ##########################################################################################
# ### grid graph ###
# dim = 41
# g = hpw.Grid(dim)
# num_vert = g.number_of_vertices()
# qw = hpw.Coined(g, shift="ff", marked={'-G' : [(0, 0)]})
# psi0 = qw.uniform_state()
# final_time = int(2*np.sqrt(num_vert * np.log(num_vert)))
# states = qw.simulate((final_time, 1), psi0)
# prob_dist = qw.success_probability(states)
# 
# timestamps = np.arange(final_time + 1)
# 
# res = fit_sin(timestamps, prob_dist)
# c = 0.33
# t_opt = int(np.pi * np.sqrt(c*num_vert*np.log(num_vert)) / (2*np.sqrt(2)))
# p_succ = 1/(2*c*np.log(num_vert))
# ##########################################################################################

##########################################################################################
### hypercube graph ###
dim = 12
g = hpw.Hypercube(dim)
num_vert = g.number_of_vertices()
marked = [2**(dim // 2), 10, 2**dim - 1, 5]
qw = hpw.Coined(g, shift="ff", marked={'-G' : marked})
psi0 = qw.uniform_state()
final_time = int(np.ceil(3*np.sqrt(num_vert)))
states = qw.simulate((final_time, 1), psi0)
prob_dist = qw.success_probability(states)

timestamps = np.arange(final_time + 1)

res = fit_sin(timestamps, prob_dist)
c = 2
# t_opt = int(np.pi*np.sqrt(c*num_vert) / 4)
t_opt = int(np.pi*np.sqrt(c*num_vert/len(marked)) / 4)
p_succ = 1/c
##########################################################################################

### printing and plotting ###
est_t_opt = int(res['period'] / 2)
print(est_t_opt)
est_t_opt = int( (np.pi/2 - res['phase'])/res['omega'] )
print("Estimated t_opt: " + str(est_t_opt))
print("Analytical t_opt: " + str(t_opt))
print("Estimated p_succ: " + str(prob_dist[est_t_opt]))
print("Analytical p_succ: " + str(p_succ))

plt.scatter(timestamps, prob_dist, label="prob dist")
plt.plot(timestamps, res["fitfunc"](timestamps), color="blue", label="fit")
plt.legend(loc="best")
plt.show()



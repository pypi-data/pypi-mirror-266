.. _sec-virtual_listener:

****************
Virtual listener
****************

The responses of the virtual listener are determined by a psychometric function (PF) that represents the proportion of "Yes" (I heard a sound) responses as a function of stimulus level. A logistic function ([KussEtAl2005]_; [KingdomAndPrins2016]_) is used:

.. math::
   :name: Logistic psychometric function

   \psi(x;\alpha,\beta,\gamma,\lambda)  = \gamma + (1-\gamma - \lambda) \left(\frac{1}{1+e^{\beta(\alpha-x)}}\right)

where :math:`\alpha` is the midpoint, :math:`\beta` the slope, :math:`\gamma` the lower asymptote, and :math:`\lambda` the upper asymptote of the PF; :math:`x` is the stimulus level at which the function is evaluated.

The midpoint is the stimulus level at which the PF reaches half of its amplitude, so for a virtual listener with :math:`\gamma = 0` and :math:`\lambda=0`, the midpoint :math:`\alpha` is the stimulus level at which the listener gives (on the long run) 50% of "Yes" responses. The Hughson-Westlake procedure declares the threshold as the lowest point at which the listener gives at least 50% "Yes" responses (over at least 3 trials). Therefore, the threshold (as defined with the Hughson-Westlake) procedure will be generally found at or above the midpoint :math:`\alpha` [MarshallAndJesteadt1986]_. Obviously it is possible that on occasion the threshold will be found at a lower level because the proportion of "Yes" responses found over a small number of trials may differ from the proportion of correct responses expected over the long run.

The slope :math:`\beta` controls the speed at which the PF goes from its lowest to its highest value as the stimulus level increases. Rather than reasoning in terms of slope, it is often more intuitive to reason in terms of "width" of the PF ([Alcalá-QuintanaAndGarcía-Pérez2004]_; [KussEtAl2005]_), which is inversely correlated with the slope. ``audiometry_trainer`` asks the user the desired 90% width of the PF in order to generate case files. For example, a width of 5 dB indicates that the function (for a virtual listener with :math:`\gamma = 0` and :math:`\lambda=0`) goes from 5% to 95% probability of a "Yes" response within a change in stimulus level of 5 dB.

The lower asymptote, :math:`\gamma`, represents the propensity of the listener to respond "Yes", even in the absence of a stimulus. This propensity is not formally measured in the clinical audiometry procedure [Barr-HamiltonEtAl1969]_ [MarshallAndJesteadt1986]_. In a Yes/No task with temporally marked trials, in which a signal is presented or not, it would correspond to the false alarm rate. For example, a listener with a :math:`\gamma` of 0.1 would respond "Yes" in 1 out of 10 trials in which no stimulus was presented. Under the perspective of signal detection theory this propensity of the listener to say "Yes" reflects an internal criterion which can be more or less conservative. Although the actual measurement of :math:`\gamma` requires "blank" trials without a signal, the criterion determines the decision process also when a signal is present, hence the value of :math:`\gamma` will affect the PF underlying the clinical audiometry procedure. 

The upper asymptote, :math:`\lambda` is the lapse rate, it represents the tendency of the listener to fail responding because of attentional lapses, even for a stimulus that is clearly audible.

When performing clinical masking with ``audiometry_trainer``, the effect of the noise is to shift the midpoint of the PF, *if* the noise level arriving at the cochlea, in dB of effective masking (EM) units, exceeds the midpoint of the PF. The shift is equal to the level by which the noise exceeds the midpoint. For example, if the noise level is 5 dB above the unmasked midpoint, the masked midpoint will be 5 dB higher.

Because the effect of the noise varies between listeners, another variable ``msk_diff`` causes a further shift to the PF midpoint in the presence of noise. ``msk_diff`` is randomly drawn from a Normal distribution with a mean of 0 and a standard deviation of 3 for each frequency/ear combination when case files are generated. These values reflect the fact that interindividual differences in the effectiveness of the masking noise will be in the range of ~10 dB (this is the reason why a 10 dB safety pad is typically added to calculated noise levels in masking formulas). It should be noted that ``msk_diff`` can be either positive or negative. A positive ``msk_diff`` means that the masking effect is greater than average (the PF midpoint is shifted upward), while a negative ``msk_diff`` means that the masking effect is smaller than average (the PF midpoint is shifted downward).



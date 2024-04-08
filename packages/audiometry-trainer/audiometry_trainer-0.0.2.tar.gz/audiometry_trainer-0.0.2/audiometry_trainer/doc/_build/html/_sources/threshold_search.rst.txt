.. _sec-threshold_search:

*****************
Threshold search
***************** 

The ``S`` marker in the audiogram window shows the current stimulus level. You can use the up/down arrow keys on the keyboard to change stimulus level and the right/left arrow keys to change stimulus frequency. Pressing the spacebar "plays" the stimulus to the virtual listener (the ``Stimulus light`` at the bottom will light up). If the virtual listener heard the stimulus the ``Response light`` on the left side will light up. You can also use the ``Play stimulus`` button to play the stimulus, but using the keyboard is generally more efficient.

On the left panels there are buttons to either mark the current level as the threshold, mark a no response or a masking dilemma. Keyboard shortcuts for these three actions are ``T`` to mark the threshold, ``N`` for no response, and ``X`` for masking dilemma. Pressing the ``Delete`` or the ``D`` keys will delete the currently marked response.

``audiometry_trainer`` keeps counts of acending responses to assist in determining threshold according to the Hughson-Westlake procedure. If you do not wish to see these response counts uncheck the ``Show response counts`` checkbox.

If the ``Show response ear`` checkbox is checked the response light will be red if the response is coming from the right ear, blue if it is coming from the left ear, and white if both ears respond to the tone. This is useful to illustrate cross-hearing. This can also simulate the situation in which the audiologist asks the listener whether they're hearing the sound in their left or right ear to ensure, for example, that masking is effectively silencing the non-test ear. This latter usage should not be abused while training to learn clinical audiometry because while ``audiometry_trainer`` will always indicate the correct answer regarding the response ear, in real life listeners may not always be reliable in indicating the response ear, therefore you should not rely on this.

The ``Auto. thresh. search`` button performs an automatic threshold search using the Hughson-Westlake procedure for all the frequencies using the currently selected transducer for channel 1. The automatic threshold search is available only for the measurement of unmasked thresholds. This feature was added because the most interesting aspect of audiometry is the measurement of masked thresholds (if needed), so one can quickly get the unmasked thresholds using the automatic thresholds to then move on to determine if masking is needed, and if so measure the masked thresholds.

The ``Show estimated thresholds`` checkboxes can be used to show/hide the thresholds that have been measured. By default all the measured thresholds are shown on the audiogram, but sometimes this generates clutter (e.g. when masked thresholds are obtained after unmasked ones) and it may be useful to hide some of the estimated thresholds.

To compare the thresholds that you've estimated with the actual expected thresholds by using the ``Show actual thresholds`` checkboxes at the bottom of the left panel. Virtual patients are modeled via psychometric functions (see Section :ref:`sec-virtual_listener`) and the "actual" thresholds are computed via Monte Carlo simulations (see Section :ref:`sec-generate_case`), therefore, exact matches to the estimated thresholds should not always be expected, but they should generally be very close.They "actual" thresholds are the median thresholds obtained over a large number of simulations; 95% confidence intervals for these thresholds can be shown by checking the ``CI`` checkboxes.

.. _sec-internals:

****************************
Internals
****************************


Estimated thresholds are stored on a dict of the form
```
self.est_aud['unmasked']['bone']['right']
```

matplotlib plotting points are stored in a parallel dict with the same structure:
```
self.pnts['unmasked']['bone']['right']
```

another dictionary with a similar structure stores important parameters regarding the audiometric data and the plots:
```
self.plot_prms['unmasked']['air']['left']
```

in particular the `thresh_status` key
```
self.plot_prms['masked']['bone']['right']['thresh_status']
```
is used to differentiate between points marked as thresholds ('found' key), no responses at the maximum level ('NR' key), and masking dilemmas ('MD' key). Note that in each of these cases the stimulus level at which the cursor is located when marking the threshold will be stored in `self.est_aud`. The `thresh_status` key in the `self.plot_prms` dict allows to treat them differently according to the cases seen above.

Another key stored in `self.plot_prms` is used to indicate whether points for a given transducer and masking status should be displayed on the plot or hidden:

```
self.plot_prms['masked']['bone']['right']['visible']
```

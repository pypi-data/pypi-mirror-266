.. _sec-masking:

*******
Masking
*******

In order to mask the non-test ear (NTE) during air-conduction audiometry set the ``Chan. 2 level`` to the desired value and make sure the ``Chan. 2 ON`` checkbox is checked.

For masking during bone conduction audiometry, additionnally, the ``Non-test ear status`` has to be set to ``Earphone on`` (otherwise the software considers that the noise is being played through the earphone, but the earphone is not on the listener's ear, so no noise actually arrives at the listener's ear). ``audiometry_trainer`` automatically sets the ``Non-test ear status`` to ``Earphone on`` when you check the ``Chan. 2 ON`` checkbox. This small complication for masking in bone conduction audiometry is due to the fact that ``audiometry_trainer`` lets you test bone conduction thresholds either with the NTE uncovered, or with the NTE covered by the earphone while the earphone is not playing any noise. This is useful to measure the size of the occlusion effect (see :ref:`subsubsec-measure_OE`).

The ``Lock channels`` checkbox can be used to "lock" the test ear (TE) and NTE channels so that changing the signal level sent to the TE changes the noise level sent to the NTE by the same amount.

======================
Interaural attenuation
======================

Interaural attenuation (IA) values for supra-aural and insert earphones are drawn randomly for each case from a uniform distribution. The lower and upper limits of the distribution are frequency specific and are based on the min/max IA values reported by [MunroAndAgnew1999]_. For frquencies that were not tested in [MunroAndAgnew1999]_ the values of an adjacent frequency are used. The lower and upper values of the uniform distribution as a function of frequency are shown in Table table-IA_supra_ for supra-aural earphones and in Table table-IA_insert_ for insert earphones.

.. _table-IA_supra:
.. table:: Lower and upper limits of the uniform distribution for IA for supra-aural headphones.
   :widths: auto

   ==========  =====  ======
     Freq.      Low    High
   ==========  =====  ======
   125 Hz        48     74
   250 Hz        48     74
   500 Hz        44     74
   750 Hz        44     74
   1000 Hz       48     72
   1500 Hz       48     72
   2000 Hz       44     74
   3000 Hz       56     82
   4000 Hz       50     82
   6000 Hz       44     82
   8000 Hz       42     80
   ==========  =====  ======

.. _table-IA_insert:
.. table:: Lower and upper limits of the uniform distribution for IA for insert earphones.
   :widths: auto

   ==========  =====  ======
     Freq.      Low    High
   ==========  =====  ======
   125 Hz        72     103
   250 Hz        72     103
   500 Hz        64     96
   750 Hz        64     96
   1000 Hz       58     86
   1500 Hz       58     86
   2000 Hz       56     82
   3000 Hz       58     96
   4000 Hz       72     98
   6000 Hz       54     96
   8000 Hz       62     82
   ==========  =====  ======

IA values for bone conduction (BC) are drawn for each case from a uniform distribution. The lower and upper values of the uniform distribution as a function of frequency are shown in Table table-IA_bone_. These values were chosen to reflect the observation that IA for bone conducted stimuli using a mastoid placement is essentially zero at 250 Hz and increases up to ~15 dB at 4000 Hz ([Studebaker1967]_; [Gelfand2016]_). More nuanced data on IA for BC are available [Stenfelt2012]_ and may be integrated to future versions of ``audiometry_trainer``.

.. _table-IA_bone:
.. table:: Lower and upper limits of the uniform distribution for IA for bone conduction.
   :widths: auto

   ==========  =====  ======
     Freq.      Low    High
   ==========  =====  ======
   125 Hz        0       0
   250 Hz        0       0
   500 Hz        0       2
   750 Hz        0       3
   1000 Hz       0       4
   1500 Hz       0       5
   2000 Hz       0       7
   3000 Hz       0      10
   4000 Hz       0      15
   6000 Hz       0      15
   8000 Hz       0      15
   ==========  =====  ======

================
Occlusion effect
================

For cases without a conductive hearing loss the size of the occlusion effect (OE) is drawn randomly for each case and frequency from a uniform distribution. The lower and upper values for the uniform distribution as a function of frequency is shown in Table table-OE_supra_ for supra-aural headphones and Table table-OE_insert_ for insert earphones. These values were chosen to reflect approximately the range of values found in various studies and summarized in [Gelfand2016]_.

.. _table-OE_supra:
.. table:: Lower and upper limits of the uniform distribution for the OE for supra-aural earphones. For frequencies > 1000 Hz the OE is always zero.
   :widths: auto

   ==========  =====  ======
     Freq.      Low    High
   ==========  =====  ======
   125 Hz       15      30
   125 Hz       15      30
   500 Hz        8      26
   750 Hz        8      26
   1000 Hz       4      12
   ==========  =====  ======

.. _table-OE_insert:
.. table:: Lower and upper limits of the uniform distribution for the OE for insert earphones. For frequencies > 1000 Hz the OE is always zero.
   :widths: auto

   ==========  =====  ======
     Freq.      Low    High
   ==========  =====  ======
   125 Hz        2      10
   125 Hz        2      10
   500 Hz        2      10
   750 Hz        2      10
   1000 Hz       2      10
   ==========  =====  ======
	    
The OE is absent when a conductive/mixed hearing with an air-bone gap (ABG) >= 20 dB is present [MartinEtAl1974]_. For this reason, if there is an ABG >= 20 dB the OE is set to zero. For ABGs between 0 and 20 dB the size of the OE is scaled by the ABG using the following equation:

.. math::
   :name: Occlusion effect scaling by the air-bone gap

   OE_{out} = OE_{inp} - OE_{inp} (ABG/20)

where :math:`OE_{inp}` is the OE before the scaling and :math:`OE_{out}` is the OE after the scaling. This means that the size of the OE is progressively reduced as the ABG increases, reaching zero for an ABG of 20 dB.

The OE will affect the level of the signal arriving at the NTE while masking during BC testing [Gelfand2016]_. One thing that is rarely mentioned is that the OE, or better the lack of an OE when the TE is not occluded during BC testing, will affect the calculation of the noise level arriving at the TE. The IA values for the earphones used to deliver the masking noise to the NTE are based on the assumption that both ears are occluded with the earphones. If one ear is not occluded with an earphone, the IA for sounds arriving to that ear is increased by the size of the OE ([Yacullo1997]_,  [Turner2004]_). This means that for low-frequency sounds that are affected by this issue, while the OE increases the minimum masking level (because the signal level will be boosted at the NTE), this increase is "offset" in a way by a parallel increaseof the the maximum masking level (because the IA for the noise will be larger).

.. _subsubsec-measure_OE:

------------------------------
Measuring the occlusion effect
------------------------------

Some authors (e.g. [Gelfand2016]_) recommend measuring the OE in individual listeners to determine the value to be used in masking formulas. This can be done by covering the NTE with the earphone and measuring BC thresholds, without presenting any masking noise to the NTE. The thresholds obtained in this "earphones ON" condition can then be compared to those obtained without covering the NTE to estimate the magnitude of the occlusion effect [MartinEtAl1974]_. To obtain BC thresholds with the NTE covered by an earphone, but without delivery of masking noise, in ``audiometry_trainer`` you need to set the ``Non-test ear status`` to ``Earphones ON`` and make sure that the ``Chan. 2 ON`` checkbox is uncheked. The size of the OE measured in this way will depend on the earphones used for ``Chan. 2``, so make sure that you select the same earphone type that will be later used to deliver the masking noise.

A limitation of this technique is that in some cases it can underestimate the size of the OE ([FagelsonAndMartin1994]_; [Yacullo1997]_). This may happen in the case of a listener with NTE BC thresholds close to the lower output limits of the BC vibrator. For example, if the listener has a BC threshold of 0 dB HL and the BC vibrator has a lower output level limit of -20 dB HL, then OEs larger than 20 dB would be underestimated. This may also happen if the TE BC threshold is lower than the NTE BC threshold. Suppose for example that the TE BC threshold is 20 dB HL, the NTE BC threshold is 30 dB HL, and the NTE OE is 30 dB. The threshold recorded in the unoccluded condition will be 20 dB HL and when the NTE is occluded the threshold recorded will be 0 dB HL; the difference between the two, the estimated OE, will be 20 dB rather than the actual NTE OE of 30 dB. If masking is used only to confirm that the unmasked TE BC threshold is genuine, underestimating the OE will be of no consequence; the TE had the lowest threshold to start with, so undermasking will simply confirm, "in the wrong way", a correct decision that that threshold was coming from the TE. If the estimated OE is used for a full-blown masked threshold search, the masked TE BC threshold may be lower than the unmasked one because the NTE will be undermasked. 


===============
Central masking
===============

``audiometry_trainer`` simulates central masking effects by increasing the TE threshold when the level of the masking noise at the NTE is audible to the virtual patient. The size of the central masking effect drawn randomly for each virtual listener and each frequency from a folded normal distribution with a mean of zero and a standard deviation of 3. This reflects the fact that central masking effects are usually small, in the order of 5 dB [Yacullo1997]_. 

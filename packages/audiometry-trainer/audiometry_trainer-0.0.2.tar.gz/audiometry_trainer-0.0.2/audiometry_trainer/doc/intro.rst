.. _sec-intro:

*************
Introduction
*************

``audiometry_trainer`` is a software for practicing clinical audiometry. The software simulates patient's responses loaded from case files, and allows practicing essential aspects of the procedure including air/bone conduction threshold search and clinical masking. Figure :ref:`fig-audiometry_trainer_screenshot` shows the main window of ``audiometry_trainer``.

.. _fig-audiometry_trainer_screenshot:

.. figure:: Figures/audiometry_trainer.png
   :scale: 50%
   :alt: Screenshot of the ``audiometry_trainer`` interface

   Screenshot of the ``audiometry_trainer`` interface

At startup ``audiometry_trainer`` selects a random virtual patient case file (you can load other case files from the ``File menu``). The ``S`` marker in the audiogram window shows the current stimulus level. The threshold search is more conveniently conducted using the keyboard rather than via mouse button presses. Press the space bar to play the stimulus (the ``Stimulus light`` at the bottom will light up). If the virtual patient heard the stimulus the ``Response light`` on the left side will light up. Use the up/down arrows to change the stimulus level. Once you've found the threshold, press the ``T`` key to mark it on the audiogram plot. Use the right/left arrow keys to move to another frequency.

You can compare the thresholds that you've estimated with the actual expected thresholds by using the ``Show actual thresholds`` checkboxes at the bottom of the left panel. Virtual patients are modeled via psychometric functions and the "actual" thresholds are computed via Monte Carlo simulations: they are the median thresholds obtained over a large number of simulations; 95% confidence intervals can be shown by checking the ``CI`` checkboxes.

You can move from right to left era and from air to bone conduction stimulation by selecting the desired options in the drop-down menus for ``Channel 1`` at the top of the left panel. ``Channel 2`` is used to deliver masking noise. To turn on ``Channel 2`` check the ``Chan. 2 ON`` check box on the right panel, a ``M`` marker on the audiogram window will indicate the masking noise level. You can use the ``Chan. 2 level`` box and the up/down arrows on its right to set the masker level. You can also ``lock`` the ``Channel 1`` and ``Channel 2`` levels using the ``Lock Channels`` checkbox on the left panel; when the channels are locked increasing/decreasing the stimulus level by a given amount will automatically change the masker level by the the same amount.

A detailed description of all the features of ``audiometry_trainer`` will be given in the next sections. Section :ref:`sec-installation` tells how to obtain and install ``audiometry_trainer``. Sections :ref:`sec-threshold_search` and :ref:`sec-masking` explain how to perform a threshold search and how to use masking, respectively.

``audiometry_trainer`` uses psychometric functions to model virtual patient responses. Responses are not deterministic (always yes/no above/below a given stimulus level) but probabilistic, with the probability of a response increasing with the stimulus level. This adds realism to the software because in real life the responses of patients are not deterministic. Section :ref:`sec-virtual_listener` details the psychometric function model used by ``audiometry_trainer``.

``audiometry_trainer`` allows you to create and use your own case files. This functionality can be accessed via the ``Generate case`` button under the ``File menu`` and will be described in detail in Section :ref:`sec-generate_case`. Some knowledge of the psychometric function model used by ``audiometry_trainer`` will be needed to create your own case files.

Section :ref:`sec-user_interface` covers in details all the user interface. Section :ref:`sec-internals` describes some of the internals of the software and is mainly intended for developers rather than for end users.

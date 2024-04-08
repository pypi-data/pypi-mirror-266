# -*- coding: utf-8 -*-
#   Copyright (C) 2023-2024 Samuele Carcagno <sam.carcagno@gmail.com>
#   This file is part of audiometry_trainer

#    audiometry_trainer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    audiometry_trainer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with audiometry_trainer.  If not, see <http://www.gnu.org/licenses/>.

import copy
import numpy as np

def acoust_values(seed=None):

    rng = np.random.default_rng(seed=seed)
    
    OE_supra = {}
    OE_supra[125] = rng.uniform(low=15, high=30)
    OE_supra[250] = rng.uniform(low=15, high=30)
    OE_supra[500] = rng.uniform(low=8, high=26)
    OE_supra[750] = rng.uniform(low=8, high=26)
    OE_supra[1000] = rng.uniform(low=4, high=12)
    OE_supra[1500] = 0
    OE_supra[2000] = 0
    OE_supra[3000] = 0
    OE_supra[4000] = 0
    OE_supra[6000] = 0
    OE_supra[8000] = 0

    OE_circum = {}
    OE_circum[125] = rng.uniform(low=10, high=22)
    OE_circum[250] = rng.uniform(low=10, high=22)
    OE_circum[500] = rng.uniform(low=4, high=16)
    OE_circum[750] = rng.uniform(low=4, high=16)
    OE_circum[1000] = rng.uniform(low=2, high=8)
    OE_circum[1500] = 0
    OE_circum[2000] = 0
    OE_circum[3000] = 0
    OE_circum[4000] = 0
    OE_circum[6000] = 0
    OE_circum[8000] = 0

    OE_insert = {}
    OE_insert[125] = rng.uniform(low=2, high=10)
    OE_insert[250] = rng.uniform(low=2, high=10)
    OE_insert[500] = rng.uniform(low=2, high=10)
    OE_insert[750] = rng.uniform(low=2, high=10)
    OE_insert[1000] = 0
    OE_insert[1500] = 0
    OE_insert[2000] = 0
    OE_insert[3000] = 0
    OE_insert[4000] = 0
    OE_insert[6000] = 0
    OE_insert[8000] = 0

    IA_supra = {}
    IA_supra[125] = rng.uniform(low=48, high=74)
    IA_supra[250] = rng.uniform(low=48, high=74)
    IA_supra[500] = rng.uniform(low=44, high=74)
    IA_supra[750] = rng.uniform(low=44, high=74)
    IA_supra[1000] = rng.uniform(low=48, high=72)
    IA_supra[1500] = rng.uniform(low=48, high=72)
    IA_supra[2000] = rng.uniform(low=44, high=74)
    IA_supra[3000] = rng.uniform(low=56, high=82)
    IA_supra[4000] = rng.uniform(low=50, high=82)
    IA_supra[6000] = rng.uniform(low=44, high=82)
    IA_supra[8000] = rng.uniform(low=42, high=80)

    IA_insert = {}
    IA_insert[125] = rng.uniform(low=72, high=103)
    IA_insert[250] = rng.uniform(low=72, high=103)
    IA_insert[500] = rng.uniform(low=64, high=96)
    IA_insert[750] = rng.uniform(low=64, high=96)
    IA_insert[1000] = rng.uniform(low=58, high=86)
    IA_insert[1500] = rng.uniform(low=58, high=86)
    IA_insert[2000] = rng.uniform(low=56, high=82)
    IA_insert[3000] = rng.uniform(low=58, high=96)
    IA_insert[4000] = rng.uniform(low=72, high=98)
    IA_insert[6000] = rng.uniform(low=54, high=96)
    IA_insert[8000] = rng.uniform(low=62, high=82)

    ##invented but minimum 50
    IA_circum = {}
    IA_circum[125] = rng.uniform(low=50, high=75)
    IA_circum[250] = rng.uniform(low=50, high=75)
    IA_circum[500] = rng.uniform(low=55, high=75)
    IA_circum[750] = rng.uniform(low=55, high=75)
    IA_circum[1000] = rng.uniform(low=50, high=75)
    IA_circum[1500] = rng.uniform(low=50, high=75)
    IA_circum[2000] = rng.uniform(low=50, high=75)
    IA_circum[3000] = rng.uniform(low=60, high=85)
    IA_circum[4000] = rng.uniform(low=55, high=85)
    IA_circum[6000] = rng.uniform(low=50, high=85)
    IA_circum[8000] = rng.uniform(low=50, high=85)

    IA_bone = {}
    IA_bone[125] = rng.uniform(low=0, high=0)
    IA_bone[250] = rng.uniform(low=0, high=0)
    IA_bone[500] = rng.uniform(low=0, high=2)
    IA_bone[750] = rng.uniform(low=0, high=3)
    IA_bone[1000] = rng.uniform(low=0, high=4)
    IA_bone[1500] = rng.uniform(low=0, high=5)
    IA_bone[2000] = rng.uniform(low=0, high=7)
    IA_bone[3000] = rng.uniform(low=0, high=10)
    IA_bone[4000] = rng.uniform(low=0, high=15)
    IA_bone[6000] = rng.uniform(low=0, high=15)
    IA_bone[8000] = rng.uniform(low=0, high=15)

    ## Bone conduction attenuation limit, Berger DI foam plug + lead muff
    BCAL = {}
    BCAL[125] = rng.normal(loc=46.5, scale=6)
    BCAL[250] = rng.normal(loc=50.8, scale=6.2)
    BCAL[500] = rng.normal(loc=56.8, scale=5.2)
    BCAL[750] = rng.normal(loc=51.9, scale=4.43)
    BCAL[1000] = rng.normal(loc=47, scale=3.5)
    BCAL[1500] = rng.normal(loc=42.85, scale=3.2)
    BCAL[2000] = rng.normal(loc=38.7, scale=2.9)
    BCAL[3000] = rng.normal(loc=47.5, scale=3.7)
    BCAL[4000] = rng.normal(loc=49.3, scale=3.7)
    BCAL[6000] = rng.normal(loc=48.7, scale=4.6)
    BCAL[8000] = rng.normal(loc=48.7, scale=4.1)


    ## Supra ambient attenuation Berger and Killion 1989
    supra_amb_att_mean = {}
    supra_amb_att_mean[125] = 6.5
    supra_amb_att_mean[250] = 5.4
    supra_amb_att_mean[500] = 6
    supra_amb_att_mean[1000] = 11.7
    supra_amb_att_mean[2000] = 17
    supra_amb_att_mean[4000] = 22.2
    supra_amb_att_mean[8000] = 22.7
    supra_amb_att_mean[750] = np.interp(np.log(750), np.log([500, 1000]), [supra_amb_att_mean[500], supra_amb_att_mean[1000]])
    supra_amb_att_mean[1500] = np.interp(np.log(1500), np.log([1000, 1500]), [supra_amb_att_mean[1000], supra_amb_att_mean[2000]])
    supra_amb_att_mean[3000] = np.interp(np.log(3000), np.log([2000, 4000]), [supra_amb_att_mean[2000], supra_amb_att_mean[4000]])
    supra_amb_att_mean[6000] = np.interp(np.log(6000), np.log([4000, 8000]), [supra_amb_att_mean[4000], supra_amb_att_mean[8000]])


    supra_amb_att_sd = {}
    supra_amb_att_sd[125] = 4.8
    supra_amb_att_sd[250] = 5
    supra_amb_att_sd[500] = 5.3
    supra_amb_att_sd[1000] = 4.8
    supra_amb_att_sd[2000] = 5.6
    supra_amb_att_sd[4000] = 5.4
    supra_amb_att_sd[8000] = 6.3
    supra_amb_att_sd[750] = np.sqrt(np.interp(np.log(750), np.log([500, 1000]), [supra_amb_att_sd[500]**2, supra_amb_att_sd[1000]**2]))
    supra_amb_att_sd[1500] = np.sqrt(np.interp(np.log(1500), np.log([1000, 1500]), [supra_amb_att_sd[1000]**2, supra_amb_att_sd[2000]**2]))
    supra_amb_att_sd[3000] = np.sqrt(np.interp(np.log(3000), np.log([2000, 4000]), [supra_amb_att_sd[2000]**2, supra_amb_att_sd[4000]**2]))
    supra_amb_att_sd[6000] = np.sqrt(np.interp(np.log(6000), np.log([4000, 8000]), [supra_amb_att_sd[4000]**2, supra_amb_att_sd[8000]**2]))

    supra_amb_att = {}
    supra_amb_att[125] = rng.normal(loc=supra_amb_att_mean[125], scale=supra_amb_att_sd[125])
    supra_amb_att[250] = rng.normal(loc=supra_amb_att_mean[250], scale=supra_amb_att_sd[250])
    supra_amb_att[500] = rng.normal(loc=supra_amb_att_mean[500], scale=supra_amb_att_sd[500])
    supra_amb_att[750] = rng.normal(loc=supra_amb_att_mean[750], scale=supra_amb_att_sd[750])
    supra_amb_att[1000] = rng.normal(loc=supra_amb_att_mean[1000], scale=supra_amb_att_sd[1000])
    supra_amb_att[1500] = rng.normal(loc=supra_amb_att_mean[1500], scale=supra_amb_att_sd[1500])
    supra_amb_att[2000] = rng.normal(loc=supra_amb_att_mean[2000], scale=supra_amb_att_sd[2000])
    supra_amb_att[3000] = rng.normal(loc=supra_amb_att_mean[3000], scale=supra_amb_att_sd[3000])
    supra_amb_att[4000] = rng.normal(loc=supra_amb_att_mean[4000], scale=supra_amb_att_sd[4000])
    supra_amb_att[6000] = rng.normal(loc=supra_amb_att_mean[6000], scale=supra_amb_att_sd[6000])
    supra_amb_att[8000] = rng.normal(loc=supra_amb_att_mean[8000], scale=supra_amb_att_sd[8000])


    ## Insert ambient attenuation Berger and Killion 1989
    insert_amb_att_mean = {}
    insert_amb_att_mean[125] = 32.3
    insert_amb_att_mean[250] = 35.8
    insert_amb_att_mean[500] = 37.6
    insert_amb_att_mean[1000] = 36.6
    insert_amb_att_mean[2000] = 33.1
    insert_amb_att_mean[4000] = 39.4
    insert_amb_att_mean[8000] = 42.5
    insert_amb_att_mean[750] = np.interp(np.log(750), np.log([500, 1000]), [insert_amb_att_mean[500], insert_amb_att_mean[1000]])
    insert_amb_att_mean[1500] = np.interp(np.log(1500), np.log([1000, 1500]), [insert_amb_att_mean[1000], insert_amb_att_mean[2000]])
    insert_amb_att_mean[3000] = np.interp(np.log(3000), np.log([2000, 4000]), [insert_amb_att_mean[2000], insert_amb_att_mean[4000]])
    insert_amb_att_mean[6000] = np.interp(np.log(6000), np.log([4000, 8000]), [insert_amb_att_mean[4000], insert_amb_att_mean[8000]])

    insert_amb_att_sd = {}
    insert_amb_att_sd[125] = 6.4
    insert_amb_att_sd[250] = 6.3
    insert_amb_att_sd[500] = 5.4
    insert_amb_att_sd[1000] = 3.5
    insert_amb_att_sd[2000] = 3.2
    insert_amb_att_sd[4000] = 3.5
    insert_amb_att_sd[8000] = 3.4
    insert_amb_att_sd[750] = np.sqrt(np.interp(np.log(750), np.log([500, 1000]), [insert_amb_att_sd[500]**2, insert_amb_att_sd[1000]**2]))
    insert_amb_att_sd[1500] = np.sqrt(np.interp(np.log(1500), np.log([1000, 1500]), [insert_amb_att_sd[1000]**2, insert_amb_att_sd[2000]**2]))
    insert_amb_att_sd[3000] = np.sqrt(np.interp(np.log(3000), np.log([2000, 4000]), [insert_amb_att_sd[2000]**2, insert_amb_att_sd[4000]**2]))
    insert_amb_att_sd[6000] = np.sqrt(np.interp(np.log(6000), np.log([4000, 8000]), [insert_amb_att_sd[4000]**2, insert_amb_att_sd[8000]**2]))


    insert_amb_att = {}
    insert_amb_att[125] = rng.normal(loc=insert_amb_att_mean[125], scale=insert_amb_att_sd[125])
    insert_amb_att[250] = rng.normal(loc=insert_amb_att_mean[250], scale=insert_amb_att_sd[250])
    insert_amb_att[500] = rng.normal(loc=insert_amb_att_mean[500], scale=insert_amb_att_sd[500])
    insert_amb_att[750] = rng.normal(loc=insert_amb_att_mean[750], scale=insert_amb_att_sd[750])
    insert_amb_att[1000] = rng.normal(loc=insert_amb_att_mean[1000], scale=insert_amb_att_sd[1000])
    insert_amb_att[1500] = rng.normal(loc=insert_amb_att_mean[1500], scale=insert_amb_att_sd[1500])
    insert_amb_att[2000] = rng.normal(loc=insert_amb_att_mean[2000], scale=insert_amb_att_sd[2000])
    insert_amb_att[3000] = rng.normal(loc=insert_amb_att_mean[3000], scale=insert_amb_att_sd[3000])
    insert_amb_att[4000] = rng.normal(loc=insert_amb_att_mean[4000], scale=insert_amb_att_sd[4000])
    insert_amb_att[6000] = rng.normal(loc=insert_amb_att_mean[6000], scale=insert_amb_att_sd[6000])
    insert_amb_att[8000] = rng.normal(loc=insert_amb_att_mean[8000], scale=insert_amb_att_sd[8000])

    #invented: just taking the values from insert ambient attenuation
    circum_amb_att = {}
    circum_amb_att[125] = rng.normal(loc=insert_amb_att_mean[125], scale=insert_amb_att_sd[125])
    circum_amb_att[250] = rng.normal(loc=insert_amb_att_mean[250], scale=insert_amb_att_sd[250])
    circum_amb_att[500] = rng.normal(loc=insert_amb_att_mean[500], scale=insert_amb_att_sd[500])
    circum_amb_att[750] = rng.normal(loc=insert_amb_att_mean[750], scale=insert_amb_att_sd[750])
    circum_amb_att[1000] = rng.normal(loc=insert_amb_att_mean[1000], scale=insert_amb_att_sd[1000])
    circum_amb_att[1500] = rng.normal(loc=insert_amb_att_mean[1500], scale=insert_amb_att_sd[1500])
    circum_amb_att[2000] = rng.normal(loc=insert_amb_att_mean[2000], scale=insert_amb_att_sd[2000])
    circum_amb_att[3000] = rng.normal(loc=insert_amb_att_mean[3000], scale=insert_amb_att_sd[3000])
    circum_amb_att[4000] = rng.normal(loc=insert_amb_att_mean[4000], scale=insert_amb_att_sd[4000])
    circum_amb_att[6000] = rng.normal(loc=insert_amb_att_mean[6000], scale=insert_amb_att_sd[6000])
    circum_amb_att[8000] = rng.normal(loc=insert_amb_att_mean[8000], scale=insert_amb_att_sd[8000])

    ## earplug att Berger et al 2003
    ## this is the attenuation to both air and body paths measured using thresholds, air-only attenuation may actually be higher
    earplug_att_mean = {}
    earplug_att_mean[125] = 39.9
    earplug_att_mean[250] = 44.4
    earplug_att_mean[500] = 47.8
    earplug_att_mean[1000] = 43.7
    earplug_att_mean[2000] = 37.4
    earplug_att_mean[4000] = 44.4
    earplug_att_mean[8000] = 47
    earplug_att_mean[750] = np.interp(np.log(750), np.log([500, 1000]), [earplug_att_mean[500], earplug_att_mean[1000]])
    earplug_att_mean[1500] = np.interp(np.log(1500), np.log([1000, 1500]), [earplug_att_mean[1000], earplug_att_mean[2000]])
    earplug_att_mean[3000] = np.interp(np.log(3000), np.log([2000, 4000]), [earplug_att_mean[2000], earplug_att_mean[4000]])
    earplug_att_mean[6000] = np.interp(np.log(6000), np.log([4000, 8000]), [earplug_att_mean[4000], earplug_att_mean[8000]])

    earplug_att_sd = {}
    earplug_att_sd[125] = 5.5
    earplug_att_sd[250] = 4.8
    earplug_att_sd[500] = 3.5
    earplug_att_sd[1000] = 4.2
    earplug_att_sd[2000] = 2.9
    earplug_att_sd[4000] = 3.7
    earplug_att_sd[8000] = 4.7
    earplug_att_sd[750] = np.sqrt(np.interp(np.log(750), np.log([500, 1000]), [earplug_att_sd[500]**2, earplug_att_sd[1000]**2]))
    earplug_att_sd[1500] = np.sqrt(np.interp(np.log(1500), np.log([1000, 1500]), [earplug_att_sd[1000]**2, earplug_att_sd[2000]**2]))
    earplug_att_sd[3000] = np.sqrt(np.interp(np.log(3000), np.log([2000, 4000]), [earplug_att_sd[2000]**2, earplug_att_sd[4000]**2]))
    earplug_att_sd[6000] = np.sqrt(np.interp(np.log(6000), np.log([4000, 8000]), [earplug_att_sd[4000]**2, earplug_att_sd[8000]**2]))

    earplug_att = {}
    earplug_att[125] = rng.normal(loc=earplug_att_mean[125], scale=earplug_att_sd[125])
    earplug_att[250] = rng.normal(loc=earplug_att_mean[250], scale=earplug_att_sd[250])
    earplug_att[500] = rng.normal(loc=earplug_att_mean[500], scale=earplug_att_sd[500])
    earplug_att[750] = rng.normal(loc=earplug_att_mean[750], scale=earplug_att_sd[750])
    earplug_att[1000] = rng.normal(loc=earplug_att_mean[1000], scale=earplug_att_sd[1000])
    earplug_att[1500] = rng.normal(loc=earplug_att_mean[1500], scale=earplug_att_sd[1500])
    earplug_att[2000] = rng.normal(loc=earplug_att_mean[2000], scale=earplug_att_sd[2000])
    earplug_att[3000] = rng.normal(loc=earplug_att_mean[3000], scale=earplug_att_sd[3000])
    earplug_att[4000] = rng.normal(loc=earplug_att_mean[4000], scale=earplug_att_sd[4000])
    earplug_att[6000] = rng.normal(loc=earplug_att_mean[6000], scale=earplug_att_sd[6000])
    earplug_att[8000] = rng.normal(loc=earplug_att_mean[8000], scale=earplug_att_sd[8000])


    ## earmold attenuation
    earmold_att_mean = copy.deepcopy(earplug_att_mean)
    earmold_att_sd = copy.deepcopy(earplug_att_sd)

    earmold_att = {}
    earmold_att[125] = rng.normal(loc=earmold_att_mean[125], scale=earmold_att_sd[125])
    earmold_att[250] = rng.normal(loc=earmold_att_mean[250], scale=earmold_att_sd[250])
    earmold_att[500] = rng.normal(loc=earmold_att_mean[500], scale=earmold_att_sd[500])
    earmold_att[750] = rng.normal(loc=earmold_att_mean[750], scale=earmold_att_sd[750])
    earmold_att[1000] = rng.normal(loc=earmold_att_mean[1000], scale=earmold_att_sd[1000])
    earmold_att[1500] = rng.normal(loc=earmold_att_mean[1500], scale=earmold_att_sd[1500])
    earmold_att[2000] = rng.normal(loc=earmold_att_mean[2000], scale=earmold_att_sd[2000])
    earmold_att[3000] = rng.normal(loc=earmold_att_mean[3000], scale=earmold_att_sd[3000])
    earmold_att[4000] = rng.normal(loc=earmold_att_mean[4000], scale=earmold_att_sd[4000])
    earmold_att[6000] = rng.normal(loc=earmold_att_mean[6000], scale=earmold_att_sd[6000])
    earmold_att[8000] = rng.normal(loc=earmold_att_mean[8000], scale=earmold_att_sd[8000])


    ## Digitized from Cubick et al. 2022
    dome_open_att_mean = {}
    dome_open_att_mean[125] = 0.2
    dome_open_att_mean[250] = 0.3
    dome_open_att_mean[500] = 0.13
    dome_open_att_mean[750] = 0.27
    dome_open_att_mean[1000] = 0.13
    dome_open_att_mean[1500] = 1.7
    dome_open_att_mean[2000] = 0.3
    dome_open_att_mean[3000] = -2.2
    dome_open_att_mean[4000] = -2.2
    dome_open_att_mean[6000] = -2.6
    dome_open_att_mean[8000] = -0.8

    dome_open_att_sd = {}
    dome_open_att_sd[125] = 1.5
    dome_open_att_sd[250] = 1.1
    dome_open_att_sd[500] = 0.9
    dome_open_att_sd[750] = 0.8
    dome_open_att_sd[1000] = 1.1
    dome_open_att_sd[1500] = 2.1
    dome_open_att_sd[2000] = 1.6
    dome_open_att_sd[3000] = 2.7
    dome_open_att_sd[4000] = 2.9
    dome_open_att_sd[6000] = 3.1
    dome_open_att_sd[8000] = 4.8

    dome_open_att = {}
    dome_open_att[125] = rng.normal(loc=dome_open_att_mean[125], scale=dome_open_att_sd[125])
    dome_open_att[250] = rng.normal(loc=dome_open_att_mean[250], scale=dome_open_att_sd[250])
    dome_open_att[500] = rng.normal(loc=dome_open_att_mean[500], scale=dome_open_att_sd[500])
    dome_open_att[750] = rng.normal(loc=dome_open_att_mean[750], scale=dome_open_att_sd[750])
    dome_open_att[1000] = rng.normal(loc=dome_open_att_mean[1000], scale=dome_open_att_sd[1000])
    dome_open_att[1500] = rng.normal(loc=dome_open_att_mean[1500], scale=dome_open_att_sd[1500])
    dome_open_att[2000] = rng.normal(loc=dome_open_att_mean[2000], scale=dome_open_att_sd[2000])
    dome_open_att[3000] = rng.normal(loc=dome_open_att_mean[3000], scale=dome_open_att_sd[3000])
    dome_open_att[4000] = rng.normal(loc=dome_open_att_mean[4000], scale=dome_open_att_sd[4000])
    dome_open_att[6000] = rng.normal(loc=dome_open_att_mean[6000], scale=dome_open_att_sd[6000])
    dome_open_att[8000] = rng.normal(loc=dome_open_att_mean[8000], scale=dome_open_att_sd[8000])

    ## Digitized from Cubick et al. 2022
    dome_tulip_att_mean = {}
    dome_tulip_att_mean[125] = -0.3
    dome_tulip_att_mean[250] = 0.1
    dome_tulip_att_mean[500] = 0.5
    dome_tulip_att_mean[750] = 0.9
    dome_tulip_att_mean[1000] = 0.5
    dome_tulip_att_mean[1500] = 0.9
    dome_tulip_att_mean[2000] = -1.97
    dome_tulip_att_mean[3000] = -9
    dome_tulip_att_mean[4000] = -6.1
    dome_tulip_att_mean[6000] = -5
    dome_tulip_att_mean[8000] = -2.7

    dome_tulip_att_sd = {}
    dome_tulip_att_sd[125] = 1.3
    dome_tulip_att_sd[250] = 0.6
    dome_tulip_att_sd[500] = 0.64
    dome_tulip_att_sd[750] = 1.1
    dome_tulip_att_sd[1000] = 2.1
    dome_tulip_att_sd[1500] = 4.3
    dome_tulip_att_sd[2000] = 3.9
    dome_tulip_att_sd[3000] = 3.8
    dome_tulip_att_sd[4000] = 3.7
    dome_tulip_att_sd[6000] = 4.5
    dome_tulip_att_sd[8000] = 4.4

    dome_tulip_att = {}
    dome_tulip_att[125] = rng.normal(loc=dome_tulip_att_mean[125], scale=dome_tulip_att_sd[125])
    dome_tulip_att[250] = rng.normal(loc=dome_tulip_att_mean[250], scale=dome_tulip_att_sd[250])
    dome_tulip_att[500] = rng.normal(loc=dome_tulip_att_mean[500], scale=dome_tulip_att_sd[500])
    dome_tulip_att[750] = rng.normal(loc=dome_tulip_att_mean[750], scale=dome_tulip_att_sd[750])
    dome_tulip_att[1000] = rng.normal(loc=dome_tulip_att_mean[1000], scale=dome_tulip_att_sd[1000])
    dome_tulip_att[1500] = rng.normal(loc=dome_tulip_att_mean[1500], scale=dome_tulip_att_sd[1500])
    dome_tulip_att[2000] = rng.normal(loc=dome_tulip_att_mean[2000], scale=dome_tulip_att_sd[2000])
    dome_tulip_att[3000] = rng.normal(loc=dome_tulip_att_mean[3000], scale=dome_tulip_att_sd[3000])
    dome_tulip_att[4000] = rng.normal(loc=dome_tulip_att_mean[4000], scale=dome_tulip_att_sd[4000])
    dome_tulip_att[6000] = rng.normal(loc=dome_tulip_att_mean[6000], scale=dome_tulip_att_sd[6000])
    dome_tulip_att[8000] = rng.normal(loc=dome_tulip_att_mean[8000], scale=dome_tulip_att_sd[8000])

    ## Digitized from Cubick et al. 2022
    dome_2_vents_att_mean = {}
    dome_2_vents_att_mean[125] = 0.1
    dome_2_vents_att_mean[250] = 0.145
    dome_2_vents_att_mean[500] = 0.55
    dome_2_vents_att_mean[750] = 1.42
    dome_2_vents_att_mean[1000] = 1.4
    dome_2_vents_att_mean[1500] = 0.7
    dome_2_vents_att_mean[2000] = -4.1
    dome_2_vents_att_mean[3000] = -9.8
    dome_2_vents_att_mean[4000] = -6.6
    dome_2_vents_att_mean[6000] = -4.3
    dome_2_vents_att_mean[8000] = -3.2

    dome_2_vents_att_sd = {}
    dome_2_vents_att_sd[125] = 0.9
    dome_2_vents_att_sd[250] = 0.7
    dome_2_vents_att_sd[500] = 0.99
    dome_2_vents_att_sd[750] = 1
    dome_2_vents_att_sd[1000] = 1.6
    dome_2_vents_att_sd[1500] = 3.6
    dome_2_vents_att_sd[2000] = 4
    dome_2_vents_att_sd[3000] = 4
    dome_2_vents_att_sd[4000] = 4.2
    dome_2_vents_att_sd[6000] = 4.6
    dome_2_vents_att_sd[8000] = 5.2

    dome_2_vents_att = {}
    dome_2_vents_att[125] = rng.normal(loc=dome_2_vents_att_mean[125], scale=dome_2_vents_att_sd[125])
    dome_2_vents_att[250] = rng.normal(loc=dome_2_vents_att_mean[250], scale=dome_2_vents_att_sd[250])
    dome_2_vents_att[500] = rng.normal(loc=dome_2_vents_att_mean[500], scale=dome_2_vents_att_sd[500])
    dome_2_vents_att[750] = rng.normal(loc=dome_2_vents_att_mean[750], scale=dome_2_vents_att_sd[750])
    dome_2_vents_att[1000] = rng.normal(loc=dome_2_vents_att_mean[1000], scale=dome_2_vents_att_sd[1000])
    dome_2_vents_att[1500] = rng.normal(loc=dome_2_vents_att_mean[1500], scale=dome_2_vents_att_sd[1500])
    dome_2_vents_att[2000] = rng.normal(loc=dome_2_vents_att_mean[2000], scale=dome_2_vents_att_sd[2000])
    dome_2_vents_att[3000] = rng.normal(loc=dome_2_vents_att_mean[3000], scale=dome_2_vents_att_sd[3000])
    dome_2_vents_att[4000] = rng.normal(loc=dome_2_vents_att_mean[4000], scale=dome_2_vents_att_sd[4000])
    dome_2_vents_att[6000] = rng.normal(loc=dome_2_vents_att_mean[6000], scale=dome_2_vents_att_sd[6000])
    dome_2_vents_att[8000] = rng.normal(loc=dome_2_vents_att_mean[8000], scale=dome_2_vents_att_sd[8000])

    ## Digitized from Cubick et al. 2022
    dome_1_vent_att_mean = {}
    dome_1_vent_att_mean[125] = 0.2
    dome_1_vent_att_mean[250] = 0.25
    dome_1_vent_att_mean[500] = 0.97
    dome_1_vent_att_mean[750] = 1.73
    dome_1_vent_att_mean[1000] = 1
    dome_1_vent_att_mean[1500] = -1.3
    dome_1_vent_att_mean[2000] = -5.97
    dome_1_vent_att_mean[3000] = -11.5
    dome_1_vent_att_mean[4000] = -8.4
    dome_1_vent_att_mean[6000] = -7.3
    dome_1_vent_att_mean[8000] = -5

    dome_1_vent_att_sd = {}
    dome_1_vent_att_sd[125] = 1
    dome_1_vent_att_sd[250] = 0.7
    dome_1_vent_att_sd[500] = 1
    dome_1_vent_att_sd[750] = 1.2
    dome_1_vent_att_sd[1000] = 1.8
    dome_1_vent_att_sd[1500] = 4.3
    dome_1_vent_att_sd[2000] = 4.5
    dome_1_vent_att_sd[3000] = 5.7
    dome_1_vent_att_sd[4000] = 3.7
    dome_1_vent_att_sd[6000] = 4.8
    dome_1_vent_att_sd[8000] = 6.4

    dome_1_vent_att = {}
    dome_1_vent_att[125] = rng.normal(loc=dome_1_vent_att_mean[125], scale=dome_1_vent_att_sd[125])
    dome_1_vent_att[250] = rng.normal(loc=dome_1_vent_att_mean[250], scale=dome_1_vent_att_sd[250])
    dome_1_vent_att[500] = rng.normal(loc=dome_1_vent_att_mean[500], scale=dome_1_vent_att_sd[500])
    dome_1_vent_att[750] = rng.normal(loc=dome_1_vent_att_mean[750], scale=dome_1_vent_att_sd[750])
    dome_1_vent_att[1000] = rng.normal(loc=dome_1_vent_att_mean[1000], scale=dome_1_vent_att_sd[1000])
    dome_1_vent_att[1500] = rng.normal(loc=dome_1_vent_att_mean[1500], scale=dome_1_vent_att_sd[1500])
    dome_1_vent_att[2000] = rng.normal(loc=dome_1_vent_att_mean[2000], scale=dome_1_vent_att_sd[2000])
    dome_1_vent_att[3000] = rng.normal(loc=dome_1_vent_att_mean[3000], scale=dome_1_vent_att_sd[3000])
    dome_1_vent_att[4000] = rng.normal(loc=dome_1_vent_att_mean[4000], scale=dome_1_vent_att_sd[4000])
    dome_1_vent_att[6000] = rng.normal(loc=dome_1_vent_att_mean[6000], scale=dome_1_vent_att_sd[6000])
    dome_1_vent_att[8000] = rng.normal(loc=dome_1_vent_att_mean[8000], scale=dome_1_vent_att_sd[8000])

    ## Digitized from Cubick et al. 2022
    double_dome_att_mean = {}
    double_dome_att_mean[125] = 0.06
    double_dome_att_mean[250] = 0.16
    double_dome_att_mean[500] = 0.3
    double_dome_att_mean[750] = -0.66
    double_dome_att_mean[1000] = -2.3
    double_dome_att_mean[1500] = -5.8
    double_dome_att_mean[2000] = -9.7
    double_dome_att_mean[3000] = -16
    double_dome_att_mean[4000] = -10
    double_dome_att_mean[6000] = -6.9
    double_dome_att_mean[8000] = -4.2

    double_dome_att_sd = {}
    double_dome_att_sd[125] = 1
    double_dome_att_sd[250] = 0.8
    double_dome_att_sd[500] = 2.3
    double_dome_att_sd[750] = 3.6
    double_dome_att_sd[1000] = 5.1
    double_dome_att_sd[1500] = 6.4
    double_dome_att_sd[2000] = 7.1
    double_dome_att_sd[3000] = 7.3
    double_dome_att_sd[4000] = 4.4
    double_dome_att_sd[6000] = 3.9
    double_dome_att_sd[8000] = 5.2

    double_dome_att = {}
    double_dome_att[125] = rng.normal(loc=double_dome_att_mean[125], scale=double_dome_att_sd[125])
    double_dome_att[250] = rng.normal(loc=double_dome_att_mean[250], scale=double_dome_att_sd[250])
    double_dome_att[500] = rng.normal(loc=double_dome_att_mean[500], scale=double_dome_att_sd[500])
    double_dome_att[750] = rng.normal(loc=double_dome_att_mean[750], scale=double_dome_att_sd[750])
    double_dome_att[1000] = rng.normal(loc=double_dome_att_mean[1000], scale=double_dome_att_sd[1000])
    double_dome_att[1500] = rng.normal(loc=double_dome_att_mean[1500], scale=double_dome_att_sd[1500])
    double_dome_att[2000] = rng.normal(loc=double_dome_att_mean[2000], scale=double_dome_att_sd[2000])
    double_dome_att[3000] = rng.normal(loc=double_dome_att_mean[3000], scale=double_dome_att_sd[3000])
    double_dome_att[4000] = rng.normal(loc=double_dome_att_mean[4000], scale=double_dome_att_sd[4000])
    double_dome_att[6000] = rng.normal(loc=double_dome_att_mean[6000], scale=double_dome_att_sd[6000])
    double_dome_att[8000] = rng.normal(loc=double_dome_att_mean[8000], scale=double_dome_att_sd[8000])


    ## loosely inspired by Kuk and Keenan 2006
    OE_dome_open = {}
    OE_dome_open[125] = 0
    OE_dome_open[250] = 0
    OE_dome_open[500] = 0
    OE_dome_open[750] = 0
    OE_dome_open[1000] = 0
    OE_dome_open[1500] = 0
    OE_dome_open[2000] = 0
    OE_dome_open[3000] = 0
    OE_dome_open[4000] = 0
    OE_dome_open[6000] = 0
    OE_dome_open[8000] = 0

    OE_dome_tulip = {}
    OE_dome_tulip[125] = rng.uniform(low=0, high=4)
    OE_dome_tulip[250] = rng.uniform(low=0, high=4)
    OE_dome_tulip[500] = rng.uniform(low=0, high=5)
    OE_dome_tulip[750] = rng.uniform(low=0, high=5)
    OE_dome_tulip[1000] = rng.uniform(low=0, high=2)
    OE_dome_tulip[1500] = rng.uniform(low=0, high=2)
    OE_dome_tulip[2000] = 0
    OE_dome_tulip[3000] = 0
    OE_dome_tulip[4000] = 0
    OE_dome_tulip[6000] = 0
    OE_dome_tulip[8000] = 0

    OE_dome_2_vents = {}
    OE_dome_2_vents[125] = rng.uniform(low=2, high=7)
    OE_dome_2_vents[250] = rng.uniform(low=2, high=13)
    OE_dome_2_vents[500] = rng.uniform(low=2, high=12)
    OE_dome_2_vents[750] = rng.uniform(low=2, high=8)
    OE_dome_2_vents[1000] = rng.uniform(low=0, high=3)
    OE_dome_2_vents[1500] = rng.uniform(low=0, high=3)
    OE_dome_2_vents[2000] = 0
    OE_dome_2_vents[3000] = 0
    OE_dome_2_vents[4000] = 0
    OE_dome_2_vents[6000] = 0
    OE_dome_2_vents[8000] = 0

    OE_dome_1_vent = {}
    OE_dome_1_vent[125] = rng.uniform(low=2, high=8)
    OE_dome_1_vent[250] = rng.uniform(low=3, high=15)
    OE_dome_1_vent[500] = rng.uniform(low=3, high=13)
    OE_dome_1_vent[750] = rng.uniform(low=2, high=8)
    OE_dome_1_vent[1000] = rng.uniform(low=0, high=3)
    OE_dome_1_vent[1500] = rng.uniform(low=0, high=3)
    OE_dome_1_vent[2000] = 0
    OE_dome_1_vent[3000] = 0
    OE_dome_1_vent[4000] = 0
    OE_dome_1_vent[6000] = 0
    OE_dome_1_vent[8000] = 0

    OE_double_dome = {}
    OE_double_dome[125] = rng.uniform(low=3, high=15)
    OE_double_dome[250] = rng.uniform(low=4, high=18)
    OE_double_dome[500] = rng.uniform(low=4, high=15)
    OE_double_dome[750] = rng.uniform(low=3, high=10)
    OE_double_dome[1000] = rng.uniform(low=0, high=5)
    OE_double_dome[1500] = rng.uniform(low=0, high=5)
    OE_double_dome[2000] = 0
    OE_double_dome[3000] = 0
    OE_double_dome[4000] = 0
    OE_double_dome[6000] = 0
    OE_double_dome[8000] = 0

    OE_earmold = {}
    OE_earmold[125] = rng.uniform(low=3, high=20)
    OE_earmold[250] = rng.uniform(low=5, high=25)
    OE_earmold[500] = rng.uniform(low=5, high=20)
    OE_earmold[750] = rng.uniform(low=4, high=18)
    OE_earmold[1000] = rng.uniform(low=2, high=10)
    OE_earmold[1500] = rng.uniform(low=1, high=8)
    OE_earmold[2000] = 0
    OE_earmold[3000] = 0
    OE_earmold[4000] = 0
    OE_earmold[6000] = 0
    OE_earmold[8000] = 0

    #copied from OE insert
    OE_earplug = {}
    OE_earplug[125] = rng.uniform(low=2, high=10)
    OE_earplug[250] = rng.uniform(low=2, high=10)
    OE_earplug[500] = rng.uniform(low=2, high=10)
    OE_earplug[750] = rng.uniform(low=2, high=10)
    OE_earplug[1000] = 0
    OE_earplug[1500] = 0
    OE_earplug[2000] = 0
    OE_earplug[3000] = 0
    OE_earplug[4000] = 0
    OE_earplug[6000] = 0
    OE_earplug[8000] = 0

    

    return OE_supra, OE_circum, OE_insert, OE_earplug, OE_earmold, OE_dome_open, OE_dome_tulip, OE_dome_2_vents, OE_dome_1_vent, OE_double_dome, supra_amb_att, circum_amb_att, insert_amb_att, earplug_att, earmold_att, dome_open_att, dome_tulip_att, dome_2_vents_att, dome_1_vent_att, double_dome_att, IA_supra, IA_insert, IA_circum, IA_bone, BCAL






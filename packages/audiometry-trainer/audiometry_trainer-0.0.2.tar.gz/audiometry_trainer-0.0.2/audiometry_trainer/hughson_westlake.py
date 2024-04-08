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

import multiprocessing
import numpy as np
import numpy.random as nprand
from .pysdt import*

class HughsonWestlake():
    def __init__(self,
                 adaptive_param=np.nan,
                 st_min = -20,
                 st_max = 120,
                 step_up=5,
                 step_down=10,
                 min_n_resp=3,
                 curr_dir="down",
                 thresh_obt = False,
                 thresh = np.nan,
                 asce_levs = np.empty(shape=0),
                 asce_n = np.empty(shape=0),
                 asce_yes = np.empty(shape=0),
                 asce_yes_prop = np.empty(shape=0),
                 track_levs = np.empty(shape=0),
                 track_resp = np.empty(shape=0)
                 ):

        self.adaptive_param = adaptive_param
        self.st_min = st_min
        self.st_max = st_max
        self.step_up = step_up
        self.step_down = step_down
        self.min_n_resp = min_n_resp
        self.curr_dir = curr_dir
        self.thresh_obt = thresh_obt
        self.thresh = thresh
        self.asce_levs = asce_levs
        self.asce_n = asce_n
        self.asce_yes = asce_yes
        self.asce_yes_prop = asce_yes_prop
        self.track_levs = track_levs
        self.track_resp = track_resp

    def update(self, resp, st_lev):
        self.track_levs = np.append(self.track_levs, st_lev)
        self.track_resp = np.append(self.track_resp, resp)
        if resp == True:
            if (self.curr_dir == "up") or (st_lev==self.st_min):
                if (st_lev in self.asce_levs) == False:
                    self.asce_levs = np.append(self.asce_levs, st_lev)
                    self.asce_n = np.append(self.asce_n, 1)
                    self.asce_yes = np.append(self.asce_yes, 1)
                else:
                    idx = np.where(self.asce_levs==st_lev)[0][0]
                    self.asce_n[idx] = self.asce_n[idx]+1
                    self.asce_yes[idx] = self.asce_yes[idx]+1

            self.adaptive_param = st_lev - self.step_down
            self.curr_dir = "down"
        else:
            if (self.curr_dir == "up") or (st_lev==self.st_min):
                if (st_lev in self.asce_levs) == False:
                    self.asce_levs = np.append(self.asce_levs, st_lev)
                    self.asce_n = np.append(self.asce_n, 1)
                    self.asce_yes = np.append(self.asce_yes, 0)
                else:
                    idx = np.where(self.asce_levs==st_lev)[0][0]
                    self.asce_n[idx] = self.asce_n[idx]+1

            self.adaptive_param = st_lev + self.step_up
            self.curr_dir = "up"


        sortidx = np.argsort(self.asce_levs)
        self.asce_levs = self.asce_levs[sortidx]
        self.asce_n = self.asce_n[sortidx]
        self.asce_yes = self.asce_yes[sortidx]

        self.asce_yes_prop = self.asce_yes/self.asce_n

        for idx in range(len(self.asce_levs)):
            if ((self.asce_n[idx] >= self.min_n_resp) and (self.asce_yes_prop[idx] >= 0.5)) or ((self.asce_n[idx] < self.min_n_resp) and (self.asce_yes[idx]/self.min_n_resp >= 0.5)):
                if self.asce_levs[idx] <= self.st_min:
                    self.thresh = self.asce_levs[idx]
                    self.thresh_obt = True
                if (self.asce_levs[idx]-self.step_up in self.asce_levs):
                    if ((self.asce_n[idx-1] >= self.min_n_resp) & (self.asce_yes_prop[idx-1] < 0.5)) or ((self.asce_n[idx-1] < self.min_n_resp) & ((self.asce_n[idx-1]-self.asce_yes[idx-1])/self.min_n_resp > 0.5)):
                        self.thresh = self.asce_levs[idx]
                        self.thresh_obt = True

        # for idx in range(len(self.asce_levs)):
        #     if (self.asce_n[idx] >= self.min_n_resp) and (self.asce_yes_prop[idx] >= 0.5):
        #         if self.asce_levs[idx] <= self.st_min:
        #             self.thresh = self.asce_levs[idx]
        #             self.thresh_obt = True
        #         if (self.asce_levs[idx]-self.step_up in self.asce_levs) and (self.asce_n[idx-1] >= self.min_n_resp) & (self.asce_yes_prop[idx-1] < 0.5):
        #             self.thresh = self.asce_levs[idx]
        #             self.thresh_obt = True


        if (self.st_max in self.asce_levs):
            idx = np.where(self.asce_levs==self.st_max)[0][0]
            if (self.asce_n[idx] >=10) and (self.asce_yes_prop[idx] < 0.5):
                self.thresh = np.inf
                self.thresh_obt = True


def run_HughsonWestlake(mdp, width, guess, lapse, st_lev, st_min, st_max, step_up, step_down, min_n_resp):

    HW = HughsonWestlake(st_min = st_min,
                         st_max = st_max,
                         step_up=step_up,
                         step_down=step_down,
                         min_n_resp=min_n_resp)
    while HW.thresh_obt == False:
        pcorr = logisticPsyWd(st_lev, mdp, width, guess, lapse)
        resp = nprand.choice([True, False], p=[pcorr, 1-pcorr])
        HW.update(resp, st_lev)
        st_lev = HW.adaptive_param
        if st_lev < st_min:
            st_lev = st_min
        if st_lev > st_max:
            st_lev = st_max

    #pcorr_at_thresh = logisticPsyWd(HW.thresh, mdp, width, guess, lapse)
        
    return HW.thresh

def simulate_audiogram(freqs, mdps, widths, guesses, lapses, st_min=-20,
                       st_max=120, step_up=5, step_down=10, 
                       min_n_resp=3, n_sim=1000):
    st_lev = 35
    thresh_matr = np.zeros((n_sim, len(freqs)))


    for i in range(len(freqs)):
        tn = []
        pool = multiprocessing.Pool()
        for n in range(n_sim):
            pool.apply_async(run_HughsonWestlake, (mdps[i], widths[i], guesses[i], lapses[i], st_lev, st_min, st_max, step_up, step_down, min_n_resp), callback=tn.append)

        pool.close()
        pool.join()
        thresh_matr[:,i] = tn
            
    return thresh_matr

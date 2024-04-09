from __future__ import annotations

import os
import numpy as np
import pandas as pd
import copy
import arrow
import functools
from os.path import abspath
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple
import mosaik_api_v3
from collections import OrderedDict
from mosaik_api_v3.types import (
    CreateResult,
    CreateResultChild,
    Meta,
    ModelDescription,
    OutputData,
    OutputRequest,
)

DEFAULT_STEP_SIZE = 15 * 60 # minutes
DATE_FORMAT = "YYYY-MM-DD HH:mm:ss"
DEFAULT_DATA_FILE = Path(abspath(__file__)).parent / 'data' / 'data.csv'
DEFAULT_CONFIG = OrderedDict([ # the order makes sense!
    ('method', None), # a callable that directly transforms input data to output 
    ('co2_emission_factor', None), # a factor that represents [tones CO₂eq. / MWh]
    ('fuel', None), # a certain type of fuel used to produce electricity
    ('state', None), # a certain state of the country to filter the carbon intensity database out
                     # it shuld be defined along with the country
    ('country', None), # just country to filter the carbon intensity database out
    ('coefficient', 1.0) # multiplies emissions output
    ])

META = {
    "api_version": "3.0",
    "type": "time-based",
    "models": {
        "Emission": {
            "public": True,
            "any_inputs": True,
            #"persistent": [],
            "params": list(DEFAULT_CONFIG.keys()), 
            "attrs": ["P[MW]",      # input/output from generator/external grid (p_mw float active power supply at the external grid [MW])
                      #"Q[MVar]",   # input from generator/external grid (q_mvar float reactive power supply at the external grid [MVar])
                      "E[tCO2eq]"   # output estimated total tonnes CO₂eq.
            ],   
        }
    },
}

class Simulator(mosaik_api_v3.Simulator):

    def __init__(self) -> None:
        super().__init__(META)
    
    def init(self, sid: str, time_resolution: float, start: str, end: int,
             step_size: int = DEFAULT_STEP_SIZE, 
             data_file: str = DEFAULT_DATA_FILE):
        self._time_resolution = time_resolution
        self._data_file = data_file
        self._step_size = step_size
        self._start = start
        self._end = end
        self._sid = sid
        self.entities = {}
        self.current_step = pd.to_datetime(arrow.get(self._start, DATE_FORMAT).datetime, utc=True) - pd.Timedelta(self._step_size, unit='seconds')
        self.database = pd.read_csv(data_file, parse_dates=True, sep=';', low_memory=False, dtype={'year' : 'Int64'})
        self.database['datetime'] = pd.to_datetime(self.database['datetime'], utc=True)
        self.database.set_index('datetime', inplace=True)
        return self.meta

    def create(self, num: int, model: str, **model_params: Any) -> List[CreateResult]:
        new_entities = []
        if not len(model_params):
            raise ValueError(f"No methods specified")
        params = OrderedDict(DEFAULT_CONFIG)
        params.update(model_params)
        coefficient = params.pop('coefficient', 1.0) 
        for n in range(len(self.entities), len(self.entities) + num):
            eid = f"{model}-{n}"
            self.entities.update({eid: {'params' : params,
                                        'coefficient' : coefficient,
                                        'cache' : {},
                                        }})
            new_entities.append({
                "eid": eid,
                "type": model,
            })
        return new_entities

    @functools.cache
    def get_stored_values(self, **kwargs):
        data = self.database.copy()
        try:
            # filter database with model_params
            for key, value in kwargs.items():
                if pd.notna(value) and key in data:
                    if key == 'fuel':
                        data = data[data[key] == value][['year', 'carbon_emission_factor']]
                        # [kg CO₂eq. / TJ] -> [1 TJ = 277.7778 MWh] -> [tones CO₂eq. / MWh]
                        data['carbon_emission_factor'] = data['carbon_emission_factor'] / 1000 / 277.7778 
                        break
                    elif key == 'state': # it shuld be defined along with the country
                        data = data[(data[key] == value) & (data['country'] == kwargs['country'])][['year', 'carbon_intensity_factor']]
                        break
                    elif key == 'country':
                        data = data[pd.isna(data['state']) & (data[key] == kwargs['country'])][['year', 'carbon_intensity_factor']]
                        break
                    else:  
                        data = data[data[key] == value]

            # change history year to current one
            filtered_data = data[data['year'] == self.current_step.year]
            if len(filtered_data) == 0:
                filtered_data = data[data['year'] == data['year'].max()]
                ydiff = self.current_step.year - filtered_data.index[0].year
                filtered_data.index += pd.offsets.DateOffset(years=ydiff) 
                filtered_data['year'] += ydiff
            
            if len(filtered_data) > 0:
                filtered_data.drop('year', axis=1, inplace=True)
                return filtered_data

            raise ValueError(f"No data for: {kwargs}")
        except Exception as e:
            raise ValueError(f"Getting value error for: {kwargs}, error: {str(e)}")
        
    def get_emission_factor(self, eid, attr, entity):
        params = self.entities[eid]['params']
        if attr in ['P[MW]']:
            if 'method' in params and callable(params['method']):
                return params['method'](eid, attr, entity, self.current_step, params)
            elif 'co2_emission_factor' in params and pd.notna(params['co2_emission_factor']):
                return params['co2_emission_factor']
            else:
                factor = self.get_stored_values(**params)
                index = factor.index.get_indexer([self.current_step], method='nearest')[0]
                if index < 0:
                    index = 0
                factor = factor.iloc[index].values[0]
                return factor
        else:
            raise ValueError(f"No appropriate method assigned for '{attr}'")

    def step(self, time, inputs, max_advance):
        # {'Emission-0': {'P[MW]': {'Grid-0.Gen-0': 1.0}}}
        self.current_step += pd.Timedelta(self._step_size, unit='seconds')
        for eid, data in inputs.items():
            self.entities[eid]['cache']['E[tCO2eq]'] = 0
            for attr, values in data.items():
                self.entities[eid]['cache'][attr] = 0
                for k, v in values.items():
                    self.entities[eid]['cache'][attr] += v
                    self.entities[eid]['cache']['E[tCO2eq]'] += v * self.get_emission_factor(eid, attr, k) * self.entities[eid]['coefficient']
        return time + self._step_size
     
    def get_data(self, outputs: OutputRequest) -> OutputData:
        return {eid: {attr: self.entities[eid]['cache'][attr] 
                            for attr in attrs
                                } for eid, attrs in outputs.items()}
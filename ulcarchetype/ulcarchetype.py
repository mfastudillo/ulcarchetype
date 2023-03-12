from itertools import tee
from dataclasses import dataclass,field
from typing import List
import math
import statistics
import bw2data
import numpy as np

@dataclass
class CharacterisationFactor():
    """representation of a characterization factor of an LCIA method"""
    database: str = None
    code: str = None
    name: str = None
    unit: str = None
    directionality: str = None
    context: list = None
    value: float = None
    values_possible: List[float] = field(default_factory=list)
    level: int = None
    uncertainty_param: dict = field(default_factory=dict)


@dataclass
class LCIAMethod():
    """representation of an LCIA method"""
    cfs: List[CharacterisationFactor] = field(default_factory=list)
        
    def maxlevel(self):
        """maximum level of 'depth' of the contexts used in the method """
        return max([cf.level for cf in self.cfs])
    
    def get_children(self,cf):
        """for a given CF, returns the cfs whose context is a more detailed 
        version of the CF context, only one level lower"""
        #TODO: maybe simply the level is lower
        children = [cf_child for cf_child in self.cfs if (cf_child.level==cf.level+1) 
         and (cf.name==cf_child.name) 
         and (cf.directionality==cf_child.directionality)
         and (cf.context==cf_child.context[:-1])]
        
        return children

    def get_descendents(self,cf):
        """for a given CF, returns the cfs whose context is a more detailed 
        version of the CF context, regardless of the level"""
        children = [cf_child for cf_child in self.cfs if (cf_child.level>cf.level) 
         and (cf.name == cf_child.name) 
         and (cf.directionality == cf_child.directionality)
         and (cf.context == cf_child.context[0:cf.level])]
        
        return children

    def set_freqparent(self,totalamount_dict):
        """adds a frequency to a CF relative to the parent level"""

        # loops the CF, get the children and set 
        for cf in sorted(self.cfs,key=lambda x:x.level,reverse=True):
            children = self.get_children(cf)

            if len(children)>0:
                freq = {children:totalamount_dict.get((children.database,children.code),0)}
                freq = {k:v/sum(freq.values()) for k,v in freq.items()}

    
    def transform_method(self,method):
        """transforms an brightway impact assessment method on a method following
        the object structure of the ulcarchetype library. """

        self.cfs = initialise_cf_list(method)

        # once all cfs have been added, we can loop again and 
        # add the possible values
        for cf in sorted(self.cfs,key=lambda x:x.level,reverse=True):
            children = self.get_children(cf)

            if len(children)>0:
                # case when children have not themselves possible values
                possible_values = [c.value for c in children]
                # filter out very similar ones those with relative diff < 0.01%
                possible_values = filter_close_list(possible_values,rel_tol=1e-5)
                cf.values_possible = possible_values
                cf.uncertainty_param['uncertainty type'] = 1 # by default no uncertainty
                cf.uncertainty_param['minimum'] = min(possible_values)
                cf.uncertainty_param['maximum'] = max(possible_values)
                cf.uncertainty_param['amount'] = cf.value
                cf.uncertainty_param['loc'] = statistics.mean(possible_values)

    def transform_method2(self,method):
        """transforms an brightway impact assessment method on a method following
        the object structure of the ulcarchetype library. """


        self.cfs = initialise_cf_list(method)

        # once all cfs have been added, we can loop again and 
        # add the possible values #TODO as a separate function.
        for cf in sorted(self.cfs,key=lambda x:x.level,reverse=True):
            children = self.get_descendents(cf)

            if len(children)>0:
                
                possible_values = []
                for child in children:
                    # if it only has one then
                    if child.values_possible == []:
                        child.values_possible = [{'value':child.value,
                                                  'freq':1/len(children)}]
                    
                    possible_values += child.values_possible
            
                cf.values_possible = possible_values

            # if there are only two possible values and are very very close,
            # ignore the case
 
# TODO: try to facilitate the use of given frequencies, separating the possible
# values from the setting of the rest of parameters.

    def set_uncertainty_from_possiblevalues(self):
        """"""

        for cf in self.cfs:
            possible_values = cf.values_possible

            if len(possible_values) == 1:
                continue

            # possible values and their frequencies
            vals = [v['value'] for v in possible_values]
            freqs = [v['freq'] for v in possible_values]

            assert math.isclose(sum(freqs),1),f'frequency sum should be 100% {possible_values} {cf}'

            if (len(possible_values) == 2) and (math.isclose(*vals)):
                continue
            else:

                weighed_avg =  np.average(vals,weights=freqs)
                weighed_std = math.sqrt(np.average((vals-weighed_avg)**2,weights=freqs))

                cf.uncertainty_param['uncertainty type'] = 1 # by default no uncertainty
                cf.uncertainty_param['minimum'] = min(vals)
                cf.uncertainty_param['maximum'] = max(vals)
                cf.uncertainty_param['amount'] = cf.value
                cf.uncertainty_param['loc'] = weighed_avg
                cf.uncertainty_param['scale'] = weighed_std



    def set_uncertainty_type(self,utype:int):
        """sets the uncertainty type """
        # TODO: use stat_arrays package to define utype as strings.. or improve
        # docstring
        assert isinstance(utype,int),'uncertainty type must be an integer type'
        
        for cf in self.cfs:
            # if it has uncertainty
            if len(cf.uncertainty_param) > 0:
                cf.uncertainty_param['uncertainty type'] = utype
            
    
    def build_cf_list(self):
        """creates a list of tuples to create a brightway 
        method"""
        
        list_of_cf = []
        for cf in self.cfs:
            # if its 0 is an emtpy dict, the default
            if len(cf.uncertainty_param) == 0:
                cf_value = cf.value
            else:
                cf_value = cf.uncertainty_param
            
            list_of_cf.append(((cf.database,cf.code),cf_value))
        
        return list_of_cf
    
    # methods to make it iterable .. not sure if needed because cfs was already iterable
    def __iter__(self):
        return self
    
    def __post_init__(self):
        self.idx=0
    
    def __next__(self):
        try:
            item = self.cfs[self.idx]
        except IndexError:
            raise StopIteration()
        self.idx += 1
        return item



# itertools recipe (https://docs.python.org/3/library/itertools.html)
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a,b)

def filter_close_list(alist,rel_tol=1e-4):
    """removes close elements from a list"""
    filtered_list = alist.copy()
    
    for i,inext in pairwise(sorted(alist)):
        if math.isclose(i,inext,rel_tol=rel_tol):
            filtered_list.remove(i)
        
    return filtered_list

def read_category(category):
    """transforms the category of a flowable into a list.
    (e.g. ('air','urban') -> ['air','urban']
          ('air')
    . """
    # if len(category)==2:
    #     compartment,subcompartment = category
    #     result = [compartment] + subcompartment.split(',')
    # elif len(category)==1:
    #     compartment = category[0]
    #     result = [compartment]
    reclass = {
    # ('air',),
    # ('air', 'indoor'),
    # ('air', 'low population density, long-term'),
    # ('air', 'lower stratosphere + upper troposphere'),
    # ('air', 'non-urban air or from high stacks'),
    # ('air', 'urban air close to ground'),
    # ('economic', 'primary production factor'),
    # ('inventory indicator', 'output flow'),
    # ('inventory indicator', 'resource use'),
    # ('inventory indicator', 'waste'),
    # ('natural resource', 'biotic'),
    # ('natural resource', 'fossil well'),
    # ('natural resource', 'in air'),
    # ('natural resource', 'in ground'),
    # ('natural resource', 'in water'),
    # ('natural resource', 'land'),
    # ('social',),
    # ('soil',),
    # ('soil', 'agricultural'),
    # ('soil', 'forestry'),
    # ('soil', 'industrial'),
    # ('water',),
    # ('water', 'fossil well'),
    # ('water', 'ground-'),
    ('water', 'ground-, long-term'):('water', 'ground-','long-term'),
    # ('water', 'ocean'),
    # ('water', 'surface water')
    }

    return reclass.get(category,category)


def initialise_cf_list(method):

    cfs = []
    for key,cf in method.load():
            
        if isinstance(cf,dict):
            raise ValueError(f"for the moment uncertain CF are not supported {cf}")

        flow = bw2data.get_activity(key)
        database,code = key
        cntx = read_category(flow['categories'])

        cf = CharacterisationFactor(database=database,
                                    code=code,
                                    name=flow['name'],
                                    unit=flow['unit'],
                                    directionality=flow['type'],
                                    context=cntx,
                                    level=len(cntx),
                                    value=cf)
        cfs += [cf]
    return cfs
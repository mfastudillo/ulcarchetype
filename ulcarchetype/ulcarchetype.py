from itertools import tee
from dataclasses import dataclass,field
from typing import List
import math
import statistics
import brightway2 as bw

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
    
    def get_childs(self,cf):
        """for a given CF, returns the cfs whose context is a more detailed 
        version of the CF context"""
        childs = [cf_child for cf_child in self.cfs if (cf_child.level==cf.level+1) 
         and (cf.name==cf_child.name) 
         and (cf.directionality==cf_child.directionality)
         and (cf.context==cf_child.context[:-1])]
        
        return childs
    
    def transform_method(self,method):

        for key,cf in method.load():
            flow = bw.get_activity(key)
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
            self.cfs += [cf]

        # once all cfs have been added, we can loop again and 
        # add the possible values
        for cf in sorted(self.cfs.cfs,key=lambda x:x.level,reverse=True):
            childs = self.get_childs(cf)

            if len(childs)>0:
                # case when childs have not themselves possible values
                possible_values = [c.value for c in childs]
                # filter out very similar ones those with relative diff < 0.01%
                possible_values = filter_close_list(possible_values,rel_tol=1e-5)
                cf.values_possible = possible_values
                cf.uncertainty_param['uncertainty type'] = 1 # by default no uncertainty
                cf.uncertainty_param['minimum'] = min(possible_values)
                cf.uncertainty_param['maximum'] = max(possible_values)
                cf.uncertainty_param['amount'] = cf.value
                #TODO: clarify why is "amount" are not "loc", not clear
                cf.uncertainty_param['loc'] = statistics.mean(possible_values)
                

    def set_uncertainty_type(self,utype):
        """sets the uncertainty type """
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
    
    if len(category)==2:
        compartment,subcompartment = category
        result = [compartment] + subcompartment.split(',')
    elif len(category)==1:
        compartment = category[0]
        result = [compartment]
        
    return result
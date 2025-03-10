import pickle
import os

from PySONIC.core import PulsedProtocol, BalancedPulsedProtocol
from PySONIC.utils import logger

from MorphoSONIC.models import SennFiber
from MorphoSONIC.sources import *
from MorphoSONIC.plt import *

print("This is the proper test code")
class GammaAcousticSource(GammaSource, AbstractAcousticSource):

    def __init__(self, gamma_dict, f, A=None):
        GammaSource.__init__(self, gamma_dict, f=f)
        AbstractAcousticSource.__init__(self, f, A=A)

    def computeDistributedAmps(self, fiber):
        return {k: self.A*v for k,v in GammaSource.computeDistributedAmps(self,fiber).items()}

    def copy(self):
        return self.__class__(self.gamma_dict, self.f, A=self.A)

    @staticmethod
    def inputs():
        return {**GammaSource.inputs(), **AbstractAcousticSource.inputs()}

a = 3.2e-08
fs = 1.0
input_path = os.environ['INPUT_FOLDER']

with open(input_path+'/axon_details','rb') as f:
    axondetails = pickle.load(f)
with open(input_path+'/gamma_dicts','rb') as f:
    gamma_dicts = pickle.load(f)

fiberD = [ad[2] for ad in axondetails]
nnodes = [len(ad[3]) for ad in axondetails]

# Create fiber models
fibers = [SennFiber(fiberD, nnodes=nnodes, a=a, fs=fs) for fiberD, nnodes in zip(fiberD, nnodes)] 

tpulse = 0.0001
toffset = 0.0005
pp = PulsedProtocol(tpulse, toffset)  

gamma_source = [GammaAcousticSource(gamma_dict, f=500000.0, A=100000.0) for gamma_dict in gamma_dicts]  

data_meta_list = []
for fiber, source in zip(fibers, gamma_source): # TODO can be setted to a number
# Simulate model with each source-protocol pair, and plot results
    data, meta = fiber.simulate(source, pp)
    #SectionCompTimeSeries([(data, meta)], 'Vm', fiber.nodeIDs).render()
    data_meta_list.append((data, meta))

output_path = "/home/jovyan/work/outputs/output_1"
with open(output_path+'/neuron_sims.pickle','wb') as f:
    pickle.dump(data_meta_list,f)

# print("Hello World")


from ipykernel.kernelapp import IPKernelApp
from . import ArduinoKernel

IPKernelApp.launch_instance(kernel_class=ArduinoKernel)

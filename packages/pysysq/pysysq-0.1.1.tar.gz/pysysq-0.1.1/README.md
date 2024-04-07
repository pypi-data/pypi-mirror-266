# PySysQ
PySysQ is a python package helping to implement discrete event simulations based on queueing theory.
The package provides the following elements to create a simulation

## Installation
```bash
pip install pysysq
```


## Simulation Elements

### 1. SQSimulator
SQSimulator composes all the simulation elements and creates relationship between them.
SQSimulator runs the simulation event loop.Each loop is counted as a single simulation time tick.
#### Properties
- `max_sim_time`: Maximum number of loops the simulator will run.
- `time_step`: the delay in seconds between two simulation loops.

### 2. SQClock
SQClock is a simulation object that ticks at specific interval on the simulation loops. 
Other Simulation Objects can make use of the SQClock object to generate self clock timing.
The Simulation objects using the same clock object as their clock source will be operating in a synchronous manner.
#### Properties
- `clk_divider`: the delay in seconds between two clock ticks with respect to the simulation loops.

### 3. SQPacketGenerator
SQPacketGenerator is a simulation object that generates packets at specific interval on the simulation loops.
#### Properties
- `clk`: clock for timing packet generation.
- `output_q`: the queue to which the generated packets will be pushed.
- `helper`: the helper class from loaded plugins.

### 4. SQFilter
SQFilter is a simulation object that filters packets based on the filter condition.
#### Properties
- `input_q`: the queue from which the packets will be filtered.
- `output_q`: the queue to which the filtered packets will be pushed.
- `helper`: the helper class from loaded plugins.
- `clk`: the clock for timing the filter operation.

### 5. SQMerger
SQMerger is a simulation object that merges packets from multiple input queues to a single output queue.
#### Properties
- `input_qs`: the list of input queues from which the packets will be merged.
- `output_q`: the queue to which the merged packets will be pushed.
- `clk`: The clock for timing the merge operation.

### 6. SQMux
SQMux is a simulation object that multiplexes packets from a single input queue to multiple output queues.
#### Properties
- `input_q`: the queue from which the packets will be multiplexed.
- `output_qs`: the list of output queues to which the multiplexed packets will be pushed.
- `clk`: The clock for timing the multiplex operation.
- `helper`: the helper class from loaded plugins.
### 7. SQDemux
SQDemux is a simulation object that demultiplexes packets from multiple input queues to a single output queue.
#### Properties
- `input_qs`: the list of input queues from which the packets will be demultiplexed.
- `output_q`: the queue to which the demultiplexed packets will be pushed.
- `clk`: The clock for timing the demultiplex operation.
- `helper`: the helper class from loaded plugins.

### 8. SQPktProcessor
SQPktProcessor is a simulation object that processes packets with specific processing ticks.
#### Properties
- `input_q`: the queue from which the packets will be processed.
- `output_q`: the queue to which the processed packets will be pushed.
- `clk`: The clock for timing the processing operation.
- `helper`: the helper class from loaded plugins.
### 9. SQPktSink
SQPktSink is a simulation object that consumes and mark the termination of  packets.
#### Properties
- `input_q`: the queue from which the packets will be consumed.
- `clk`: The clock for timing the consumption operation.

### 10. SQQueue
SQQueue is a simulation object that holds packets. Every simulation objects except SQClock and SQSimulator are connected to each other via Queues.
#### Properties
- `capacity`: the maximum number of packets the queue can hold.

## Writing Plugins for the Simulation Objects
Many simulation object can be configured with user defined plugins to extend the default behaviour
The Plugin need to be implemented as seperate python package. The Package must contain a class that inherit from 
SQHelper class. The Helper class must implement the following methods
- `set_owner`: The method is called by the owner object to set the owner of the helper object.
- `generate_packets`: The method is called by the SQPktGenerator object to generate packets. The method is a python generator.
- `get_processing_cycles` : The method is called by the SQPktProcessor object to get the processing cycles for the packet.
- `process_packet` : The method is called by the SQPktProcessor object to process the packet.
- `filter_packet` : The method is called by the SQFilter object to filter the packet.
- `process_data` : The method is called by the Simulation Objects to process  the data flow.
- `select_input_queue` : The method is called by the SQMux object to select the input queue for the packet.
- `select_output_queue` : The method is called by the SQDemux object to select the output queue for the packet.
The Package also need to contain mandatorily a function with the name `register`
An example implementation of the register function is shown below
```python
def register(helper_factory: SQHelperFactory):
    helper_factory.register(name="plugin_name", factory=Constructor_for_helper_class())
```
The same name mentioned above need to be used as the helper name in the json file for the simulation object.
:warning: The Plugin package must be installed in the python environment where the simulation is run.
If the plugin requires any extra parameters then those parameters needs to be added using the `helper_params` property in the json file for the simulation object.
## Configuring the Simulation
The Simulation can be configured via a Json File. An Example Json File can be found in the sq_sim_setup_generator/config folder.
The below code can be used to generate the simulation setup class from the json metadata. 
```python
from pysysq import *
if __name__ == "__main__":
    sim_setup = SQSimSetupGen(json_file='path/to/json_file')
    sim_setup.generate(output_folder='output')
```
### Configuring the Data Flow
Some times it is necessary to pass metadata generated by some simulation objects to another simulation object. 
In order to configure the data flow between simulation objects , the json file can specify the data flow elements. 
An example of data flow specification is shown below
```json
 {
          "name": "Processor1",
          "type": "SQPktProcessor",
          "description": "Processor",
          "default_factory": true,
          "factory_method": "create_packet_processor",
          "plot": true,
          "data_flow": [
            {
              "data":[ "progress"],
              "destination": "Processor2"
            }
          ],
          "clk":"Clock",
          "input_q": "Pkt_q",
          "output_q": "Proc_q"
      }
```
In the above example the Processor1 object is configured to pass the progress metadata to the Processor2 object.
The Processor2 can access the progress metadata by accessing the list  member `self.data_flow_map`. The `data_flow_map` constains a list of SQMetadata objects which are updated based on the generated new values of the metadata.
#### SQMetadata
The SQMetadata class is a simple class that holds the metadata information. The class has the following properties
- `name`: The name of the metadata
- `value`: The value of the metadata
- `owner`: The owner of the metadata
In order to access the metadata in the destination object , the destination object can access the metadata by the following code
```python
metadata = self.get_metadata_received(owner='Processor1',data_name='progress')
value = metadata.value
```
## Running the Simulation
Once the Simulation setup is generated the simulation can be run by executing the simulation setup file generated. 
```python
python  simulator.py # The simulator.py is the file generated by the SQSimSetupGen class
```
## Analysing Simulation Results
The PysysQ package provides a way to register properties from each of the Simulation Objects. 
The Package comes with some preconfigured properties for the above simulation objects. 
For example The SQPktProcessor comes inbuilt with the property `load` indicating the load on the PacketProcessor. 
The SQQueue comes inbuilt with the property `pending_pkts` indicating the number of packets pending in the queue.

The pysysq simulator samples  the registered properties from the simulation objects at each simulation ticks. The information is stored in a statistics object. 
Later at the end of the simulation the statisitcs can be plotted in a graph using `SQPlotter` class.
In order to enable plotting for an object set the `plot` property to `true` in the json file for the simulation object. 



### Adding new properties from helper classes. 
In order to register a new property from the helper class , the helper class can first add a member attribute in the class 
then call the `register_property` method in the owner class to register the property.

```python

    def set_owner(self,owner):
        self.owner = owner
        self.owner.register_property(owner=self,name='filter_result')

```
Now if the plot property of the Filter object is set to true in the json at the end of simulation a plot of the Property value `filter_result` will be plotted against each simulation tick.
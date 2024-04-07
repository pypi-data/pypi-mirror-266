from abc import ABC, abstractmethod
from .sq_sim_data_model import (SQSimDataModel, DataFlow)


class SQSimDataGenStrategy(ABC):
    def __init__(self, context):
        self.context = context

    @abstractmethod
    def generate(self, data: dict) -> SQSimDataModel:
        pass

    def get_array_repr(self, array: list):
        return '[' + ','.join([f'self.{x}'.lower() for x in array]) + ']'

    def append_helper_params(self, data: dict, object_data: dict):
        helper_params = data.get('helper_params', {})
        for k, v in helper_params.items():
            object_data[k] = v


    def get_data_flows(self, data: dict):
        data_flows = []
        if 'data_flow' not in data:
            return data_flows
        for d in data['data_flow']:
            data_flows.append(DataFlow(data=d['data'], destination=d['destination']))
        return data_flows


class SQClockDataGenStrategy(SQSimDataGenStrategy):
    def __init__(self, ctx):
        super().__init__(ctx)

    def generate(self, data: dict) -> SQSimDataModel:
        obj_data = dict(
            name="\"" + data['name'] + "\"",
            clk_divider=data['clk_divider']
        )
        self.append_helper_params(data, obj_data)
        clk_model = SQSimDataModel(
            name=data['name'],
            type=data['type'],
            comment=data['description'],
            data_flows=self.get_data_flows(data),
            plot=data['plot'],
            sq_object_data=obj_data,
            children=[],
        )
        return clk_model


class SQSimulatorDataGenStrategy(SQSimDataGenStrategy):
    def __init__(self, ctx):
        super().__init__(ctx)

    def generate(self, data: dict) -> SQSimDataModel:
        children = [self.context.generate(x) for x in data['children']]
        children_names = self.get_array_repr([x.name for x in children])

        print(children_names)
        obj_data = dict(
            name="\"" + data['name'] + "\"",
            max_sim_time=data['max_sim_time'],
            time_step=data['time_step'],
            children=children_names,
        )
        self.append_helper_params(data, obj_data)
        return SQSimDataModel(
            name=data['name'],
            type=data['type'],
            comment=data['description'],
            data_flows=self.get_data_flows(data),
            plot=data['plot'],
            sq_object_data=obj_data,
            children=children,
        )


class SQSISODataGenStrategy(SQSimDataGenStrategy):
    def __init__(self, ctx):
        super().__init__(ctx)

    def generate(self, data: dict) -> SQSimDataModel:
        obj_data = dict(
            name="\"" + data['name'] + "\"",
            clk='self.' + str(data['clk']).lower(),
            input_q='self.' + str(data['input_q']).lower(),
            output_q='self.' + str(data['output_q']).lower(),
            helper="\"" + data.get('helper', 'default') + "\""
        )
        self.append_helper_params(data, obj_data)
        return SQSimDataModel(
            name=data['name'],
            type=data['type'],
            comment=data['description'],
            data_flows=self.get_data_flows(data),
            plot=data['plot'],
            sq_object_data=obj_data,
            children=[],
        )


class SQSIMODataGenStrategy(SQSimDataGenStrategy):
    def __init__(self, ctx):
        super().__init__(ctx)

    def generate(self, data: dict) -> SQSimDataModel:
        output_qs = self.get_array_repr(data['output_qs'])
        obj_data = dict(
            name="\"" + data['name'] + "\"",
            clk='self.' + str(data['clk']).lower(),
            input_q='self.' + str(data['input_q']).lower(),
            output_qs=output_qs,
            helper="\"" + data.get('helper', 'default') + "\""
        )
        self.append_helper_params(data, obj_data)
        return SQSimDataModel(
            name=data['name'],
            type=data['type'],
            comment=data['description'],
            data_flows=self.get_data_flows(data),
            plot=data['plot'],
            sq_object_data=obj_data,
            children=[],
        )


class SQMISODataGenStrategy(SQSimDataGenStrategy):
    def __init__(self, ctx):
        super().__init__(ctx)

    def generate(self, data: dict) -> SQSimDataModel:
        input_qs = self.get_array_repr(data['input_qs'])
        obj_data = dict(
            name="\"" + data['name'] + "\"",
            clk='self.' + str(data['clk']).lower(),
            input_qs=input_qs,
            output_q='self.' + str(data['output_q']).lower(),
            helper="\"" + data.get('helper', 'default') + "\""
        )
        self.append_helper_params(data, obj_data)
        return SQSimDataModel(
            name=data['name'],
            type=data['type'],
            comment=data['description'],
            data_flows=self.get_data_flows(data),
            plot=data['plot'],
            sq_object_data=obj_data,
            children=[],
        )


class SQSINODataGenStrategy(SQSimDataGenStrategy):
    def __init__(self, ctx):
        super().__init__(ctx)

    def generate(self, data: dict) -> SQSimDataModel:
        obj_data = dict(
            name="\"" + data['name'] + "\"",
            clk='self.' + str(data['clk']).lower(),
            input_q='self.' + str(data['input_q']).lower(),
            helper="\"" + data.get('helper', 'default') + "\""
        )
        self.append_helper_params(data, obj_data)
        return SQSimDataModel(
            name=data['name'],
            type=data['type'],
            comment=data['description'],
            data_flows=self.get_data_flows(data),
            plot=data['plot'],
            sq_object_data=obj_data,
            children=[],

        )


class SQNISODataGenStrategy(SQSimDataGenStrategy):
    def __init__(self, ctx):
        super().__init__(ctx)

    def generate(self, data: dict) -> SQSimDataModel:
        obj_data = dict(
            name="\"" + data['name'] + "\"",
            clk='self.' + str(data['clk']).lower(),
            output_q='self.' + str(data['output_q']).lower(),
            helper="\"" + data.get('helper', 'default') + "\""
        )
        self.append_helper_params(data, obj_data)
        return SQSimDataModel(
            name=data['name'],
            type=data['type'],
            comment=data['description'],
            data_flows=self.get_data_flows(data),
            plot=data['plot'],
            sq_object_data=obj_data,
            children=[],
        )


class SQQueueDataGenStrategy(SQSimDataGenStrategy):
    def __init__(self, ctx):
        super().__init__(ctx)

    def generate(self, data: dict) -> SQSimDataModel:
        obj_data = dict(
            name="\"" + data['name'] + "\"",
            capacity=data['capacity'],
        )
        self.append_helper_params(data, obj_data)
        qs = SQSimDataModel(
            name=data['name'],
            type=data['type'],
            comment=data['description'],
            data_flows=self.get_data_flows(data),
            children=[],
            plot=data['plot'],
            sq_object_data=obj_data,
        )
        return qs

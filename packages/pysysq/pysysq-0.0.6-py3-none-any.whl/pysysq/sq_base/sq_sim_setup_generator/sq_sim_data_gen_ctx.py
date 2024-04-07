from .sq_sim_data_gen_strategy import SQSimulatorDataGenStrategy, \
    SQClockDataGenStrategy, SQSISODataGenStrategy, SQMISODataGenStrategy, \
    SQSIMODataGenStrategy, SQNISODataGenStrategy, SQSINODataGenStrategy, SQQueueDataGenStrategy


class SQSimDataGenCtx:
    def __init__(self):
        self.str = None
        self.strategy_map = {
            'SQSimulator': SQSimulatorDataGenStrategy(ctx=self),
            'SQClock': SQClockDataGenStrategy(ctx=self),
            'SQFilter': SQSISODataGenStrategy(ctx=self),
            'SQMerger': SQMISODataGenStrategy(ctx=self),
            'SQMux': SQMISODataGenStrategy(ctx=self),
            'SQDemux': SQSIMODataGenStrategy(ctx=self),
            'SQPacketGenerator': SQNISODataGenStrategy(ctx=self),
            'SQPktProcessor': SQSISODataGenStrategy(ctx=self),
            'SQPktSink': SQSINODataGenStrategy(ctx=self),
            'SQQueue': SQQueueDataGenStrategy(ctx=self),
            'SQSplitter': SQSIMODataGenStrategy(ctx=self)

        }

        self.type = None

    @property
    def strategy(self):
        return self.str

    @strategy.setter
    def strategy(self, strategy):
        self.str = strategy

    def generate(self, data: dict):
        self.type = data['type']
        if self.type in self.strategy_map:
            self.strategy = self.strategy_map[self.type]
        else:
            raise ValueError(f'Invalid Type {self.type}')
        return self.strategy.generate(data)

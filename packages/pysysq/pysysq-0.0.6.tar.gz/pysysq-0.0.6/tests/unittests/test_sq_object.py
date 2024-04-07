import unittest
from unittest.mock import MagicMock

from pysysq.sq_base import SQTimeBase
from pysysq.sq_base.sq_event import SQEventManager, SQEvent
from pysysq.sq_base.sq_event.sq_event import EventType
from pysysq.sq_base.sq_object import SQObject
from pysysq.sq_base.sq_packet.sq_metadata import SQMetadata


class TestSQObject(unittest.TestCase):
    def setUp(self):
        self.event_mgr = SQEventManager()
        # Initialize an instance of SQObject before each test
        self.producer = SQObject('producer', self.event_mgr)
        self.consumer = SQObject('consumer', self.event_mgr)

    def test_subscribe_metadata(self):
        # Arrange
        owner = 'producer'
        data_name = 'test_data'

        # Act
        self.consumer.subscribe_metadata(owner, data_name)

        # Assert
        self.assertTrue(self.consumer._is_metadata_subscribed(owner, data_name))

    def test_register_property(self):
        # Arrange
        property_name = 'test_property'

        # Act
        self.producer.register_property(property_name)

        # Assert
        self.assertIn(property_name, self.producer.statistics_properties)

    def test_data_flow_with_str_metadata(self):
        # Arrange
        evt = SQEvent(_name='test_event', owner=self.producer)
        evt.type = EventType.METADATA_EVT
        evt.data = SQMetadata(owner='producer', name='test_data', value='test_value')
        self.producer.data_flow(self.consumer, ['test_data'])
        self.consumer.process_data = MagicMock()

        # Act
        self.producer.data_indication(data=evt.data)
        SQTimeBase.update_current_sim_time()
        self.event_mgr.run()

        # Assert
        self.consumer.process_data.assert_called_once()
        self.assertEqual(self.consumer.process_data.call_args[0][0].data.value,'test_value')

    def test_data_flow_with_int_metadata(self):
        # Arrange
        evt = SQEvent(_name='test_event', owner=self.producer)
        evt.type = EventType.METADATA_EVT
        evt.data = SQMetadata(owner='producer', name='test_data', value=20)
        self.producer.data_flow(self.consumer, ['test_data'])
        self.consumer.process_data = MagicMock()

        # Act
        self.producer.data_indication(data=evt.data)
        SQTimeBase.update_current_sim_time()
        self.event_mgr.run()

        # Assert
        self.consumer.process_data.assert_called_once()
        self.assertEqual(self.consumer.process_data.call_args[0][0].data.value, 20)

    def test_data_flow_with_bool_metadata(self):
        # Arrange
        evt = SQEvent(_name='test_event', owner=self.producer)
        evt.type = EventType.METADATA_EVT
        evt.data = SQMetadata(owner='producer', name='test_data', value=True)
        self.producer.data_flow(self.consumer, ['test_data'])
        self.consumer.process_data = MagicMock()

        # Act
        self.producer.data_indication(data=evt.data)
        SQTimeBase.update_current_sim_time()
        self.event_mgr.run()

        # Assert
        self.consumer.process_data.assert_called_once()
        self.assertEqual(self.consumer.process_data.call_args[0][0].data.value, True)




if __name__ == '__main__':
    unittest.main()

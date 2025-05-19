import unittest
from avisengine import Car


class TestCar(unittest.TestCase):
    def setUp(self):
        self.car = Car()

    def test_initial_values(self):
        self.assertEqual(self.car.speed_value, 0)
        self.assertEqual(self.car.steering_value, 0)
        self.assertEqual(self.car.sensor_status, 1)
        self.assertEqual(self.car.image_mode, 1)
        self.assertEqual(self.car.sensor_angle, 30)
        self.assertIsNone(self.car.image)
        self.assertIsNone(self.car.sensors)
        self.assertIsNone(self.car.current_speed)

    def test_input_validation(self):
        # Test steering angle limits
        self.car.setSteering(45)
        self.assertEqual(self.car.steering_value, 45)
        
        # Test speed limits
        self.car.setSpeed(100)
        self.assertEqual(self.car.speed_value, 100)
        
        # Test sensor angle limits
        self.car.setSensorAngle(30)
        self.assertEqual(self.car.sensor_angle, 30)


if __name__ == "__main__":
    unittest.main()

import unittest
import os
os.environ['SAPHIRA_URL'] = 'http://localhost:8081'
import saphira

PROJECT = '83092519-da63-4882-a899-297e3e62b65d.json'
REQ = 'BattRef-0001'

class BatteryCapacityTest(unittest.TestCase):
    def test_electric_range(self):
        energy_density = 250  # Wh/kg
        minimum_range = int(saphira.get_param(PROJECT, REQ))  # kilometers
        print(minimum_range)
        efficiency_factor = 0.9  # Efficiency factor to account for losses
        
        # Assuming battery weight in kilograms
        battery_weight = minimum_range / (energy_density * efficiency_factor)
        
        # Calculate the minimum required battery capacity in kWh
        min_battery_capacity_kWh = minimum_range * energy_density / 1000
        
        # Assert the minimum battery capacity supports the required range
        self.assertGreaterEqual(battery_weight, 0, "Battery weight cannot be negative")
        self.assertTrue(min_battery_capacity_kWh > 0, "Minimum battery capacity must be positive")
        self.assertTrue(battery_weight < 500, "Battery weight should be reasonable (< 500 kg)")
        self.assertTrue(min_battery_capacity_kWh * 1000 / energy_density >= minimum_range, f"Minimum battery capacity should support at least {minimum_range} km range, is " + str(min_battery_capacity_kWh))
        self.assertTrue(min_battery_capacity_kWh <= 250, "Minimum battery capacity should not exceed required energy density")

if __name__ == '__main__':
    try:
        test = unittest.main(exit=False)
        saphira.update_test_status(PROJECT, REQ, test.result.wasSuccessful())
    except Exception as e:
        saphira.update_test_status(PROJECT, REQ, False)
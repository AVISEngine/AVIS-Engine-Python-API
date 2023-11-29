using UnityEngine;

public class IMUSimulator : MonoBehaviour
{
    public Vector3 accelerometerNoise = new Vector3(0.05f, 0.05f, 0.05f); // Adjust accelerometer noise
    public Vector3 gyroscopeNoise = new Vector3(0.1f, 0.1f, 0.1f); // Adjust gyroscope noise

    private Vector3 accelerometer;
    private Vector3 gyroscope;

    void Update()
    {
        SimulateIMU();
    }

    void SimulateIMU()
    {
        // Simulate accelerometer data with noise
        accelerometer = new Vector3(
            -Input.acceleration.x + Random.Range(-accelerometerNoise.x, accelerometerNoise.x),
            -Input.acceleration.y + Random.Range(-accelerometerNoise.y, accelerometerNoise.y),
            -Input.acceleration.z + Random.Range(-accelerometerNoise.z, accelerometerNoise.z)
        );

        // Simulate gyroscope data with noise
        gyroscope = new Vector3(
            -Input.gyro.rotationRate.x + Random.Range(-gyroscopeNoise.x, gyroscopeNoise.x),
            -Input.gyro.rotationRate.y + Random.Range(-gyroscopeNoise.y, gyroscopeNoise.y),
            -Input.gyro.rotationRate.z + Random.Range(-gyroscopeNoise.z, gyroscopeNoise.z)
        );

        // Use the simulated data in your application as needed
        // For example, you can integrate accelerometer data to calculate velocity or position.
        // Gyroscope data can be used to update orientation.
    }

    // Accessors for getting simulated data
    public Vector3 GetAccelerometerData()
    {
        return accelerometer;
    }

    public Vector3 GetGyroscopeData()
    {
        return gyroscope;
    }
}
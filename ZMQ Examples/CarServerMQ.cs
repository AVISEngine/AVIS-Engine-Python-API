using UnityEngine;
using NetMQ;
using NetMQ.Sockets;

public class CarServer : MonoBehaviour
{
    // ... (existing code)

    private void Start()
    {
        // ... (existing code)

        // Set useZMQ to true to enable ZMQ
        useZMQ = true;

        if (useZMQ)
        {
            Task.Run(() => Publish());
        }
        else
        {
            // ... (existing code)
        }
    }

    private void Publish()
    {
        using (var publisher = new PublisherSocket())
        {
            publisher.Bind("tcp://*:25005");

            while (true)
            {
                // Publish simulated data
                publisher.SendMoreFrame("/car/steering").SendFrame(Steering.ToString());
                publisher.SendMoreFrame("/car/velocity").SendFrame(Speed.ToString());
                publisher.SendMoreFrame("/car/frontsensor/right").SendFrame(sensorsClass.distanceRight.ToString());
                publisher.SendMoreFrame("/car/frontsensor/middle").SendFrame(sensorsClass.distanceCenter.ToString());
                publisher.SendMoreFrame("/car/frontsensor/left").SendFrame(sensorsClass.distanceLeft.ToString());
                publisher.SendMoreFrame("/car/frontsensor/config/angle").SendFrame(sensor_angle.ToString());
                publisher.SendMoreFrame("/car/camera/rgb").SendFrame(cameraSens.cameraImageString);
                publisher.SendMoreFrame("/car/speed").SendFrame(current_speed.ToString());

                Thread.Sleep(100);  // Adjust the sleep time as needed
            }
        }
    }
    
    // ... (existing code)
}
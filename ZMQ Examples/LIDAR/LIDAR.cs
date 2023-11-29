using UnityEngine;
using System.Collections.Generic;
using System.IO;

public class LidarSimulator : MonoBehaviour
{
    public int numRays = 360;
    public float maxDistance = 10f;

    private List<Vector3> pointCloud = new List<Vector3>();

    void Update()
    {
        ClearLines();
        SimulateLidar();
        CreatePointCloud();
    }

    void SimulateLidar()
    {
        for (int i = 0; i < numRays; i++)
        {
            float angle = i * 360f / numRays;
            Vector3 direction = Quaternion.Euler(0, angle, 0) * transform.forward;

            RaycastHit hit;

            if (Physics.Raycast(transform.position, direction, out hit, maxDistance))
            {
                Debug.DrawLine(transform.position, hit.point, Color.red);
                pointCloud.Add(hit.point);
            }
            else
            {
                Vector3 endPoint = transform.position + direction * maxDistance;
                Debug.DrawLine(transform.position, endPoint, Color.green);
            }
        }
    }

    void CreatePointCloud()
    {
        // Export the point cloud to a CSV file
        string filePath = Application.dataPath + "/pointCloud.csv";

        using (StreamWriter writer = new StreamWriter(filePath))
        {
            foreach (Vector3 point in pointCloud)
            {
                writer.WriteLine($"{point.x},{point.y},{point.z}");
            }
        }

        Debug.Log($"Point cloud saved to: {filePath}");
    }

    void ClearLines()
    {
        Debug.ClearDeveloperConsole();
    }
}

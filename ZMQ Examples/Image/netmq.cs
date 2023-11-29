using UnityEngine;
using NetMQ;
using NetMQ.Sockets;

public class FramePublisher : MonoBehaviour
{
    public Camera captureCamera;
    public RenderTexture renderTexture;

    private PublisherSocket publisherSocket;
    private Texture2D texture2D;

    private void Start()
    {
        // Create and bind the ZeroMQ publisher socket
        publisherSocket = new PublisherSocket();
        publisherSocket.Bind("tcp://*:5555");

        // Create a reusable Texture2D object
        texture2D = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);
    }

    private void LateUpdate()
    {
        // Capture frames from the camera and publish them
        Graphics.Blit(captureCamera.targetTexture, renderTexture);

        byte[] encodedBytes = EncodeFrame();

        // Publish the encoded frame with a topic
        string topic = "CameraFrames";
        publisherSocket.SendMoreFrame(topic).SendFrame(encodedBytes);
    }

    private byte[] EncodeFrame()
    {
        // Encode the frame as a more efficient format, such as WebP or PNG
        // You can use the FrameEncoder code from the previous response

        // Example: Encoding as WebP
        RenderTexture.active = renderTexture;
        texture2D.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        texture2D.Apply();

        byte[] encodedBytes = WebPEncoder.Encode(texture2D, quality: 80);

        return encodedBytes;
    }

    public byte[] EncodeFrameJPG()
    {
        // Read pixel data from RenderTexture into Texture2D
        RenderTexture.active = captureTexture;
        texture2D.ReadPixels(new Rect(0, 0, captureTexture.width, captureTexture.height), 0, 0);
        texture2D.Apply();

        // Encode Texture2D as JPEG
        byte[] encodedBytes = texture2D.EncodeToJPG();

        return encodedBytes;
    }
    private void OnDestroy()
    {
        // Close the ZeroMQ publisher socket
        publisherSocket.Close();

        // Clean up the Texture2D object
        Destroy(texture2D);
    }
}
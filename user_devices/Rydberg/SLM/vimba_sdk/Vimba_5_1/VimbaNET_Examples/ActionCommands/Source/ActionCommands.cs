/*=============================================================================
  Copyright (C) 2021 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        ActionCommands.cs

  Description: This example will create an Action Command and send it to any
               camera, given by parameter. The following can be set up with
               parameters as well:
                -send Action Command as broadcast on specific network interface
                -send Action Command as broadcast to all network interfaces
                -send Action Command to specific IP address (unicast)

-------------------------------------------------------------------------------

  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE,
  NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A PARTICULAR  PURPOSE ARE
  DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
  AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

=============================================================================*/

using System;
using System.Net;

namespace AVT {
namespace VmbAPINET {
namespace Examples {

public struct tActionCommand
{
    public int mDeviceKey;
    public int mGroupKey;
    public int mGroupMask;
}

public enum tFeatureOwner
{
    eFeatureOwnerUnknown     = 0,
    eFeatureOwnerSystem      = 1,
    eFeatureOwnerInterface   = 2,
    eFeatureOwnerCamera      = 3
}

public enum tFeatureType
{
    eFeatureTypeUnknown = 0,
    eFeatureTypeInt     = 1,
    eFeatureTypeFloat   = 2,
    eFeatureTypeEnum    = 3,
    eFeatureTypeString  = 4,
    eFeatureTypeBool    = 5
}

class cActionCommands
{
    private Vimba mSystem;
    private Interface mInterface;
    private Camera mCamera;

    private bool mSystemFlag;
    private bool mInterfaceFlag;
    private bool mCameraFlag;
    private bool mStreamingFlag;

    /// <summary>
    /// Constructor
    /// </summary>
    public cActionCommands()
    {
        this.mSystem = new Vimba();
    }

    /// <summary>
    /// Destructor
    /// </summary>
    ~cActionCommands()
    {
    }

    /// <summary>
    /// Frame callback
    /// </summary>
    private void FrameReceived(Frame aFrame)
    {
        try
        {
            if (VmbFrameStatusType.VmbFrameStatusComplete == aFrame.ReceiveStatus)
            {
                Console.WriteLine("......Frame has been received.");
            }

            // re-queue frame
            this.mCamera.QueueFrame(aFrame);
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Failure during frame reception.");
        }
    }

    /// <summary>
    /// Called when any failure occurs whithin the example.
    /// Ensures to stop streaming, close interface, close camera and shutdown Vimba.
    /// </summary>
    public void FailureShutdown()
    {
        if (true == this.mStreamingFlag)
        {
            try
            {
                // stop streaming
                this.mCamera.StopContinuousImageAcquisition();
            }
            catch(VimbaException ve)
            {
                Console.WriteLine("[F]...Could not stop camera acquisition.");
            }

            Console.WriteLine("......Streaming has been stopped.");
        }

        if (true == this.mCameraFlag)
        {
            try
            {
                // close camera
                this.mCamera.Close();
            }
            catch(VimbaException ve)
            {
                Console.WriteLine("[F]...Could not close camera.");
            }

            Console.WriteLine("......Camera has been closed.");
        }

        if (true == this.mInterfaceFlag)
        {
            try
            {
                // close interface
                this.mInterface.Close();
            }
            catch(VimbaException ve)
            {
                Console.WriteLine("[F]...Could not close interface.");
            }

            Console.WriteLine("......Interface has been closed.");
        }

        if (true == this.mSystemFlag)
        {
            try
            {
                // shutdown Vimba
                this.mSystem.Shutdown();
            }
            catch(VimbaException ve)
            {
                Console.WriteLine("[F]...Could not shutdown Vimba.");
            }

            Console.WriteLine("......Vimba has been stopped.");
        }
    }

    /// <summary>
    /// Start Vimba and open camera with given string
    /// </summary>
    /// <param name="aCamera">The ID or IP address of the camera to work with</param>
    public void PrepareCamera(String aCamera)
    {
        // check parameter
        if (0 == aCamera.Length)
        {
            throw new VimbaException(-7, "[F]...Invalid device ID or IP address given.");
        }

        try
        {
            // start Vimba
            this.mSystem.Startup();
        }
        catch (VimbaException ve)
        {
            throw new VimbaException(ve.ReturnCode, "[F]...Could not start Vimba.");
        }

        this.mSystemFlag = true;
        Console.WriteLine("......Vimba has been started.");

        try
        {
            // open camera with given string (could be device ID or IP address)
            this.mCamera = this.mSystem.OpenCameraByID(aCamera, VmbAccessModeType.VmbAccessModeFull);
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not open camera.");
        }

        this.mCameraFlag =  true;
        Console.WriteLine(string.Format("......Camera has been opened ({0}).",aCamera));
    }

    /// <summary>
    /// Close camera and shutdown Vimba
    /// </summary>
    public void StopCamera()
    {
        try
        {
            // close camera
            this.mCamera.Close();
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode,"[F]...Could not close camera.");
        }

        this.mCameraFlag = false;
        Console.WriteLine("......Camera has been closed.");

        try
        {
            // shutdown Vimba
            this.mSystem.Shutdown();
        }
        catch (VimbaException ve)
        {
            throw new VimbaException(ve.ReturnCode, "[F]...Could not stop Vimba.");
        }

        this.mSystemFlag = false;
        Console.WriteLine("......Vimba has been stopped.");
    }

    /// <summary>
    /// Prepare trigger information in the camera
    /// </summary>
    public void PrepareTrigger()
    {
        try
        {
            // select FrameStart trigger via TriggerSelector feature
            this.mCamera.Features["TriggerSelector"].EnumValue = "FrameStart";
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not set TriggerSelector to FrameStart.");
        }

        try
        {
            // set trigger source to Action0
            this.mCamera.Features["TriggerSource"].EnumValue = "Action0";
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not set TriggerSource to Action0.");
        }

        try
        {
            // enable trigger
            this.mCamera.Features["TriggerMode"].EnumValue = "On";
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not set TriggerMode to On.");
        }

        Console.WriteLine("......Trigger FrameStart has been activated and set to Action0");
    }

    /// <summary>
    /// Prepare Action Command in either System, Interface or Camera
    /// </summary>
    /// <param name="aOwner">Feature owner</param>
    /// <param name="aCommand">Action Command</param>
    public void PrepareActionCommand(tFeatureOwner aOwner, tActionCommand aCommand)
    {
        switch (aOwner)
        {
            case tFeatureOwner.eFeatureOwnerSystem:
                try
                {
                    // set device key
                    this.mSystem.Features["ActionDeviceKey"].IntValue = aCommand.mDeviceKey;
                    // set group key
                    this.mSystem.Features["ActionGroupKey"].IntValue = aCommand.mGroupKey;
                    // set group mask
                    this.mSystem.Features["ActionGroupMask"].IntValue = aCommand.mGroupMask;
                }
                catch (VimbaException ve)
                {
                    FailureShutdown();
                    throw new VimbaException(ve.ReturnCode, "[F]...Could not set Action Command to Vimba System.");
                }
                break;

            case tFeatureOwner.eFeatureOwnerInterface:
                try
                {
                    // set device key
                    this.mInterface.Features["ActionDeviceKey"].IntValue = aCommand.mDeviceKey;
                    // set group key
                    this.mInterface.Features["ActionGroupKey"].IntValue = aCommand.mGroupKey;
                    // set group mask
                    this.mInterface.Features["ActionGroupMask"].IntValue = aCommand.mGroupMask;
                }
                catch (VimbaException ve)
                {
                    FailureShutdown();
                    throw new VimbaException(ve.ReturnCode, "[F]...Could not set Action Command to Vimba Interface.");
                }
                break;

            case tFeatureOwner.eFeatureOwnerCamera:
                try
                {
                    // set device key
                    this.mCamera.Features["ActionDeviceKey"].IntValue = aCommand.mDeviceKey;
                    // set group key
                    this.mCamera.Features["ActionGroupKey"].IntValue = aCommand.mGroupKey;
                    // set group mask
                    this.mCamera.Features["ActionGroupMask"].IntValue = aCommand.mGroupMask;
                }
                catch (VimbaException ve)
                {
                    FailureShutdown();
                    throw new VimbaException(ve.ReturnCode, "[F]...Could not set Action Command to camera.");
                }
                break;
        }

        Console.WriteLine(string.Format("......Action Command has been prepared ({0},{1},{2})",aCommand.mDeviceKey,aCommand.mGroupKey,aCommand.mGroupMask));
    }

    /// <summary>
    /// Prepare camera acquisition
    /// </summary>
    public void PrepareStreaming()
    {
        try
        {
            // set GVSP packet size to max value (MTU)
            // and wait until command is done
            this.mCamera.Features["GVSPAdjustPacketSize"].RunCommand();

            // check if operation is done
            bool lFlag = false;
            do
            {
                lFlag = this.mCamera.Features["GVSPAdjustPacketSize"].IsCommandDone();
            } while (false == lFlag);
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not adjust GVSP packet size.");
        }

        try
        {
            // get GVSP packet size, which was actually set in the camera
            Console.WriteLine(string.Format("......GVSP packet size has been set to maximum ({0})", this.mCamera.Features["GVSPPacketSize"].IntValue));
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not retrieve GVSP packet size.");
        }

        try
        {
            // register frame callback
            this.mCamera.OnFrameReceived += this.FrameReceived;
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not register frame callback.");
        }

        try
        {
            // start continuous image acquisition
            this.mCamera.StartContinuousImageAcquisition(3);
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not start camera acquisition.");
        }

        this.mStreamingFlag = true;
        Console.WriteLine("......Streaming has been started");
    }

    /// <summary>
    /// Stop camera acquisition
    /// </summary>
    public void StopStreaming()
    {
        try
        {
            // unregister frame callback
            this.mCamera.OnFrameReceived -= FrameReceived;
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not unregister frame callback.");
        }

        try
        {
            // stop continuous image acquisition
            this.mCamera.StopContinuousImageAcquisition();
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not stop camera acquisition.");
        }

        this.mStreamingFlag = false;
        Console.WriteLine("......Streaming has been stopped");
    }

    /// <summary>
    /// Send Action Command as broadcast via all interfaces
    /// </summary>
    /// <param name="aCamera">Camera ID or IP address</param>
    /// <param name="aCommand">Action Command</param>
    public void SendActionCommandOnAllInterfaces(String aCamera, tActionCommand aCommand)
    {
        // -start Vimba
        // -open camera in full access mode and get handle
        PrepareCamera(aCamera);

        // -select FrameStart trigger feature
        // -set source to Action0
        // -enable trigger
        PrepareTrigger();

        // Set Action Command to camera
        // -set device key
        // -set group key
        // -set group mask
        PrepareActionCommand(tFeatureOwner.eFeatureOwnerCamera, aCommand);

        // -adjust GVSP packet size
        // -get payload size
        // -allocate memory for frame buffers
        // -announce frames and move them to buffer input pool
        // -start capture engine
        // -move frames to capture queue (buffer output queue)
        // -call start acquisition feature in the camera
        PrepareStreaming();

        try
        {
            // determine if Action Command shall be send as uni- or broadcast
            // if IP address was given, send it as unicast
            IPAddress lIP;
            bool lFlag = IPAddress.TryParse(aCamera, out lIP);
            if (true == lFlag)
            {
                uint lHostOrderIP = (uint)IPAddress.NetworkToHostOrder((int)lIP.Address);
                this.mSystem.Features["GevActionDestinationIPAddress"].IntValue = (long)lHostOrderIP;
                Console.WriteLine(string.Format("......Action Command will be send as unicast to IP '{0}' ({1})", aCamera, lIP));
            }
        }
        catch (Exception e)
        {
            FailureShutdown();
            throw new VimbaException(-13, "[F]...Could not convert string to IP address.");
        }

        // set Action Command to Vimba system
        // -device key
        // -group key
        // -group mask
        PrepareActionCommand(tFeatureOwner.eFeatureOwnerSystem, aCommand);

        Console.WriteLine();
        Console.WriteLine("<< Please hit 'a' to send prepared Action Command. To stop example hit 'q' >>");
        Console.WriteLine();

        // repeat this until user hits ESC
        ConsoleKeyInfo lKey;
        do
        {
            // wait for user input
            lKey = Console.ReadKey();

            if( ConsoleKey.A == lKey.Key )
            {

                try
                {
                    // send Action Command by calling command feature
                    mSystem.Features["ActionCommand"].RunCommand();
                }
                catch (VimbaException ve)
                {
                    FailureShutdown();
                    throw new VimbaException(ve.ReturnCode, "[F]...Could not send Action Command.");
                }

                Console.WriteLine("......Action Command has been sent");
            }

        } while( ConsoleKey.Q != lKey.Key );

        // stop streaming
        StopStreaming();

        // -close camera
        // -shutdown Vimba
        StopCamera();
    }

    /// <summary>
    /// Send Action Command as broadcast via all interfaces
    /// </summary>
    /// <param name="aCamera">Camera ID or IP address</param>
    /// <param name="aInterface">Interface index</param>
    /// <param name="aCommand">Action Command</param>
    public void SendActionCommandOnInterface(String aCamera, String aInterface, tActionCommand aCommand)
    {
        // -start Vimba
        // -open camera in full access mode and get handle
        PrepareCamera(aCamera);

        // -select FrameStart trigger feature
        // -set source to Action0
        // -enable trigger
        PrepareTrigger();

        // Set Action Command to camera
        // -set device key
        // -set group key
        // -set group mask
        PrepareActionCommand(tFeatureOwner.eFeatureOwnerCamera, aCommand);

        // -adjust GVSP packet size
        // -get payload size
        // -allocate memory for frame buffers
        // -announce frames and move them to buffer input pool
        // -start capture engine
        // -move frames to capture queue (buffer output queue)
        // -call start acquisition feature in the camera
        PrepareStreaming();

        try
        {
            // get interface with given index
            this.mInterface = this.mSystem.GetInterfaceByID(aInterface);

            // open interface
            this.mInterface.Open();
        }
        catch(VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not open interface.");
        }

        this.mInterfaceFlag = true;
        Console.WriteLine(string.Format("......Interface '{0}' has been opened.", aInterface));

        try
        {
            // determine if Action Command shall be send as uni- or broadcast
            // if IP address was given, send it as unicast
            IPAddress lIP;
            bool lFlag = IPAddress.TryParse(aCamera, out lIP);
            if (true == lFlag)
            {
                uint lHostOrderIP = (uint)IPAddress.NetworkToHostOrder((int)lIP.Address);
                this.mInterface.Features["GevActionDestinationIPAddress"].IntValue = (long)lHostOrderIP;
                Console.WriteLine(string.Format("......Action Command will be send as unicast to IP '{0}' ({1})", aCamera, lIP));
            }
        }
        catch (Exception e)
        {
            FailureShutdown();
            throw new VimbaException(-13, "[F]...Could not convert string to IP address.");
        }

        // set Action Command to the selected interface
        // -device key
        // -group key
        // -group mask
        PrepareActionCommand(tFeatureOwner.eFeatureOwnerInterface, aCommand);

        Console.WriteLine();
        Console.WriteLine("<< Please hit 'a' to send prepared Action Command. To stop example hit 'q' >>");
        Console.WriteLine();

        // repeat this until user hits ESC
        ConsoleKeyInfo lKey;
        do
        {
            // wait for user input
            lKey = Console.ReadKey();

            if (ConsoleKey.A == lKey.Key)
            {

                try
                {
                    // send Action Command by calling command feature
                    this.mInterface.Features["ActionCommand"].RunCommand();
                }
                catch (VimbaException ve)
                {
                    FailureShutdown();
                    throw new VimbaException(ve.ReturnCode, "[F]...Could not send Action Command.");
                }

                Console.WriteLine("......Action Command has been sent");
            }

        } while (ConsoleKey.Q != lKey.Key);

        try
        {
            // close interface
            this.mInterface.Close();
        }
        catch (VimbaException ve)
        {
            FailureShutdown();
            throw new VimbaException(ve.ReturnCode, "[F]...Could not close interface.");
        }

        this.mInterfaceFlag = false;
        Console.WriteLine("......Interface has been closed.");

        // stop streaming
        StopStreaming();

        // -close camera
        // -shutdown Vimba
        StopCamera();
    }
}

}}} // Namespace AVT::VmbAPINET::Examples
/*=============================================================================
  Copyright (C) 2012 - 2016 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        BandwidthHelper.cs

  Description: The BandwidthHelper example demonstrates how to get and set the
               bandwidth used by a camera using VimbaNET.

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

namespace AVT {
namespace VmbAPINET {
namespace Examples {

/// <summary>
/// Calculates and sets the bandwidth allocated to one device on a bus or network.
/// This effects the actual throughput (and therefore the frame rate) of a device.
/// </summary>
class BandwidthHelper
{
    private const int PACKET_SIZE_MAX_1394_S100 = 1024;
    private const int PACKET_SIZE_MAX_1394_S200 = 2048;
    private const int PACKET_SIZE_MAX_1394_S400 = 4096;
    private const int PACKET_SIZE_MAX_1394_S800 = 8192;

    /// <summary>
    /// Calculates the current bandwidth usage of a camera in relation to a free bus / network
    /// </summary>
    /// <param name="camera">Our device</param>
    /// <returns>The current bandwidth usage (maximum 1)</returns>
    public static double GetBandwidthUsage( Camera camera )
    {
        if ( null == camera )
        {
            throw new ArgumentNullException("camera");
        }

        double fBandwidth = 0;
        Int64 nValue;
        Vimba system = new Vimba();

        switch ( (VmbInterfaceType)system.GetInterfaceByID( camera.InterfaceID ).Type )
        {
            case VmbInterfaceType.VmbInterfaceEthernet:
            {
                nValue = camera.Features["StreamBytesPerSecond"].IntValue;
                Int64 nMax = camera.Features["StreamBytesPerSecond"].IntRangeMax;
                                
                fBandwidth = (double)nValue / nMax;
            }
            break;

            case VmbInterfaceType.VmbInterfaceFirewire:
            {
                nValue = camera.Features["IIDCPacketSize"].IntValue;
                int nPhySpeed = Int32.Parse(camera.Features["IIDCPhyspeed"].EnumValue.Substring(1));
                switch (nPhySpeed)
                {
                    case 100: nPhySpeed = PACKET_SIZE_MAX_1394_S100;
                        break;
                    case 200: nPhySpeed = PACKET_SIZE_MAX_1394_S200;
                        break;
                    case 400: nPhySpeed = PACKET_SIZE_MAX_1394_S400;
                        break;
                    case 800: nPhySpeed = PACKET_SIZE_MAX_1394_S800;
                        break;
                    default: throw new Exception("Unsupported phy speed");
                }
                        
                fBandwidth = (double)nValue / (double)nPhySpeed;
            }
            break;

            case VmbInterfaceType.VmbInterfaceUsb:
            {
                string strMode = camera.Features["DeviceLinkThroughputLimitMode"].EnumValue;
                // If link speed limit is disabled, the used bandwidth can be up to 100%
                if ( "Off" == strMode )
                {
                    fBandwidth = 1.0;
                }
                else
                {
                    // If link speed limit is enabled, get its current value
                    nValue = camera.Features["DeviceLinkThroughputLimit"].IntValue;
                    Int64 nMax = camera.Features["DeviceLinkThroughputLimit"].IntRangeMax;
                    fBandwidth = (double)nValue / nMax;
                }
            }
            break;

            default:
                throw new VimbaException((int)VmbErrorType.VmbErrorWrongType, "Unsupported interface type");
        }

        return fBandwidth;
    }

    /// <summary>
    /// Sets the current bandwidth usage in relation to a free bus / network
    /// </summary>
    /// <param name="camera">Our device</param>
    /// <param name="fBandwidth">The bandwidth to be set (maximum 1)</param>
    public static void SetBandwidthUsage( Camera camera, double fBandwidth )
    {
        if ( null == camera )
        {
            throw new ArgumentNullException("camera");
        }

        Int64 nValue;
        Vimba system = new Vimba();

        switch ( (VmbInterfaceType)system.GetInterfaceByID( camera.InterfaceID ).Type )
        {
            case VmbInterfaceType.VmbInterfaceEthernet:
            {
                Int64 nMax = camera.Features["StreamBytesPerSecond"].IntRangeMax;
                nValue = (Int64)(fBandwidth * nMax);
                camera.Features["StreamBytesPerSecond"].IntValue = nValue;
            }
            break;

            case VmbInterfaceType.VmbInterfaceFirewire:
            {
                camera.Features["IIDCPacketSizeAuto"].EnumValue = "Off";
                int nPhySpeed = Int32.Parse(camera.Features["IIDCPhyspeed"].EnumValue.Substring(1));
                switch ( nPhySpeed )
                {
                    case 100 : nPhySpeed = PACKET_SIZE_MAX_1394_S100;
                        break;
                    case 200 : nPhySpeed = PACKET_SIZE_MAX_1394_S200;
                        break;
                    case 400 : nPhySpeed = PACKET_SIZE_MAX_1394_S400;
                        break;
                    case 800 : nPhySpeed = PACKET_SIZE_MAX_1394_S800;
                        break;
                    default: throw new Exception("Unsupported phy speed");
                }
                // Set packet size to new percentage
                nValue = (Int64)(fBandwidth * nPhySpeed);
                // Adjust new value to fit increment
                Int64 nInc = camera.Features["IIDCPacketSize"].IntIncrement;
                nValue -= (nValue % nInc);
                // Write new value
                camera.Features["IIDCPacketSize"].IntValue = nValue;
            }
            break;

            case VmbInterfaceType.VmbInterfaceUsb:
            {
                // Enable link speed limit
                camera.Features["DeviceLinkThroughputLimitMode"].EnumValue = "On";
                Int64 nMax = camera.Features["DeviceLinkThroughputLimit"].IntRangeMax;
                nValue = (Int64)(fBandwidth * nMax);
                // Set link speed limit
                camera.Features["DeviceLinkThroughputLimit"].IntValue = nValue;
            }
            break;

            default:
                throw new VimbaException((int)VmbErrorType.VmbErrorWrongType, "Unsupported interface type");
        }
    }

    /// <summary>
    /// The relative minimum bandwidth usage as reported by the device
    /// </summary>
    /// <param name="camera">Our device</param>
    /// <returns>The ratio of minimum and maximum of either stream bytes per second or the packet size</returns>
    public static double GetMinPossibleBandwidthUsage( Camera camera )
    {
        if ( null == camera )
        {
            throw new ArgumentNullException("camera");
        }

        double fBandwidth = 0;
        Int64 nMinValue;
        Int64 nMaxValue;
        Vimba system = new Vimba();

        switch ( (VmbInterfaceType)system.GetInterfaceByID( camera.InterfaceID ).Type )
        {
            case VmbInterfaceType.VmbInterfaceEthernet:
            {
                nMinValue = camera.Features["StreamBytesPerSecond"].IntRangeMin;
                nMaxValue = camera.Features["StreamBytesPerSecond"].IntRangeMax;
                                
                fBandwidth = (double)nMinValue / nMaxValue;
            }
            break;

            case VmbInterfaceType.VmbInterfaceFirewire:
            {
                nMinValue = camera.Features["IIDCPacketSize"].IntRangeMin;
                int nPhySpeed = Int32.Parse(camera.Features["IIDCPhyspeed"].EnumValue.Substring(1));
                switch (nPhySpeed)
                {
                    case 100: nPhySpeed = PACKET_SIZE_MAX_1394_S100;
                        break;
                    case 200: nPhySpeed = PACKET_SIZE_MAX_1394_S200;
                        break;
                    case 400: nPhySpeed = PACKET_SIZE_MAX_1394_S400;
                        break;
                    case 800: nPhySpeed = PACKET_SIZE_MAX_1394_S800;
                        break;
                    default: throw new Exception("Unsupported phy speed");
                }
                        
                fBandwidth = (double)nMinValue / (double)nPhySpeed;
            }
            break;

            case VmbInterfaceType.VmbInterfaceUsb:
            {
                nMinValue = camera.Features["DeviceLinkThroughputLimit"].IntRangeMin;
                nMaxValue = camera.Features["DeviceLinkThroughputLimit"].IntRangeMax;
                fBandwidth = (double)nMinValue / nMaxValue;
            }
            break;

            default:
                throw new VimbaException((int)VmbErrorType.VmbErrorWrongType, "Unsupported interface type");
        }

        return fBandwidth;
    }

    /// <summary>
    /// The relative maximum bandwidth usage as reported by the device
    /// </summary>
    /// <param name="camera">Our device</param>
    /// <returns>The ratio of maximum packet size as reported by the device and the maximum of the bus (for technologies other than fire wire always 1)</returns>
    public static double GetMaxPossibleBandwidthUsage( Camera camera )
    {
        if ( null == camera )
        {
            throw new ArgumentNullException("camera");
        }

        double fBandwidth = 0;
        Int64 nMaxValue;
        Vimba system = new Vimba();

        switch ( (VmbInterfaceType)system.GetInterfaceByID( camera.InterfaceID ).Type )
        {
            case VmbInterfaceType.VmbInterfaceEthernet:
            {
                fBandwidth = 1.0;
            }
            break;

            case VmbInterfaceType.VmbInterfaceFirewire:
            {
                nMaxValue = camera.Features["IIDCPacketSize"].IntRangeMax;
                int nPhySpeed = Int32.Parse(camera.Features["IIDCPhyspeed"].EnumValue.Substring(1));
                switch (nPhySpeed)
                {
                    case 100: nPhySpeed = PACKET_SIZE_MAX_1394_S100;
                        break;
                    case 200: nPhySpeed = PACKET_SIZE_MAX_1394_S200;
                        break;
                    case 400: nPhySpeed = PACKET_SIZE_MAX_1394_S400;
                        break;
                    case 800: nPhySpeed = PACKET_SIZE_MAX_1394_S800;
                        break;
                    default: throw new Exception("Unsupported phy speed");
                }
                        
                fBandwidth = (double)nMaxValue / (double)nPhySpeed;
            }
            break;
            
            case VmbInterfaceType.VmbInterfaceUsb:
            {
                fBandwidth = 1.0;
            }
            break;

            default:
                throw new VimbaException((int)VmbErrorType.VmbErrorWrongType, "Unsupported interface type");
        }

        return fBandwidth;
    }
}

}}} // Namespace AVT::VmbAPINET::Examples

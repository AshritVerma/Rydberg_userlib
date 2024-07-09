/*=============================================================================
  Copyright (C) 2014 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision is prohibited.

-------------------------------------------------------------------------------

  File:         SerialIO.c

  Description:  The SerialIO example will read and write from the cameras
                serial port.
                To setup and use the serial IO, it is needed to use the direct
                register access of the camera.

          Camera                              PC
                                             ____
         _________        GigE Cable        | __ |
      __| Allied  |~~~~~~~~~~~~~~~~~~~~~~~~~|    |
     (__|  Vision |       RS232 Cable       |    |
        |_________|~~~~~~~~~~~~~~~~~~~~~~~~~|____|
           GigE

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

#include <sstream>
#include <iostream>
#include <vector>
#include <algorithm>

#include <SerialIO.h>
#include <ComPort.h>

#include "VimbaCPP/Include/VimbaCPP.h"
#include "Common/StreamSystemInfo.h"
#include "Common/ErrorCodeToMessage.h"

namespace AVT {
namespace VmbAPI {
namespace Examples {

const Uint64Vector  SERIAL_INQUIRY_ADDRESS          ( 1, 0x16000 );
const Uint64Vector  SERIAL_ERROR_STATUS_ADDRESS     ( 1, 0x16010 );
const Uint64Vector  SERIAL_MODE_INQUIRY_ADDRESS     ( 1, 0x16100 );
const Uint64Vector  SERIAL_MODE_ADDRESS             ( 1, 0x16104 );
const Uint64Vector  SERIAL_TX_INQUIRY_ADDRESS       ( 1, 0x16120 );
const Uint64Vector  SERIAL_TX_STATUS_ADDRESS        ( 1, 0x16124 );
const Uint64Vector  SERIAL_TX_CONTROL_ADDRESS       ( 1, 0x16128 );
const Uint64Vector  SERIAL_TX_LENGTH_ADDRESS        ( 1, 0x1612C );
const Uint64Vector  SERIAL_RX_INQUIRY_ADDRESS       ( 1, 0x16140 );
const Uint64Vector  SERIAL_RX_STATUS_ADDRESS        ( 1, 0x16144 );
const Uint64Vector  SERIAL_RX_CONTROL_ADDRESS       ( 1, 0x16148 );
const Uint64Vector  SERIAL_RX_LENGTH_ADDRESS        ( 1, 0x1614C );
const VmbUint64_t   SERIAL_TX_BUFFER_ADDRESS        = 0x16400;
const VmbUint64_t   SERIAL_RX_BUFFER_ADDRESS        = 0x16800;

// Purpose: Serial IO Test Function.
//
// Parameter:
// [in ]    std::string cameraID        The ID of the camera to use. May be NULL.
// [in ]    std::string comPortName     The name of the used com port. May be NULL.
void SerialIO::RunTest( std::string cameraID, std::string comPortName )
{
    VimbaSystem&        sys             = VimbaSystem::GetInstance();                               // Get a reference to the VimbaSystem singleton
    std::cout << "Vimba C++ API Version " << sys << "\n";                                                  // Print Vimba Version
    VmbErrorType        err                 = sys.Startup();                                        // Initialize the Vimba API
    CameraPtr           pCamera             = CameraPtr();                                          // Our camera
    ComPort             *pComPort           = new ComPort();
    Uint64Vector        registerBuffer(1);
    UcharVector         memoryBuffer;

    // Register variables to handle the camera register layout
    SerialInquiryRegister       serialInquiryRegister       = {0};
    SerialModeInquiryRegister   serialModeInquiryRegister   = {0};
    SerialModeRegister          serialModeRegister          = {0};
    SerialTxInquiryRegister     serialTxInquiryRegister     = {0};
    SerialTxStatusRegister      serialTxStatusRegister      = {0};
    SerialTxControlRegister     serialTxControlRegister     = {0};
    SerialTxLengthRegister      serialTxLengthRegister      = {0};
    SerialRxInquiryRegister     serialRxInquiryRegister     = {0};
    SerialRxStatusRegister      serialRxStatusRegister      = {0};
    SerialRxControlRegister     serialRxControlRegister     = {0};
    SerialRxLengthRegister      serialRxLengthRegister      = {0};

    if( VmbErrorSuccess == err )
    {
        if( cameraID.empty() )                                                                      // If no ID was provided use the first camera
        {
            CameraPtrVector cameras;
            err = sys.GetCameras( cameras );                                                        // Get the amount of known cameras

            if(     VmbErrorSuccess == err
                &&  !cameras.empty() )
            {
                pCamera = cameras[0];                                                               // Get the camera
                err = pCamera->Open( VmbAccessModeFull );                                           // Open the camera
                if( VmbErrorSuccess == err )
                {
                    err = pCamera->GetID( cameraID );
                }
            }
        }
        else
        {
            err = sys.OpenCameraByID( cameraID.c_str(), VmbAccessModeFull, pCamera );               // Get and open the camera
        }

        if(    NULL != pCamera
            && VmbErrorSuccess == err )
        {
            if( 0 == pComPort->Init( comPortName ) )
            {
                err = pCamera->ReadRegisters( SERIAL_INQUIRY_ADDRESS, registerBuffer );
                serialInquiryRegister.RawData = registerBuffer[0];

                if( VmbErrorSuccess == err )
                {
                    // Setup the serial port of the camera with a baud rate of 115.2 kBaud, 8 data bits, no parity and 1 stop bit
                    serialModeRegister.BaudRate         = VmbSerialBaudRate115200;
                    serialModeRegister.CharacterLength  = VmbSerialCharLength8Bits;
                    serialModeRegister.Parity           = VmbSerialParityNone;
                    serialModeRegister.StopBits         = VmbSerialStopBits1;

                    registerBuffer.assign( 1, serialModeRegister.RawData );
                    err = pCamera->WriteRegisters( SERIAL_MODE_ADDRESS, registerBuffer );

                    if( VmbErrorSuccess == err )
                    {
                        if( VmbInquiryYes == serialInquiryRegister.TransmitterInquiry )
                        {
                            serialTxControlRegister.TransmitterEnable = 1;                          // Enable the transmitter of the camera serial port

                            registerBuffer.assign( 1, serialTxControlRegister.RawData );
                            err = pCamera->WriteRegisters( SERIAL_TX_CONTROL_ADDRESS, registerBuffer );

                            if( VmbErrorSuccess == err )
                            {
                                std::string input( "Allied Vision" );
                                UcharVector writeData( input.length() );
                                // Fill the test data
                                std::transform(input.begin(), input.end(), writeData.begin(),  [](char c)
                                {
                                    return static_cast<unsigned char>(c);
                                });

                                err = pCamera->WriteMemory( SERIAL_TX_BUFFER_ADDRESS, writeData );

                                if( VmbErrorSuccess == err )
                                {
                                    serialTxLengthRegister.DataLength = writeData.size();            // Write the register, how much data has to be written on the serial port

                                    registerBuffer.assign( 1, serialTxLengthRegister.RawData );
                                    err = pCamera->WriteRegisters( SERIAL_TX_LENGTH_ADDRESS, registerBuffer );
                                    if( VmbErrorSuccess == err )
                                    {
                                        size_t bufferLength = writeData.size();
                                        char *pDataBuffer = (char*)malloc( bufferLength + 1 );
                                        memset( pDataBuffer, 0, bufferLength + 1 );

                                        if( NULL != pDataBuffer )
                                        {
                                            if( 0 == pComPort->Read( pDataBuffer, bufferLength ) )
                                            {
                                                std::cout << "Received message on the serial port: '" << pDataBuffer << "'\n";
                                            }
                                            else
                                            {
                                                std::cout << "Could not read on the serial port.\n";
                                            }

                                            free( pDataBuffer );
                                        }
                                        else
                                        {
                                            std::cout << "Could not alloc the data buffer.\n";
                                        }
                                    }
                                    else
                                    {
                                        std::cout << "Could not write the length of the written buffer. Error code: " << err << " (" << AVT::VmbAPI::Examples::ErrorCodeToMessage( err ) << ")" << "\n";
                                    }
                                }
                                else
                                {
                                    std::cout << "Could not fill the transmit buffer. Error code: " << err << " (" << AVT::VmbAPI::Examples::ErrorCodeToMessage( err ) << ")" << "\n";
                                }
                            }
                            else
                            {
                                std::cout << "Could not enable the transmitter within the camera. Error code: " << err << " (" << AVT::VmbAPI::Examples::ErrorCodeToMessage( err ) << ")" << "\n";
                            }
                        }
                        else
                        {
                            std::cout << "The selected camera has no serial transmitter.\n";
                        }

                        if( VmbInquiryYes == serialInquiryRegister.ReceiverInquiry )
                        {
                            serialRxControlRegister.ReceiverReset   = 1;                            // Reset the receiver to clear the RxBuffer
                            serialRxControlRegister.ReceiverEnable  = 1;                            // Enable the receiver of the camera serial port

                            registerBuffer.assign( 1, serialRxControlRegister.RawData );
                            err = pCamera->WriteRegisters( SERIAL_RX_CONTROL_ADDRESS, registerBuffer );

                            if( VmbErrorSuccess == err )
                            {
                                if( 0 == pComPort->Write( "Allied Vision", sizeof( "Allied Vision" ) ) )
                                {
                                    err = pCamera->ReadRegisters( SERIAL_RX_LENGTH_ADDRESS, registerBuffer );
                                    serialRxLengthRegister.RawData = registerBuffer[0];

                                    if( VmbErrorSuccess == err )
                                    {
                                        UcharVector readData( serialRxLengthRegister.DataLength );
                                        err = pCamera->ReadMemory( SERIAL_RX_BUFFER_ADDRESS, readData );

                                        if( VmbErrorSuccess == err)
                                        {
                                            std::string stringMessage(readData.begin(), readData.end());
                                            std::cout << "Received message on the camera serial: '" << stringMessage << "'\n";
                                        }
                                        else
                                        {
                                            std::cout << "Could not read the receive buffer from the camera. Error code: " << err << " (" << AVT::VmbAPI::Examples::ErrorCodeToMessage( err ) << ")" << "\n";
                                        }
                                    }
                                    else
                                    {
                                        std::cout << "Could not read the length of the received data. Error code: " << err << " (" << AVT::VmbAPI::Examples::ErrorCodeToMessage( err ) << ")" << "\n";
                                    }
                                }
                                else
                                {
                                    std::cout << "Could not write on the serial port.\n";
                                }
                            }
                            else
                            {
                                std::cout << "Could not enable the receiver within the camera. Error code: " << err << " (" << AVT::VmbAPI::Examples::ErrorCodeToMessage( err ) << ")" << "\n";
                            }
                        }
                        else
                        {
                            std::cout << "The selected camera has no serial receiver.\n";
                        }
                    }
                    else
                    {
                        std::cout << "Could not setup the serial mode on the camera. Error code: " << err << " (" << AVT::VmbAPI::Examples::ErrorCodeToMessage( err ) << ")" << "\n";
                    }
                }
                else
                {
                    std::cout << "Could not read inquiry register. Error code: " << err << " (" << AVT::VmbAPI::Examples::ErrorCodeToMessage( err ) << ")" << "\n";
                }

                pComPort->Close();                                                                  // Close the com port
            }

            pCamera->Close();                                                                       // Close the camera
        }
        else
        {
            std::cout << "Could not open camera or no camera available. Error code: " << err << " (" << AVT::VmbAPI::Examples::ErrorCodeToMessage( err ) << ")" << "\n";
        }
        
        sys.Shutdown();                                                                             // Close Vimba
    }
    else
    {
        std::cout << "Could not start system. Error code: " << err << " (" << AVT::VmbAPI::Examples::ErrorCodeToMessage( err ) << ")" << "\n";
    }
}

}}} // namespace AVT::VmbAPI::Examples
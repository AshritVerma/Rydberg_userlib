/*=============================================================================
  Copyright (C) 2014 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision is prohibited.

-------------------------------------------------------------------------------

  File:         ComPort.c

  Description:  TBD

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
#include <Windows.h>

#include <ComPort.h>

namespace AVT {
namespace VmbAPI {
namespace Examples {

HANDLE g_ComPortHandle = NULL;                                              // Global handle of the PC's com port


// Purpose: Open the used com port of the PC and configure it to with a
//          baud rate of 115200 Baud, data with of 8, no parity and 1 stop
//          bit.
//
// Parameter:
// [in ]    const char* portName            The Name of the com port to use.
//
// Returns:
//          0 in case of success otherwise a negative which indicates the error
int ComPort::Init( std::string portName )
{
    int             returnValue     = 0;
    DCB             comPortConfig   = {0};                                  // Com port configuration struct
    COMMTIMEOUTS    comPortTimeout  = {0};                                  // Com port timeout struct

    LPCSTR          comPortName     = NULL;
    int             length          = 0;

    if( !portName.empty() )                                                 // Use the COM1 as default if the comport name is not specified
    {
        comPortName = portName.c_str();
    }
    else
    {
        comPortName = "COM1";
    }

    if( 0 == returnValue )
    {
        g_ComPortHandle = CreateFile(   comPortName,                        // Open the com port with read/write access
                                        GENERIC_READ | GENERIC_WRITE,
                                        0,
                                        NULL,
                                        OPEN_EXISTING,
                                        FILE_ATTRIBUTE_NORMAL,
                                        NULL );

        if( INVALID_HANDLE_VALUE != g_ComPortHandle )
        {
            if( 0 != GetCommState( g_ComPortHandle, &comPortConfig ) )
            {
                comPortConfig.BaudRate   = CBR_115200;                      // Configure the com port to 115200 Baud and 8N1
                comPortConfig.ByteSize   = 8;
                comPortConfig.Parity     = NOPARITY;
                comPortConfig.StopBits   = ONESTOPBIT;

                if( 0 != SetCommState( g_ComPortHandle, &comPortConfig ) )
                {
                    comPortTimeout.ReadIntervalTimeout = 3;                 // Configure the timeout for the used com port
                    comPortTimeout.ReadTotalTimeoutMultiplier = 3;
                    comPortTimeout.ReadTotalTimeoutConstant = 2;
                    comPortTimeout.WriteTotalTimeoutMultiplier = 3;
                    comPortTimeout.WriteTotalTimeoutConstant = 2;

                    if( 0 != SetCommTimeouts( g_ComPortHandle, &comPortTimeout ) )
                    {
                        printf( "PC's com port initialized.\n" );
                    }
                    else
                    {
                        printf( "Could not set the timeouts for the serial port.\n" );
                        CloseHandle( g_ComPortHandle );
                        returnValue = -5;
                    }
                }
                else
                {
                    printf( "Could not store the serial port configuration for the PC.\n" );
                    CloseHandle( g_ComPortHandle );
                    returnValue = -4;
                }

            }
            else
            {
                printf( "Could not get the serial port configuration from the PC.\n" );
                CloseHandle( g_ComPortHandle );
                returnValue = -3;
            }
        }
        else
        {
            printf( "Could not open the serial port.\n" );
            returnValue = -2;
        }
    }

    return returnValue;
}


// Purpose: Write the given data over the configured com port of the PC.
//
// Parameter:
// [in ]    void*   pBytesToTransmit            String of data to transmit over the com port.
// [in ]    size_t  lengthToTransmit            Amount of data which has to write.
//
// Returns:
//          0 in case of success otherwise a negative which indicates the error
int ComPort::Write( void* pDataToTransmit, size_t lengthToTransmit )
{
    DWORD   bytesWritten    = 0;
    int     returnValue     = 0;

    if(0 == WriteFile( g_ComPortHandle, pDataToTransmit, lengthToTransmit, &bytesWritten, NULL ) )
    {
        returnValue = -1;
    }

    if( bytesWritten != lengthToTransmit )
    {
        returnValue = -2;
    }

    return returnValue;
}


// Purpose: Read data from the configured com port of the PC into the given array.
//
// Parameter:
// [out]    void*   pDataToReceive              Data array buffer to write the received data into.
// [in ]    int     lengthToReceive             Amount of data which has to read.
//
// Returns:
//          0 in case of success otherwise a negative which indicates the error
int ComPort::Read( void* pDataToReceive, size_t lengthToReceive )
{
    DWORD   bytesRead   = 0;
    int     returnValue = 0;
    
    if( 0 == ReadFile( g_ComPortHandle, pDataToReceive, lengthToReceive, &bytesRead, NULL ) )
    {
        returnValue = -1;
    }

    if( bytesRead != lengthToReceive )
    {
        returnValue = -2;
    }

    return returnValue;
}


// Purpose: Close the com port of the PC correctly.
//
// Returns:
//          0 in case of success otherwise a negative which indicates the error
int ComPort::Close()
{
    if( INVALID_HANDLE_VALUE != g_ComPortHandle )
    {
        CloseHandle( g_ComPortHandle );
    }

    return 0;
}

}}} // namespace AVT::VmbAPI::Examples
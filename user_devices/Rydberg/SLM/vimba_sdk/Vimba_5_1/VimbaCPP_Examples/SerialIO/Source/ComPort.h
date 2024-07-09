/*=============================================================================
  Copyright (C) 2014 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:         ComPort.h

  Description:  

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

#ifndef COM_PORT_H_
#define COM_PORT_H_

namespace AVT {
namespace VmbAPI {
namespace Examples {

class ComPort {

public :
    // Purpose: Open the used com port of the PC and configure it to with a
    //          baud rate of 115200 Baud, data with of 8, no parity and 1 stop
    //          bit.
    //
    // Parameter:
    // [in ]    std::string comPortName             The Name of the com port to use.
    //
    // Returns:
    //          0 in case of success otherwise a negative which indicates the error
    int Init( std::string comPortName );

    // Purpose: Write the given data over the configured com port of the PC.
    //
    // Parameter:
    // [in ]    void*   pBytesToTransmit            String of data to transmit over the com port.
    // [in ]    size_t  lengthToTransmit            Amount of data which has to write.
    //
    // Returns:
    //          0 in case of success otherwise a negative which indicates the error
    int Write( void* pDataToTransmit, size_t lengthToTransmit );

    // Purpose: Read data from the configured com port of the PC into the given array.
    //
    // Parameter:
    // [out]    void*   pDataToReceive              Char array buffer to write the received data into.
    // [in ]    int     lengthToReceive             Amount of data which has to read.
    //
    // Returns:
    //          0 in case of success otherwise a negative which indicates the error
    int Read( void* pDataToReceive, size_t lengthToReceive );

    // Purpose: Close the com port of the PC correctly.
    //
    // Returns:
    //          0 in case of success otherwise a negative which indicates the error
    int Close();
};

}}} // namespace AVT::VmbAPI::Examples

#endif
/*=============================================================================
  Copyright (C) 2017 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        Program.cs

  Description: Main entry point of ActionCommands example of VimbaCPP.

               annotations:
                -local variables are prefixed with 'l' for local
                -function parameter are prefixed with 'a' for 'argument'
                -structs are prefixed with 't' for 'type'
                -classes are prefixed with 'c' for 'class'
                -class attributes and struct members are prefixed with 'm' for members
                -enum literals are prefixed with 'e' for 'enumeration'

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

using AVT.VmbAPINET;

namespace AVT {
namespace VmbAPINET {
namespace Examples {

class Program
{
    static void PrintHelp()
    {
        Console.WriteLine("Usage: ActionCommands <CameraID/IPAdress> <InterfaceIndex>");
        Console.WriteLine();
        Console.WriteLine("Parameters:   CameraID         ID of the camera to be used");
        Console.WriteLine("              IPAddress        IP address of camera to react on Action Command");
        Console.WriteLine("              InterfaceID      ID of network interface to send out Action Command");
        Console.WriteLine("                               'ALL' enables broadcast on all interfaces (default, if no index given)");
        Console.WriteLine();
    }

    static void Main( string[] args )
    {
        Console.WriteLine();
        Console.WriteLine("/////////////////////////////////////////" );
        Console.WriteLine("/// Vimba API Action Commands Example ///");
        Console.WriteLine("/////////////////////////////////////////" );
        Console.WriteLine();

        try
        {
            // check number of arguments
            if( 2 == args.Length )
            {
                // create Action Command example instance
                cActionCommands lProgram = new cActionCommands();

                // define Action Command to be set in the camera
                // and used by either Vimba system or interface module
                tActionCommand lActionCommand;
                lActionCommand.mDeviceKey = 1;
                lActionCommand.mGroupKey = 1;
                lActionCommand.mGroupMask = 1;

                // check if interface index is '-1' to send out Action Command on all interfaces
                // if not, send Action Command via given network interface
                if( 0 == args[1].CompareTo("ALL") )
                {
                    lProgram.SendActionCommandOnAllInterfaces(args[0], lActionCommand);
                }
                else
                {
                    lProgram.SendActionCommandOnInterface(args[0], args[1], lActionCommand);
                }
            }
            else
            {
                Console.WriteLine("[F]...Invalid number of parameters given!");
                Console.WriteLine();
                PrintHelp();
            }
        }
        catch ( VimbaException ve )
        {
            Console.WriteLine(ve.Message + ". Reason: " + ve.ReturnCode.ToString() + "(" + ve.MapReturnCodeToString() + ")");
        }
        catch ( Exception e )
        {
            Console.WriteLine("Unknown exception: '" + e.Message + "'");
        }

        Console.WriteLine();
    }

}

}}} // Namespace AVT::VmbAPINET::Examples

/*=============================================================================
  Copyright (C) 2016 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        Program.cs

  Description: Main entry point of LoadSaveSettings example of VimbaNET.

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
using System.Collections.Specialized;

using AVT.VmbAPINET;

namespace AVT {
namespace VmbAPINET {
namespace Examples {

class Program
{
    static void Main( string[] args )
    {
        bool apiFlag = false;
        Vimba sys = new Vimba();
        Camera camera;

        try
        {
            Console.WriteLine();
            Console.WriteLine("////////////////////////////////////////////");
            Console.WriteLine("/// Vimba API Load/Save Settings Example ///");
            Console.WriteLine("////////////////////////////////////////////");
            Console.WriteLine();

        //  start VimbaNET API
            sys.Startup();
            apiFlag = true;
            Console.WriteLine("--> VimbaNET has been started");

        //  open first camera in list
            CameraCollection cameras = sys.Cameras;
            camera = cameras[0];
            camera.Open(VmbAccessModeType.VmbAccessModeFull);
            string cameraId = camera.Id;
            Console.WriteLine("--> Camera with id '" + cameraId + "' has been opened");

        //  create XML file name
            string fileName = cameraId + ".xml";

        //  -------------------------------------------------------------------------------------
        //  setup load/save settings behaviour:
        //      in VimbaNET the LoadSaveSettingsSetup() method has to be called beforehand
        //      if you want to use different settings for SaveCameraSettings() or 
        //      LoadCameraSettings(). Without calling it the default settings will be used,
        //      which are shown in the example.
        //
        //      set which features shall be persisted (saved to XML):
        //          VmbFeaturePersistType.VmbFeaturePersistAll:             all features shall be persisted (including LUTs).
        //          VmbFeaturePersistType.VmbFeaturePersistStreamable:      only streamable features shall be persisted.
        //          VmbFeaturePersistType.VmbFeaturePersistNoLUT:           all features shall be persisted except for LUT,
        //                                                                  which is the recommended setting, because it might be very time consuming.
        //
        //      set logging level (0:info only, 1: with errors, 2: with warnings, 3: with debug, 4: with traces)
        //
        //      since its difficult to catch all feature dependencies during loading,
        //      multiple iterations are used (compare desired value with camera value and write it to camera)
        //  -------------------------------------------------------------------------------------
            camera.LoadSaveSettingsSetup(VmbFeaturePersistType.VmbFeaturePersistNoLUT, 2, 4);

        //  save camera settings to xml file
            camera.SaveCameraSettings(fileName);
            Console.WriteLine("--> Camera settings have been saved");

        //  restore factory settings by loading user default set
            Feature feature = camera.Features["UserSetSelector"];
            feature.EnumValue = "Default";
            feature = camera.Features["UserSetLoad"];
            feature.RunCommand();
            Console.WriteLine("--> All feature values have been restored to default");

        //  load camera setting from stored XML file
            camera.LoadCameraSettings(fileName);
            Console.WriteLine("--> Feature values have been loaded from given XML file '" + fileName + "'");

        //  close camera
            camera.Close();
            Console.WriteLine("--> Camera has been closed");

        //  stop VimbaNET API
            sys.Shutdown();
            apiFlag = false;
            Console.WriteLine("--> VimbaNET has been shut down");

            Console.WriteLine();
            Console.WriteLine("<<press any key to close example>>");
            Console.ReadKey();

        }
        catch( Exception exception )
        {
            Console.WriteLine( exception.Message );
            if (true == apiFlag)
            {
                sys.Shutdown();
                apiFlag = false;
            }
        }

    }
}

}}} // Namespace AVT.VmbAPINET.Examples

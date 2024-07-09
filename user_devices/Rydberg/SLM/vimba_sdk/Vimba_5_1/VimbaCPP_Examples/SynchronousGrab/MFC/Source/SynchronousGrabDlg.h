/*=============================================================================
  Copyright (C) 2012 - 2016 Allied Vision Technologies.  All Rights Reserved.

  Redistribution of this file, in original or modified form, without
  prior written consent of Allied Vision Technologies is prohibited.

-------------------------------------------------------------------------------

  File:        SynchronousGrabDlg.h

  Description: MFC dialog class for the GUI of the SynchronousGrab example of
               VimbaCPP.

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

#pragma once

#include <vector>
#include <afxwin.h>
#include <atlimage.h>

#include "VimbaCPP/Include/VimbaCPP.h"

#include "ApiController.h"


using AVT::VmbAPI::Examples::ApiController;

class CSynchronousGrabDlg : public CDialog
{
public:
    CSynchronousGrabDlg(CWnd* pParent = NULL);

    enum { IDD = IDD_SYNCHRONOUSGRAB_DIALOG };

    protected:
    virtual void DoDataExchange(CDataExchange* pDX);

protected:
    HICON m_hIcon;

    virtual BOOL OnInitDialog();
    afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
    afx_msg void OnPaint();
    afx_msg HCURSOR OnQueryDragIcon();
    afx_msg void OnBnClickedButtonStartstop();
    DECLARE_MESSAGE_MAP()

    //
    // This event handler is triggered through a MFC message posted by the camera observer
    //
    // Parameters:
    //  [in]    reason          The reason why the callback of the observer was triggered (plug-in, plug-out, ...)
    //  [in]    lParam          [Unused, demanded by MFC signature]
    //
    // Returns:
    //  Nothing, always returns 0
    //
    afx_msg LRESULT OnCameraListChanged( WPARAM reason, LPARAM lParam );

private:
    // Our controller that wraps API access
    ApiController *             m_pApiController;
    // A list of known camera IDs
    std::vector<std::string>    m_cameras;
    // Our MFC image to display
    CImage                      m_Image;

    //
    // Queries and lists all known camera
    //
    void UpdateCameraListBox();
    
    //
    // Prints out a given logging string, error code and the descriptive representation of that error code
    //
    // Parameters:
    //  [in]    strMsg          A given message to be printed out
    //  [in]    eErr            The API status code
    //
    void Log( string_type strMsg, VmbErrorType eErr );
    
    //
    // Prints out a given logging string
    //
    // Parameters:
    //  [in]    strMsg          A given message to be printed out
    //
    void Log( string_type strMsg);
    
    //
    // Converts mono 8 bit to mono bgr
    //
    // Parameters:
    //  [in]    pInBuffer       The input mono 8 byte buffer to convert
    //  [out]   pOutBuffer      The output bgr byte buffer
    //  [in]    nInSize         The size of the input buffer
    //
    void MonoToBGR( VmbUchar_t *pInBuffer, VmbUchar_t *pOutBuffer, VmbUint32_t nInSize );
    
    //
    // Copies the content of a byte buffer to a MFC image with respect to the image's alignment
    //
    // Parameters:
    //  [in]    pInbuffer       The byte buffer as received from the cam
    //  [out]   OutImage        The filled MFC image
    //
    void CopyToImage( VmbUchar_t *pInBuffer, CImage *pOutImage );

    // MFC Controls
    CListBox    m_ListBoxCameras;
    CListBox    m_ListLog;
    CButton     m_ButtonStartStop;
    CStatic     m_PictureBoxStream;
};


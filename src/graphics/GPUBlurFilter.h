//
//  libavg - Media Playback Engine. 
//  Copyright (C) 2003-2014 Ulrich von Zadow
//
//  This library is free software; you can redistribute it and/or
//  modify it under the terms of the GNU Lesser General Public
//  License as published by the Free Software Foundation; either
//  version 2 of the License, or (at your option) any later version.
//
//  This library is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
//  Lesser General Public License for more details.
//
//  You should have received a copy of the GNU Lesser General Public
//  License along with this library; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  Current versions can be found at www.libavg.de
//

#ifndef _GPUBlurFilter_H_
#define _GPUBlurFilter_H_

#include "../api.h"
#include "GPUFilter.h"
#include "MCShaderParam.h"
#include "MCTexture.h"

namespace avg {

class AVG_API GPUBlurFilter: public GPUFilter
{
public:
    GPUBlurFilter(const IntPoint& size, PixelFormat pfSrc, PixelFormat pfDest, 
            float stdDev, bool bClipBorders, bool bStandalone=true, 
            bool bUseFloatKernel=false);
    virtual ~GPUBlurFilter();
    
    void setStdDev(float stdDev);
    virtual void applyOnGPU(GLContext* pContext, GLTexturePtr pSrcTex);

private:
    void setDimensions(IntPoint size, float stdDev);

    float m_StdDev;
    bool m_bClipBorders;
    bool m_bUseFloatKernel;
    WrapMode m_WrapMode;

    MCTexturePtr m_pGaussCurveTex;
    ImagingProjectionPtr m_pProjection2;

    FloatMCShaderParamPtr m_pHorizWidthParam;
    IntMCShaderParamPtr m_pHorizRadiusParam;
    IntMCShaderParamPtr m_pHorizTextureParam;
    IntMCShaderParamPtr m_pHorizKernelTexParam;

    FloatMCShaderParamPtr m_pVertWidthParam;
    IntMCShaderParamPtr m_pVertRadiusParam;
    IntMCShaderParamPtr m_pVertTextureParam;
    IntMCShaderParamPtr m_pVertKernelTexParam;
};

typedef boost::shared_ptr<GPUBlurFilter> GPUBlurFilterPtr;

}
#endif


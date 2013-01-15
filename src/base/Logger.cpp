//
//  libavg - Media Playback Engine. 
//  Copyright (C) 2003-2011 Ulrich von Zadow
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

#include "Logger.h"

#include "OSHelper.h"
#include "Exception.h"

#ifdef _WIN32
#include <Winsock2.h>
#undef ERROR
#undef WARNING
#include <time.h>
#include <Mmsystem.h>
#else
#include <sys/time.h>
#include <syslog.h>
#endif
#include <iostream>
#include <iomanip>
#include <boost/thread.hpp>

using namespace std;

namespace avg {

const long Logger::NONE=0;
const long Logger::PROFILE=2;
const long Logger::PROFILE_VIDEO=8;
const long Logger::EVENTS=16;
const long Logger::EVENTS2=32;
const long Logger::CONFIG=64;  
const long Logger::WARNING=128;
const long Logger::ERROR=256;  
const long Logger::MEMORY=512;
const long Logger::APP=1024;
const long Logger::PLUGIN=2048;
const long Logger::PLAYER=4096;
const long Logger::SHADER=8192;
const long Logger::DEPRECATION=16384;

Logger* Logger::m_pLogger = 0;
boost::mutex logMutex;

Logger * Logger::get()
{

    if (!m_pLogger) {
        boost::mutex::scoped_lock lock(logMutex);
        m_pLogger = new Logger;
    }
    return m_pLogger;
}

Logger::Logger():
    m_pyLogger(0)
{
    m_Flags = ERROR | WARNING | APP | DEPRECATION;
    string sEnvCategories;
    bool bEnvSet = getEnv("AVG_LOG_CATEGORIES", sEnvCategories);
    if (bEnvSet) {
        m_Flags = ERROR | APP;
        bool bDone = false;
        string sCategory;
        do {
            string::size_type pos = sEnvCategories.find(":");
            if (pos == string::npos) {
                sCategory = sEnvCategories;
                bDone = true;
            } else {
                sCategory = sEnvCategories.substr(0, pos);
                sEnvCategories = sEnvCategories.substr(pos+1);
            }
            long category = stringToCategory(sCategory);
            m_Flags |= category;
        } while (!bDone);
    }
}

Logger::~Logger()
{
}

int Logger::getCategories() const
{
    boost::mutex::scoped_lock lock(logMutex);
    return m_Flags;
}

void Logger::setCategories(int flags)
{
    boost::mutex::scoped_lock lock(logMutex);
    m_Flags = flags | ERROR | WARNING;
}
    
void Logger::pushCategories()
{
    boost::mutex::scoped_lock lock(logMutex);
    m_FlagStack.push_back(m_Flags);
}

void Logger::popCategories()
{
    boost::mutex::scoped_lock lock(logMutex);
    if (m_FlagStack.empty()) {
        throw Exception(AVG_ERR_OUT_OF_RANGE, "popCategories: Nothing to pop.");
    }
    m_Flags = m_FlagStack.back();
    m_FlagStack.pop_back();
}

void Logger::setPythonLogger(PyObject* pyLogger)
{
    /*
    m_pyLogger = pyLogger;
    Py_INCREF(m_pyLogger);
    */
}

void Logger::trace(int category, const UTF8String& sMsg)
{
    boost::mutex::scoped_lock lock(logMutex);
    if (category & m_Flags) {
        struct tm* pTime;
#ifdef _WIN32
        __int64 now;
        _time64(&now);
        pTime = _localtime64(&now);
        DWORD tms = timeGetTime();
        unsigned millis = unsigned(tms % 1000);
#else
        struct timeval time;
        gettimeofday(&time, NULL);
        pTime = localtime(&time.tv_sec);
        unsigned millis = time.tv_usec/1000;
#endif
        if(m_pyLogger){
            //PyEval_CallMethod(m_pyLogger, "debug", "(s)", sMsg.c_str());
        }else{
            char timeString[256];
            strftime(timeString, sizeof(timeString), "%y-%m-%d %H:%M:%S", pTime);
            cerr << "[" << timeString << "." << 
                setw(3) << setfill('0') << millis << setw(0) << "] ";
            cerr << categoryToString(category) << ": ";
            cerr << sMsg << endl;
            cerr.flush();
        }
    }
}

const char * Logger::categoryToString(int category)
{
    switch(category) {
        case PROFILE:
        case PROFILE_VIDEO:
            return "PROFILE";
        case EVENTS:
        case EVENTS2:
            return "EVENTS";
        case CONFIG:
            return "CONFIG";
        case WARNING:
            return "WARNING";
        case ERROR:
            return "ERROR";
        case MEMORY:
            return "MEMORY";
        case APP:
            return "APP";
        case PLUGIN:
            return "PLUGIN";
        case PLAYER:
            return "PLAYER";
        case SHADER:
            return "SHADER";
        case DEPRECATION:
            return "DEPRECATION";
        default:
            return "UNKNOWN";
    }
}

int Logger::stringToCategory(const string& sCategory)
{
    if (sCategory == "PROFILE") {
        return PROFILE;
    } else if (sCategory == "PROFILE_VIDEO") {
        return PROFILE_VIDEO;
    } else if (sCategory == "EVENTS") {
        return EVENTS;
    } else if (sCategory == "EVENTS2") {
        return EVENTS2;
    } else if (sCategory == "CONFIG") {
        return CONFIG;
    } else if (sCategory == "WARNING") {
        return WARNING;
    } else if (sCategory == "ERROR") {
        return ERROR;
    } else if (sCategory == "MEMORY") {
        return MEMORY;
    } else if (sCategory == "APP") {
        return APP;
    } else if (sCategory == "PLUGIN") {
        return PLUGIN;
    } else if (sCategory == "PLAYER") {
        return PLAYER;
    } else if (sCategory == "SHADER") {
        return SHADER;
    } else if (sCategory == "DEPRECATION") {
        return DEPRECATION;
    } else {
        throw Exception (AVG_ERR_INVALID_ARGS, "Unknown logger category " + sCategory
                + " set using AVG_LOG_CATEGORIES.");
    }
}

}

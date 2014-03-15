'''
    gdrive XBMC Plugin
    Copyright (C) 2013 dmdsoftware

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''

import os
import re
import urllib, urllib2

import xbmc, xbmcaddon, xbmcgui, xbmcplugin

addon = xbmcaddon.Addon(id='plugin.video.gdrive')

def log(msg, err=False):
    if err:
        xbmc.log(addon.getAddonInfo('name') + ': ' + msg, xbmc.LOGERROR)
    else:
        xbmc.log(addon.getAddonInfo('name') + ': ' + msg, xbmc.LOGDEBUG)

class gdrive:


    def __init__(self, user, password, auth_writely, auth_wise, user_agent, authenticate=True):
        self.user = user
        self.password = password
        self.writely = auth_writely
        self.wise = auth_wise
        self.user_agent = user_agent

        # if we have an authorization token set, try to use it
        if auth_writely != '' and auth_wise != '':
          log('using token')

          return

        # allow for playback of public videos without authentication
        if (authenticate == True):
          log('logging in gdrive')
          self.login();
          self.loginWISE();

        return


    def login(self):

        url = 'https://www.google.com/accounts/ClientLogin'
        header = { 'User-Agent' : self.user_agent }
        values = {
          'Email' : self.user,
          'Passwd' : self.password,
          'accountType' : 'HOSTED_OR_GOOGLE',
          'source' : 'dmdgdrive',
          'service' : 'writely'
        }

        log('logging in gdrive')

#        log('username %s %s' % (user,urllib.urlencode(values)))
        req = urllib2.Request(url, urllib.urlencode(values), header)

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if e.code == 403:
              xbmcgui.Dialog().ok(addon.getLocalizedString(30000), 'Login information is incorrect or permission is denied')
            log(str(e), True)
            return

        response_data = response.read()

        for r in re.finditer('SID=(.*).+?' +
                             'LSID=(.*).+?' +
                             'Auth=(.*).+?' ,
                             response_data, re.DOTALL):
            sid,lsid,auth = r.groups()

        log('parameters: %s %s %s' % (sid, lsid, auth))

        self.writely = auth

        return

    def loginWISE(self):

        url = 'https://www.google.com/accounts/ClientLogin'
        header = { 'User-Agent' : self.user_agent }
        values = {
          'Email' : self.user,
          'Passwd' : self.password,
          'accountType' : 'HOSTED_OR_GOOGLE',
          'source' : 'dmdgdrive',
          'service' : 'wise'
        }


        req = urllib2.Request(url, urllib.urlencode(values), header)

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if e.code == 403:
              xbmcgui.Dialog().ok(addon.getLocalizedString(30000), 'Login information is incorrect or permission is denied')
            log(str(e), True)
            return

        response_data = response.read()

        for r in re.finditer('SID=(.*).+?' +
                             'LSID=(.*).+?' +
                             'Auth=(.*).+?' ,
                             response_data, re.DOTALL):
            sid,lsid,auth = r.groups()

        log('parameters: %s %s %s' % (sid, lsid, auth))

        self.wise = auth

        return


    def returnHeaders(self, forceWritely=False):
        #effective 2014/02, video stream calls require a wise token instead of writely token
        if forceWritely == True:
          return urllib.urlencode({ 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' })
        else:
          return urllib.urlencode({ 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.wise, 'GData-Version' : '3.0' })


    def getList(self):

        url = 'https://docs.google.com/feeds/default/private/full?showfolders=true'
        header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }

        req = urllib2.Request(url, None, header)

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if e.code == 403 or e.code == 401:
              self.login()
              header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }
              req = urllib2.Request(url, None, header)
              try:
                response = urllib2.urlopen(req)
              except urllib2.URLError, e:
                log(str(e), True)
                return
            else:
              log(str(e), True)
              return

        response_data = response.read()

        nextURL = ''
        for r in re.finditer('<link rel=\'(next)\'' ,
                             response_data, re.DOTALL):
            nextURL = r.groups()

        log('next URL %s' % nextURL)



    def getVideosHashMemoryCache(self):

        header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }

        url = 'https://docs.google.com/feeds/default/private/full?showfolders=true'


        videos = {}
        while True:
            log('url = %s header = %s' % (url, header))
            req = urllib2.Request(url, None, header)

            try:
              response = urllib2.urlopen(req)
            except urllib2.URLError, e:
              if e.code == 403 or e.code == 401:
                self.login()
                header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }
                req = urllib2.Request(url, None, header)
                try:
                  response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                  log(str(e), True)
                  return
              else:
                log(str(e), True)
                return

            response_data = response.read()


            for r in re.finditer('<title>([^<]+)</title><content type=\'video/[^\']+\' src=\'([^\']+)\'.+?rel=\'http://schemas.google.com/docs/2007/thumbnail\' type=\'image/[^\']+\' href=\'([^\']+)\'' ,
                             response_data, re.DOTALL):
                title,url,thumbnail = r.groups()
                log('found video %s %s' % (title, url))
                videos[title] = {'url': url, 'thumbnail' : thumbnail}

            #for playing video.google.com videos linked to your google drive account
            for r in re.finditer('<title>([^<]+)</title><link rel=\'alternate\' type=\'text/html\' href=\'([^\']+).+?rel=\'http://schemas.google.com/docs/2007/thumbnail\' type=\'image/[^\']+\' href=\'([^\']+)\'' ,
                             response_data, re.DOTALL):
                title,url,thumbnail = r.groups()
                log('found video %s %s' % (title, url))
                videos[title] = {'url': url, 'thumbnail' : thumbnail}


            nextURL = ''
            for r in re.finditer('<link rel=\'next\' type=\'[^\']+\' href=\'([^\']+)\'' ,
                             response_data, re.DOTALL):
                nextURL = r.groups()
                log('next URL url='+nextURL[0])

            response.close()

            if nextURL == '':
                break
            else:
                url = nextURL[0]

        return videos


    def getVideosHashStream(self):

        header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }

        url = 'https://docs.google.com/feeds/default/private/full?showfolders=true'

        videos = {}
        while True:
            log('url = %s header = %s' % (url, header))
            req = urllib2.Request(url, None, header)

            try:
              response = urllib2.urlopen(req)
            except urllib2.URLError, e:
              if e.code == 403 or e.code == 401:
                self.login()
                header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }
                req = urllib2.Request(url, None, header)
                try:
                  response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                  log(str(e), True)
                  return
              else:
                log(str(e), True)
                return

            response_data = response.read()


            for r in re.finditer('<title>([^<]+)</title><content type=\'video/[^\']+\' src=\'([^\']+)\'.+?rel=\'http://schemas.google.com/docs/2007/thumbnail\' type=\'image/[^\']+\' href=\'([^\']+)\'' ,
                             response_data, re.DOTALL):
                title,url,thumbnail = r.groups()
                log('found video %s %s' % (title, url))
                videos[title] = {'url': 'plugin://plugin.video.gdrive/?mode=streamVideo&title=' + title, 'thumbnail' : thumbnail}


            #for playing video.google.com videos linked to your google drive account
            for r in re.finditer('<title>([^<]+)</title><link rel=\'alternate\' type=\'text/html\' href=\'([^\']+).+?rel=\'http://schemas.google.com/docs/2007/thumbnail\' type=\'image/[^\']+\' href=\'([^\']+)\'' ,
                             response_data, re.DOTALL):
                title,url,thumbnail = r.groups()
                videos[title] = {'url': 'plugin://plugin.video.gdrive/?mode=streamVideo&title=' + title, 'thumbnail' : thumbnail}


            nextURL = ''
            for r in re.finditer('<link rel=\'next\' type=\'[^\']+\' href=\'([^\']+)\'' ,
                             response_data, re.DOTALL):
                nextURL = r.groups()
                log('next URL url='+nextURL[0])

            response.close()

            if nextURL == '':
                break
            else:
                url = nextURL[0]

        return videos

    def getVideoLink(self,title):

        header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }


	params = urllib.urlencode({'title': title, 'title-exact': 'true'})
        url = 'https://docs.google.com/feeds/default/private/full?' + params


        log('url = %s header = %s' % (url, header))
        req = urllib2.Request(url, None, header)
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if e.code == 403 or e.code == 401:
              self.login()
              header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }
              req = urllib2.Request(url, None, header)
              try:
                response = urllib2.urlopen(req)
              except urllib2.URLError, e:
                log(str(e), True)
                return
            else:
              log(str(e), True)
              return

        response_data = response.read()

        for r in re.finditer('<title>([^<]+)</title><content type=\'video/[^\']+\' src=\'([^\']+)\'' ,
                             response_data, re.DOTALL):
          title,url = r.groups()
          log('found video %s %s' % (title, url))
          videoURL = url

        response.close()


        return videoURL

    def getVideoPlayerLink(self,title):

        header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }


	params = urllib.urlencode({'title': title, 'title-exact': 'true'})
        url = 'https://docs.google.com/feeds/default/private/full?' + params


        log('url = %s header = %s' % (url, header))
        req = urllib2.Request(url, None, header)

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if e.code == 403 or e.code == 401:
              self.login()
              header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }
              req = urllib2.Request(url, None, header)
              try:
                response = urllib2.urlopen(req)
              except urllib2.URLError, e:
                log(str(e), True)
                return
            else:
              log(str(e), True)
              return

        response_data = response.read()

        for r in re.finditer('<title>([^<]+)</title><content type=\'video/[^\']+\' src=\'([^\']+)\'' ,
                             response_data, re.DOTALL):
          title,url = r.groups()
          log('found video %s %s' % (title, url))
          videoURL = url

        for r in re.finditer('\;docid=([^\&]+)(\&)' ,
                             response_data, re.DOTALL):
          (docid,u) = r.groups()
          log('found docid %s' % (docid))
          return self.getPlayerLink(docid)

        response.close()


        return False

    def getPlayerLink(self,docid):

        #effective 2014/02, video stream calls require a wise token instead of writely token
        self.loginWISE()
        header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.wise, 'GData-Version' : '3.0' }


        params = urllib.urlencode({'docid': docid})
        url = 'https://docs.google.com/get_video_info?docid=' + str((docid))


        log('url = %s header = %s' % (url, header))
        req = urllib2.Request(url, None, header)

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if e.code == 403 or e.code == 401:
              self.loginWISE()
              header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.wise, 'GData-Version' : '3.0' }
              req = urllib2.Request(url, None, header)
              try:
                response = urllib2.urlopen(req)
              except urllib2.URLError, e:
                log(str(e), True)
                return
            else:
              log(str(e), True)
              return

        response_data = response.read()


        urls = response_data
        urls = urllib.unquote(urllib.unquote(urllib.unquote(urllib.unquote(urllib.unquote(urls)))))

        serviceRequired = ''
        for r in re.finditer('ServiceLogin\?(service)=([^\&]+)\&' ,
                             urls, re.DOTALL):
            (service, serviceRequired) = r.groups()


        #effective 2014/02, video stream calls require a wise token instead of writely token
        #backward support for account not migrated to the 2014/02 change
        if serviceRequired == 'writely':

          header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }

          log('url = %s header = %s' % (url, header))
          req = urllib2.Request(url, None, header)

          try:
              response = urllib2.urlopen(req)
          except urllib2.URLError, e:
              if e.code == 403 or e.code == 401:
                self.login()
                header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }
                req = urllib2.Request(url, None, header)
                try:
                  response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                  log(str(e), True)
                  return
              else:
                log(str(e), True)
                return

          response_data = response.read()


          urls = response_data
          urls = urllib.unquote(urllib.unquote(urllib.unquote(urllib.unquote(urllib.unquote(urls)))))

          serviceRequired = ''
          for r in re.finditer('ServiceLogin\?(service)=([^\&]+)\&' ,
                               urls, re.DOTALL):
              (service, serviceRequired) = r.groups()


          if serviceRequired != '':
            log('an unexpected service token is required: %s' % (serviceRequired), True)

        elif serviceRequired != '':
          log('an unexpected service token is required: %s' % (serviceRequired), True)


        urls = re.sub('\&url\=https://', '\@', urls)

        for r in re.finditer('\@([^\@]+)' ,urls):
          videoURL = r.group(0)
          log('found videoURL %s' % (videoURL))
        videoURL1 = 'https://' + videoURL


        response.close()


        return videoURL1


    # for playing public URLs
    def getPlayerLinkURL(self,url):

        #try to use no authorization token (for pubic URLs)
        header = { 'User-Agent' : self.user_agent, 'GData-Version' : '3.0' }


        log('url = %s header = %s' % (url, header))
        req = urllib2.Request(url, None, header)

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if e.code == 403 or e.code == 401:
              self.loginWISE()
              header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.wise, 'GData-Version' : '3.0' }
              req = urllib2.Request(url, None, header)
              try:
                response = urllib2.urlopen(req)
              except urllib2.URLError, e:
                log(str(e), True)
                return
            else:
              log(str(e), True)
              return

        response_data = response.read()



        serviceRequired = ''
        for r in re.finditer('ServiceLogin\?(service)=([^\&]+)\&' ,
                             response_data, re.DOTALL):
            (service, serviceRequired) = r.groups()

        for r in re.finditer('AccountChooser.+?(service)=([^\']+)\'' ,
                             response_data, re.DOTALL):
            (service, serviceRequired) = r.groups()


        #effective 2014/02, video stream calls require a wise token instead of writely token
        #backward support for account not migrated to the 2014/02 change
        if serviceRequired == 'writely':

          if (self.writely == ''):
            self.login();

          header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }

          log('url = %s header = %s' % (url, header))
          req = urllib2.Request(url, None, header)

          try:
              response = urllib2.urlopen(req)
          except urllib2.URLError, e:
              if e.code == 403 or e.code == 401:
                self.login()
                header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.writely, 'GData-Version' : '3.0' }
                req = urllib2.Request(url, None, header)
                try:
                  response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                  log(str(e), True)
                  return
              else:
                log(str(e), True)
                return

          response_data = response.read()


          for r in re.finditer('"(fmt_stream_map)":"([^\"]+)"' ,
                             response_data, re.DOTALL):
              (urlType, urls) = r.groups()

          urls = re.sub('\\\\u003d', '=', urls)
          urls = re.sub('\\\\u0026', '&', urls)


          serviceRequired = ''
          for r in re.finditer('ServiceLogin\?(service)=([^\&]+)\&' ,
                               urls, re.DOTALL):
              (service, serviceRequired) = r.groups()


          if serviceRequired != '':
            log('an unexpected service token is required: %s' % (serviceRequired), True)

        elif serviceRequired == 'wise':

          if (self.wise == ''):
            self.loginWISE();

          header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.wise, 'GData-Version' : '3.0' }

          log('url = %s header = %s' % (url, header))
          req = urllib2.Request(url, None, header)

          try:
              response = urllib2.urlopen(req)
          except urllib2.URLError, e:
              if e.code == 403 or e.code == 401:
                self.loginWISE()
                header = { 'User-Agent' : self.user_agent, 'Authorization' : 'GoogleLogin auth=%s' % self.wise, 'GData-Version' : '3.0' }
                req = urllib2.Request(url, None, header)
                try:
                  response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                  log(str(e), True)
                  return
              else:
                log(str(e), True)
                return

          response_data = response.read()


          for r in re.finditer('"(fmt_stream_map)":"([^\"]+)"' ,
                             response_data, re.DOTALL):
              (urlType, urls) = r.groups()

          urls = re.sub('\\\\u003d', '=', urls)
          urls = re.sub('\\\\u0026', '&', urls)


          serviceRequired = ''
          for r in re.finditer('ServiceLogin\?(service)=([^\&]+)\&' ,
                               urls, re.DOTALL):
              (service, serviceRequired) = r.groups()


          if serviceRequired != '':
            log('an unexpected service token is required: %s' % (serviceRequired), True)


        elif serviceRequired != '':
          log('an unexpected service token is required: %s' % (serviceRequired), True)

        for r in re.finditer('"(fmt_stream_map)":"([^\"]+)"' ,
                             response_data, re.DOTALL):
            (urlType, urls) = r.groups()

        urls = re.sub('\\\\u003d', '=', urls)
        urls = re.sub('\\\\u0026', '&', urls)


        urls = re.sub('\d+\|https://', '\@', urls)

        for r in re.finditer('\@([^\@]+)' ,urls):
          videoURL = r.group(0)
          log('found videoURL %s' % (videoURL))
        videoURL1 = 'https://' + videoURL


        response.close()


        return videoURL1


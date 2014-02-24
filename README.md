XBMC-gdrive
===========

Google Drive Video add-on for XBMC

A video add-on for XBMC that enables playback of videos stored in a Google Drive account.

Supports [Tested on]:
All XBMC 12 and 12.2 including Linux, Windows, OS X, Android, Pivos, iOS (including ATV2)

*Note for Raspberry Pi users*: Due to a bug in libcurl with HTTPS streams (Google Drive uses HTTPS only), please ensure that the "stream" option is set for playback type in settings.

The plugin uses the Google Docs API 3.

Getting Started:
1) download the .zip file
2) transfer the .zip file to XBMC
3) in Video Add-on, select Install from .zip

Before starting the add-on for the first time, either "Configure" or right click and select "Add-on Settings".  Enter your fully-qualified Username (including @gmail.com or @domain) and Password.

Features and limitations:
- will index videos in your google drive account, sorted by title name
- folders are ignored but the files contained in them are indexed for playback
- only indexes and playback videos; no pictures at this time

Modes:
1) standard index
- starting the plugin via video add-ons will display a directory containing all video files within the Google Drive account or those that are shared to that account
- click on the video to playback
- don't create favourites from the index, as the index will contain a URL that will expire after 12-24 hours
2) mode=playvideo
* uses default method of streaming (either #2 or #3) based on the value of Playback Type is in Settings.
- you can create .strm or .m3u files that run Google Drive videos direct
- create .strm or .m3u files containing the following: plugin://plugin.video.gdrive?mode=playvideo&amp;title=Title_of_video
- if your video is composed of multiple clips, you can create a .m3u that makes the above plugin:// call, one line for each clip.  You can then create a .strm file that points to the .m3u.  XBMC can index movies and shows contained in your Google Drive account by either a .strm containing a single plugin:// call to the video, or a .strm that points to a local .m3u file that contains a list of plugin:// calls representing the video
3) mode=memoryCacheVideo
- playback via HTTPS as if you were downloading the video -- playback is therefore in native format
- bypasses Playback Type in Settings
* HTTPS playback is problematic on a Raspberry Pi (fails most of the time -- due not use this method on a Raspberry Pi)
- create .strm or .m3u files containing the following: plugin://plugin.video.gdrive?mode=memoryCacheVideo&amp;title=Title_of_video
- if your video is composed of multiple clips, you can create a .m3u that makes the above plugin:// call, one line for each clip.  You can then create a .strm file that points to the .m3u.  XBMC can index movies and shows contained in your Google Drive account by either a .strm containing a single plugin:// call to the video, or a .strm that points to a local .m3u file that contains a list of plugin:// calls representing the video
4) mode=streamVideo
- playback via stream (automatically transcoded by Google Drive playback services)
- bypasses Playback Type in Settings
- create .strm or .m3u files containing the following: plugin://plugin.video.gdrive?mode=streamVideo&amp;title=Title_of_video
- if your video is composed of multiple clips, you can create a .m3u that makes the above plugin:// call, one line for each clip.  You can then create a .strm file that points to the .m3u.  XBMC can index movies and shows contained in your Google Drive account by either a .strm containing a single plugin:// call to the video, or a .strm that points to a local .m3u file that contains a list of plugin:// calls representing the video
5) mode=streamURL
- playback a specific Google Drive Video URL (format: https://docs.google.com/file/d/#####/preview) via stream (automatically transcoded by Google Drive playback services)
- handy for playback of publicly shared videos stored in Google Drive
- bypasses Playback Type in Settings
- create .strm or .m3u files containing the following: plugin://plugin.video.gdrive?mode=streamURL&amp;url=https://docs.google.com/file/d/#####/preview
- if your video is composed of multiple clips, you can create a .m3u that makes the above plugin:// call, one line for each clip.  You can then create a .strm file that points to the .m3u.  XBMC can index movies and shows contained in your Google Drive account by either a .strm containing a single plugin:// call to the video, or a .strm that points to a local .m3u file that contains a list of plugin:// calls representing the video

FAQ:

1) Is there support for Google Apps Google Drive accounts?
Yes.  Use your fully qualified username whether that is username@gmail.com or username@domain 

2) Is there support for multiple accounts?
Sort of.  For now, you should share all your videos from subsquent Google Drive accounts to the main Google Drive account that you use with this add-on.  The shared videos will appear in the index and are viewwable.

3) Does thie add-on support Pictures or other filetypes?
Not at this time.  I had no need for viewing files other then Video, therefore, the initial public release features only the features I have been using.

4) Any limitations?
I've tested the add-on with several Google Drive accounts, including one with over 700 videos.
 
Current Version:

0.2.7
- added streamURL parameter: mode=streamURL
- playback a specific Google Drive Video URL (format: https://docs.google.com/file/d/#####/preview) via stream (automatically transcoded by Google Drive playback services)
- handy for playback of publicly shared videos stored in Google Drive
- bypasses Playback Type in Settings
- create .strm or .m3u files containing the following: plugin://plugin.video.gdrive?mode=streamURL&amp;url=https://docs.google.com/file/d/#####/preview
- if your video is composed of multiple clips, you can create a .m3u that makes the above plugin:// call, one line for each clip.  You can then create a .strm file that points to the .m3u.  XBMC can index movies and shows contained in your Google Drive account by either a .strm containing a single plugin:// call to the video, or a .strm that points to a local .m3u file that contains a list of plugin:// calls representing the video

0.2.6
- Plays video.google.com videos that are linked in your google drive account
0.2.5
- Important! due to recent undocumented changes in the Google Docs API, the plugin may have begun to fail to play video (only display a list of videos).  This has been updated with the following change.
- updated for a google drive change on or about 2014/02 where the video download and streaming now uses the 'wise' service instead of 'writely'
- if your google drive account has not been updated to the new UI (that is, the change from writely to wise hasn't kicked in), you can enable the old behaviour of using writely for downloading and streaming by setting "Force old writely service for plackback" to ON/TRUE in settings
0.2.2
- updated xbmc.python from 1.0 to 2.1.0 for XBMC 13
0.2.1
- fix for authorization token being populated even when experimental feature is left turned off
  - the authorization token can cause login errors; the feature is not ready to be released yet.
  - the correction fixes the feature turning on by itself
- if you authorization token field is populated, click defaults to unset it.
0.2.0
- Public release
0.1.0
- Initial version

Roadmap to future releases:
- support for multipel Google Drive accounts
- support for OAUTH
- support for pictures
- support for caching account contents
- support for folders and pagination (crucial for accounts with thousands of videos)

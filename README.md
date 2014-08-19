# movme 
Move files and/or directory (or execute cmd) following rules and priority set in a config file

## Introduction
Through a configuration file (xml) where you define the rules (file name, extension, size, etc) and priority, the files are moved to specific folders.
You can use a kind of namespace (group) to define rules and priority and inherit it in sub-folder. Execute some action (script) after moving files.

*note: I use this script for organaize dowloaded files by aMule/eMule and torrent client...but you can use for all you want*

## Usage
```
Usage: movme [-h -s][-v X] [-c path/to/file.xml] [-l path/to/file.log] {-d path/to/

    -h          displays this help usage        --help
    -s          don't move files (use with -v)  --simulate
    -r          with -d walk on sub-dirs        --recursive
    -a          with -d manage dirs as files    --dirasfile
    -v X        verbose mode X = [1:3]          --verbose
    -c path     config file                     --config=path    
    -l path     make file log                   --log=path
    -d path     target dir path                 --dir=path
    -f path     target file path                --file=path           
    
Move all files (also in sub-dirs --recursive):
 movme -r -d /home/user/.aMule/Incoming

Move Alien3.avi and create a log file:
 movme -v 2 -l /home/user/.aMule/movme.log -f /home/user/.aMule/Incoming/Alien3.avi

Testing xml config (don't move anythings):
 movme -v 2 -s -r -d /home/user/.aMule/Incoming
```

You can also view this: [old guide to movme (italian)](http://muttley.eb2a.com/2010/movme-programma-per-smistare-file-e-cartelle/)

## Graph of config (xml) structure
![Config structure](http://s28.postimg.org/kujnscp99/movme.png "Config structure")

## Notes
+ Case Insensitive
+ `filename`: regular expression case-Insesitive. 
+ `filesize_bigger` / `filesize_smaller`: can use G, M, K, B (or g, m ,k ,b) (default byte b)
+ `exec_linux_cmd`: [0..n]
+ `all rules`: [0..n]
+ `fileext`: extension separated by space
+ `mkdir`: 1 - create the directory or the whole directories through the path if not exist (default 0)
 != 1 && != 0 directory permissions (ex. 755)      
+ `needed`: 1 - subtract priority 1000 (default 0) 
 n.b. needed it's only for filename and fileext
+ `exec_linux_cmd`: all commands are executed in background (&)
 special placeholder:
 + %n file name
 + %d full path
 + %f full path + file name


## Config.xml file example
```xml
<?xml version="1.0" encoding="utf-8"?>
<movme>
	<group name="amule">
		<actions>
			<exec_linux_cmd>chmod 664 "%filepath"</exec_linux_cmd>
		</actions>
		
		<!-- Movies -->
		<group name="movies">

			<group name="films">
				<rules>
					<filename priority="20">[hx]?\.?264|DivX|XviD|AC3|ITA|DVDRip|CD0?[2-4]</filename>
					<filename priority="2">MP3|AAC</filename>
					<fileext priority="10" needed="1">avi mkv</fileext>
				</rules>
				<actions>
					<exec_linux_cmd><![CDATA[/opt/bin/rssappend-movme-wrapper.sh "%filepath" "%filename" "%filtername" "%actioninherit" film]]></exec_linux_cmd>
				</actions>
				
				<!-- SD movies -->
				<filter name="Films" path="/home/p2p/Downloads/movies/films/">
					<rules>
						<filesize_bigger priority="10">600M</filesize_bigger>
						<filesize_bigger priority="-15">3G</filesize_bigger>
						<filesize_smaller priority="-15">600M</filesize_smaller>
					</rules>
				</filter>
				
				<!-- HD Movies -->
				<filter name="Films HD" path="/home/p2p/Downloads/movies/films hd/">
					<rules>
						<filesize_bigger priority="10">2G</filesize_bigger>
						<filesize_smaller priority="-15">2G</filesize_smaller>
					</rules>
				</filter>
			</group>
			
			<filter name="Subtitles" path="/home/p2p/Downloads/movies/subtitles/">
				<rules>
					<filename priority="20">FORCED|All.?Subs?|Subs?|Pack</filename>
					<filesize_bigger priority="-1000">100M</filesize_bigger>
					<filesize_bigger priority="-10">10M</filesize_bigger>
					<filesize_smaller priority="10">500K</filesize_smaller>
					<fileext priority="30">srt</fileext>
					<fileext priority="5">rar zip</fileext>
				</rules>
			</filter>
			
			<!-- Series -->
			<group name="series">
				<rules>
					<fileext needed="1" priority="10">avi mp3 srt mkv</fileext>
				</rules>
				<actions>
					<exec_linux_cmd><![CDATA[/opt/bin/rssappend-movme-wrapper.sh "%filepath" "%filename" "%filtername" "%actioninherit" serie]]></exec_linux_cmd>
				</actions>
				
				<filter name="Breaking Bad" mkdir="775" path="/home/p2p/Downloads/movies/series/tv/Breaking Bad/">
					<rules>
						<filename needed="1" priority="100">Breaking\.bad</filename>
					</rules>
				</filter>
				<filter name="South Park" mkdir="775" path="/home/p2p/Downloads/movies/series/cartoon/South Park/Stagione 14">
					<rules>
						<filename needed="1" priority="100">South Park</filename>
					</rules>
				</filter>
				<filter name="Fringe" mkdir="775" path="/home/p2p/Downloads/movies/series/tv/Fringe/">
					<rules>
						<filename needed="1" priority="100">Fringe\.</filename>
					</rules>
				</filter>
				<filter name="The Big Bang Theory" mkdir="775" path="/home/p2p/Downloads/movies/series/tv/The Big Bang Theory/">
					<rules>
						<filename needed="1" priority="100">The\.Big\.Bang\.Theory</filename>
					</rules>
				</filter>
				<!-- DISABLED FILTER
				<filter name="Misfits" mkdir="775" path="/home/p2p/Downloads/movies/series/tv/Misfits/">
					<rules>
						<filename needed="1" priority="100">Misfits</filename>
					</rules>
				</filter> -->
			</group>
		</group>
		<group name="generic">
			<actions>
				<exec_linux_cmd><![CDATA[/usr/local/sbin/rssappend -m 10 -t "%filename" -d "<h3>category: <strong>%filtername</strong></h3><br/><h5>moved: '%filedir'</h5>" -a "aMule" -c "p2p" -g "%filename" -k /var/www/feed/p2p-report.xml]]></exec_linux_cmd>
			</actions>
			
			<!-- Music -->
			<filter name="Music" path="/home/p2p/Downloads/music/zipped/">
				<rules>
					<filename priority="20">Album|Soundtrack</filename>
					<filename priority="5">MP3|OGG|WMV</filename>
					<filesize_bigger priority="15">50M</filesize_bigger>
					<filesize_bigger priority="-10">150M</filesize_bigger>
					<filesize_smaller priority="-10">10M</filesize_smaller>
					<fileext priority="5" needed="1">rar zip mp3</fileext>
				</rules>
			</filter>
			
			<!-- Others -->
			<filter name="Others" path="/home/p2p/Downloads/others/">
				<rules>
					<filename priority="10">.*</filename>
					<filename priority="100">xbox</filename>
				</rules>
			</filter>
		</group>
	</group>
</movme>
```
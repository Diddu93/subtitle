## A simple Subtitle conversion script

### Requirements : 

- python 2.7
- python-chardet

### Installation

`git clone subtitle`

`ln -s subtitle/subtitle $binaries_path/subtitle`

where `$binaries_path` is `/usr/local/bin` or `/home/$username/bin` etc...
  
### Configuration

edit the file `lib/config.py`.

```
SUBTITLES_ENCODING = 'UTF-8-SIG'  # in which encoding subtitles must be converted.
SUBTITLES_USER = "myuser"  # the user who subtitle files should belong to.
SUBTITLES_GROUP = "mygroup"  # the group who subtitle files should belong to.
SUBTITLES_UMASK = 0775  # the umask to apply to subtitle files.
```

If you comment out the `SUBTITLES_USER` and `SUBTITLES_USER` lines, they will be the current user name. 

### Usage

`i, info		<file>`

###### Displays properties of a subtitle file.

`l, list         <path_or_file>`

###### Lists a path or file to display subtitles properties.

`c, check	<path_or_file>`

###### Checks a path or file to convert subtitles charset.

`b, backup	<file>`

###### Backs up a subtitle file.

`r, restore	<file>`

###### Restores a subtitle from its backup file

`s, shift	<file>	<value> [--start <start>] [--end <end>]`

###### Applies a shift to a subtitle file.

Where value is in a valid [time value format](#time-value-format).

Optional arguments `<start>` and `<end>` can be used to start applying shift from and to those arguments, they have to be in a valid [Subtitle time format](#subtitle-time-format).

`d, delta	<file>	<value> [--start <start>] [--end <end>]`

###### Applies a delta to a subtitle file.

Where value is in a valid [time value format](#time-value-format).

Optional arguments `<start>` and `<end>` can be used to start applying delta from and to those arguments, they have to be in a valid [Subtitle time format](#subtitle-time-format).


### Time value format

Time format tells the script by which time unit measurement we have to edit the subtitle sentences.

A time format consists in three parts :

* an operand (`+`, `-`, `p`, `m`) 
* a quantifier (`10`, `484`, `8`, `98`)
* a unit (`m`, `s`, `ms`)

##### some examples :

###### shifting up a subtitle by 36 seconds:
 
`subtitle s file.srt +36s` or `subtitle s file.srt p36s`

###### shifting down a subtitle by 485 milliseconds:
 
`subtitle s file.srt -485ms` or `subtitle s file.srt m485ms`


### Subtitle Time format

A SubtitleTime format is defined by a string representing the time when a SubtitleSentence is displayed.

It consists in four parts :

* hours
* minutes
* seconds
* milliseconds

##### some examples :

###### shifting up a subtitle by 36 seconds starting from 20 minutes, 1 second and 185 milliseconds :
 
`subtitle s file.srt +36s --start 00:20:01,185` or `subtitle s file.srt p36s --start 00:20:01,185`

###### shifting down a subtitle by 485 milliseconds from 20 minutes, 1 second and 185 milliseconds to 1 hour, 34 minutes:
 
`subtitle s file.srt -485ms --start 00:20:01,185 --end 01:34:00,000` or `subtitle s file.srt m485ms --start 00:20:01,185 --end 01:34:00,000`


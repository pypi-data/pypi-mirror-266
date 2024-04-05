
# cd /home/lutzray/SyncQUO/Dev/AtomicSync/Sources/PostProduction/tictacsync/tictacsync
# while inotifywait --recursive -e close_write . ; do python entry.py  tests/multi2/; done
# above for linux

TRACKSFN = 'tracks.txt'
SILENT_TRACK_TOKENS = '-0n'


av_file_extensions = \
"""webm mkv flv flv vob ogv ogg drc gif gifv mng avi MTS M2TS TS mov qt
wmv yuv rm rmvb viv asf amv mp4 m4p m4v mpg mp2 mpeg mpe mpv mpg mpeg m2v
m4v svi 3gp 3g2 mxf roq nsv flv f4v f4p f4a f4b 3gp aa aac aax act aiff alac
amr ape au awb dss dvf flac gsm iklax ivs m4a m4b m4p mmf mp3 mpc msv nmf
ogg oga mogg opus ra rm raw rf64 sln tta voc vox wav wma wv webm 8svx cda MOV AVI
WEBM MKV FLV FLV VOB OGV OGG DRC GIF GIFV MNG AVI MTS M2TS TS MOV QT
WMV YUV RM RMVB VIV ASF AMV MP4 M4P M4V MPG MP2 MPEG MPE MPV MPG MPEG M2V
M4V SVI 3GP 3G2 MXF ROQ NSV FLV F4V F4P F4A F4B 3GP AA AAC AAX ACT AIFF ALAC
AMR APE AU AWB DSS DVF FLAC GSM IKLAX IVS M4A M4B M4P MMF MP3 MPC MSV NMF
OGG OGA MOGG OPUS RA RM RAW RF64 SLN TTA VOC VOX WAV WMA WV WEBM 8SVX CDA MOV AVI BWF""".split()

from dataclasses import dataclass
import ffmpeg, os, sys
from os import listdir
from os.path import isfile, join, isdir
from collections import namedtuple
from pathlib import Path
from pprint import pformat 
# from collections import defaultdict
from loguru import logger
# import pathlib, os.path
import sox, tempfile
# from functools import reduce
from rich import print
from itertools import groupby
# from sklearn.cluster import AffinityPropagation
# import distance
try:
    from . import multi2polywav
except:
    import multi2polywav


# utility for accessing pathnames
def _pathname(tempfile_or_path):
    if isinstance(tempfile_or_path, str):
        return tempfile_or_path
    if isinstance(tempfile_or_path, Path):
        return str(tempfile_or_path)
    if isinstance(tempfile_or_path, tempfile._TemporaryFileWrapper):
        return tempfile_or_path.name
    else:
        raise Exception('%s should be Path or tempfile...'%tempfile_or_path)

def print_grby(grby):
    for key, keylist in grby:
        print('\ngrouped by %s:'%key)
        for e in keylist:
            print(' ', e)


@dataclass
class Tracks:
    # track numbers start at 1 for first track (as needed by sox)
    ttc: int # track number of TicTacCode signal
    unused: list # of unused tracks
    stereomics: list # of stereo mics track tuples (Lchan#, Rchan#)
    mix: list # of mixed tracks, if a pair, order is L than R
    others: list #of all other tags: (tag, track#) tuples
    rawtrx: list # list of strings read from file
    error_msg: str # 'None' if none

@dataclass
class Device:
    UID: int
    folder: Path
    name: str
    dev_type: str # CAM or REC
    n_chan: int
    tracks: Tracks
    def __hash__(self):
        return self.UID
    def __eq__(self, other):
        return self.UID == other

@dataclass
class Media:
    """A custom data type that represents data for a media file.
    """
    path: Path
    device: Device
def media_at_path(input_structure, p):
    # return Media object for mediafile using ffprobe
    dev_UID, dt = get_device_ffprobe_UID(p)
    dev_name = None 
    if input_structure == 'folder_is_device':
        dev_name = p.parent.name
        if dev_UID is None:
            dev_UID = hash(dev_name)
    if dt == 'CAM':
        streams = ffmpeg.probe(p)['streams']
        audio_streams = [
            stream 
            for stream
            in streams
            if stream['codec_type']=='audio'
            ]
        if len(audio_streams) > 1:
            raise Exception('ffprobe gave multiple audio streams?')
        audio_str = audio_streams[0]
        n = audio_str['channels']
        # pprint(ffmpeg.probe(p))
    else:
        n = sox.file_info.channels(_pathname(p)) # eg 2
    logger.debug('for file %s dev_UID established %s'%(p.name, dev_UID))
    return Media(p,
        Device(UID=dev_UID, folder=p.parent, name=dev_name, dev_type=dt,
                n_chan=n, tracks=None))

def get_device_ffprobe_UID(file):
    """
    Tries to find an unique hash integer identifying the device that produced
    the file based on the string inside ffprobe metadata  without any
    reference to date nor length nor time. Find out with ffprobe the type
    of device: CAM or REC for videocamera or audio recorder.

    Device UIDs are used later in Montage._get_concatenated_audiofile_for()
    for grouping each audio or video clip along its own timeline track.
    
    Returns a tuple: (UID, CAM|REC)
    
    If an ffmpeg.Error occurs, returns (None, None)
    if no UID is found, but device type is identified, returns (None, CAM|REC)

    """
    file = Path(file)
    logger.debug('trying to find UID probe for %s'%file)
    try:
        probe = ffmpeg.probe(file)
    except ffmpeg.Error as e:
        print('ffmpeg.probe error')
        print(e.stderr, file)
        return None, None
        # fall back to folder name
    streams = probe['streams']
    codecs = [stream['codec_type'] for stream in streams]
    device_type = 'CAM' if 'video' in codecs else 'REC'
    format_dict = probe['format'] # all files should have this
    if 'tags' in format_dict:
        probe_string = pformat(format_dict['tags'])
        probe_lines = [l for l in probe_string.split('\n') 
                if '_time' not in l 
                and 'time_' not in l 
                and 'date' not in l ]
        # this removes any metadata related to the file
        # but keeps metadata related to the device
        UID = hash(''.join(probe_lines))
    else:
        UID = None
    logger.debug('ffprobe_UID is: %s'%UID)
    return UID, device_type

class Scanner:
    """
    Class that encapsulates scanning of the directory given as CLI argument.
    Depending on the input_structure detected (loose|folder_is_device), enforce
    some directory structure (or not). Build a list of media files found and a
    try to indentify uniquely the device used to record each media file.

    Attributes:

        input_structure: string
            Any of:
                'loose'
                    all files audio + video are in top folder
                'folder_is_device'
                    eg for multicam on Davinci Resolve
            input_structure is set in scan_media_and_build_devices_UID()

        top_directory : string
            String of path where to start searching for media files.

        top_dir_has_multicam : bool
            If top dir is folder structures AND more than on cam

        found_media_files: list of Media objects
    """

    def __init__(
                    self,
                    top_directory,
                    stay_silent=False,
                ):
        """
        Initialises Scanner

        """
        self.top_directory = top_directory
        self.found_media_files = []
        self.stay_silent = stay_silent

    def get_devices_number(self):
        # how many devices have been found
        return len(set([m.device.UID for m in self.found_media_files]))

    def get_devices(self):
        return set([m.device for m in self.found_media_files])

    def get_media_for_device(self, dev):
        return [m for m in self.found_media_files if m.device == dev]

    def CAM_numbers(self):
        devices = [m.device for m in self.found_media_files]
        CAMs = [d for d in devices if d.dev_type == 'CAM']
        return len(set(CAMs))

    def scan_media_and_build_devices_UID(self, recursive=True):
        """
        Scans Scanner.top_directory recursively for files with known audio-video
        extensions. For each file found, a device fingerprint is obtained from
        their ffprobe result to ID the device used.

        Also looked for are multifile recordings: files with the exact same
        length. When done, calls

        Returns nothing

        Populates Scanner.found_media_files, a list of Media objects

        Sets Scanner.input_structure = 'loose'|'folder_is_device'

        """
        visible = [f for f in listdir(self.top_directory) if f[0] != '.']
        logger.debug('visible: %s'%visible)
        are_dir = all([isdir(join(self.top_directory, f)) for f in visible])
        are_files = all([isfile(join(self.top_directory, f)) for f in visible])
        logger.debug('dir: %s'%[isdir(join(self.top_directory, f)) for f
              in visible])
        if are_dir:
            visible = [e for e in visible if e != 'SyncedMedia']
            print('\nAssuming those are device folders: ',end='')
            [print('[gold1]%s[/gold1]'%f, end=', ') for f in visible[:-1]]
            print('[gold1]%s[/gold1].'%visible[-1])
            self.input_structure = 'folder_is_device'
        else: # are_files
            self.input_structure = 'loose'
            self.top_dir_has_multicam = False
        files = Path(self.top_directory).rglob('*.*')
        paths = [
            p
            for p in files
            if p.suffix[1:] in av_file_extensions
            and 'SyncedMedia' not in p.parts
        ]
        for p in paths:
            new_media = media_at_path(self.input_structure, p) # dev UID set here
            self.found_media_files.append(new_media)
        # files from devices without UID or name
        def _same(l):
            return all(e == l[0] for e in l)
        def _try_name(medias):
            # return common first strings in filename
            names = [m.path.name for m in medias]
            transposed_names = list(map(list, zip(*names)))
            same = list(map(_same, transposed_names))
            try:
                first_diff = same.index(False)
            except:
                return names[0].split('.')[0]
            return names[0][:first_diff]
        no_device_UID_media = [m for m in self.found_media_files
                    if not m.device.UID]
        if no_device_UID_media:
            logger.debug('no_device_UID_media %s'%no_device_UID_media)
            # print(no_device_UID_media)
            start_string = _try_name(no_device_UID_media)
            if len(start_string) < 2:
                print('\nError, cant identify the device for those files:')
                [print('%s, '%m.path.name, end='') for m in no_device_UID_media]
                print('\n')
                sys.exit(1)
            one_device = no_device_UID_media[0].device
            one_device.name = start_string
            if not one_device.UID:
                one_device.UID = hash(start_string)
            print('\nWarning, guessing a device ID for those files:')
            [print('[gold1]%s[/gold1], '%m.path.name, end='') for m in no_device_UID_media]
            print('UID: [gold1]%s[/gold1]'%start_string)
            for m in no_device_UID_media:
                m.device = one_device
            logger.debug('new device added %s'%self.found_media_files)
        logger.debug('Scanner.found_media_files = %s'%self.found_media_files)
        if self.input_structure == 'folder_is_device':
            self._check_folders_have_same_device()
            # self._use_folder_as_device_name()
            devices = set([m.device for m in self.found_media_files])
            audio_devices = [d for d in devices if d.dev_type == 'REC']
            for recorder in audio_devices:
                recorder.tracks = self._get_tracks_from_file(recorder)
        no_name_devices = [m.device for m in self.found_media_files
            if not m.device.name]
        # if no_name_devices:
        #     pprint_no_name = pformat([(d, self.get_media_for_device(d)) for d in no_name_devices])
        #     print('those are anon devices%s\n'%pprint_no_name)
        #     logger.debug('those media have anon device%s'%no_name_devices)
        for anon_dev in no_name_devices:
            medias = self.get_media_for_device(anon_dev)
            guess_name = _try_name(medias)
            # print('dev %s has no name, guessing %s'%(anon_dev, guess_name))
            logger.debug('dev %s has no name, guessing %s'%(anon_dev, guess_name))
            anon_dev.name = guess_name
        pprint_found_media_files = pformat(self.found_media_files)
        logger.debug('scanner.found_media_files = %s'%pprint_found_media_files)
        logger.debug('all devices %s'%[m.device for m in self.found_media_files])
        # print('devices 312 %s'%set([m.device for m in self.found_media_files]))

    def _get_tracks_from_file(self, device) -> Tracks:
        """        
        Look for track names in TRACKSFN file, possibly stored inside the
        recorder folder alongside the audio files. If there, returns a Tracks
        object, if not returns None. 
        """        
        source_audio_folder = device.folder
        tracks_file = source_audio_folder/TRACKSFN
        track_names = False
        a_recording = [m for m in self.found_media_files
                                                if m.device == device][0]
        logger.debug('a_recording for device %s : %s'%(device, a_recording))
        nchan = sox.file_info.channels(str(a_recording.path))
        if os.path.isfile(tracks_file):
            logger.debug('found file: %s'%(TRACKSFN))
            tracks = self._parse_track_values(tracks_file)
            if tracks.error_msg:
                print('\nError parsing [gold1]%s[/gold1] file: %s, quitting.\n'%
                    (tracks_file, tracks.error_msg))
                sys.exit(1)
            logger.debug('parsed tracks %s'%tracks)
            ntracks = 2*len(tracks.stereomics)
            ntracks += len(tracks.mix)
            ntracks += len(tracks.unused)
            ntracks += len(tracks.others)
            ntracks += 1 # for ttc track
            logger.debug(' n chan: %i n tracks file: %i'%(nchan, ntracks))
            # if ntracks != nchan:
            #     print('\nError parsing %s content'%tracks_file)
            #     print('incoherent number of tracks, %i vs %i quitting\n'%
            #                                         (nchan, ntracks))
                # sys.exit(1)
            err_msg = tracks.error_msg
            if  err_msg != None:
                print('Error, quitting: in file %s, %s'%(tracks_file, err_msg))
                raise Exception
            else:
                return tracks
        else:
            logger.debug('no tracks.txt file found')
            return None

    # def _use_folder_as_device_name(self):
    #     """
    #     For each media in self.found_media_files replace existing Device.name by
    #     folder name.

    #     Returns nothing
    #     """
    #     for m in self.found_media_files:
    #         m.device.name = m.path.parent.name
    #     logger.debug(self.found_media_files)

    def _check_folders_have_same_device(self):
        """
        Since input_structure == 'folder_is_device,
        checks for files in self.found_media_files for structure as following.

        Warns user and quit program for:
          A- folders with mix of video and audio
          B- folders with mix of uniquely identified devices and unUIDied ones
          C- folders with mixed audio (or video) devices
        
        Warns user but proceeds for:
          D- folder with only unUIDied files (overlaps will be check later)
        
        Proceeds silently if 
          E- all files in the folder are from the same device

        Returns nothing
        """
        def _list_duplicates(seq):
          seen = set()
          seen_add = seen.add
          # adds all elements it doesn't know yet to seen and all other to seen_twice
          seen_twice = set( x for x in seq if x in seen or seen_add(x) )
          # turn the set into a list (as requested)
          return list( seen_twice )
        folder_key = lambda m: m.path.parent
        medias = sorted(self.found_media_files, key=folder_key)
        # build lists for multiple reference of iterators
        media_grouped_by_folder = [ (k, list(iterator)) for k, iterator
                        in groupby(medias, folder_key)]
        logger.debug('media_grouped_by_folder %s'%media_grouped_by_folder)
        complete_path_folders = [e[0] for e in media_grouped_by_folder]
        name_of_folders = [p.name for p in complete_path_folders]
        logger.debug('complete_path_folders with media files %s'%complete_path_folders)
        logger.debug('name_of_folders with media files %s'%name_of_folders)
        # unique_folder_names = set(name_of_folders)
        repeated_folders = _list_duplicates(name_of_folders)
        logger.debug('repeated_folders %s'%repeated_folders)
        if repeated_folders:
            print('There are conflicts for some repeated folder names:')
            for f in [str(p) for p in repeated_folders]:
                print(' [gold1]%s[/gold1]'%f)
            print('Here are the complete paths:')
            for f in [str(p) for p in complete_path_folders]:
                print(' [gold1]%s[/gold1]'%f)
            print('please rename and rerun. Quitting..')
            sys.exit(1)
        # print(media_grouped_by_folder)
        n_CAM_folder = 0
        for folder, list_of_medias_in_folder in media_grouped_by_folder:
            # check all medias are either video or audio recordings in folder
            # if not, warn user and quit.
            dev_types = set([m.device.dev_type for m in list_of_medias_in_folder])
            logger.debug('dev_types %s'%dev_types)
            if dev_types == {'CAM'}:
                n_CAM_folder += 1
            if len(dev_types) != 1:
                print('\nProblem while scanning for media files. In [gold1]%s[/gold1]:'%folder)
                print('There is a mix of video and audio files:')
                [print('[gold1]%s[/gold1]'%m.path.name, end =', ')
                    for m in list_of_medias_in_folder]
                print('\nplease move them in exclusive folders and rerun.\n')
                sys.exit(1)
            unidentified = [m for m in list_of_medias_in_folder
                if m.device.UID == None]
            UIDed = [m for m in list_of_medias_in_folder
                if m.device.UID != None]
            logger.debug('devices in folder %s:'%folder)
            logger.debug('  media with unknown devices %s'%unidentified)
            logger.debug('  media with UIDed devices %s'%UIDed)
            if len(unidentified) != 0 and len(UIDed) != 0:
                print('\nProblem while grouping files in [gold1]%s[/gold1]:'%folder)
                print('There is a mix of unidentifiable and identified devices.')
                print('Is this file:')
                for m in unidentified:
                    print(' [gold1]%s[/gold1]'%m.path.name)
                answer = input("In the right folder?")
                if answer.upper() in ["Y", "YES"]:
                    continue
                elif answer.upper() in ["N", "NO"]:
                    # Do action you need
                    print('please move the following files in a folder named appropriately:\n')
                    sys.exit(1)
            # if, in a folder, there's a mix of different identified devices,
            # Warn user and quit.
            if len(dev_types) != 1:
                print('\nProblem while scanning for media files. In [gold1]%s[/gold1]:'%folder)
                print('There is a mix of files from different devices:')
                [print('[gold1]%s[/gold1]'%m.path.name, end =', ')
                    for m in list_of_medias_in_folder]
                print('\nplease move them in exclusive folders and rerun.\n')
                sys.exit(1)
            if len(unidentified) == len(list_of_medias_in_folder):
                # all unidentified
                if len(unidentified) > 1:
                    print('Assuming those files are from the same device:')
                    [print('[gold1]%s[/gold1]'%m.path.name, end =', ')
                        for m in unidentified]
                    print('\nIf not, there\'s a risk of error: put them in exclusive folders and rerun.')
            # if we are here, the check is done: either 
            #   all files in folder are from unidentified device or
            #   all files in folder are from the same identified device
        logger.debug('n_CAM_folder %i'%n_CAM_folder)
        if n_CAM_folder > 1 :
            self.top_dir_has_multicam = True
        else:
            self.top_dir_has_multicam = False
        logger.debug('top_dir_has_multicam: %s'%self.top_dir_has_multicam)
        return

    def _parse_track_values(self, tracks_file) -> Tracks:
        """
        read track names for naming separated ISOs
        from tracks_file.

        repeting prefixes signals a stereo track
        and entries will correspondingly panned into
        a stero mix named mixL.wav and mixR.wav

        mic1 L # space is optionnal and will be removed
        mic1 R
        mic2 L
        mic2 R

        mixL

        Returns: a Tracks instance:
                # track numbers start at 1 for first track (as needed by sox)
                ttc: int # track number of TicTacCode signal
                unused: list # of unused tracks
                stereomics: list # of stereo mics track tuples (Lchan#, Rchan#)
                mix: list # of mixed tracks, if a pair, order is L than R
                others: list #of all other tags: (tag, track#) tuples
                rawtrx: list # list of strings read from file
                error_msg: str # 'None' if none
        """
        def _WOspace(chaine):
            ch = [c for c in chaine if c != ' ']
            return ''.join(ch)
        def _WO_LR(chaine):
            ch = [c for c in chaine if c not in 'lr']
            return ''.join(ch)
        def _seemsStereoMic(tag):
            # is tag likely a stereo pair tag?
            # should start with 'mic' and end with 'l' or 'r'
            return tag[:3]=='mic' and tag[-1] in 'lr'
        file=open(tracks_file,"r")
        whole_txt = file.read()
        logger.debug('all_lines:\n%s'%whole_txt)
        tracks_lines = [l.split('#')[0] for l in whole_txt.splitlines() if len(l) > 0 ]
        tracks_lines = [_WOspace(l).lower() for l in tracks_lines if len(l) > 0 ]
        rawtrx = tracks_lines
        tracks_lines = [(t,ix+1) for ix,t in enumerate(tracks_lines)]
        # tracks_lines = [l for l in tracks_lines if l not in ['ttc', '0']]
        # track_names = [l.split()[0] for l in tracks_lines if l != 'ttc']
        logger.debug('tracks_lines: %s'%tracks_lines)
        # first check for stereo mic pairs (could be more than one pair):
        spairs = [e for e in tracks_lines if _seemsStereoMic(e[0])]
        # spairs is stereo pairs candidates
        msg = 'Confusing stereo pair tags: %s'%' '.join([e[0]
                                                for e in spairs])
        error_output_stereo = Tracks(None,[],[],[],[],[],msg)
        if len(spairs)%2 == 1: # not pairs?, quit.
            return error_output_stereo
        logger.debug('_seemsStereoM: %s'%spairs)
        output_tracks = Tracks(None,[],[],[],[],rawtrx,None)
        def _LR(p):
            # p = (('mic1l', 1), ('mic1r', 2))
            # check if L then R
            p1, p2 = p
            return p1[0][-1] == 'l' and p2[0][-1] == 'r'
        if spairs:
            even_idxes = range(0,len(spairs),2)
            paired = [(spairs[i], spairs[i+1]) for i in even_idxes]
            # eg [(('mic1l', 1), ('mic1r', 2)), (('mic2l', 3), ('mic2r', 4))]
            def _mic_same(p):
                # p = (('mic1l', 1), ('mic1r', 2))
                # check if mic1 == mic1
                p1, p2 = p
                return _WO_LR(p1[0]) == _WO_LR(p2[0])
            mic_prefix_OK = all([_mic_same(p) for p in paired])
            logger.debug('mic_prefix_OK: %s'%mic_prefix_OK)
            if not mic_prefix_OK:
                return error_output_stereo
            mic_LR_OK = all([_LR(p) for p in paired])
            logger.debug('mic_LR_OK %s'%mic_LR_OK)
            if not mic_LR_OK:
                return error_output_stereo
            def _stereo_mic_pref_chan(p):
                # p = (('mic1l', 1), ('mic1r', 2))
                # returns ('mic1', (1,2))
                first, second = p
                mic_prefix = _WO_LR(first[0])
                return (mic_prefix, (first[1], second[1]) )
            grouped_stereo_mic_channels = [_stereo_mic_pref_chan(p) for p
                                            in paired]
            logger.debug('grouped_stereo_mic_channels: %s'%
                                        grouped_stereo_mic_channels)
            output_tracks.stereomics = grouped_stereo_mic_channels
        [tracks_lines.remove(e) for e in spairs]
        logger.debug('stereo mic pairs done, continue with %s'%tracks_lines)
        # second, check for stereo mix down (one mixL mixR pair)
        def _seemsStereoMix(tag):
            # is tag likely a stereo pair tag?
            # should start with 'mic' and end with 'l' or 'r'
            return tag[:3]=='mix' and tag[-1] in 'lr'
        stereo_mix_tags = [e for e in tracks_lines if _seemsStereoMix(e[0])]
        logger.debug('stereo_mix_tags: %s'%stereo_mix_tags)
        str_msg = 'Confusing mix pair tags: %s L should appear before R'%' '.join([e[0]
                                            for e in stereo_mix_tags])
        # error_output = Tracks(None,[],[],[],[],msg)
        def _error_Track(msg):
            return Tracks(None,[],[],[],[],[],msg)
        if stereo_mix_tags: 
            if len(stereo_mix_tags) != 2:
                return _error_Track(str_msg)
            mix_LR_OK = _LR(stereo_mix_tags)
            logger.debug('mix_LR_OK %s'%mix_LR_OK)
            if not mix_LR_OK:
                return _error_Track(str_msg)
            stereo_mix_channels = [t[1] for t in stereo_mix_tags]
            output_tracks.mix = stereo_mix_channels
            logger.debug('output_tracks.mix %s'%stereo_mix_channels)
        [tracks_lines.remove(e) for e in stereo_mix_tags]
        logger.debug('stereo mix done, will continue with %s'%tracks_lines)
        # third, check for a mono mix
        mono_mix_tags = [e for e in tracks_lines if e[0] == 'mix']
        if not output_tracks.mix and mono_mix_tags:
            logger.debug('mono_mix_tags: %s'%mono_mix_tags)
            if len(mono_mix_tags) != 1:
                return _error_Track('more than one "mix" token')
            output_tracks.mix = [mono_mix_tags[0][1]]
        [tracks_lines.remove(e) for e in mono_mix_tags]
        logger.debug('mono mix done, will continue with %s'%tracks_lines)
        # fourth, look for 'ttc'
        ttc_chan = [idx for tag, idx in tracks_lines if tag == 'ttc']
        if ttc_chan:
            if len(ttc_chan) > 1:
                return _error_Track('more than one "ttc" token')
            output_tracks.ttc = ttc_chan[0]
            tracks_lines.remove(('ttc', ttc_chan[0]))
        else:
            return _error_Track('no "ttc" token')
        # fifth, check for '0'
        logger.debug('ttc done, will continue with %s'%tracks_lines)
        zeroed = [idx for tag, idx in tracks_lines if tag == '0']
        logger.debug('zeroed %s'%zeroed)
        if zeroed:
            output_tracks.unused = zeroed
            [tracks_lines.remove(('0',i)) for i in zeroed]
        else:
            output_tracks.unused = []
        # sixth, check for 'others'
        logger.debug('0s done, will continue with %s'%tracks_lines)
        if tracks_lines:
            output_tracks.others = tracks_lines
        else:
            output_tracks.others = []
        logger.debug('Tracks %s'%output_tracks)
        return output_tracks






# print('Loading modules...', end='')

# I know, the following is ugly, but I need those try's to
# run the command in my dev setting AND from
# a deployment set-up... surely I'm setting
# things wrong [TODO] find why and clean up this mess

try:
    from . import yaltc
    from . import device_scanner
    from . import timeline
    from . import multi2polywav
except:
    import yaltc
    import device_scanner
    import timeline
    import multi2polywav

import argparse
from loguru import logger
from pathlib import Path
# import os, sys
import os, sys
from rich.progress import track
# from pprint import pprint
from rich.console import Console
# from rich.text import Text
from rich.table import Table
from rich import print
from pprint import pprint 

av_file_extensions = \
"""MOV webm mkv flv flv vob ogv ogg drc gif gifv mng avi MTS M2TS TS mov qt
wmv yuv rm rmvb viv asf amv mp4 m4p m4v mpg mp2 mpeg mpe mpv mpg mpeg m2v
m4v svi 3gp 3g2 mxf roq nsv flv f4v f4p f4a f4b 3gp aa aac aax act aiff alac
amr ape au awb dss dvf flac gsm iklax ivs m4a m4b m4p mmf mp3 mpc msv nmf
ogg oga mogg opus ra rm raw rf64 sln tta voc vox wav wma wv webm 8svx cda""".split()

logger.level("DEBUG", color="<yellow>")

def process_files_with_progress_bars(medias):
    recordings = []
    rec_with_yaltc = []
    times = []
    for m in track(medias,
            description="1/4 Initializing Recordings:"):
        # file_alias = 'dummy'
        recordings.append(yaltc.Recording(m))
    for r in track(recordings,
            description="2/4  Looking for TicTacCode:"):
        if r.seems_to_have_TicTacCode_at_beginning():
            rec_with_yaltc.append(r)
    for r in track(rec_with_yaltc,
            description="3/4     Finding start times:"):
        times.append(r.get_start_time())
    return recordings, rec_with_yaltc, times

def process_files(medias):
    recordings = []
    rec_with_yaltc = []
    times = []
    for m in medias:
        recordings.append(yaltc.Recording(m))
    for r in recordings:
        # print('%s duration %.2fs'%(r.AVpath.name, r.get_duration()))
        if r.seems_to_have_TicTacCode_at_beginning():
            rec_with_yaltc.append(r)
    for r in rec_with_yaltc:
        times.append(r.get_start_time())
    return recordings, rec_with_yaltc, times

def process_single(file, args):
    # argument is a single file
    m = device_scanner.media_at_path(None, Path(file))
    a_rec = yaltc.Recording(m)
    time = a_rec.get_start_time(plots=args.plotting)
    if time != None:
        frac_time = int(time.microsecond / 1e2)
        d = '%s.%s'%(time.strftime("%Y-%m-%d %H:%M:%S"),frac_time)
        if args.terse:
            print('%s UTC:%s pulse: %i in chan %i'%(file, d, a_rec.sync_position,
                        a_rec.TicTacCode_channel))
        else:
            print('\nRecording started at [gold1]%s[/gold1] UTC'%d)
            print('true sample rate: [gold1]%.3f Hz[/gold1]'%a_rec.true_samplerate)
            print('first sync at [gold1]%i[/gold1] samples in channel %i'%(a_rec.sync_position,
                        a_rec.TicTacCode_channel))
            print('N.B.: all results are precise to the displayed digits!\n')
    else:
        if args.terse:
            print('%s UTC: None'%(file))
        else:
            print('Start time couldnt be determined')
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
                "directory",
                type=str,
                nargs=1,
                help="path of media directory"
                )
    # parser.add_argument("directory", nargs="?", help="path of media directory")
    # parser.add_argument('-v', action='store_true')
    parser.add_argument('-v', action='store_true', default=False,
                    dest='verbose_output',
                    help='Set verbose ouput')
    parser.add_argument('-o', nargs=1,
                    help='where to write synced clips')
    parser.add_argument('-p', action='store_true', default=False,
                    dest='plotting',
                    help='Make plots')
    parser.add_argument('--isos', action='store_true', default=False,
                    dest='write_ISOs',
                    help='Write ISO sound files')
    parser.add_argument('--nosync', action='store_true',
                    dest='nosync',
                    help='just scan and decode')
    parser.add_argument('--terse', action='store_true',
                    dest='terse',
                    help='terse output')
    args = parser.parse_args()
    if args.verbose_output:
        logger.add(sys.stderr, level="DEBUG")
    # logger.add(sys.stdout, filter="__main__")
    # logger.add(sys.stdout, filter="device_scanner")
    # logger.add(sys.stdout, filter="yaltc") _extract_sound_to_merge
    logger.add(sys.stdout, filter=lambda r: r["function"] == "build_audio_and_write_video")
    # logger.add(sys.stdout, filter=lambda r: r["function"] == "_get_audio_devices")
    logger.add(sys.stdout, filter=lambda r: r["function"] == "_get_mix")
    logger.add(sys.stdout, filter=lambda r: r["function"] == "_sox_mix")
    top_dir = args.directory[0]
    if os.path.isfile(top_dir):
        file = top_dir
        process_single(file, args)
    if not os.path.isdir(top_dir):
        print('%s is not a directory or doesnt exist.'%top_dir)
        sys.exit(1)
    # logger.debug('args.o %s'%args.o)
    # print('args.o %s'%args.o)
    if args.o:
        arg_out_dir = args.o[0]
    else:
        arg_out_dir = None
    if args.o and not os.path.isdir(arg_out_dir):
        print('%s is not a directory or doesnt exist.'%arg_out_dir)
        sys.exit(1)
    multi2polywav.poly_all(top_dir)
    scanner = device_scanner.Scanner(top_dir, stay_silent=args.terse)
    scanner.scan_media_and_build_devices_UID() 
    if not args.terse:
        if scanner.input_structure == 'folder_is_device':
            print('\nDetected structured folders', end='')
            if scanner.top_dir_has_multicam:
                print(', multicam')
            else:
                print()
        else:
            print('\nDetected loose structure')
            if scanner.CAM_numbers() > 1:
                print('\nNote: different CAMs are present, will sync audio')
                print('for each of them but if you want to set their')
                print('respective timecode for NLE timeline alignement')
                print('you should regroup clips by CAM under their own DIR.')
        print('\nFound [gold1]%i[/gold1] media files '%(
            len(scanner.found_media_files)), end='')
        print('from [gold1]%i[/gold1] devices:\n'%(
            scanner.get_devices_number()))
        for dev in scanner.get_devices():
            print('  [gold1]%s[/gold1] with files:'%dev.name, end = ' ')
            medias = scanner.get_media_for_device(dev)
            for m in medias[:-1]:
                print('[gold1]%s[/gold1]'%m.path.name, end=', ')
            print('[gold1]%s[/gold1]'%medias[-1].path.name)
        # print('\nThese recordings will be analysed for timestamps:\n')
        # for m in (scanner.found_media_files):
        #     print('   ', '[gold1]%s[/gold1]'%m.path.name)
        print()
    if args.verbose_output or args.terse: # verbose or terse, so no progress bars
        rez = process_files(scanner.found_media_files)
    else: 
        rez = process_files_with_progress_bars(scanner.found_media_files)
    recordings, rec_with_yaltc, times = rez
    recordings_with_time =  [
        rec 
        for rec in rec_with_yaltc
        if rec.get_start_time()
        ]
    if not args.terse:    
        print('\n\n')
        table = Table(title="tictacsync results")
        table.add_column("Recording\n", justify="center", style='gold1')
        table.add_column("TicTacCode\nChannel", justify="center", style='gold1')
        # table.add_column("Device\n", justify="center", style='gold1')
        table.add_column("UTC times\nstart:end", justify="center", style='gold1')
        table.add_column("Clock drift\n(ppm)", justify="right", style='gold1')
        table.add_column("SN ratio\n(dB)", justify="center", style='gold1')
        table.add_column("Date\n", justify="center", style='gold1')
        rec_WO_time = [
            rec.AVpath.name
            for rec in rec_with_yaltc
            if not rec.get_start_time()
            ]
        if rec_WO_time:
            print('No time found for: ',end='')
            [print(rec, end=' ') for rec in rec_WO_time]
            print('\n')
        for r in recordings_with_time:
            date = r.get_start_time().strftime("%y-%m-%d")
            start_HHMMSS = r.get_start_time().strftime("%Hh%Mm%Ss")
            end_MMSS = r.get_end_time().strftime("%Mm%Ss")
            times_range = start_HHMMSS + ':' + end_MMSS
            table.add_row(
                str(r.AVpath.name),
                str(r.TicTacCode_channel),
                # r.device,
                times_range,
                # '%.6f'%(r.true_samplerate/1e3),
                '%2i'%(r.get_samplerate_drift()),
                '%.0f'%r.decoder.SN_ratio,
                date
                )
        console = Console()
        console.print(table)
        print()
    n_devices = scanner.get_devices_number()
    OUT_struct_for_mcam = scanner.top_dir_has_multicam
    # if n_devices > 2:
    #     print('\nMerging for more than 2 devices is not implemented yet, quitting...')
    #     sys.exit(1)
    if len(recordings_with_time) < 2:
        if not args.terse:
            print('\nNothing to sync, exiting.\n')
        sys.exit(1)
    matcher = timeline.Matcher(recordings_with_time)
    matcher.scan_audio_for_each_ref_rec()
    if not matcher.video_mergers:
        if not args.terse:
            print('\nNothing to sync, bye.\n')
        sys.exit(1)
    asked_ISOs = args.write_ISOs
    if asked_ISOs and scanner.input_structure != 'folder_is_device':
        print('Warning, can\'t write ISOs without structured folders: [gold1]--isos[/gold1] option ignored.\n')
        asked_ISOs = False
    output_dir = args.o
    if args.verbose_output or args.terse: # verbose, so no progress bars
        for stitcher in matcher.video_mergers:
            stitcher.build_audio_and_write_video(top_dir, arg_out_dir,
            OUT_struct_for_mcam,
            asked_ISOs,)
    else:
        print() 
        for stitcher in track(matcher.video_mergers,
            description="4/4         Merging sound to videos:"):
            stitcher.build_audio_and_write_video(top_dir, arg_out_dir,
                    OUT_struct_for_mcam,
                    asked_ISOs,)
    if not args.terse:
        print("\n")
    # find out where files were wrtitten
    a_stitcher = matcher.video_mergers[0]
    print('\nWrote output in folder [gold1]%s[/gold1]'%(
            a_stitcher.synced_clip_dir))
    for stitcher in matcher.video_mergers:
        print('[gold1]%s[/gold1]'%stitcher.ref_recording.AVpath.name, end='')
        for audio in stitcher.get_matched_audio_recs():
            print(' + [gold1]%s[/gold1]'%audio.AVpath.name, end='')
        new_file = stitcher.ref_recording.final_synced_file.parts
        print(' became [gold1]%s[/gold1]'%stitcher.ref_recording.final_synced_file.name)
        # matcher._build_otio_tracks_for_cam()
    matcher.shrink_gaps_between_takes()
    sys.exit(0)
    
if __name__ == '__main__':
    main()







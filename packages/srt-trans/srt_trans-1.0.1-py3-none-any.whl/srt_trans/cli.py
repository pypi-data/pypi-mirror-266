from googletrans import Translator
import pysrt
import os
import sys
import shutil
import ffmpeg

def extract_subtitles(video_file, output_srt):
    # Extract subtitles using FFmpeg
    try:
        (
            ffmpeg
            .input(video_file)
            .output(output_srt, f='srt')
            .run()
        )
        print(f'Subtitles extracted from {video_file} and saved to {output_srt}')
    except ffmpeg.Error as e:
        print(f'Error: {e}')


def split_list(input_list, chunk_size):
    return [input_list[i:i+chunk_size] for i in range(0, len(input_list), chunk_size)]


def flatten_list(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


def translate_lines(translator, lines, source_language, target_language):
    source_text = "\n❂".join(lines)
    translation = translator.translate(source_text, src=source_language, dest=target_language)
    translated_lines = translation.text.split("\n❂")
    return translated_lines


def translate_srt(input_file, output_file, source_language, target_language):
    result = True

    # Load SRT file
    srt_file = pysrt.open(input_file, encoding='utf-8')
    
    lines = [sub.text for sub in srt_file]
    # split all lines into small list of lines(no more than 200 lines in each sub list)
    sub_lines_list = split_list(lines, 200)

    # Initialize translator
    translator = Translator()

    translated_lines_list = []
    # Loop each each small list of lines, translate them.
    for sub_lines in sub_lines_list:
        translated_lines = translate_lines(translator, sub_lines, source_language, target_language)
        if len(translated_lines) == len(sub_lines):
            translated_lines_list.append(translated_lines)
        else:
            print("Can not translate the subtitle correctly.")
            result = False
            break
    
    if not result:
        return result

    translated_lines = flatten_list(translated_lines_list)
    # Translate each subtitle
    for sub, translated_line in zip(srt_file, translated_lines):
        # Merge the source subtitle and the translated subtitle.
        sub.text = "<font color='#ffff54'>" + sub.text + "</font>" + "\n" + translated_line

    # Save translated SRT file
    srt_file.save(output_file, encoding='utf-8')

    return result


def print_usage():
    print("""
        Usage: srt_trans test_file.srt [-src_lang en -dest_lang zh-CN -proxy http://youdomain:your_port]
        Example:
            srt_trans ./test_video.mkv
            srt_trans ./test_video.mkv -src_lang en -dest_lang zh-TW
            srt_trans ./test_video.mkv -src_lang en -dest_lang zh-CN -proxy http://127.0.0.1:8118
            srt_trans test_file.srt
            srt_trans test_file.srt -src_lang en -dest_lang zh-TW
            srt_trans test_file.srt -src_lang en -dest_lang ja
            srt_trans test_file.srt -src_lang en -dest_lang zh-CN
            srt_trans test_file.srt -src_lang en -dest_lang fr -proxy http://127.0.0.1:8118
    """)


def pre_process_srt_file(input_file):
    # Load SRT file
    srt_file = pysrt.open(input_file, encoding='utf-8')
    for sub in srt_file:
        sub.text = str(sub.text).replace("\n", " ").replace("<i>", "").replace("</i>", "")
    srt_file.save(input_file, encoding='utf-8')


def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"{input_file} not exists!")
        return
    
    if str(input_file).lower().endswith(".mkv"):
        video_file = input_file.lower()
        input_file = video_file.replace(".mkv", ".srt")
        extract_subtitles(video_file, input_file)
    
    pre_process_srt_file(input_file)

    source_language = "en"      # Source language code (e.g., "en" for English)
    target_language = "zh-CN"   # Target language code (e.g., "zh-CN" for Simple Chinese)
    if len(sys.argv) == 6 and sys.argv[2] == "-src_lang" and sys.argv[4] == "-dest_lang":
        source_language = sys.argv[3]
        target_language = sys.argv[5]
    if len(sys.argv) == 8 and sys.argv[2] == "-src_lang" and sys.argv[4] == "-dest_lang" and sys.argv[6] == "-proxy":
        source_language = sys.argv[3]
        target_language = sys.argv[5]
        proxy = sys.argv[7]
        # Set environment variables (replace with your details)
        # os.environ['http_proxy'] = "http://127.0.0.1:8118"
        # os.environ['https_proxy'] = "http://127.0.0.1:8118"
        os.environ['http_proxy'] = proxy
        os.environ['https_proxy'] = proxy

    output_file = str(input_file).replace(".srt", f".{target_language}.srt")
    translate_result = translate_srt(input_file, output_file, source_language, target_language)
    if not translate_result:
        return
    
    os.remove(input_file)
    shutil.move(output_file, input_file)


if __name__ == "__main__":
    main()
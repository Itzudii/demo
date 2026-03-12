"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
# from dependencies.tree import TreeNode
FILES = 'icons/files'
FOLDERS = 'icons/folders'

type_to_image = {
'adobe-illustrator': 'adobe-illustrator.png',
 'apk': 'apk.png',
 'css': 'css.png',
 'disc': 'disc.png',
 'doc': 'doc.png',
 'excel': 'excel.png',
 'font-file': 'font-file.png',
 'image': 'image.png',
 'iso': 'iso.png',
 'javascript': 'javascript.png',
 'js-file': 'js-file.png',
 'mail': 'mail.png',
 'mp3': 'mp3.png',
 'music': 'music.png',
 'pdf': 'pdf.png',
 'php': 'php.png',
 'powerpoint': 'powerpoint.png',
 'ppt': 'ppt.png',
 'psd': 'psd.png',
 'py': 'py.png',
 'record': 'record.png',
 'sql': 'sql.png',
 'svg': 'svg.png',
 'text': 'text.png',
 'ttf': 'ttf.png',
 'txt': 'txt.png',
 'vector': 'vector.png',
 'video': 'video.png',
 'word': 'word.png',
 'xls': 'xls.png',
 'zip': 'zip.png'
 }

known_file_types = {

    # =========================
    # TEXT FILES
    # =========================
    ".txt": "txt",        # plain text file
    ".log": "text",       # log files
    ".md": "text",        # markdown documentation
    ".rtf": "text",       # rich text format

    # =========================
    # IMAGE FILES
    # =========================
    ".png": "image",      # portable network graphics
    ".jpg": "image",      # jpeg image
    ".jpeg": "image",     # jpeg image variant
    ".gif": "image",      # animated/static gif
    ".bmp": "image",      # bitmap image
    ".webp": "image",     # modern compressed image
    ".tiff": "image",     # high quality image format

    # =========================
    # VECTOR / DESIGN FILES
    # =========================
    ".svg": "svg",        # scalable vector graphic
    ".ai": "adobe-illustrator",  # adobe illustrator design file
    ".psd": "psd",        # photoshop project file

    # =========================
    # MUSIC FILES
    # =========================
    ".flac": "music",     # lossless audio
    ".ogg": "music",      # open source compressed audio
    ".m4a": "music",      # apple audio format
    ".aac": "music",      # advanced audio coding
    ".alac": "music",     # apple lossless
    ".opus": "music",     # modern streaming codec
    ".wma": "music",      # windows media audio

    # =========================
    # MP3 (separate icon)
    # =========================
    ".mp3": "mp3",        # mp3 music file

    # =========================
    # AUDIO RECORDINGS
    # =========================
    ".wav": "record",     # uncompressed audio recording
    ".amr": "record",     # mobile voice recording
    ".caf": "record",     # apple core audio format
    ".aiff": "record",    # apple audio recording
    ".aif": "record",     # audio interchange format

    # =========================
    # VIDEO FILES
    # =========================
    ".mp4": "video",      # mpeg-4 video
    ".mkv": "video",      # matroska video container
    ".avi": "video",      # audio video interleave
    ".mov": "video",      # quicktime video
    ".webm": "video",     # web optimized video
    ".flv": "video",      # flash video
    ".wmv": "video",      # windows media video
    ".3gp": "video",      # mobile video format

    # =========================
    # DOCUMENT FILES
    # =========================
    ".pdf": "pdf",        # portable document format
    ".doc": "word",       # microsoft word document
    ".docx": "word",      # modern word document
    ".odt": "word",       # open document text

    # =========================
    # SPREADSHEET FILES
    # =========================
    ".xls": "excel",      # old excel spreadsheet
    ".xlsx": "excel",     # modern excel spreadsheet
    ".xlsm": "excel",     # excel with macros
    ".csv": "excel",      # comma separated spreadsheet

    # =========================
    # PRESENTATION FILES
    # =========================
    ".ppt": "ppt",        # powerpoint presentation
    ".pptx": "powerpoint",# modern powerpoint file
    ".odp": "powerpoint", # open document presentation

    # =========================
    # PROGRAMMING FILES
    # =========================
    ".py": "py",          # python source code
    ".js": "javascript",  # javascript file
    ".ts": "js-file",     # typescript file
    ".php": "php",        # php backend script
    ".css": "css",        # stylesheet file
    ".sql": "sql",        # database query script
    ".html": "text",      # html webpage
    ".htm": "text",       # html variant

    # =========================
    # DATABASE FILES
    # =========================
    ".db": "disc",        # database file
    ".sqlite": "disc",    # sqlite database
    ".sqlite3": "disc",   # sqlite database version

    # =========================
    # ARCHIVE / COMPRESSED
    # =========================
    ".zip": "zip",        # zip archive
    ".rar": "zip",        # rar archive
    ".7z": "zip",         # 7zip archive
    ".tar": "zip",        # tar archive
    ".gz": "zip",         # gzip compressed

    # =========================
    # DISC / IMAGE FILES
    # =========================
    ".iso": "iso",        # disc image
    ".img": "iso",        # raw disk image
    ".bin": "disc",       # binary disk image

    # =========================
    # EMAIL FILES
    # =========================
    ".msg": "mail",       # outlook email
    ".eml": "mail",       # email message file

    # =========================
    # FONTS
    # =========================
    ".ttf": "ttf",        # true type font
    ".otf": "font-file",  # open type font
    ".woff": "font-file", # web font
    ".woff2": "font-file",# compressed web font

    # =========================
    # APP / INSTALLER FILES
    # =========================
    ".apk": "apk",        # android package
    ".exe": "disc",       # windows executable
    ".msi": "disc",       # windows installer

    # =========================
    # TORRENT
    # =========================
    ".torrent": "disc",   # bittorrent metadata

    # =========================
    # DATA / GENERIC
    # =========================
    ".json": "text",      # json structured data
    ".dat": "disc",       # generic data file
    ".out": "text",       # output log
    ".tmp": "text",       # temporary file

    # =========================
    # DUMMY / INTERNAL
    # =========================
    ".xxx": "disc",       # placeholder extension for branch icon

    ".unknown" : "text"  # for file withoout extension
}

folder_to_image = {
    "folder-lock":"folder-lock.png",
    "folder-modified":"folder-modified.png",
    "folder":"folder.png"
}
def img(src,w=40,h=40):
    return f'<img src="{src}" alt="" srcset="" width="{w}px">'

def get_icon(node):
    if node.is_dir:
        if node.is_locked:
            i = folder_to_image['folder-lock']
            return img(f'{FOLDERS}/{i}')
        
        i = folder_to_image['folder']
        return img(f'{FOLDERS}/{i}') 
    t = known_file_types.get(f'.{node.ext}','text')
    i = type_to_image[t]
    return img(f'{FILES}/{i}')  

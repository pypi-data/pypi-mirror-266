"""Download the custom and generic SPICE kernels from the
GRSS GitHub repository and the NAIF FTP server"""
import os
import sys

# get the path to the directory containing this script
script_dir = os.path.dirname(os.path.realpath(__file__))

GRSS_SITE = 'https://raw.githubusercontent.com/rahil-makadia/grss/main/grss/kernels'
NAIF_SITE = 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels'
SSD_SITE = 'https://ssd.jpl.nasa.gov/ftp'
# get the custom spice kernels if they are not already present
# de431 planets + big16 1950-2350
if not os.path.exists(f'{script_dir}/planets_big16_de431_1950_2350.bsp'):
    print('Downloading combined DE430/431 planets and big16 asteroid SPK kernels...')
    os.system((f'curl -H "Accept: application/vnd.github+json" '
                f'-L --silent --show-error -o {script_dir}/planets_big16_de431_1950_2350.bsp '
                f'{GRSS_SITE}/planets_big16_de431_1950_2350.bsp'))
if not os.path.exists(f'{script_dir}/planets_big16_de431_1950_2350.tm'):
    print('Downloading combined DE430/431 planets and big16 asteroid meta-kernel...')
    os.system((f'curl -H "Accept: application/vnd.github+json" '
                f'-L --silent --show-error -o {script_dir}/planets_big16_de431_1950_2350.tm '
                f'{GRSS_SITE}/planets_big16_de431_1950_2350.tm'))
# de441 planets + big16 1950-2350
if not os.path.exists(f'{script_dir}/planets_big16_de441_1950_2350.bsp'):
    print('Downloading combined DE440/441 planets and big16 asteroid kernels...')
    os.system((f'curl -H "Accept: application/vnd.github+json" '
                f'-L --silent --show-error -o {script_dir}/planets_big16_de441_1950_2350.bsp '
                f'{GRSS_SITE}/planets_big16_de441_1950_2350.bsp'))
if not os.path.exists(f'{script_dir}/planets_big16_de441_1950_2350.tm'):
    print('Downloading combined DE440/441 planets and big16 asteroid meta-kernel...')
    os.system((f'curl -H "Accept: application/vnd.github+json" '
                f'-L --silent --show-error -o {script_dir}/planets_big16_de441_1950_2350.tm '
                f'{GRSS_SITE}/planets_big16_de441_1950_2350.tm'))

# get the generic spice kernels if they are not already present
# de430 planets + de431 big16
if (not os.path.exists(f'{script_dir}/de430.bsp') or
    not os.path.exists(f'{script_dir}/sb431-n16s.bsp')):
    print('Downloading generic DE430/431 planets and big16 asteroid kernels...')
    os.system((f'curl --silent --show-error -o {script_dir}/de430.bsp '
                f'{NAIF_SITE}/spk/planets/de430.bsp'))
    os.system((f'curl --silent --show-error -o {script_dir}/sb431-n16s.bsp '
                f'{SSD_SITE}/xfr/sb431-n16s.bsp'))
# de440 planets + de441 big16
if (not os.path.exists(f'{script_dir}/de440.bsp') or
    not os.path.exists(f'{script_dir}/sb441-n16s.bsp')):
    print('Downloading generic DE440/441 planets and big16 asteroid kernels...')
    os.system((f'curl --silent --show-error -o {script_dir}/de440.bsp '
                f'{NAIF_SITE}/spk/planets/de440.bsp'))
    os.system((f'curl --silent --show-error -o {script_dir}/sb441-n16s.bsp '
                f'{SSD_SITE}/xfr/sb441-n16s.bsp'))

# get the latest spice leap second kernel
if not os.path.exists(f'{script_dir}/latest_leapseconds.tls'):
    print('Downloading latest leap second kernel...')
    os.system((f'curl --silent --show-error -o {script_dir}/latest_leapseconds.tls '
                f'{NAIF_SITE}/lsk/latest_leapseconds.tls'))
# get the earth orientation binary spice kernels and their comments if they are not already present
# latest earth pck
if not os.path.exists(f'{script_dir}/earth_latest_high_prec.bpc'):
    print('Downloading latest Earth binary PCK...')
    os.system((f'curl --silent --show-error -o {script_dir}/earth_latest_high_prec.cmt '
                f'{NAIF_SITE}/pck/earth_latest_high_prec.cmt'))
    os.system((f'curl --silent --show-error -o {script_dir}/earth_latest_high_prec.bpc '
                f'{NAIF_SITE}/pck/earth_latest_high_prec.bpc'))
# historical earth pck
if not os.path.exists(f'{script_dir}/earth_720101_230601.bpc'):
    print('Downloading historical Earth binary PCK...')
    os.system((f'curl --silent --show-error -o {script_dir}/earth_720101_230601.bpc '
                f'{NAIF_SITE}/pck/earth_720101_230601.bpc'))
    os.system((f'curl --silent --show-error -o {script_dir}/earth_720101_230601.cmt '
                f'{NAIF_SITE}/pck/earth_720101_230601.cmt'))
# predicted earth pck
if not os.path.exists(f'{script_dir}/earth_200101_990825_predict.bpc'):
    print('Downloading predicted Earth binary PCK...')
    os.system((f'curl --silent --show-error -o {script_dir}/earth_200101_990825_predict.bpc '
                f'{NAIF_SITE}/pck/earth_200101_990825_predict.bpc'))
    os.system((f'curl --silent --show-error -o {script_dir}/earth_200101_990825_predict.cmt '
                f'{NAIF_SITE}/pck/earth_200101_990825_predict.cmt'))
# generic frame kernels
if not os.path.exists(f'{script_dir}/pck00011.tpc'):
    print('Downloading generic frame kernels...')
    os.system((f'curl --silent --show-error -o {script_dir}/pck00011.tpc '
                f'{NAIF_SITE}/pck/pck00011.tpc'))

# run this code if the no-tm-overwrite flag argument is not present
if len(sys.argv) > 1:
    TM_OVERWRITE = sys.argv[1] != '--no-tm-overwrite'
else:
    TM_OVERWRITE = True
if TM_OVERWRITE:
    # open the spice meta-kernels and update the line that defines
    # the PATH_VALUES variable to point to the same directory as this script
    meta_kernels = [
        f'{script_dir}/planets_big16_de431_1950_2350.tm',
        f'{script_dir}/planets_big16_de441_1950_2350.tm'
    ]
    for mk in meta_kernels:
        # read the meta-kernel and find the line that defines the PATH_VALUES variable
        with open(mk, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            NUM_CHUNKS = 0
            for i, line in enumerate(lines):
                if 'PATH_VALUES' in line and 'placeholder' in line:
                    # update the path to the directory containing this script
                    # if script_dir is more that 40 characters long, then break it up
                    # into chunks of 40 characters each
                    CUTOFF = 40
                    if len(script_dir) > CUTOFF:
                        NUM_CHUNKS, remainder = divmod(len(script_dir), CUTOFF)
                        chunks = [script_dir[i*CUTOFF:(i+1)*CUTOFF] for i in range(NUM_CHUNKS)]
                        if remainder > 0:
                            chunks.append(script_dir[-remainder:])
                            NUM_CHUNKS += 1
                        lines[i] = f"    PATH_VALUES  = ( '{chunks[0]}',\n"
                        for chunk in chunks[1:]:
                            END_CHAR = " )" if chunk == chunks[-1] else ","
                            lines[i] += f"                     '{chunk}'{END_CHAR}\n"
                    else:
                        NUM_CHUNKS = 1
                        lines[i] = f"    PATH_VALUES  = ( '{script_dir}" + "' )\n"
                if 'PATH_SYMBOLS' in line and "'GRSS'" in line and NUM_CHUNKS > 1:
                    # replace PATH_SYMBOLS = ( 'GRSS' ) with PATH_SYMBOLS = ( 'GRSS_1', ... )
                    lines[i] = "    PATH_SYMBOLS = ( 'GRSS1',\n"
                    for j in range(2, NUM_CHUNKS+1):
                        END_CHAR = " )" if j == NUM_CHUNKS else ","
                        lines[i] += f"                     'GRSS{j}'{END_CHAR}\n"
                if '$GRSS' in line and NUM_CHUNKS > 1:
                    # replace '$GRSS' with '$GRSS1$GRSS2$GRSS3...' according to the number of chunks
                    REPLACE_STR = '$GRSS1'
                    for j in range(2, NUM_CHUNKS+1):
                        REPLACE_STR += f'$GRSS{j}'
                    lines[i] = line.replace('$GRSS', REPLACE_STR)
        # write the updated meta-kernel
        with open(mk, 'w', encoding='utf-8') as f:
            f.writelines(lines)

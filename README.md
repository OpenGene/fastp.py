# Python scripts to process files within a folder in parallel

# fastp.py
A python script to use [fastp](https://github.com/OpenGene/fastp) to preprocess all FASTQ files within a folder. It will automatically couple the paired-end FASTQ files.  

This script will generate an `overall.html` to present an aggregate summary for all processed FASTQ files.  

## example
```shell
python fastp.py -i /path/to/input/folder -o /path/to/output/folder -a '-f 3 -t 2'
```
which means to
```
. process all the FASTQ data in the folder
. using fastp in PATH
. with arguments -f 3 and -t 3, which means trimming 3bp in head and 2bp in tail
. output all clean data and reports to another folder
```

## all fastp.py options
```shell
Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir=INPUT_DIR
                        the folder contains the FASTQ files to be
                        preprocessed, by default is current dir (.)
  -o OUT_DIR, --out_dir=OUT_DIR
                        the folder to store the clean FASTQ. If not specified,
                        then there will be no output files.
  -r REPORT_DIR, --report_dir=REPORT_DIR
                        the folder to store QC reports. If not specified, use
                        out_dir if out_dir is specified, otherwise use
                        input_dir.
  -c COMMAND, --command=COMMAND
                        the path to fastp/fastplong command, if not specified,
                        then it will use 'fastp' in PATH
  -a ARGS, --args=ARGS  the arguments that will be passed to fastp. Enclose in
                        quotation marks. Like --args='-f 3 -t 3'
  -p PARALLEL, --parallel=PARALLEL
                        the number of fastp processes can be run in parallel,
                        if not specified, then it will be CPU_Core/4
  -1 READ1_FLAG, --read1_flag=READ1_FLAG
                        specify the name flag of read1, default is R1, which
                        means a file with name *R1* is read1 file
  -2 READ2_FLAG, --read2_flag=READ2_FLAG
                        specify the name flag of read2, default is R2, which
                        means a file with name *R2* is read2 file
```

# fastplong.py
A python script to use [fastplong](https://github.com/OpenGene/fastplong) to preprocess all FASTQ files within a folder. It will automatically couple the paired-end FASTQ files.  

This script will generate an `overall.html` to present an aggregate summary for all processed FASTQ files.  

## example
```shell
python parallel.py -i /path/to/input/folder -o /path/to/output/folder -r /path/to/reports/folder -a '--cut_front --cut_tail'
```
which means to  
```
. process all the FASTQ data in /path/to/input/folder
. using fastplong in PATH
. the arguments --cut_front and --cut_tail will be passed to fastplong, to apply sliding window quality trimming from front and tail
. output all clean data to /path/to/output/folder
. output all HTML and JSON reports to /path/to/reports/folder
```

## all fastplong.py options
```shell
Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir=INPUT_DIR
                        the folder contains the FASTQ files to be
                        preprocessed, by default is current dir (.)
  -o OUT_DIR, --out_dir=OUT_DIR
                        the folder to store the clean FASTQ. If not specified,
                        then there will be no output files.
  -r REPORT_DIR, --report_dir=REPORT_DIR
                        the folder to store QC reports. If not specified, use
                        out_dir if out_dir is specified, otherwise use
                        input_dir.
  -c COMMAND, --command=COMMAND
                        the path to fastplong command, if not specified, then
                        it will use 'fastplong' in PATH
  -a ARGS, --args=ARGS  the arguments that will be passed to fastplong.
                        Enclose in quotation marks. Like --args='-f 3 -t 3'
  -p PARALLEL, --parallel=PARALLEL
                        the number of fastplong processes can be run in
                        parallel, if not specified, then it will be CPU_Core/4
```

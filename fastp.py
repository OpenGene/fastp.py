#!/usr/bin/env python

import os,sys
from optparse import OptionParser
import time
from multiprocessing import Process, Queue
import copy
import subprocess
from concurrent.futures import ThreadPoolExecutor

FASTP_PY_VERSION = "0.0.1"

def parseCommand():
    usage = "A python script to use fastp/fastplong to preprocess all FASTQ files within a folder"
    parser = OptionParser(usage = usage, version = FASTP_PY_VERSION)
    parser.add_option("-i", "--input_dir", dest = "input_dir", default = ".",
        help = "the folder contains the FASTQ files to be preprocessed, by default is current dir (.)")
    parser.add_option("-o", "--out_dir", dest = "out_dir", default = None,
        help = "the folder to store the clean FASTQ. If not specified, then there will be no output files.")
    parser.add_option("-r", "--report_dir", dest = "report_dir", default = None,
        help = "the folder to store QC reports. If not specified, use out_dir if out_dir is specified, otherwise use input_dir.")
    parser.add_option("-c", "--command", dest = "command", default = None,
        help = "the path to fastp/fastplong command, if not specified, then it will use 'fastp' in PATH")
    parser.add_option("-a", "--args", dest = "args", default = None,
        help = "the arguments that will be passed to fastp. Enclose in quotation marks. Like --args='-f 3 -t 3' ")
    parser.add_option("-p", "--parallel", dest = "parallel", default = None, type = "int",
        help = "the number of fastp processes can be run in parallel, if not specified, then it will be CPU_Core/4")
    parser.add_option("-1", "--read1_flag", dest = "read1_flag", default = "R1",
        help = "specify the name flag of read1, default is R1, which means a file with name *R1* is read1 file")
    parser.add_option("-2", "--read2_flag", dest = "read2_flag", default = "R2",
        help = "specify the name flag of read2, default is R2, which means a file with name *R2* is read2 file")
    return parser.parse_args()

def matchFlag(filename, flag):
    if flag.endswith('.') or flag.endswith('_') or flag.endswith('-'):
        return flag in filename
    else:
        return (flag+"." in filename) or (flag+"_" in filename) or (flag+"-" in filename)
    
def getBaseName(filename):
    fqext = (".fq.gz", ".fastq.gz", ".fq", ".fastq")
    for ext in fqext:
        if filename.endswith(ext):
            return filename[:-len(ext)]

def processDir(folder, options):
    fqext = (".fq", ".fastq", ".fq.gz", ".fastq.gz")
    read1name = options.read1_flag
    read2name = options.read2_flag
    
    #is not a dir
    if not os.path.isdir(folder):
        return
        
    options_list = []
    processed =  set()  # to avoid processing the same file multiple times
    
    files = os.listdir(folder)
    for f in files:
        path = os.path.join(folder, f)
        if os.path.isdir(path):
            continue
        
        isfq = False
        for ext in fqext:
            if f.endswith(ext):
                isfq = True
        if isfq == False:
            continue

        if processed.__contains__(path):
            continue

        # skip read2 files here, we will find read1 files first
        if matchFlag(f, read2name):
            continue

        processed.add(path)

        # here we skip those files with name starting with Undetermined
        # because these files are usually with unknown barcode and have no need to be processed
        if f.startswith("Undetermined"):
            continue
        
        #find read1 file, try to find read2 file
        if matchFlag(f, read1name):
            opt = copy.copy(options)
            read1 = path
            opt.read1_file = read1
            read2 = read1.replace(read1name, read2name)
            if os.path.exists(read2):
                opt.read2_file = read2
                processed.add(read2)
            options_list.append(opt)
        else:
            # if not read1 file, then run fastp as single-end
            opt = copy.copy(options)
            opt.read1_file = path
            options_list.append(opt)

    commands = []
    for opt in options_list:
        cmd = ""
        if opt.command:
            cmd = opt.command
            if not os.path.exists(cmd):
                print(f"Error: {cmd} not found, please specify the correct path to fastp/fastplong with -c option")
                sys.exit(1)
        else:
            cmd = "fastp"
        
        cmd = cmd + " -i " + opt.read1_file
        if hasattr(opt, 'read2_file'):
            cmd += " -I " + opt.read2_file
        if opt.out_dir:
            if not os.path.exists(opt.out_dir):
                os.makedirs(opt.out_dir)
            out_prefix1 = os.path.join(opt.out_dir, os.path.basename(getBaseName(opt.read1_file)))
            cmd += " -o " + out_prefix1 + ".clean.fastq.gz"
            if hasattr(opt, 'read2_file'):
                out_prefix2 = os.path.join(opt.out_dir, os.path.basename(getBaseName(opt.read2_file)))
                cmd += " -O " + out_prefix2 + ".clean.fastq.gz"
        
        if opt.args:
            cmd += " " + opt.args

        if opt.report_dir:
            if not os.path.exists(opt.report_dir):
                os.makedirs(opt.report_dir)
        
        report_file = os.path.join(opt.report_dir, os.path.basename(opt.read1_file).replace(opt.read1_flag, "pe"))
        cmd += " --html=" + report_file + ".html --json=" + report_file + ".json"
        
        commands.append(cmd)
    
    if len(options_list) == 0:
        print("No FASTQ file found, do you call the program correctly?")
        print("See -h for help")
        return

    if options.parallel is None:
        options.parallel = max(1, os.cpu_count() // 4)

    with ThreadPoolExecutor(max_workers=opt.parallel) as executor:
        futures = [executor.submit(run_command, cmd) for cmd in commands]
        
        for future in futures:
            print(future.result())

def run_command(command):
    print("Running command: " + command)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout
    
def main():
    time1 = time.time()
    
    (options, args) = parseCommand()
    options.version = FASTP_PY_VERSION

    if options.input_dir == None:
        options.input_dir="."

    if options.report_dir == None:
        if options.out_dir:
            options.report_dir = options.out_dir
        else:
            # if out_dir is not specified, use input_dir as report_dir
            options.report_dir = options.input_dir
    
    processDir(options.input_dir, options)
    
    time2 = time.time()
    print('Time used: ' + str(time2-time1))
    
if __name__  == "__main__":
    main()

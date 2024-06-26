#!/usr/bin/env python3

import os
import sys
import glob
import shutil
import subprocess
from lib import cd, Submission, run_cmd

source_path = os.path.dirname(os.path.abspath(__file__)) # /a/b/c/d/e

build_points = 1 # points for building. tentative
submission_points = 1
# test_cases = 0
# test_case_points = 0

def buildAndTest(submissionpath, sourceTestPath, no_remove, gcc=False):
    points = submission_points
    test_case_points=0
    test_cases=0
    script_path = os.path.dirname(os.path.realpath(__file__))

    # create temporary directory so that previous students' results will not affect subsequent tests
    testCasePath = sourceTestPath

    testCases = glob.glob(os.path.join(testCasePath, "*.simplec"))
    #print(f"testCases {testCases}")
    if not no_remove:
        for i in glob.glob(os.path.join(submissionpath, "*.o")):
            if os.path.exists(i):
                os.remove(i)
    progname = os.path.join(submissionpath, "simplec")
    if os.path.exists(progname):
        os.remove(progname)

    if len(testCases) == 0:
        print("# no tests found.  double-check your path: " + testCasePath)
        sys.exit()


    if os.path.exists(submissionpath + "/simplec"):
        os.remove(submissionpath + "/simplec")
    out = subprocess.run(['make'], cwd = submissionpath,
            stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

    output = ""
    err = ""
    if out.returncode != 0:
        output += "Make failed."  
        print(output + " Do you have a Makefile?") # can't even compile the compiler 
        return 0, output 
    else:
        print("Build succeeded!")
        points += build_points # points to build. tentative   
    
    # simpleC compilers lives so lets go through every test case now
    for case in testCases:
        base_name = os.path.basename(case)
        ground_truth = case.replace(".simplec", ".ast")
        if gcc:
            ground_truth = case.replace(".simplec", ".out")
        output_file = base_name.replace(".simplec", ".out")
        diff_file = base_name.replace(".simplec", ".diff")
        print(f"Testing {base_name}:", end=" ")

        with cd(submissionpath):
            
            if gcc:
                cmd = f"cat \"{case}\" | ./simplec > {output_file}.s"
                return_code, stdout_, stderr_ = run_cmd(cmd)
                
                cmd = f"gcc -o {output_file}.bin {output_file}.s "
                return_code, stdout_, stderr_ = run_cmd(cmd)
                
                cmd = f"./{output_file}.bin"
                return_code, stdout_, stderr_ = run_cmd(cmd)
                
                # open a (new) file to write
                fp = open(output_file, "w")
                fp.write(f"{return_code}")
                fp.close()


            else:
                cmd = f"cat \"{case}\" | ./simplec > {output_file}"
            return_code, stdout_, stderr_ = run_cmd(cmd)
            cmd = f"diff -w -B \"{ground_truth}\" {output_file}"
            print(f"Running command: {cmd}")
            return_code, stdout_, stderr_ = run_cmd(cmd,False)
            if return_code == 0 and len(stdout_) == 0:
                print("Success!")
                test_case_points += 1
                test_cases +=1
            if return_code == 1 and len(stdout_) > 0:
                with open(ground_truth, 'r') as f:
                    total_lines = len(f.readlines())
                print(f"Failure. See {diff_file} for diff and {output_file} for output.")
                diff_out = open(diff_file, "w")
                diff_out.write(stdout_)
                diff_out.close()

                with open(diff_file, 'r') as f:
                    diff_lines = len(f.readlines())
                if gcc:
                    pass
                else:
                    matching_percentage = (total_lines - (diff_lines-1))/ total_lines
                    test_case_points += matching_percentage
                    print(f"Percentage of matching lines: {matching_percentage}")

                return_code, stdout_, stderr_ = run_cmd(cmd,False)
            if return_code > 1:
                print(f"diff exited with an unknown return code. This shouldn't happen. Here is the stderr: {stderr_}")
    print(f"{test_cases} / {len(testCases)} test casing passing. ")
    points += test_case_points*10/len(testCases)
    print(f"Points awarded - {points:.1f} ")
    return points, output 

def error(app, f):

    return "# ERROR " + app + " failed on " + f + "\n"
    

if __name__ == "__main__":

    try:
        submissionDirectory = os.path.abspath(sys.argv[1])
        sourceTestPath = os.path.abspath(sys.argv[2])
        norm = sys.argv[3]
        usegcc = sys.argv[4]
    except:
        print("USAGE: path/to/your/repo path/to/the/tests")
        print("example: ./ ../syllabus/projects/tests/proj0/")
        sys.exit()
    no_remove = True if norm == "true" else False
    gcc = True if usegcc == "true" else False
    buildAndTest(submissionDirectory, sourceTestPath, no_remove, gcc)

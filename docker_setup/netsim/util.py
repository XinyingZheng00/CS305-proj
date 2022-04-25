import sys, select, time
from subprocess import Popen, PIPE, STDOUT

def check_output(args, shouldPrint=True):
    return check_both(args, shouldPrint)[0]

def check_both(args, shouldPrint=True, check=True):
    out = ""
    p = Popen(args,shell=True,stdout=PIPE,stderr=STDOUT)
    poll_obj = select.poll()
    poll_obj.register(p.stdout, select.POLLIN)
    t = time.time()
    while (time.time() - t) < 3:
        poll_result = poll_obj.poll(0)
        if poll_result:
            line = p.stdout.readline()
            if not line:
                break
            if shouldPrint: sys.stdout.write(line.decode('utf-8'))
            out += line.decode('utf-8')
            t = time.time()
    rc = p.wait()
    out = (out,"")
    out = (out, rc)
    if check and rc is not 0:
        #print "Error processes output: %s" % (out,)
        raise Exception("subprocess.CalledProcessError: Command '%s'" \
                            "returned non-zero exit status %s" % (args, rc))
    return out

def run_bg(args):
    Popen(args, shell=True)

# A generator returning each line in a file with comments removed
# f is an open file object
def strip_comments(f):
    for line in f:
        if '#' in line:
            line = line.split('#')[0]
        line = line.strip()
        if line is not '':
            yield line
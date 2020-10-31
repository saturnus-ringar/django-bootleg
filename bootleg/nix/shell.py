import subprocess

from bootleg.utils.strings import nl2br


def run_command(args):
    process = subprocess.Popen(args,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode("utf-8").strip()


def get_var(file, name):
    cmd = 'echo $(source %s; echo $%s)' % (file, name)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    return p.stdout.readlines()[0].strip().decode("utf-8")


def output_to_list(output, lines_to_ignore=None):
    list = []
    for index, line in enumerate(output.split("\n")):
        add = True
        if lines_to_ignore and index in lines_to_ignore:
            add = False

        if add:
            list.append(line.split())

    return list


def outout_to_html(output):
    return nl2br(output.decode("utf-8"))

#subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

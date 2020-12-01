import subprocess

from bootleg.utils.strings import nl2br


class CommandException(Exception):
    pass


def run_command(args):
    process = subprocess.Popen(args,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        raise CommandException("The process [%s] raised an error: %s" % (args, stderr.decode()))
    return stdout.decode("utf-8").strip()


# https://stackoverflow.com/a/13332300
def run_command_with_pipe(args1, args2):
    process = subprocess.Popen(args1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(args2, stdin=process.stdout)


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


def output_to_list_and_ignore_string(output, string, lines_to_ignore=None):
    cleaned_data = []
    for row in output_to_list(output, lines_to_ignore):
        if row and string not in row:
            cleaned_data.append(row)

    return cleaned_data

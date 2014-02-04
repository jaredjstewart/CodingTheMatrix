1########                                     ######## 
# Hi there, curious student.                         #
#                                                    #
# This submission script downloads some tests,       #
#  runs the tests against your code,                 #
#and then sends the results to a server for grading. #
#                                                    #
# Changing this script might cause your              #
# submissions to fail.                               #
#You can use the option '--dry-run' to see the tests #
# that would be run without actually running them.   #
########                                     ########

import os, sys, doctest, traceback, urllib.request, urllib.parse, urllib.error, base64, ast, re, imp, ast


SUBMIT_VERSION = '2.0'

RECEIPT_DIR = os.path.join('../', 'receipts');
grader_url = 'edition1.gradingthematrix.appspot.com'
static_url = 'edition1tests.codingthematrix.com'
protocol = 'http'
rcptdir_ok = None
overwrite_policy = None
receipts = None
dry_run = False
tests=None
solutions=None
verbose = False
show_submission = False
show_feedback = False

################ FOR VERIFYING SIGNATURE ON TESTS ################
from collections import namedtuple
from hashlib import sha512
hashfn = sha512

PublicKey = namedtuple('PublicKey', ('N', 'e'))

def hash(lines, salt):
    m = hashfn()
    for line in lines:
        m.update(str(line).encode())
    m.update(str(salt).encode())
    return m.digest()

def unsign(m, key): return pow(m, key.e, key.N)

def b2i(m): return int.from_bytes(m, 'little')

def verify_signature(lines, signature, key):
    salt, sig = signature
    hashed = hash(lines, salt)
    return b2i(hashed) == unsign(sig, key)

def verify_signature_lines(lines, key):
    i = iter(lines)
    firstline = next(i)
    salt_str, sign_str = firstline.split(' ')
    (salt, sig) = int(salt_str), int(sign_str)
    return verify_signature(i, (salt, sig), key)

def check_signature(response):
    key = PublicKey(N=10810480223307555270754793974348137028346231911887128372498894236522333862768535904711981770850660563024357718007478468455827997422651868772756940504390694970913100697704378592429214786267348296187069428987220571233110244818841009602583740157557662581909170939997953247229188236715181458561434858401678704933253698171424919513416718407303681363275403114095516851428969948115240989059101545870985909066841768134526273721190057338992190632073739245354402667060338194897351550243889777461715790352313337931,e=356712077277075117461112781152011833907464773700347296194891295955027010053581043972802545021976353698381277440683503945344229100132712230552438667754457538982795034975143122540063545095552633393479508230675918312833788633196124838699032398201767280061)
    return verify_signature_lines(response, key)

def get_asgn_data(asgn_name):
    try:
        with urllib.request.urlopen('%s://%s/%s.tests'%(protocol, static_url, asgn_name)) as tf:
            response = tf.read().decode('utf8').split('\n')
    except urllib.error.URLError:
        print("Check your Internet connection.")
        sys.exit(1)
    except urllib.error.HTTPError:
        print("Tests not available for assignment '%s'"%asgn_name)
        sys.exit(1)

    if check_signature(response):
        return ast.literal_eval('\n'.join(response[1:]))
    else:
        print("Assignment data improperly signed!")
        sys.exit(1)

########### END OF SIGNATURE-VERIFICATION CODE ###############

########### SOME AUXILIARY PROCEDURES FOR DOCTESTING #########
def test_format(obj, precision=6):
    tf = lambda o: test_format(o, precision)
    delimit = lambda o: ', '.join(o)
    otype = type(obj)
    if otype is str:
        return "'%s'" % obj
    elif otype is float or otype is int:
        if otype is int:
            obj = float(obj)
        if -0.000001 < obj < 0.000001:
            obj = 0.0
        fstr = '%%.%df' % precision
        return fstr % obj
    elif otype is set:
        if len(obj) == 0:
            return 'set()'
        return '{%s}' % delimit(sorted(map(tf, obj)))
    elif otype is dict:
        return '{%s}' % delimit(sorted(tf(k)+': '+tf(v) for k,v in obj.items()))
    elif otype is list:
        return '[%s]' % delimit(map(tf, obj))
    elif otype is tuple:
        return '(%s%s)' % (delimit(map(tf, obj)), ',' if len(obj) == 1 else '')
    elif otype.__name__ in ['Vec','Mat']:
        entries = tf({x:obj.f[x] for x in obj.f if tf(obj.f[x]) != tf(0)})
        return '%s(%s, %s)' % (otype.__name__, test_format(obj.D), entries)
    else:
        return str(obj)
         
def find_lines(varname):
    return [line for line in open(asgn_name+'.py') if line.startswith(varname)]

def find_line(varname):
    ls = find_lines(varname)
    if len(ls) != 1:
        print("ERROR: stencil file should have exactly one line containing the string '%s'" % varname)
        return None
    return ls[0]


def use_comprehension(varname):
    line = find_line(varname)
    return "comprehension" in ast.dump(ast.parse(line))

def double_comprehension(varname):
    line = find_line(varname)
    return ast.dump(ast.parse(line)).count("comprehension") == 2

def line_contains_substr(varname, word):
    line = find_line(varname)
    return word in line

def substitute_in_assignment(varname, new_env):
    assignment = find_line(varname)
    g = globals().copy()
    g.update(new_env)
    return eval(compile(ast.Expression(ast.parse(assignment).body[0].value), '', 'eval'), g)

##### END AUXILIARY PROCEDURES FOR TESTS ################

def output(tests, test_vars):
    dtst = doctest.DocTestParser().get_doctest(tests, test_vars, 0, '<string>', 0)
    runner = ModifiedDocTestRunner()
    runner.run(dtst)
    return runner.results

class ModifiedDocTestRunner(doctest.DocTestRunner):
    def __init__(self, *args, **kwargs):
        self.results = []
        return super(ModifiedDocTestRunner, self).__init__(*args, checker=OutputAccepter(), **kwargs)
    
    def report_success(self, out, test, example, got):
        self.results.append(got)
    
    def report_unexpected_exception(self, out, test, example, exc_info):
        exf = traceback.format_exception_only(exc_info[0], exc_info[1])[-1]
        self.results.append(exf)
        sys.stderr.write("TEST ERROR: "+exf) #added so as not to fail silently

class OutputAccepter(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        return True

def parse_feedback(feedback):
    try:
        return dict(item.split(':\n', 1) for item in feedback.split('\n=====\n'))
    except:
        return {}

def get_result(feedback):
    return parse_feedback(feedback).get('result')

def submit(asgn_name, parts_string, login):   
    print('= Coding the Matrix Homework and Lab Submission')

    print('Fetching problems')
    source_files, problems = get_asgn_data(asgn_name)

    print('Importing your stencil file')
    try:
        solution = __import__(asgn_name)
        test_vars = vars(solution).copy()
    except Exception as exc:
        print(exc)
        print("!! It seems that you have an error in your stencil file. Please fix before submitting.")
        sys.exit(1)

    test_vars['test_format'] = test_vars['tf'] = test_format
    test_vars['find_lines'] = find_lines
    test_vars['find_line'] = find_line
    test_vars['use_comprehension'] = use_comprehension
    test_vars['double_comprehension'] = double_comprehension
    test_vars['line_contains_substr'] = line_contains_substr
    test_vars['substitute_in_assignment'] = substitute_in_assignment
    if not login:
        login = login_prompt()
    if not parts_string: 
        parts_string = parts_prompt(problems)

    parts = parse_parts(parts_string, problems)

    check_rcptdir()
    check_overwrite_policy(parts)

    for sid, name, part_tests in parts:
        print('== Submitting "%s"' % name)

        if dry_run:
            print(part_tests)
        else:
            if 'DEV' in os.environ: sid += '-dev'

            # to stop Coursera's strip() from doing anything, we surround in parens
            results  = output(part_tests, test_vars)
            prog_out = '(%s)' % ''.join(map(str.rstrip, results))
            src      = source(source_files, sid)

            if verbose:
                res_itr = iter(results)
                for t in part_tests.split('\n'):
                    print(t)
                    if t[:3] == '>>>':
                       print(next(res_itr), end='')

            if show_submission:
                print('Submission:\n%s\n' % prog_out)

            rcptname = os.path.join(RECEIPT_DIR, '%s.receipt'%sid)
            exists = os.path.exists(rcptname)
            if exists and overwrite_policy == 'skip':
                print('Receipt already exists: %s' % rcptname)
            else:
                    feedback = submit_solution(asgn_name, login, sid, prog_out, src)
                    if feedback:
                        if show_feedback:
                            print(feedback)
                        result = get_result(feedback)
                        if result == '1':
                            print('Correct answer verified for %s' % name)
                            save_receipt(rcptname, feedback, exists)
                        elif result == '0':
                            print('Incorrect answer for %s' % name)
                        elif result is None:
                            print('Could not parse autograder response')
                        else:
                            print('Submission error: %s' % result)
                    else:
                        print('No response from autograder')
            print()

def check_rcptdir():
    global rcptdir_ok
    if receipts:
        if os.path.isdir(RECEIPT_DIR):
            rcptdir_ok = True
        else:
            print('Directory "%s" must exist to save receipts.' % RECEIPT_DIR)
            if confirm('Create receipts directory?'):
                os.mkdir(RECEIPT_DIR)
                rcptdir_ok = True
            else:
                print('Receipts directory not created')
                print('Create receipts directory and resubmit to save receipts.')
                rcptdir_ok = False

def check_overwrite_policy(parts):
    global overwrite_policy
    if receipts and rcptdir_ok and overwrite_policy is None:
        if any(os.path.exists(os.path.join(RECEIPT_DIR, '%s.receipt'%sid)) for sid,_,_ in parts):
            overwrite_policy = 'yes' if confirm('Overwrite existing receipts?') else 'no'
        else:
            overwrite_policy = 'no'

def confirm(prompt='Confirm?'):
    if sys.stdin.isatty():
        for i in range(3):
            response =  input(prompt+' (y/n): ').lower()
            if response == 'y':
                return True
            elif response == 'n' :
                return False
            else:
                print('Invalid response')
    return False

def login_prompt():
    return input('username: ')

def parts_prompt(problems):
    print('This assignment has the following parts:')
    # change to list all the possible parts?
    for i, (name, parts) in enumerate(problems):
        if parts:
            print('  %d) %s' % (i+1, name))
        else:
            print('  %d) [NOT AUTOGRADED] %s' % (i+1, name))

    return input('\nWhich parts do you want to submit? (Ex: 1, 4-7): ')

def parse_range(s, problems):
    try:
        s = s.split('-')
        if len(s) == 1:
            index = int(s[0])
            if(index == 0):
                return list(range(1, len(problems)+1))
            else:
                return [int(s[0])]
        elif len(s) == 2:
            return list(range(int(s[0], 0, ), 1+int(s[1])))
    except:
        pass
    return []  # Invalid value

def parse_parts(string, problems):
    pr = lambda s: parse_range(s, problems)
    parts = map(pr, string.split(','))
    flat_parts = sum(parts, [])
    return sum((problems[i-1][1] for i in flat_parts if 0<i<=len(problems)), [])

def submit_solution(asgn_name, login, sid, output, source):
    b64ize = lambda s: str(base64.encodebytes(s.encode('utf-8')), 'ascii')
    values = { 'assignment_part_sid' : sid
             , 'email_address'       : login
             , 'submission'          : b64ize(output)
             , 'submit_version'      : SUBMIT_VERSION
             , 'module_name'         : asgn_name
             , 'report'              : report
             , 'location'            : location
             }

    submit_url = '%s://%s/submit' % (protocol, grader_url)
    data     = urllib.parse.urlencode(values).encode('utf-8')
    req      = urllib.request.Request(submit_url, data)
    with urllib.request.urlopen(req) as response:
        return response.readall().decode('utf-8')

def save_receipt(rcptname, feedback, exists):
    if receipts and rcptdir_ok:
        print('Saving receipt')
        if exists and overwrite_policy == 'no':
            print('Receipt already exists: %s' % rcptname)
        else:
            with open(rcptname,'w') as rcptfile:
                rcptfile.write(feedback)
            if exists:
                print('Receipt overwritten: %s' % rcptname)
            else:
                print('Receipt saved: %s' % rcptname)
    else:
        print('Receipt not saved')

def import_module(module):
    mpath, mname = os.path.split(module)
    mname = os.path.splitext(mname)[0]
    return imp.load_module(mname, *imp.find_module(mname, [mpath]))

# Check solution using local file
def check_solution(sub, sid, module):
    solution =  import_module(module)
    regex = solution.solutions_dict[sid]
    return int(bool(re.match(regex, sub)))

def source(source_files, sid):
    src = ['# submit version: %s\n' % SUBMIT_VERSION]
    for fn in source_files:
        src.append('# %s' % fn)
        with open(fn) as source_f:
            src.append(source_f.read())
        src.append('')
    return '\n'.join(src)

def strip(s): return s.strip() if isinstance(s, str) else s

if __name__ == '__main__':
    with open("../profile.txt") as f:
        try:
            profile = dict([line.split(maxsplit=1) for line in f])
        except IOError:
            profile = {}
    import argparse
    parser = argparse.ArgumentParser()
    helps = [ 'assignment name'
            , 'numbers or ranges of problems/tasks to submit'
            , 'your username'
            , 'your geographical location (optional, used for mapping activity)'
            , 'display tests without actually running them'
            , 'specify a URL to which to send the results'
            , 'overwrite existing receipts'
            , 'do not overwrite existing receipts'
            , 'skip problems with existing receipts'
            , 'do not create receipts'
            , 'use an encrypted connection to the grading server'
            , 'use an unencrypted connection to the grading server'
            ]
    ihelp = iter(helps)
    parser.add_argument('assign', help=next(ihelp))
    parser.add_argument('tasks', default=profile.get('TASKS',None), nargs='*', help=next(ihelp))
    parser.add_argument('--username', '--login', default=profile.get('USERNAME',None), help=next(ihelp))
    parser.add_argument('--location', default=profile.get('LOCATION',None), help=next(ihelp))
    parser.add_argument('--dry-run', default=False, action='store_true', help=next(ihelp))
    parser.add_argument('--report', default=profile.get('REPORT',None), help=next(ihelp))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--overwrite', dest="overwrite", const="yes", action='store_const', help=next(ihelp))
    group.add_argument('--no-overwrite', dest="overwrite", const="no", action='store_const', help=next(ihelp))
    group.add_argument('--skip-existing', dest="overwrite", const="skip", action='store_const', help=next(ihelp))

    group.add_argument('--no-receipts', action='store_true', help=next(ihelp))

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--https', dest="protocol", const="https", action="store_const", help=next(ihelp))
    group.add_argument('--http', dest="protocol", const="http", action="store_const", help=next(ihelp))

    parser.add_argument('--verbose', default=False, action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--show-submission', default=False, action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--show-feedback', default=False, action='store_true', help=argparse.SUPPRESS)

    args = parser.parse_args()
    global asgn_name
    asgn_name = os.path.splitext(args.assign)[0]
    global report
    report = args.report
    global location
    location = args.location
    dry_run = args.dry_run
    overwrite_policy = args.overwrite if args.overwrite else strip(profile.get('OVERWRITE',None))
    receipts = not args.no_receipts
    if args.protocol: protocol = args.protocol
    verbose = args.verbose
    show_submission = args.show_submission
    show_feedback = args.show_feedback
    submit(asgn_name, ','.join(args.tasks), args.username)

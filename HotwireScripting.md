# The current (0.620) Hotwire language #

Hotwire's current language is based arounds pipes (`|`).  It is extremely limited and **will be overhauled** in a future release.

Currently there is no support for many shell language features such as:

  * loops
  * conditionals
  * subcommands
  * variables

However, currently on Unix Hotwire will pass data given to the **sh** builtin via `sh -c`.  This means that things like the following work:

```
sh for x in $(seq 100); sleep 0.1; echo $x; done
```

# Creating a Hotwire-based language designed for system scripts #

One major item of feedback from a Hotwire presentation at FOSSCamp 2007 was that we should try to create a language.  It was felt that system scripting in Python at least in its current form wasn't ideal.

The goals of Hotwire's language should be are:

  * Be somewhat familiar for people coming from the Unix shell
  * Be concise for simple tasks
  * Be useful for embedding into Python programs

## HotwireScript Proposal ##

### Extending Hotwire Pipe ###

First, we extend the current pipe language to support three specific new features: I/O redirection, environment variables, and sequences.

```
ls | filter foo > /tmp/foofiles.txt
```

```
sleep 5; proc -a > /tmp/procs.txt ; killall foo 
```

```
JAVA_HOME=/usr/lib/java1.5 java --blah
```

These three things cover quite a bit of functionality, and would not be very difficult to implement.

### Hotwire Python ###

Second, we add an API to Python to make it trivial to execute Hotwire command language.

```
# Trivial system command invocation
for line in script("dmesg"):
  print line

# Invoking builtins (this is not /bin/ls):
pl = script(script.ls, '*.py', cwd="~/tmp")

# ERROR - no metacharacters allowed in string form
# by default
pl = script("ls *.py", cwd="~/tmp") 

# OK, Equivalent to first
pl = script("ls *.py", sh=True, cwd="~/tmp")

# File output redirection
pl = script(script.proc, '-a', script.filter, '-i', 'walters',
                  open('/tmp/procout.txt', 'w'))
pl = script("proc -a | filter -i walters cmd > /tmp/procout.txt")

# File input redirection
for line in script("filter python", open('/tmp/procout')):
  print line

# Async jobs - uses threads/subprocesses under the hood
job = script("ls /var/tmp/*.out", sh=True, async=True)
print job.is_done()
job.wait()

# Thread-local working directory for a block
with script.chdir("/var/tmp"):
  script("rm *.txt", sh=True)
  script("mkdir blah")

# Multiple commands - Hotwire needs to support this
script("mkdir foo; cd foo")

## Sample conversion of http://liquidat.wordpress.com/2007/12/03/short-tip-convert-ogg-file-to-mp3/
for f in glob("*.ogg"):
  script("oggdec -o %s", f, script.pipe,
             "lame -h -V 4 --vbr-new - %s", f.replace('.ogg', '.mp3'))
```

### Proposal from Alexander Larsson ###

Here are some examples from Alexander Larsson about what a Hotwire language could do:

```
 There is a set of basic types with things like filename, process, user
 These come in two forms, "references" and "info about" where the later is a "subclass" of the other (i.e. can be used in place of)
 operators:
 | - pipe 
 \ - grep
 () - sub command
 * - "dereference"
 (ie. turn ref object into info
```

Examples:

```
kill (procs \ user = alex cpu_use > 0.5)
* /tmp
```
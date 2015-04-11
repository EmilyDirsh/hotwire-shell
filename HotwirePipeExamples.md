# Sample Hotwire commands #

```
walk /home/me/Media | py-filter 'it.size > 10**7'
```
Find all files in `/home/me/Media` bigger than 10 megabytes.

```
svn diff
|filter -i frob
```
Generate a diff, then find all lines matching "frob" in it.

```
proc | filter frob cmd | kill
```
Kill all processes (owned by you) with `frob` in their name.  Note that **kill** is smart enough to take **Process** objects on its input.

```
walk /home/me/tmp | filter '\.zip$' basename | prop path | apply rm
```
Recursively find all zip files in `/home/me/tmp`, and move them to the trash.  Because **rm** doesn't currently take File objects as input, we convert them to paths, then use the **apply** builtin which is similar to Unix `xargs`.

```
cat /home/me/foo.txt | filter -i bar > /home/me/foo-bars.txt
```
Save all lines matching `bar` in `/home/me/foo.txt` to a new file `/home/me/foo-bars.txt`.

```
sh for x in *; do (cd ${x} && svn up); done
```
We can run traditional Unix shell script by prefixing the command with "sh ".

```
py import urllib; urllib.urlopen('http://google.com').read()
| write /tmp/google.html
```
And Python is just a "py " away.  We then save the result to a file.
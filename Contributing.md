# Submitting a patch #

  * First, be sure you've looked at the CodingStyle guidelines.
  * Make changes in a Subversion (or `git-svn`) checkout
  * Run the test suite, using `python ui/test-hotwire` (if this fails, you broke something =) )
  * Use "svn diff" to generate a diff (or `git-svn diff`)
  * Create a new issue in the [Issue Tracker](http://code.google.com/p/hotwire-shell/issues/list)
  * Wait for review from one of the current committers, make any changes necessary for review
  * Once complete, a committer will add your patch to Subversion

# Committer process #

If you're a committer on the project, welcome!  Largely, the guidelines for committers are
similar to external patches.  This means we would like major changes to be submitted through
the issue tracker so they can be peer-reviewed before commit.

If your patch is "trivial", then you should feel free to commit it
without review.  Changes which modify under 5-10 lines can be trivial, but are not always.  It
depends on the area of the code.  Use your best judgement.  For example, adding a docstring
never requires review, but adding even a trivial method to a platform interface like
`BaseFilesystem` always does.

Platform maintainers can commit to the implementation files for their platform in `sysdep` without review.

## Commit details ##

Commit logs messages should have a first line with an issue number, and very short summary (try to stay < 80 characters).  If you're committing someone else's patch, use the form (John Doe) to say who submitted the patch.

In the details, try to describe **why** you changed something, not restate **what** changed (because that can be seen in the diff).  If the reason for the change is obvious, you don't need to explain why.  For example, you don't need to mention adding a docstring.

### Example (multiple people worked on patch) ###

```
Issue 131: Add hidden file concept (Zeng.Shixin,cgwalters)
    
Reduce duplicate code between FSearchBuiltin and WalkBuiltin.
    
Need "cwd" property to HotwireContext so we can use it more directly in execute().
```

### Example 2 (your own patch) ###

```
Issue 124: Avoid checking status of a closed fd
```
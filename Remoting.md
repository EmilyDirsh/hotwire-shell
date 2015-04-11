A very early version of Hotwire supported using the [paramiko](http://www.lag.net/paramiko/) library and XML-RPC serialization to run pipelines remotely.

# Remoting architecture #

Generally, the problem is that of separate execution domains, whether those are just different user identities on one machine, or an account on another machine.  What we want is for Hotwire to cleanly support executing code and gathering data from another domain, but displaying the UI locally.  This as opposed to running an entire Hotwire UI remotely, which would have latency issues.

Hotwire is already designed around asynchrnous execution.  To implement remoting, we can take the approach of essentially wrapping the ends of a pipeline with a custom protocol.

## Protocol ##

We cannot transmit actual object instances across execution domains.  Now, there is a great amount of prior art in remoting, such as CORBA, RMI, XML-RPC, etc.  These all have different tradeoffs.  What we will do is take a loosely-coupled message passing approach, similar to D-BUS.

Our needs are to support an API where we can execute a pipeline string, and conceptually return a stream of objects, as well as invocation of methods on the context object, like metadata.  Essentially, this should be a remoted version of the current **Pipeline** API.

Potential slave interface:

```

Slave {
  int RunPipeline(string text);

  signal PipelineResult(int pipeline, string classname, json result);
  signal PipelineObjects(int pipeline, string classname, array[json]);
  signal PipelineException(int pipeline, string traceback);
}
```

You'll notice here that we're defining a type "json".  What we mean by this is that the returned object types can be any of those defined by [JSON](http://json.org) - e.g. integers, strings, objects.  To be concrete, let's say that we have a shell connected via SSH to example.com.  We invoke:

```
proc -a | filter -i foo cmd
```

We send that literal string over to the remote machine, which executes it.  It returns a result that looks like this:

```
('hotwire.sysdep.proc.Process', [{'pid': 42, 
                                  'cmd': 'foo-server', 
                                  'owner_id': 500,
                                  'owner_name': 'someuser'},
                                 {'pid': 671,
                                  'cmd': 'frobfoo --blah',
                                  'owner_id': 0,
                                  'owner_name', 'root'}
                                 ])
```

Then we can key off the first, and display the process list as normal.

## Open Questions ##

Currently in Hotwire, the renderer owns the object.  So when the user presses `Ctrl-Shift-K`, the object goes away.  But in this model, we'd need to make that a remote method invocation.  Other possible models are that the server owns the object lifecycle.

## Related software ##

This list is almost too large to mention.  Some things we might investigate reusing code from:

  * [IPython's Parallel Core](http://ipython.scipy.org/moin/Parallel_Computing)
  * [func](https://hosted.fedoraproject.org/func/)
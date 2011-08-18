# ESI: Elastic Search Investigation

## Why?

Sick of messing with curl and reading through the output to figure out
what's what with elastic search.

## Usage

    Usage: esi.py [options]

    Options:
      -h, --help            show this help message and exit
      -H HOST, --host=HOST  Host running elasticsearch
      -p PORT, --port=PORT  Port running elasticsearch
      --nodes               Get summary of nodes JSON
      --shard-distribution  Get shard distribution JSON
      --replica-distribution
                            Get replica distribution JSON
      --cluster-state       Get cluster state JSON
      --cluster-health      Get cluster health JSON
      --node-stats          Get node stats JSON
      --shards              Get shards JSON
      --indices             Get indices JSON
      --aliases             Get aliases JSON
      -v, --verbose         Enable verbose output

## Examples

### Which node is which?!

Nodes have IDs (eg, Su4FER3NTNqwB0W5ywjDRw), but they write log
messages using odd names (eg, [Whitman, Debra]).  What they do
not have is hostnames!

NB: there's a good reason for that, you can have more than one
node per server, but it does make investigating stuff very hard.
It would be ideal if nodes were identified by a combination of
hostname and PID...

In the meantime, this makes it a bit easier to get a quick summary
of nodes:

    $ ./esi.py --nodes
    {u'Su4FER3NTNqwB0W5ywjDRw': {u'attributes': {},
                                 u'name': u'Whitman, Debra',
                                 u'transport_address': u'inet[/10.110.246.163:9300]'},
     u'bvmvdyVLRHK4mYQThHP7iQ': {u'attributes': {},
                                 u'name': u'Steel Serpent',
                                 u'transport_address': u'inet[/10.32.255.68:9300]'}}

#!/usr/bin/env python


import sys
import os
import urllib
import json
from optparse import OptionParser
from pprint import pprint


class ElasticSearchClient:
    def __init__(self, host, port, verbose=False):
        self.host = host
        self.port = port
        self.verbose = verbose
        self.__cache = {}

    def get(self, path):
        url = "http://%s:%s/%s" % (self.host, self.port, path)
        if self.verbose:
            sys.stderr.write("Fetching %s...\n" % url)
        result = urllib.urlopen(url)
        return json.load(result)

    @property
    def cluster_health(self):
        if not self.__cache.has_key("cluster_health"):
            self.__cache["cluster_health"] = self.get("_cluster/health")
        return self.__cache["cluster_health"]

    @property
    def cluster_state(self):
        if not self.__cache.has_key("cluster_state"):
            self.__cache["cluster_state"] = self.get("_cluster/state")
        return self.__cache["cluster_state"]

    @property
    def node_stats(self):
        if not self.__cache.has_key("node_stats"):
            self.__cache["node_stats"] = self.get("nodes/stats")
        return self.__cache["node_stats"]

    @property
    def nodes(self):
        if not self.__cache.has_key("nodes"):
            self.__cache["nodes"] = self.cluster_state["nodes"]
        return self.__cache["nodes"]

    @property
    def aliases(self):
        if not self.__cache.has_key("aliases"):
            aliases = {}
            for index_name, index_detail in self.indices.items():
                for alias_name in index_detail["aliases"]:
                    if not aliases.has_key(alias_name):
                        aliases[alias_name] = []
                    aliases[alias_name].append(index_name)
            self.__cache["aliases"] = aliases
        return self.__cache["aliases"]

    @property
    def indices(self):
        if not self.__cache.has_key("indices"):
            metadata = self.cluster_state["metadata"]
            self.__cache["indices"] = metadata["indices"]
        return self.__cache["indices"]

    @property
    def shards(self):
        if not self.__cache.has_key("shards"):
            indices = self.cluster_state["routing_table"]["indices"]
            for index, shards in indices.items():
                # Each shard consists of primaries and replicas, pull
                # them all together into one list called all_shards
                for shard_primary_replica_map in shards.values():
                    all_shards = []
                    map(all_shards.extend, shard_primary_replica_map.values())
            self.__cache["shards"] = all_shards
        return self.__cache["shards"]

    @property
    def shard_distribution(self):
        if not self.__cache.has_key("shard_distribution"):
            distribution = {}
            for shard in self.shards:
                node = shard["node"]
                primary = shard["primary"]
                if not distribution.has_key(node):
                    distribution[node] = {
                        "total" : 0,
                        "primary" : 0,
                        "replica" : 0,
                    }
                shard_type = "primary" if shard["primary"] else "replica"
                distribution[node][shard_type] += 1
                distribution[node]["total"] += 1
            self.__cache["shard_distribution"] = distribution
        return self.__cache["shard_distribution"]

    @property
    def replica_distribution(self):
        if not self.__cache.has_key("replica_distribution"):
            self.__cache["replica_distribution"] = {}
        return self.__cache["replica_distribution"]

    def refresh(self):
        if self.verbose:
            sys.stderr.write("Clearing cache...\n")
        self.__cache = {}


def main():
    parser = OptionParser()
    parser.add_option("-H", "--host",
        help="Host running elasticsearch",
        default="localhost")
    parser.add_option("-p", "--port",
        help="Port running elasticsearch",
        default=9200, type="int")
    parser.add_option("--nodes",
        help="Get summary of nodes JSON",
        default=False, action="store_true")
    parser.add_option("--shard-distribution",
        help="Get shard distribution JSON",
        default=False, action="store_true")
    parser.add_option("--replica-distribution",
        help="Get replica distribution JSON",
        default=False, action="store_true")
    parser.add_option("--cluster-state",
        help="Get cluster state JSON",
        default=False, action="store_true")
    parser.add_option("--cluster-health",
        help="Get cluster health JSON",
        default=False, action="store_true")
    parser.add_option("--node-stats",
        help="Get node stats JSON",
        default=False, action="store_true")
    parser.add_option("--shards",
        help="Get shards JSON",
        default=False, action="store_true")
    parser.add_option("--indices",
        help="Get indices JSON",
        default=False, action="store_true")
    parser.add_option("--aliases",
        help="Get aliases JSON",
        default=False, action="store_true")
    parser.add_option("-v", "--verbose",
        help="Enable verbose output",
        default=False, action="store_true")
    opts, args = parser.parse_args()
    
    es_client = ElasticSearchClient(opts.host, opts.port, opts.verbose)
    if opts.nodes:
        pprint(es_client.nodes)
    if opts.cluster_health:
        pprint(es_client.cluster_health)
    if opts.node_stats:
        pprint(es_client.node_stats)
    if opts.cluster_state:
        pprint(es_client.cluster_state)
    if opts.shard_distribution:
        pprint(es_client.shard_distribution)
    if opts.replica_distribution:
        pprint(es_client.replica_distribution)
    if opts.shards:
        pprint(es_client.shards)
    if opts.indices:
        pprint(es_client.indices)
    if opts.aliases:
        pprint(es_client.aliases)


if __name__ == "__main__":
    main()

# vim: autoindent tabstop=4 expandtab shiftwidth=4 softtabstop=4

# vi: ts=4 expandtab
#
# Author : penguinRaider<shailrishabh@gmail.com>


import errno
import os

from cloudinit import log as logging
from cloudinit import sources
from cloudinit import util

LOG = logging.getLogger(__name__)


class DataSourceMyCloud(sources.DataSource):
    def __init__(self, sys_cfg, distro, paths):
        sources.DataSource.__init__(self, sys_cfg, distro, paths)
        self.seed = None
        self.cmdline_id = "ds=nocloud"
        self.metadata={}
        self.supported_seed_starts = ("/", "file://")


    def get_key_value(self,line):
        print line
        key_value = line.split("=")
        key_value[1] = key_value[1].split(',')
        return (key_value[0], key_value[1])
                    






    def get_instance_id(self):
        if not self.metadata:
            return None
        return self.metadata.get('instance-id')

    @property
    def launch_index(self):
        if not self.metadata:
            return None
        if 'launch-index' in self.metadata:
            return self.metadata['launch-index']
        return None

    def get_data(self):
        mydata = {'meta-data': {}}


        try:
            f_read = open("/tmp/cernVMseed").read().split("\n")
        except:
            LOG.debug("Unable to find CernVM file")
            return False

        if (len(f_read) < 1):
            return False
        try:
            # Check if f_read[0][0] = "[cernvm]"
            check_first = f_read[0]
            if f_read[0] != "[cernvm]" :
                return False
                LOG.debug("first line not correct")
        except IndexError:
            LOG.debug("seed file not in correct format")
        del f_read[0]
        common_index = 0
        try:
            for line in f_read:
                common_index+=1
                if line[0] == '#':
                    continue
                elif line == "[common]":
                    break
                else:
                    (key, value) = self.get_key_value(line)
                    mydata['meta-data'][key] = value
                    LOG.debug("Using seeded data from /tmp/cernVMseed")
        except ValueError as e:
            pass
        try:
            for line in f_read[common_index:-1] :
                if line[0] == '#':
                    continue
            else:
                (key, value) = self.get_key_value(line)
                mydata['meta-data'][key] = value
                
        except :
            pass  


        try :
            self.metadata.update(mydata['meta-data'])
            return True
        except :
            pass


        LOG.debug("%s: not claiming datasource, dsmode=%s", self, md['dsmode'])
        return False




    

class DataSourceMyCloudNet(DataSourceMyCloud):
    def __init__(self, sys_cfg, distro, paths):
        DataSourceMyCloud.__init__(self, sys_cfg, distro, paths)
        self.cmdline_id = "ds=nocloud-net"
        self.supported_seed_starts = ("http://", "https://", "ftp://")
        self.seed_dir = os.path.join(paths.seed_dir, 'nocloud-net')
        self.dsmode = "net"


# Used to match classes to dependencies
datasources = [
  (DataSourceMyCloud, (sources.DEP_FILESYSTEM, )),
  (DataSourceMyCloudNet, (sources.DEP_FILESYSTEM, sources.DEP_NETWORK)),
]


# Return a list of data sources that match this set of dependencies
def get_datasource_list(depends):
    return sources.list_from_depends(depends, datasources)

# Copyright 2018 ETH Zurich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pathlib
import random
import string
from collections import namedtuple
from scionlab.models.core import ISD, AS, Link, Host, Service
from scionlab.models.user_as import AttachmentPoint
from scionlab.models.user import User
from scionlab.models.vpn import VPN

# Create records for all the test objects to create, so that they can be
# inspected during tests as ground truth.
ISDdef = namedtuple('ISDdef', ['isd_id', 'label'])
ASdef = namedtuple('ASdef', ['isd_id', 'as_id', 'label', 'public_ip', 'is_core', 'is_ap'])
LinkDef = namedtuple('LinkDef', ['type', 'as_id_a', 'as_id_b'])
VPNDef = namedtuple('VPNDef', ['as_id', 'vpn_ip', 'vpn_port', 'subnet'])


def _expand_as_id(as_id_tail):
    """ Helper to avoid repeating the ffaa:0:-part of the ASes a gazillion times."""
    return 'ffaa:0:%x' % as_id_tail


def makeASdef(isd_id, as_id_tail, label, public_ip, is_core=False, is_ap=False):
    """ Helper for readable ASdef  declaration """
    return ASdef(isd_id, _expand_as_id(as_id_tail), label, public_ip, is_core, is_ap)


def makeLinkDef(type, as_id_tail_a, as_id_tail_b):
    return LinkDef(type, _expand_as_id(as_id_tail_a), _expand_as_id(as_id_tail_b))


# ISDs
isds = [
    ISDdef(16, 'Tsinghua'),
]

# ASes
ases = [
    makeASdef(16, 0x1101, 'vm-1', '240a:a066:100:1::11', is_core=True, is_ap=True),
    makeASdef(16, 0x1102, 'vm-2', '240a:a066:100:1::12', is_core=False, is_ap=False),
    makeASdef(16, 0x1103, 'vm-3', '240a:a066:100:1::13', is_core=False, is_ap=False),
]

# Links
links = [
    makeLinkDef(Link.PROVIDER, 0x1101, 0x1102),
    makeLinkDef(Link.PROVIDER, 0x1101, 0x1103),
]


# other than default services
extra_services = [
    (_expand_as_id(0x1101), Service.SIG),
]

# VPNs for APs, except 1303
vpns = [
]


def create_testtopo():
    create_isds()
    create_ases()
    create_links()
    create_vpn()
    create_extraservices()
    name_hosts()


def create_isds():
    for isd_def in isds:
        ISD.objects.create(**isd_def._asdict())


def create_ases():
    for as_def in ases:
        _create_as(**as_def._asdict())

    # Initialise TRCs and certificates. Deferred in AS creation to start with TRC/cert versions 1.
    for isd in ISD.objects.iterator():
        isd.update_trc_and_certificates()


def create_links():
    for link_def in links:
        _create_as_link(**link_def._asdict())


def create_vpn():
    for vpn_def in vpns:
        _create_vpn(**vpn_def._asdict())


def create_extraservices():
    for as_serv in extra_services:
        host = Host.objects.get(AS__as_id=as_serv[0])
        Service.objects.create(host=host, type=as_serv[1])


def name_hosts():
    # assign random hostnames, loosely following the scionlab host naming convention
    hosts = Host.objects.filter(AS__owner=None)
    words = pathlib.Path('/usr/share/dict/words').read_text().split('\n')
    words = [w for w in words if all(c in string.ascii_lowercase for c in w)]
    names = random.sample(words, len(hosts))
    for host, name in zip(hosts, names):
        as_short_id = host.AS.as_id.split(':')[-1]
        host.label = 'scionlab-%s-%s' % (as_short_id, name)
        host.save()


def _create_as(isd_id, as_id, label, public_ip, is_core=False, is_ap=False):
    isd = ISD.objects.get(isd_id=isd_id)
    as_ = AS.objects.create_with_default_services(
        isd=isd,
        as_id=as_id,
        label=label,
        is_core=is_core,
        public_ip=public_ip,
        init_certificates=False  # Defer certificates generation
    )

    if is_ap:
        AttachmentPoint.objects.create(AS=as_)


def _create_as_link(type, as_id_a, as_id_b):
    as_a = AS.objects.get(as_id=as_id_a)
    as_b = AS.objects.get(as_id=as_id_b)
    Link.objects.create_from_ases(type, as_a, as_b)


def _create_vpn(as_id, vpn_ip, vpn_port, subnet):
    as_ = AS.objects.get(as_id=as_id)
    server = as_.hosts.get()
    vpn = VPN.objects.create(server=server,
                             server_vpn_ip=vpn_ip, server_port=vpn_port, subnet=subnet)
    # Add vpn to AP
    ap = as_.attachment_point_info
    ap.vpn = vpn
    ap.save()

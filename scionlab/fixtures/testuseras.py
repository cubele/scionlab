# Copyright 2019 ETH Zurich
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

from scionlab.fixtures.testuser import get_testuser_admin, get_testuser_exbert
from scionlab.models.user_as import AttachmentPoint, AttachmentConf, UserAS


def create_testuserases():
    exbert = get_testuser_exbert()
    aps = AttachmentPoint.objects.all()
    # _create_user_as(exbert, aps[0], UserAS.VM, False, 'vm-2', '240a:a066:100:1::12')
    # _create_user_as(exbert, aps[0], UserAS.SRC, False, 'vm-3', '240a:a066:100:1::13')


def _create_user_as(owner, attachment_point, installation_type, use_vpn, label, public_ip):
    user_as = UserAS.objects.create(
        owner=owner,
        installation_type=installation_type,
        label=label,
        isd=attachment_point.AS.isd
    )
    user_as.update_attachments([
        AttachmentConf(
            attachment_point=attachment_point,
            use_vpn=use_vpn,
            public_ip=public_ip,
            public_port=54321
        ),
    ])

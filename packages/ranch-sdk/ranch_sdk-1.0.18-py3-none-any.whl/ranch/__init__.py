"""Rest API for ranchcomputing in Python."""

# Copyright 2023 ranchcomputing
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from .__version__ import (
    __author__,
    __author_email__,
    __build__,
    __copyright__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
)

from .exceptions import (
    RanchException,
    InvalidKeyException,
    EmptySafeException,
)


def _get_url(key, **kwargs):
    """Get and format the url for the given key."""
    urls = {
        "jobs": "/jobs/",  # POST -> Submit Job
    }
    return urls[key].format(**kwargs)

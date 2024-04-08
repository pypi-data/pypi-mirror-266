# Copyright 2018, 2019, 2020 Andrzej Cichocki

# This file is part of lagoon.
#
# lagoon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lagoon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lagoon.  If not, see <http://www.gnu.org/licenses/>.

from contextlib import contextmanager
from lagoon.util import mapcm
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import tarfile

class ContextStream:

    @classmethod
    @contextmanager
    def open(cls, dockerstdin):
        with tarfile.open(mode = 'w:gz', fileobj = dockerstdin) as tar:
            yield cls(tar)

    def __init__(self, tar):
        self.tar = tar

    def put(self, name, path):
        self.tar.add(path, name)

    def putstream(self, name, stream):
        self.tar.addfile(self.tar.gettarinfo(arcname = name, fileobj = stream), stream)

    def mkdir(self, name):
        with TemporaryDirectory() as empty:
            self.put(name, empty)

@contextmanager
def iidfile():
    with mapcm(Path, TemporaryDirectory()) as tempdir:
        path = tempdir / 'iid'
        yield SimpleNamespace(args = ('--iidfile', path), read = path.read_text)

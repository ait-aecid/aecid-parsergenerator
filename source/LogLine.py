"""This class holds relevant attributes of a single log line.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

class LogLine:
    """This class describes log lines"""
    def __init__(self, line_id, time_stamp, line_text, words):
        self.line_id = line_id
        self.time_stamp = time_stamp
        self.line_text = line_text
        self.words = words
        self.cluster = ''

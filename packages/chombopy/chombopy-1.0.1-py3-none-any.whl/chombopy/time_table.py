import os
import re
import logging

LOGGER = logging.getLogger(__name__)


class TimeTableMethod:
    """
    Representation of a method in a time.table file
    """

    def __init__(self, string_to_parse, parent_el=None):
        parts = re.findall(
            r"(\s*)\[(\d+)]\s([^\s]*)\s([\d.]+)\s+[\d.]+%\s", string_to_parse
        )

        self.parent = parent_el
        self.valid = False

        if parts:
            match = parts[0]
            self.indent = len(match[0])
            self.id = int(match[1])
            self.name = match[2].strip()
            self.time = float(match[3])
            self.valid = True

    def __repr__(self):
        return self.name

    def long_desc(self):
        """
        Longer description of this object

        Returns
        -------
        long_desc : str
            A longer description of this object
        """
        return "[%d] %s (%s)" % (self.id, self.name, self.time)


class TimeTable:
    """
    Representation of a time.table file
    """

    def __init__(self, file_path):
        self.filepath = file_path

        self.methods = []

        self.parse_file()

    def parse_file(self):
        """
        Parse the time.table file into this Python object
        """
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:

                file_contents = f.read()

                # Find the second [0] tag
                parts = file_contents.split("[0]")
                second_half = parts[2]
                lines = second_half.split("\n")

                main_method = TimeTableMethod("[0]" + lines[0])
                current_parent = main_method

                prev_method = main_method

                for line in lines[1:]:
                    method = TimeTableMethod(line)

                    if not method.valid:
                        continue

                    # If this method is more indented, change parent
                    if method.indent > prev_method.indent:
                        current_parent = prev_method

                    # If this method is less indented, parent increases
                    if method.indent < prev_method.indent:
                        indent_change = prev_method.indent - method.indent
                        while (indent_change > 0) and current_parent.parent:
                            current_parent = current_parent.parent

                            # Indent changes by 3 per level
                            indent_change = indent_change - 3

                    method.parent = current_parent

                    self.methods.append(method)

                    prev_method = method

    def get_all_children(self, parent_method_name):
        """
        Get all child methods of the parent

        Parameters
        ----------
        parent_method_name : str
            Name of the parent method

        Returns
        -------
        parent_child_items: dict
            Individual parent occurences mapping to their children

        """
        parent_children_items = {}

        for m in self.methods:
            if m.parent and m.parent.name == parent_method_name:
                if m.parent not in list(parent_children_items.keys()):
                    parent_children_items[m.parent] = []

                parent_children_items[m.parent].append(m)

        return parent_children_items

    def total_time_in_method(self, a_method_name):
        """
        Get the total time spent in a method

        Parameters
        ----------
        a_method_name : str
            Method name

        Returns
        -------
        total_time : float
            Total time spent in the method

        """
        total_time = 0
        for m in self.methods:
            if m.name == a_method_name:
                total_time = total_time + m.time

        return total_time

    def get_call_history_for_id(self, method_id):
        """
        Get the call history for a particular method ID

        Parameters
        ----------
        method_id : int
            Method ID

        Returns
        -------
        call_history : list
            List of methods called in order down to the given method_id
        """
        call_history = []

        for m in self.methods:
            if m.id == method_id:
                call_history.append(m)

                p = m.parent
                call_history.append(p)
                while p.parent:
                    p = p.parent
                    call_history.append(p)

                call_history = call_history[::-1]
                break

        return call_history

    def get_call_history_for_name(self, a_method_name):
        """
        Get call history for a method

        Parameters
        ----------
        a_method_name : str
            Method name

        Returns
        -------
        call_history : list
            List of methods called in order down to the given method_id

        """
        call_history = []

        for m in self.methods:
            if m.name == a_method_name:
                call_history.append(self.get_call_history_for_id(m.id))

        return call_history

import os
import uuid
from pathlib import Path

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Pango

from . import helpers
from .data_helpers import find_data_path
from .image_formats import IMAGES_FORMATS
from .translation import format_string
from .translation import gettext as _


_PANGO_MARKUP_SUPPORTS_RELATIVE_SIZE = (
    Pango.VERSION_MAJOR >= 1 and Pango.VERSION_MINOR >= 49
)


THUMBNAIL_INPROGRESS = GdkPixbuf.Pixbuf.new_from_file(
    find_data_path("images/thumbnail_inprogress.svg")
)


class ImageStore(object):
    # fmt: off
    FIELDS = {
        "input_file":            {"id":  0, "type": str,              "default": ""},
        "output_file":           {"id":  1, "type": str,              "default": ""},
        "input_file_display":    {"id":  2, "type": str,              "default": ""},
        "output_file_display":   {"id":  3, "type": str,              "default": ""},
        "input_size":            {"id":  4, "type": int,              "default": 0},
        "output_size":           {"id":  5, "type": int,              "default": 0},
        "input_size_display":    {"id":  6, "type": str,              "default": ""},
        "output_size_display":   {"id":  7, "type": str,              "default": ""},
        "input_format":          {"id":  8, "type": str,              "default": ""},
        "output_format":         {"id":  9, "type": str,              "default": "jpeg"},
        "output_format_display": {"id": 10, "type": str,              "default": ""},
        "preview":               {"id": 11, "type": GdkPixbuf.Pixbuf, "default": THUMBNAIL_INPROGRESS},
        "status":                {"id": 12, "type": int,              "default": 0},
        "jpeg_quality":          {"id": 13, "type": int,              "default": 94},
        "webp_quality":          {"id": 14, "type": int,              "default": 90},
        "png_slow_optimization": {"id": 15, "type": bool,             "default": False},
        "image_width":           {"id": 16, "type": int,              "default": 0},
        "image_height":          {"id": 17, "type": int,              "default": 0},
        "resize_enabled":        {"id": 18, "type": bool,             "default": False},
        "resize_width":          {"id": 19, "type": int,              "default": 1},
        "resize_height":         {"id": 20, "type": int,              "default": 1},
        "output_pattern":        {"id": 21, "type": str,              "default": ""},
        "use_output_pattern":    {"id": 22, "type": bool,             "default": True},
        "optimization_success":  {"id": 23, "type": str,              "default": ""},
        "uuid":                  {"id": 24, "type": str,              "default": ""},
    }
    # fmt: on

    STATUS_NONE = 0
    STATUS_PENDING = 1
    STATUS_IN_PROGRESS = 2
    STATUS_DONE = 3
    STATUS_CANCELED = 4
    STATUS_ERROR = 5

    gtk_list_store = None

    def __init__(self):
        store_fields = sorted(self.FIELDS.values(), key=lambda v: v["id"])
        self.gtk_list_store = Gtk.ListStore(*[f["type"] for f in store_fields])

    @property
    def length(self):
        """The length of the store."""
        return len(self.gtk_list_store)

    def append(self, **kwargs):
        """Appends a row to the image store.

        :param **kwargs: The columns key/value of the row.

        :rtype: gtk.TreeIter
        :return: the iter of the inserted value.

        >>> image_store = ImageStore()
        >>> image_store.length
        0
        >>> image_store.append(
        ...     input_file="/tmp/foobar.png",
        ...     output_file="/tmp/foobar.opti.png",
        ... )
        <Gtk.TreeIter object ...>
        >>> image_store.length
        1
        >>> image_store.append(foo="bar")
        Traceback (most recent call last):
            ...
        KeyError: "Invalid field 'foo'"
        """
        for key in kwargs:
            if key not in self.FIELDS:
                raise KeyError("Invalid field '%s'" % key)

        row = [None] * len(self.FIELDS)

        for key in self.FIELDS:
            field_info = self.FIELDS[key]
            row[field_info["id"]] = field_info["default"]

        iter_ = self.gtk_list_store.append(row)
        self.update(iter_, uuid=str(uuid.uuid4()), **kwargs)
        return iter_

    def clear(self):
        """Clears the store.

        >>> image_store = ImageStore()
        >>> image_store.append()
        <Gtk.TreeIter object ...>
        >>> image_store.length
        1
        >>> image_store.clear()
        >>> image_store.length
        0
        """
        self.gtk_list_store.clear()

    def get(self, index):
        """Gets row data.

        :param int,gtk.TreeIter index: The index of the row.

        :rtype: dict
        :returns: The row data (e.g. ``{"field_name": "value"}``.

        >>> image_store = ImageStore()
        >>> image_store.append()
        <Gtk.TreeIter object ...>
        >>> image_store.get(0)
        {...}
        >>> image_store.get(1)
        Traceback (most recent call last):
            ...
        IndexError: ...
        """
        row = self.gtk_list_store[index]
        result = {}

        for field_name, field_info in self.FIELDS.items():
            result[field_name] = row[field_info["id"]]

        return result

    def get_all(self):
        """Get all rows of the store.

        :rtype: generator

        >>> image_store = ImageStore()
        >>> image_store.get_all()
        <generator object ImageStore.get_all at ...>
        """
        for i in range(self.length):
            yield self.get(i)

    def remove(self, iter_):
        """Removes a row at given gtk.TreeIter from the store.

        :param gtk.TreeIter index: The iter of the row.
        """
        self.gtk_list_store.remove(iter_)

    def remove_at_index(self, index):
        """Removes a row at given index from the store.

        :param int index: The index of the row.

        >>> image_store = ImageStore()
        >>> image_store.append()
        <Gtk.TreeIter object ...>
        >>> image_store.length
        1
        >>> image_store.remove_at_index(0)
        >>> image_store.length
        0
        >>> image_store.remove_at_index(0)
        Traceback (most recent call last):
            ...
        IndexError: ...
        """
        try:
            iter_ = self.gtk_list_store.get_iter(index)
        except ValueError as error:
            raise IndexError(error)
        self.remove(iter_)

    def update(self, index, **kwargs):
        """Updates a row.

        :param int,Gtk.TreeIter index: The index of the row.
        :param **kwargs: The columns key/value of the row.

        >>> image_store = ImageStore()
        >>> image_store.append(
        ...     output_format="png",
        ...     output_file="aaa.png",
        ...     use_output_pattern=False,
        ... )
        <Gtk.TreeIter object ...>
        >>> image_store.get(0)["output_file"]
        '...aaa.png'
        >>> image_store.update(0, output_file="bbb.png")
        >>> image_store.get(0)["output_file"]
        '...bbb.png'
        >>> image_store.update(0, foo="bar")
        Traceback (most recent call last):
            ...
        KeyError: "Invalid field 'foo'"
        >>> image_store.update(1, output_file="ccc.png")
        Traceback (most recent call last):
            ...
        IndexError: ...
        """
        _FORMATS_EXTS = {fid: fmt["exts"][0] for fid, fmt in IMAGES_FORMATS.items()}

        for key in kwargs:
            if key not in self.FIELDS:
                raise KeyError("Invalid field '%s'" % key)

        for key in kwargs:
            self._update_field(index, key, kwargs[key])

        if "input_file" in kwargs:
            path = Path(self.get(index)["input_file"])
            self._update_field(
                index,
                "input_file_display",
                path.name,
            )

        if (
            "output_format" in kwargs
            or "jpeg_quality" in kwargs
            or "webp_quality" in kwargs
            or "png_slow_optimization" in kwargs
            or "resize_enabled" in kwargs
            or "resize_width" in kwargs
            or "resize_height" in kwargs
        ):
            output_format = self.get(index)["output_format"]

            format_ = IMAGES_FORMATS[output_format]["display_name"]
            if output_format == "jpeg":
                format_ = "%s (%i %%)" % (
                    IMAGES_FORMATS["jpeg"]["display_name"],
                    self.get(index)["jpeg_quality"],
                )
            elif output_format == "webp":
                format_ = "%s (%i %%)" % (
                    IMAGES_FORMATS["webp"]["display_name"],
                    self.get(index)["webp_quality"],
                )
            elif output_format == "png":
                format_ = "%s%s" % (
                    IMAGES_FORMATS["png"]["display_name"],
                    (
                        (" (%s)" % "slow")
                        if self.get(index)["png_slow_optimization"]
                        else ""
                    ),
                )

            resize = ""
            if self.get(index)["resize_enabled"]:
                ratio = min(
                    self.get(index)["resize_width"] / self.get(index)["image_width"],
                    self.get(index)["resize_height"] / self.get(index)["image_height"],
                )
                if ratio < 1.0:
                    if _PANGO_MARKUP_SUPPORTS_RELATIVE_SIZE:
                        markup = (
                            '<span font_size="75%%" font_weight="400">↓ %i×%i px</span>'
                        )
                    else:
                        markup = '<span font_weight="400">↓ %i×%i px</span>'
                    resize = markup % (
                        self.get(index)["image_width"] * ratio,
                        self.get(index)["image_height"] * ratio,
                    )

            if resize:
                text = "%s\n%s" % (format_, resize)
            else:
                text = format_

            self._update_field(index, "output_format_display", text)

        if (
            "input_file" in kwargs
            or "output_file" in kwargs
            or "output_format" in kwargs
            or "output_pattern" in kwargs
            or "use_output_pattern" in kwargs
        ):
            output_pattern = self.get(index)["output_pattern"]
            output_format = self.get(index)["output_format"]
            output_ext = _FORMATS_EXTS[output_format]
            input_file = Path(self.get(index)["input_file"])
            filename_without_ext = str(input_file.name)[: -len(input_file.suffix)]
            if self.get(index)["use_output_pattern"]:
                # fmt: off
                output_file = input_file.parent / output_pattern \
                    .replace("{FILENAME}", filename_without_ext) \
                    .replace("{EXT}", output_ext[1:])
                # fmt: on
            else:
                # Simply swap extension on custom paths
                output_file = Path(self.get(index)["output_file"]).with_suffix(
                    output_ext
                )
            self._update_field(index, "output_file", str(output_file.resolve()))

        if "image_width" in kwargs:
            self._update_field(index, "resize_width", kwargs["image_width"])

        if "image_height" in kwargs:
            self._update_field(index, "resize_height", kwargs["image_height"])

        if (
            "output_file" in kwargs
            or "output_format" in kwargs
            or "output_pattern" in kwargs
            or "use_output_pattern" in kwargs
        ):
            output_file = Path(self.get(index)["output_file"])
            input_file = Path(self.get(index)["input_file"])
            relative_path = os.path.relpath(output_file, start=input_file.parent)

            self._update_field(
                index,
                "output_file_display",
                "→ %s" % relative_path,
            )

        if "input_size" in kwargs:
            self._update_field(
                index,
                "input_size_display",
                helpers.human_readable_file_size(self.get(index)["input_size"]),
            )

        if "output_size" in kwargs or "status" in kwargs:
            _STATUS = {
                0: "",
                1: "⏸️ <i>%s</i>" % _("Pending"),
                2: "🔄️ <i>%s</i>" % _("In progress"),
                3: "✅️ <i>%s</i>" % _("Done"),
                4: "⏹️ <i>%s</i>" % _("Canceled"),
                5: "❌️ <i>%s</i>" % _("Error"),
            }
            input_size = self.get(index)["input_size"]
            output_size = self.get(index)["output_size"]

            output_size_display = ""
            optimization_success = ""

            if output_size > 0:
                size_delta = -(100 - output_size / input_size * 100)
                if _PANGO_MARKUP_SUPPORTS_RELATIVE_SIZE:
                    markup = (
                        '%s\n<span font_size="75%%" font_weight="400">%s%s %%</span>'
                    )
                else:
                    markup = '%s\n<span font_weight="400">%s%s %%</span>'
                output_size_display = markup % (
                    helpers.human_readable_file_size(output_size),
                    "+" if output_size > input_size else "",
                    format_string("%.1f", size_delta),
                )
                optimization_success = "⚠️ " if input_size < output_size else ""
            else:
                output_size_display = _STATUS[self.get(index)["status"]]

            self._update_field(
                index,
                "output_size_display",
                output_size_display,
            )
            self._update_field(
                index,
                "optimization_success",
                optimization_success,
            )

    def reset_status(self, index):
        """Reset the status of the image at given index.

        :param int,Gtk.TreeIter index: The index of the row.

        >>> image_store = ImageStore()
        >>> image_store.append(
        ...     status=ImageStore.STATUS_DONE,
        ...     input_size=1024,
        ...     output_size=1024,
        ... )
        <Gtk.TreeIter object ...>
        >>> image_store.get(0)["status"]
        3
        >>> image_store.get(0)["output_size"]
        1024
        >>> image_store.get(0)["output_size_display"]
        '1...'
        >>> image_store.reset_status(0)
        >>> image_store.get(0)["status"]
        0
        >>> image_store.get(0)["output_size"]
        0
        >>> image_store.get(0)["output_size_display"]
        ''
        """
        self.update(
            index,
            status=ImageStore.STATUS_NONE,
            output_size=0,
        )

    def _update_field(self, index, field_name, value):
        row = self.gtk_list_store[index]
        row[self.FIELDS[field_name]["id"]] = value

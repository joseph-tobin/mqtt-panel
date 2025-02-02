import hashlib
import json
import logging

from itertools import count

from mqtt_panel.util import blob_hash
from mqtt_panel.web.component import Component
from mqtt_panel.web.webbase import WebBase
from mqtt_panel.web.widget.widget import Widget


class Panel(Component):
    def __init__(self, blob):
        super(Panel, self).__init__(blob)
        self._groups = []
        self._web_sockets = {}
        self._client_counter = count()
        self._mqtt_online = False

    def add_group(self, group):
        self._groups.append(group)

    def open(self):
        for group in self._groups:
            group.open()
        self._identity = blob_hash([g.identity for g in self._groups])

    @property
    def icon(self):
        return self._c.get('icon', 'dashboard')

    def gen_blobs(self):
        yield self._blob()

        for group in self._groups:
            yield from group.gen_blobs()

    def mqtt_online(self, online):
        logging.debug("MQTT online status:%s", online)
        self._mqtt_online = online
        self._send_all_ws([self._blob()])

    def _get_widget(self, id):
        try:
            return self._widget_map[id]
        except KeyError as ex:
            logging.error("Widget id %s not found", ex)

    def _body(self, fh):
        fh.write(f'<div class="panel box d-none" data-title="{self.title}" data-id="panel-{self.name}">')
        for group in self._groups:
            group.html(fh)
            fh.write('\n')
        fh.write('</div>\n')

    def widgets(self):
        widgets = set()
        for group in self._groups:
            widgets.update(group.widget_classes())
        return widgets

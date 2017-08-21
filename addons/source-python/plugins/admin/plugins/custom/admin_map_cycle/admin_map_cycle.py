# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from commands import CommandReturn
from listeners import OnPluginLoaded, OnPluginUnloaded
from menus import PagedMenu, PagedOption

# Source.Python Admin
from admin.core.clients import clients
from admin.core.features import BaseFeature
from admin.core.frontends.commands import BaseFeatureCommand
from admin.core.frontends.menus import main_menu, MenuSection, MenuCommand
from admin.core.helpers import log_admin_action
from admin.core.plugins.strings import PluginStrings


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
plugin_strings = PluginStrings("admin_map_cycle")
_map_cycle_plugin = None


# =============================================================================
# >> CLASSES
# =============================================================================
class ChangeLevelFeature(BaseFeature):
    flag = 'admin.admin_map_cycle.change_level'

    def execute(self, client, map_name):
        if _map_cycle_plugin is None:
            client.tell(plugin_strings['map_cycle_not_loaded'])
            return

        if map_name is None:
            log_admin_action(
                plugin_strings['level_changed map_unknown'].tokenized(
                    admin_name=client.name,
                )
            )
        else:
            if map_name not in (
                    _map_cycle_plugin.module.external.get_map_list()):

                client.tell(plugin_strings['unknown_map'])
                return

            log_admin_action(
                plugin_strings['level_changed map_known'].tokenized(
                    admin_name=client.name,
                    map_name=map_name
                )
            )

        _map_cycle_plugin.module.external.change_level(map_name)

change_level_feature = ChangeLevelFeature()


class ChangeLevelMenuCommand(MenuCommand):
    def __init__(self, feature, parent, title, id_=None):
        super().__init__(feature, parent, title, id_)

        self.map_popup = PagedMenu(
            title=plugin_strings['popup_title change_level'])

        @self.map_popup.register_build_callback
        def build_callback(popup, index):
            popup.clear()

            for map_name in _map_cycle_plugin.module.external.get_map_list():
                popup.append(PagedOption(
                    text=map_name,
                    value=map_name,
                ))

        @self.map_popup.register_select_callback
        def select_callback(popup, index, option):
            client = clients[index]
            self.feature.execute(client, option.value)

    def select(self, client):
        if _map_cycle_plugin is None:
            client.tell(plugin_strings['map_cycle_not_loaded'])
            return

        client.send_popup(self.map_popup)


class ChangeLevelCommand(BaseFeatureCommand):
    def _execute(self, command_info, map_name):
        client = clients[command_info.index]
        client.sync_execution(self.feature.execute, (client, map_name))

    def _get_public_chat_callback(self):
        def public_chat_callback(command_info, map_name):
            self._execute(command_info, map_name)
            return CommandReturn.CONTINUE

        return public_chat_callback

    def _get_private_chat_callback(self):
        def private_chat_callback(command_info, map_name):
            self._execute(command_info, map_name)
            return CommandReturn.BLOCK

        return private_chat_callback

    def _get_client_callback(self):
        def client_callback(command_info, map_name):
            self._execute(command_info, map_name)

        return client_callback


# =============================================================================
# >> COMMAND FRONTEND
# =============================================================================
ChangeLevelCommand(["map", "change"], change_level_feature)


# =============================================================================
# >> MENU ENTRIES
# =============================================================================
menu_section = main_menu.add_entry(MenuSection(
    main_menu, plugin_strings['section_title'], 'map_cycle'))

menu_section.add_entry(ChangeLevelMenuCommand(
    change_level_feature,
    menu_section,
    plugin_strings['popup_title change_level']
))


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnPluginLoaded
def listener_on_plugin_loaded(plugin):
    if plugin.name == 'map_cycle':
        global _map_cycle_plugin
        _map_cycle_plugin = plugin


@OnPluginUnloaded
def listener_on_plugin_unloaded(plugin):
    if plugin.name == 'map_cycle':
        global _map_cycle_plugin
        _map_cycle_plugin = None

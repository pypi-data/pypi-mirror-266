# from nautobot.extras.plugins import PluginMenuButton, PluginMenuItem, PluginMenu
from nautobot.core.apps import NavMenuItem, NavMenuTab, NavMenuGroup
# from nautobot.core.choices import ButtonColorChoices


# imported_device_buttons = [
#     PluginMenuButton(
#         link='plugins:slurpit_nautobot:import',
#         title='Import',
#         icon_class='mdi mdi-sync',
#         color=ButtonColorChoices.ORANGE,
#     )
# ]

menu_items = (
    NavMenuTab(
        name='Slurp`it',
        groups=(
            NavMenuGroup(
                name='Slurp`it', 
                items = (
                    NavMenuItem(
                        link='plugins:slurpit_nautobot:settings',
                        name='Settings',
                        permissions=["slurpit_nautobot.view_settings"]
                    ),
                    NavMenuItem(
                        link='plugins:slurpit_nautobot:importeddevice_list',
                        name='Onboard devices',
                        # buttons=imported_device_buttons,
                        permissions=["slurpit_nautobot.view_onboard_devices"]
                    ),
                    NavMenuItem(
                        link='plugins:slurpit_nautobot:data_mapping_list',
                        name='Data mapping',
                        permissions=["slurpit_nautobot.view_data_mapping"]
                    ),
                    NavMenuItem(
                        link='plugins:slurpit_nautobot:reconcile_list',
                        name='Reconcile',
                        permissions=["slurpit_nautobot.view_reconcile"]
                    ),
                    NavMenuItem(
                        link='plugins:slurpit_nautobot:slurpitlog_list',
                        name='Logging',
                        permissions=["slurpit_nautobot.view_logging"]
                    ),
                )
            ),
        ),
        # icon_class='mdi mdi-swap-horizontal'
    ),
)

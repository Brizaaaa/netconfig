from base_device import BaseDevice
from ...scripts_bank.lib import netmiko_functions as nfn


class CiscoBaseDevice(BaseDevice):
    """Base class for network device vendor Cisco."""

    def check_invalid_input_detected(self, x):
        """Check for invalid input when executing command on device."""
        if "Invalid input detected" in x:
            return True
        else:
            return False

    def get_cmd_enter_configuration_mode(self):
        """Return command for entering configuration mode."""
        command = "config term"
        return command

    def get_cmd_enable_interface(self):
        """Return command for enabling interface on device."""
        command = "no shutdown"
        return command

    def get_cmd_disable_interface(self):
        """Return command for disabling interface on device."""
        command = "shutdown"
        return command

    def cleanup_ios_output(self, x):
        """Clean up returned IOS output from 'show ip interface brief'."""
        x = x.replace('OK?', '')
        x = x.replace('Method', '')
        x = x.replace('YES', '')
        x = x.replace('NO', '')
        x = x.replace('unset', '')
        x = x.replace('NVRAM', '')
        x = x.replace('IPCP', '')
        x = x.replace('CONFIG', '')
        x = x.replace('TFTP', '')
        x = x.replace('manual', '')
        x = self.replace_double_spaces_commas(x)
        x = x.replace('down down', 'down,down')
        x = x.replace(' unassigned', ',unassigned')
        x = x.replace('unassigned ', 'unassigned,')
        return x

    def cleanup_nxos_output(self, x):
        """Clean up returned NX-OS output from 'show ip interface brief'."""
        x = x.replace(' connected', ',connected')
        x = x.replace('connected ', 'connected,')
        x = x.replace(' sfpAbsent', ',sfpAbsent')
        x = x.replace('sfpAbsent ', 'sfpAbsent,')
        x = x.replace(' noOperMem', ',noOperMem')
        x = x.replace('noOperMem ', 'noOperMem,')
        x = x.replace(' disabled', ',disabled')
        x = x.replace('disabled ', 'disabled,')
        x = x.replace(' down', ',down')
        x = x.replace('down ', 'down,')
        x = x.replace(' notconnec', ',notconnec')
        x = x.replace('notconnec ', 'notconnec,')
        x = x.replace(' linkFlapE', ',linkFlapE')
        x = x.replace('linkFlapE ', 'linkFlapE,')
        return x

    def run_enable_interface_cmd(self, interface, activeSession):
        """Enable interface on device using existing SSH session."""
        cmdList = []
        cmdList.append("interface %s" % interface)
        cmdList.append("%s" % (self.get_cmd_enable_interface()))
        cmdList.append("end")

        return self.run_ssh_config_commands(cmdList, activeSession)

    def run_disable_interface_cmd(self, interface, activeSession):
        """Disable interface on device using existing SSH session."""
        cmdList = []
        cmdList.append("interface %s" % interface)
        cmdList.append("%s" % (self.get_cmd_disable_interface()))
        cmdList.append("end")

        return self.run_ssh_config_commands(cmdList, activeSession)

    def get_save_config_cmd(self):
        """Return command for saving configuration settings on device."""
        if self.ios_type == 'cisco_nxos':
            return "copy running-config startup-config"
        else:
            return "write memory"

    def save_config_on_device(self, activeSession):
        """Return command for saving configuration settings on device."""
        command = self.get_save_config_cmd()
        return self.split_on_newline(nfn.runSSHCommandInSession(command, activeSession))

    def run_edit_interface_cmd(self, interface, datavlan, voicevlan, other, activeSession):
        """Edit interface on device with specified parameters on existing SSH session."""
        cmdList = []
        cmdList.append("interface %s" % interface)

        if datavlan != '0':
            cmdList.append("switchport access vlan %s" % datavlan)
        if voicevlan != '0':
            cmdList.append("switchport voice vlan %s" % voicevlan)
        if other != '0':
            # + is used to represent spaces
            other = other.replace('+', ' ')

            # & is used to represent new lines
            for x in other.split('&'):
                cmdList.append(x)

        cmdList.append("end")

        return self.run_ssh_config_commands(cmdList, activeSession)

    def cmd_show_inventory(self):
        """Return command to display device inventory."""
        command = 'show inventory'
        return command

    def cmd_show_version(self):
        """Return command to display device version."""
        command = 'show version'
        return command

    def pull_inventory(self, activeSession):
        """Pull device inventory.

        Pulls device inventory.
        Returns output as array with each new line on a separate row.
        """
        command = self.cmd_show_inventory()
        return self.split_on_newline(self.run_ssh_command(command, activeSession))

    def pull_version(self, activeSession):
        """Pull device version.

        Pulls device version.
        Returns output as array with each new line on a separate row.
        """
        command = self.cmd_show_version()
        return self.split_on_newline(self.run_ssh_command(command, activeSession))

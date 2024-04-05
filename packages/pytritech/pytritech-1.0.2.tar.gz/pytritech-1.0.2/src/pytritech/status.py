""" The Status record from the GLF file.

This module contains the following:
    - StatusRecord - The StatusRecord class representing the status of the sonar at a particular time.
"""

__all__ = ["StatusRecord"]
__version__ = "1.0.1"
__author__ = "Benjamin Blundell <me@benjamin.computer>"

import struct


class StatusRecord:
    """The current status of the Sonar at this time."""

    def __init__(self, ciheader, dat, ids):
        """Initialise our StatusRecord object.

        Args:
            ciheader (CIHeader): the CIHeader object that preceeds this record in the GLF file.
            dat (bytes): A Bytes like file object open for reading.
            ids (int): The offset within dat to start reading from.
        """
        self.header = ciheader
        ds = ids
        self.bf_version = struct.unpack("<H", dat[ds : ds + 2])[0]
        self.da_version = struct.unpack("<H", dat[ds + 2 : ds + 4])[0]
        self.flags = dat[ds + 4 : ds + 6]
        self.device_id = struct.unpack("<H", dat[ds + 6 : ds + 8])[0]
        self.xd_selected = dat[ds + 8 : ds + 9]
        ds += 10

        # one char reserved for future use
        self.vga_T1 = struct.unpack("<d", dat[ds : ds + 8])[0]
        self.vga_T2 = struct.unpack("<d", dat[ds + 8 : ds + 16])[0]
        self.vga_T3 = struct.unpack("<d", dat[ds + 16 : ds + 24])[0]
        self.vga_T4 = struct.unpack("<d", dat[ds + 24 : ds + 32])[0]
        ds += 32

        self.psu_T = struct.unpack("<d", dat[ds : ds + 8])[0]
        self.die_T = struct.unpack("<d", dat[ds + 8 : ds + 16])[0]
        self.tx_T = struct.unpack("<d", dat[ds + 16 : ds + 24])[0]
        ds += 24

        self.afe0_top_temp = struct.unpack("<d", dat[ds : ds + 8])[0]
        self.afe0_bot_temp = struct.unpack("<d", dat[ds + 8 : ds + 16])[0]
        self.afe1_top_temp = struct.unpack("<d", dat[ds + 16 : ds + 24])[0]
        self.afe1_bot_temp = struct.unpack("<d", dat[ds + 24 : ds + 32])[0]
        self.afe2_top_temp = struct.unpack("<d", dat[ds + 32 : ds + 40])[0]
        self.afe2_bot_temp = struct.unpack("<d", dat[ds + 40 : ds + 48])[0]
        self.afe3_top_temp = struct.unpack("<d", dat[ds + 48 : ds + 56])[0]
        self.afe3_bot_temp = struct.unpack("<d", dat[ds + 56 : ds + 64])[0]
        ds += 64

        self.link_type = dat[ds : ds + 2]
        self.uplink_speed = struct.unpack("<d", dat[ds + 2 : ds + 10])[0]
        self.downlink_speed = struct.unpack("<d", dat[ds + 10 : ds + 18])[0]
        self.link_quality = struct.unpack("<H", dat[ds + 18 : ds + 20])[0]
        self.packet_count = struct.unpack("<I", dat[ds + 20 : ds + 24])[0]
        self.recv_error_count = struct.unpack("<I", dat[ds + 24 : ds + 28])[0]
        self.resent_packet_count = struct.unpack("<I", dat[ds + 28 : ds + 32])[0]
        self.dropped_packet_count = struct.unpack("<I", dat[ds + 32 : ds + 36])[0]
        self.unknown_packet_count = struct.unpack("<I", dat[ds + 36 : ds + 40])[0]
        ds += 40

        self.lost_line_count = struct.unpack("<I", dat[ds : ds + 4])[0]
        self.general_count = struct.unpack("<I", dat[ds + 4 : ds + 8])[0]
        self.sonar_alt_ip = struct.unpack("<I", dat[ds + 8 : ds + 12])[0]
        self.surface_ip = struct.unpack("<I", dat[ds + 12 : ds + 16])[0]
        self.subnet_mask = dat[ds + 16 : ds + 20]
        self.mac_addr = dat[ds + 20 : ds + 26]

        # Two unsigned ints for internal usage
        ds += 26

        # TODO - uint64_t
        self.boot_sts_register = dat[ds : ds + 4]
        self.boot_sts_register_da = dat[ds + 4 : ds + 8]
        self.fpga_time = struct.unpack("<Q", dat[ds + 8 : ds + 16])[0]
        self.dip_switch = dat[ds + 16 : ds + 18]
        # Short for internal usage
        self.shutdown_status = dat[ds + 18 : ds + 20]
        self.net_adap_found = struct.unpack("?", dat[ds + 20 : ds + 21])[0]
        ds += 22

        # self.subsea_internal_temp = struct.unpack('<d', dat[ds:ds+8])[0]
        # self.subsea_cpu_temp = struct.unpack('<d', dat[ds+8:ds+16])[0]
        # self.ui_frame = struct.unpack('<I', dat[ds+16:ds+20])[0]
        # ds += 20

        self.record_size = ds - ids

    def __len__(self):
        return self.record_size

    def __str__(self):
        return (
            str(self.bf_version)
            + ","
            + str(self.da_version)
            + ","
            + str(self.flags)
            + ","
            + str(self.device_id)
            + ","
            + str(self.xd_selected)
            + ","
            + str(self.vga_T1)
            + ","
            + str(self.vga_T2)
            + ","
            + str(self.vga_T3)
            + ","
            + str(self.vga_T4)
            + ","
            + str(self.psu_T)
            + ","
            + str(self.die_T)
            + ","
            + str(self.tx_T)
            + ","
            + str(self.afe0_top_temp)
            + ","
            + str(self.afe0_bot_temp)
            + ","
            + str(self.afe1_top_temp)
            + ","
            + str(self.afe1_bot_temp)
            + ","
            + str(self.afe2_top_temp)
            + ","
            + str(self.afe2_bot_temp)
            + ","
            + str(self.afe3_top_temp)
            + ","
            + str(self.afe3_bot_temp)
            + ","
            + str(self.link_type)
            + ","
            + str(self.uplink_speed)
            + ","
            + str(self.downlink_speed)
            + ","
            + str(self.link_quality)
            + ","
            + str(self.packet_count)
            + ","
            + str(self.recv_error_count)
            + ","
            + str(self.resent_packet_count)
            + ","
            + str(self.dropped_packet_count)
            + ","
            + str(self.unknown_packet_count)
            + ","
            + str(self.lost_line_count)
            + ","
            + str(self.general_count)
            + ","
            + str(self.sonar_alt_ip)
            + ","
            + str(self.surface_ip)
            + ","
            + str(self.subnet_mask)
            + ","
            + str(self.mac_addr)
            + ","
            + str(self.boot_sts_register)
            + ","
            + str(self.boot_sts_register_da)
            + ","
            + str(self.fpga_time)
            + ","
            + str(self.dip_switch)
            + ","
            + str(self.shutdown_status)
            + ","
            + str(self.net_adap_found)
            + ","
            + str(self.record_size)
        )

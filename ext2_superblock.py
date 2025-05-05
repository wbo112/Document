import math
import struct
from types import SimpleNamespace

# 定义超级块格式字符串（小端）
SUPERBLOCK_FORMAT = '<'  # 小端模式
SUPERBLOCK_FORMAT += 'I' * 13  # 0x00 ~ 0x30 前 20 个 u32 字段
SUPERBLOCK_FORMAT += 'H' * 6  # 0x34 ~ 0x3E: s_mnt_count,s_max_mnt_count,s_magic,s_state,s_errors,s_minor_rev_level
SUPERBLOCK_FORMAT += 'I' * 4  # 0x40 ~ 0x4C: s_lastcheck,s_checkinterval,s_creator_os,s_rev_level
SUPERBLOCK_FORMAT += 'HH'  # 0x50 ~ 0x52: s_def_resuid, s_def_resgid
SUPERBLOCK_FORMAT += 'I'  # 0x54 : s_first_ino
SUPERBLOCK_FORMAT += 'HH'  # 0x58 ~ 0x5A: s_inode_size, s_block_group_nr
SUPERBLOCK_FORMAT += 'I' * 3  # 0x5C ~ 0x68: feature compat, incompat, ro_compat
SUPERBLOCK_FORMAT += '16s'  # 0x68 ~ 0x78: s_uuid
SUPERBLOCK_FORMAT += '16s'  # 0x78 ~ 0x88: s_volume_name
SUPERBLOCK_FORMAT += '64s'  # 0x88 ~ 0xC8: s_last_mounted
SUPERBLOCK_FORMAT += 'I'  # 0xC8 ~ 0xCC: s_algo_bitmap
SUPERBLOCK_FORMAT += 'BB'  # 0xCC ~ 0xCE: s_prealloc_blocks, s_prealloc_dir_blocks
SUPERBLOCK_FORMAT += 'BB'  # 0xCE ~ 0xD0: align[0], align[1]
SUPERBLOCK_FORMAT += '16s'  # 0xD0 ~ 0xE0: s_journal_uuid
SUPERBLOCK_FORMAT += 'III'  # 0xE0 ~ 0xEC: s_journal_inum, s_journal_dev, s_last_orphan
SUPERBLOCK_FORMAT += 'IIII'  # 0xEC ~ 0xFC: s_hash_seed[4]
SUPERBLOCK_FORMAT += 'IBH'  # 0xFC ~ 0x100: s_def_hash_version, s_jnl_backup_type, s_desc_size
SUPERBLOCK_FORMAT += 'III'  # 0x100 ~ 0x10C: s_default_mount_opts, s_first_meta_bg, s_mkfs_time
from datetime import datetime, timezone


def convert_utc_timestamp(timestamp_s, fmt="%Y-%m-%d %H:%M:%S UTC"):
    """
    将 UTC 时间戳转换为格式化字符串
    :param timestamp_s: 时间戳（秒）
    :param fmt: 输出格式（默认：2025-05-01 12:34:56 UTC）
    :return: 格式化时间字符串
    """
    utc_time = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)
    return utc_time.strftime(fmt)


def parse_superblock(file_path):
    with open(file_path, "rb") as f:
        f.seek(1024)
        raw = f.read(struct.calcsize(SUPERBLOCK_FORMAT))

    unpacked = struct.unpack(SUPERBLOCK_FORMAT, raw)

    # 映射哈希算法名称
    hash_algorithms = {
        0: 'legacy',
        1: 'half_md4',
        2: 'tea',
        3: 'legacy_unsigned',
        4: 'half_md4_unsigned',
        5: 'tea_unsigned'
    }
    sb = {
        "s_inodes_count": ("inode 总数", unpacked[0]),
        "s_blocks_count_lo": ("block 总数（低 32 位）", unpacked[1]),
        "s_r_blocks_count_low": ("预留给 root 的 block 数量（低 32 位）", unpacked[2]),
        "s_free_blocks_count_low": ("当前空闲的 block 数量（低 32 位）", unpacked[3]),
        "s_free_inodes_count": ("当前空闲的 inode 数量", unpacked[4]),
        "s_first_data_block": ("第一个数据 block 编号", unpacked[5]),
        "s_log_block_size": ("log2(block_size) - 10", 1024<<unpacked[6]),
        "s_log_frag_size": ("fragment size 设置", unpacked[7]),
        "s_blocks_per_group": ("每个 block group 的 block 数量", unpacked[8]),
        "s_frags_per_group": ("每个 block group 的 fragment 数量", unpacked[9]),
        "s_inodes_per_group": ("每个 block group 的 inode 数量", unpacked[10]),
        "s_mtime": ("最后一次挂载时间戳", convert_utc_timestamp(unpacked[11])),
        "s_wtime": ("最后一次写入时间戳", convert_utc_timestamp(unpacked[12])),
        "s_mnt_count": ("已挂载次数", unpacked[13]),
        "s_max_mnt_count": ("最大允许挂载次数", unpacked[14]),
        "s_magic": ("文件系统魔数", hex(unpacked[15])),
        "s_state": ("文件系统状态", hex(unpacked[16])),
        "s_errors": ("出错处理方式", unpacked[17]),
        "s_minor_rev_level": ("次版本号", unpacked[18]),
        "s_lastcheck": ("上次 fsck 检查时间戳", convert_utc_timestamp(unpacked[19])),
        "s_checkinterval": ("下次检查最大间隔", unpacked[20]),
        "s_creator_os": ("创建者操作系统", unpacked[21]),
        "s_rev_level": ("主版本号", unpacked[22]),
        "s_def_resuid": ("默认保留 block 的 UID", unpacked[23]),
        "s_def_resgid": ("默认保留 block 的 GID", unpacked[24]),
        "s_first_ino": ("第一个非预留 inode", unpacked[25]),
        "s_inode_size": ("inode 大小（字节）", unpacked[26]),
        "s_block_group_nr": ("所在 block group 编号", unpacked[27]),
        "s_feature_compat": ("兼容特性标志位", hex(unpacked[28])),
        "s_feature_incompat": ("不兼容特性标志位", hex(unpacked[29])),
        "s_feature_ro_compat": ("只读兼容特性标志位", hex(unpacked[30])),
        "s_uuid": ("UUID", unpacked[31].hex()),
        "s_volume_name": ("卷名", unpacked[32].rstrip(b'\x00').decode('utf-8', errors='ignore')),
        "s_last_mounted": ("上次挂载路径", unpacked[33].rstrip(b'\x00').decode('utf-8', errors='ignore')),
        "s_algo_bitmap": ("压缩算法掩码", hex(unpacked[34])),
        "s_prealloc_blocks": ("文件预分配 block 数量", unpacked[35]),
        "s_prealloc_dir_blocks": ("目录预分配 block 数量", unpacked[36]),
        "align": ("对齐填充", unpacked[37:39]),
        "s_journal_uuid": ("日志设备 UUID", unpacked[39]),
        "s_journal_inum": ("日志 inode 编号", unpacked[40]),
        "s_journal_dev": ("日志设备编号", unpacked[41]),
        "s_last_orphan": ("孤儿 inode 链表头", unpacked[42]),
        "s_hash_seed": ("目录哈希种子", '-'.join([x.to_bytes(4, byteorder='little').hex() for x in unpacked[43:47]])),
        "s_def_hash_version": ("默认哈希版本", hash_algorithms.get(unpacked[47])),
        "s_jnl_backup_type": ("日志备份类型", unpacked[48]),
        "s_desc_size": ("描述符大小", unpacked[49]),
        "s_default_mount_opts": ("默认挂载选项", hex(unpacked[50])),
        "s_mkfs_time": ("创建时间戳", convert_utc_timestamp(unpacked[52])),
        "s_groups_count":("快组数量",math.ceil(unpacked[1]/unpacked[8]))
    }

    print("=== Superblock Fields ===")
    d={}
    for field, (desc, value) in sb.items():
        d.setdefault(field,value)
        print(f"{field:<24} : {value}  # {desc}")
    superblock=SimpleNamespace(**d)
    print(superblock)

if __name__ == "__main__":
    # import sys
    # if len(sys.argv) != 2:
    # print("Usage: python superblock_parser.py <ext2_image>")
    # sys.exit(1)
    parse_superblock(r'F:\tmp\ext2_0.img')

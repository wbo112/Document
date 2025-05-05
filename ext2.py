import struct
import os
from functools import lru_cache


class Ext2Parser:
    def __init__(self, filename):
        self.file = open(filename, 'rb')
        self.group_descs = []  # 先初始化空列表
        self.read_superblock()
        self.block_size = 1024 << self.s_log_block_size
        self.s_inode_size = self.s_inode_size if self.s_inode_size != 0 else 128

        # 正确初始化顺序
        self.load_group_descriptors()  # 在初始化列表之后调用

    def load_group_descriptors(self):
        """加载所有块组描述符"""
        group_desc_table_block = self.s_first_data_block + 1
        group_desc_size = 32
        groups_count = (self.s_blocks_count + self.s_blocks_per_group - 1) // self.s_blocks_per_group

        self.file.seek(group_desc_table_block * self.block_size)
        for _ in range(groups_count):
            group_desc = self.file.read(group_desc_size)
            bg_block_bitmap = struct.unpack('<I', group_desc[0:4])[0]
            bg_inode_bitmap = struct.unpack('<I', group_desc[4:8])[0]
            bg_inode_table = struct.unpack('<I', group_desc[8:12])[0]
            # bg_inode_table = struct.unpack('<I', group_desc[8:12])[0]

            # 现在self.group_descs已经初始化
            self.group_descs.append({
                'block_bitmap': bg_block_bitmap,
                'inode_bitmap': bg_inode_bitmap,
                'inode_table': bg_inode_table
            })


    def read_superblock(self):
        self.file.seek(1024)
        superblock = self.file.read(1024)

        self.s_magic = struct.unpack('<H', superblock[56:58])[0]
        assert self.s_magic == 0xEF53, "Not an ext2 filesystem"
        self.s_inodes_count = struct.unpack('<I', superblock[0:4])[0]
        self.s_blocks_count = struct.unpack('<I', superblock[4:8])[0]
        self.s_reserved_blocks_count = struct.unpack('<I', superblock[8:12])[0]
        self.s_free_block_count = struct.unpack('<I', superblock[12:16])[0]
        self.s_free_inodes_count =  struct.unpack('<I', superblock[16:20])[0]
        self.s_first_data_block = struct.unpack('<I', superblock[20:24])[0]
        self.s_log_block_size = struct.unpack('<I', superblock[24:28])[0]
        self.s_log_frag_size = struct.unpack('<I', superblock[28:32])[0]
        self.s_blocks_per_group = struct.unpack('<I', superblock[32:36])[0]
        self.s_frags_per_group = struct.unpack('<I', superblock[36:40])[0]
        self.s_inodes_per_group = struct.unpack('<I', superblock[40:44])[0]
        self.s_mtime = struct.unpack('<I', superblock[44:48])[0]
        self.s_wtime = struct.unpack('<I', superblock[48:52])[0]
        self.s_mnt_count = struct.unpack('<H', superblock[52:54])[0]
        self.s_max_mnt_count = struct.unpack('<H', superblock[54:56])[0]
        self.s_state = struct.unpack('<H', superblock[58:60])[0]

        self.s_inode_size = struct.unpack('<H', superblock[88:90])[0]


    def get_inode_location(self, inode_num):
        group_index = (inode_num - 1) // self.s_inodes_per_group
        index_in_group = (inode_num - 1) % self.s_inodes_per_group
        group_desc = self.group_descs[group_index]
        return (
                group_desc['inode_table'] * self.block_size +
                index_in_group * self.s_inode_size
        )

    def read_inode(self, inode_num):
        offset = self.get_inode_location(inode_num)
        self.file.seek(offset)
        inode_data = self.file.read(self.s_inode_size)

        i_mode = struct.unpack('<H', inode_data[0:2])[0]
        i_size = struct.unpack('<I', inode_data[4:8])[0]
        i_blocks = struct.unpack('<I', inode_data[28:32])[0]
        block_ptrs = struct.unpack('<15I', inode_data[40:100])

        return {
            'mode': i_mode,
            'size': i_size,
            'blocks': i_blocks,
            'block_ptrs': block_ptrs,
            'inode_num': inode_num
        }

    def read_directory(self, inode):
        entries = []
        processed = 0
        total_size = inode['size']

        def process_block(block_data):
            nonlocal processed
            pos = 0
            while pos + 8 <= len(block_data) and processed < total_size:
                inode_num, rec_len, name_len, file_type = struct.unpack('<IHBB', block_data[pos:pos + 8])

                if inode_num == 0 or rec_len == 0:
                    break

                # 处理非法name_len
                name_len = min(name_len, 255)
                name_end = pos + 8 + name_len
                if name_end > len(block_data):
                    break

                name = block_data[pos + 8:name_end].decode('latin-1', 'replace')
                entries.append({
                    'name': name,
                    'inode': inode_num,
                    'type': file_type,
                    'rec_len': rec_len
                })

                pos += rec_len
                processed += rec_len

        # 处理直接块
        for bn in inode['block_ptrs'][:12]:
            if bn == 0:
                continue
            block_data = self.read_block(bn)
            process_block(block_data)
            if processed >= total_size:
                break

        # 处理间接块（递归方法）
        def process_indirect(block_num, level):
            if level == 0 or processed >= total_size:
                return
            pointers = self.read_block_pointers(block_num)
            for ptr in pointers:
                if ptr == 0:
                    continue
                if level == 1:
                    block_data = self.read_block(ptr)
                    process_block(block_data)
                else:
                    process_indirect(ptr, level - 1)

        # 处理各级间接块
        for idx, level in [(12, 1), (13, 2), (14, 3)]:
            if inode['block_ptrs'][idx] != 0:
                process_indirect(inode['block_ptrs'][idx], level)

        return entries

    @lru_cache(maxsize=1024)
    def read_block(self, block_num):
        if block_num == 0:
            return b''
        self.file.seek(block_num * self.block_size)
        return self.file.read(self.block_size)

    def read_block_pointers(self, block_num):
        block_data = self.read_block(block_num)
        return struct.unpack(f'<{self.block_size // 4}I', block_data)

    def read_file_content(self, inode):
        content = bytearray()
        remaining = inode['size']

        # 处理直接块
        for bn in inode['block_ptrs'][:12]:
            if bn == 0 or remaining <= 0:
                break
            data = self.read_block(bn)[:remaining]
            content.extend(data)
            remaining -= len(data)

        # 处理间接块
        def process_indirect_block(bn, level):
            nonlocal remaining
            if level == 0 or remaining <= 0:
                return
            pointers = self.read_block_pointers(bn)
            for ptr in pointers:
                if ptr == 0 or remaining <= 0:
                    break
                if level == 1:
                    data = self.read_block(ptr)[:remaining]
                    content.extend(data)
                    remaining -= len(data)
                else:
                    process_indirect_block(ptr, level - 1)

        for idx, level in [(12, 1), (13, 2), (14, 3)]:
            if inode['block_ptrs'][idx] != 0:
                process_indirect_block(inode['block_ptrs'][idx], level)

        return bytes(content)

    def close(self):
        self.file.close()


def traverse_filesystem(parser, inode_num=2, path="/", max_content=100):
    try:
        inode = parser.read_inode(inode_num)
    except:
        return

    # 处理目录
    if (inode['mode'] & 0xF000) == 0x4000:
        print(f"\n📁 DIR: {path}")
        for entry in parser.read_directory(inode):
            if entry['name'] in ('.', '..'):
                continue

            full_path = f"{path}{entry['name']}" + ('/' if entry['type'] == 2 else '')
            traverse_filesystem(parser, entry['inode'], full_path, max_content)

    # 处理普通文件（添加内容打印）
    elif (inode['mode'] & 0xF000) == 0x8000:
        content = parser.read_file_content(inode)
        print(f"\n📄 FILE: {path}")
        print(f"   Size: {len(content)} bytes")
        print(f"   Inode: {inode['inode_num']}")

        # 打印文件内容（限制最大输出长度）
        if len(content) > 0:
            print("   First {} bytes:".format(min(max_content, len(content))))
            try:
                # 尝试UTF-8解码文本内容
                text_content = content[:max_content].decode('utf-8', errors='replace')
                print("   " + text_content.replace('\n', '\n   '))
            except UnicodeDecodeError:
                # 二进制内容以HEX显示
                hex_content = content[:max_content].hex(' ', 16)
                print("   HEX: " + hex_content)
            if len(content) > max_content:
                print("   ... (truncated)")
        else:
            print("   [Empty file]")

if __name__ == "__main__":
    parser = Ext2Parser(r'F:\tmp\ext2_image.img')
    try:
        print("Starting filesystem traversal...")
        traverse_filesystem(parser)
        print("Traversal completed.")
    finally:
        parser.close()
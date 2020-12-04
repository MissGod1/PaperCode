#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   getOpcode.py
@Time    :   2020/11/23 13:37:21
@Author  :   Baize
@Version :   1.0
@Contact :   
@License :   
@Desc    :   
'''

#%%
from io import TextIOWrapper
import re
import subprocess
import os
import logging
import sys
import threading
import queue

logging.basicConfig(level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S %a'
)

normal_file_dir='data/normal'
webshell_file_dir='data/webshell'
# normal_opcode_file_dir='data/opcode_normal'
# webshell_opcode_file_dir='data/opcode_webshell'
opcode_dir='data/opcode'
normal_opcode_file=os.path.join(opcode_dir, 'normal_opcodes.txt')
webshell_opcode_file=os.path.join(opcode_dir, 'webshell_opcodes.txt')

def get_opcode_from_file(filename) -> list:
    '''使用vld将php文件转换为opcode'''
    output = subprocess.check_output(['php', '-dvld.active=1', '-dvld.execute=0', filename], stderr=subprocess.STDOUT)
    opcodes = re.findall(rb' \b([A-Z_]{2,})\b ', output) # 使用正则表达式提取opcode
    return [ x.decode()+' ' for x in opcodes ]
    # return opcodes

def get_all_php_files(dirname, _queue, flag) -> int:
    '''
    遍历所有文件夹中的php文件
    @dirname: 遍历文件夹
    @_queue : 文件队列
    @flag   : 文件类型 0:normal file 1:webshell
    @return : 文件数目
    '''
    count = 0
    for root, dirs, files in os.walk(dirname):
        for file in files:
            if file.endswith('.php'):
                _queue.put([os.path.join(root, file), flag])
                count += 1
    return count

class GenerateOpcode(threading.Thread):
        '''生成opcode序列'''
        def __init__(self, _queue, _msg, _name) -> None:
            threading.Thread.__init__(self)
            self._queue = _queue
            self._name = _name
            self._msg = _msg

        def run(self) -> None:
            while not self._queue.empty():
                try:
                    file = self._queue.get(timeout=2)
                    opcodes = get_opcode_from_file(file[0])
                    self._msg.put([opcodes, file[1]])
                except:
                    pass
            logging.debug('Threading %s End.', self._name)

class Outfile(threading.Thread):
    '''输出文件'''
    def __init__(self, _queue) -> None:
        threading.Thread.__init__(self)
        self._queue = _queue
        self._outfile = []
        self._outfile.append(self._openfile(normal_opcode_file))
        self._outfile.append(self._openfile(webshell_opcode_file))

    def _openfile(self, filename) -> TextIOWrapper:
        fp = open(filename, 'w+')
        return fp
    
    def run(self) -> None:
        while threading.active_count() != 2 or not self._queue.empty():
            try:
                msg = self._queue.get(timeout=2)
                self._outfile[msg[1]].writelines(msg[0])
                self._outfile[msg[1]].write('\n')
            except:
                pass
        for f in self._outfile:
            f.close()

def check_init() -> None:
    '''判断所需资源是否存在'''
    if not os.path.exists(normal_file_dir):
        logging.error("%s not exists.", normal_file_dir)
        sys.exit()
    if not os.path.exists(webshell_file_dir):
        logging.error("%s not exists.", webshell_file_dir)
        sys.exit()
       
    if not os.path.exists(opcode_dir):
        logging.info("%s not exists.", opcode_dir)
        logging.info("Create %s.", opcode_dir)
        os.makedirs(opcode_dir)


if __name__ == '__main__':
    check_init()
    threadnum = 100
    threads = []
    phpfiles = queue.Queue()
    msg = queue.Queue()
    # 获取php文件
    logging.info('Get all php files')
    count = get_all_php_files(normal_file_dir, phpfiles, 0)
    logging.info('normal php files : %d', count)
    count = get_all_php_files(webshell_file_dir, phpfiles, 1)
    logging.info('webshell php files : %d', count)
    logging.info('all files : %d', phpfiles.qsize())

    # 转换php->opcode
    logging.info('Start Convert php file to opcode sequence')
    for i in range(threadnum):
        t = GenerateOpcode(phpfiles, msg, 'thread %d' % i)
        t.setDaemon(True)
        t.start()
        threads.append(t)
    
    tmsg = Outfile(msg)
    tmsg.setDaemon(True)
    tmsg.start()
    
    for t in threads:
        t.join()
    tmsg.join()
    logging.info("Done.")
# %%

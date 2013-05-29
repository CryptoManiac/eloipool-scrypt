#!/usr/bin/python3

import logging
logging.basicConfig(level=logging.DEBUG)

from binascii import b2a_hex
import bitcoin.txn
import bitcoin.varlen
import jsonrpc
import jsonrpcserver
import jsonrpc_getwork
import merkletree
import socket
from struct import pack
import sys
import threading
from time import time
from util import RejectedShare

try:
	import jsonrpc.authproxy
	jsonrpc.authproxy.USER_AGENT = 'gmp-proxy/0.1'
except:
	pass

pool = jsonrpc.ServiceProxy(sys.argv[1])

worklog = {}
currentwork = [None, 0, 0]

def makeMRD(mp):
	coinbase = bytes.fromhex(mp['coinbasetxn'])
	cbtxn = bitcoin.txn.Txn(coinbase)
	cbtxn.disassemble()
	cbtxn.originalCB = cbtxn.getCoinbase()
	txnlist = [cbtxn,] + list(map(bitcoin.txn.Txn, map(bytes.fromhex, mp['transactions'])))
	merkleTree = merkletree.MerkleTree(txnlist)
	merkleRoot = None
	prevBlock = bytes.fromhex(mp['previousblockhash'])[::-1]
	bits = bytes.fromhex(mp['bits'])[::-1]
	rollPrevBlk = False
	MRD = (merkleRoot, merkleTree, coinbase, prevBlock, bits, rollPrevBlk, mp)
	if 'coinbase/append' in mp.get('mutable', ()):
		currentwork[:] = (MRD, time(), 0)
	else:
		currentwork[2] = 0
	return MRD

def getMRD():
	now = time()
	if currentwork[1] < now - 45:
		mp = pool.getmemorypool()
		MRD = makeMRD(mp)
	else:
		MRD = currentwork[0]
		currentwork[2] += 1
	
	(merkleRoot, merkleTree, coinbase, prevBlock, bits, rollPrevBlk, mp) = MRD
	cbtxn = merkleTree.data[0]
	coinbase = cbtxn.originalCB + pack('>Q', currentwork[2]).lstrip(b'\0')
	if len(coinbase) > 100:
		if len(cbtxn.originalCB) > 100:
			raise RuntimeError('Pool gave us a coinbase that is too long!')
		currentwork[1] = 0
		return getMRD()
	cbtxn.setCoinbase(coinbase)
	cbtxn.assemble()
	merkleRoot = merkleTree.merkleRoot()
	MRD = (merkleRoot, merkleTree, coinbase, prevBlock, bits, rollPrevBlk, mp)
	return MRD

def MakeWork(username):
	MRD = getMRD()
	(merkleRoot, merkleTree, coinbase, prevBlock, bits, rollPrevBlk, mp) = MRD
	timestamp = pack('<L', int(time()))
	hdr = b'\1\0\0\0' + prevBlock + merkleRoot + timestamp + bits + b'ppmg'
	worklog[hdr[4:68]] = (MRD, time())
	return hdr

def SubmitShare(share):
	hdr = share['data'][:80]
	k = hdr[4:68]
	if k not in worklog:
		raise RejectedShare('LOCAL unknown-work')
	(MRD, issueT) = worklog[k]
	(merkleRoot, merkleTree, coinbase, prevBlock, bits, rollPrevBlk, mp) = MRD
	cbtxn = merkleTree.data[0]
	cbtxn.setCoinbase(coinbase)
	cbtxn.assemble()
	blkdata = bitcoin.varlen.varlenEncode(len(merkleTree.data))
	for txn in merkleTree.data:
		blkdata += txn.data
	data = b2a_hex(hdr + blkdata).decode('utf8')
	a = [data]
	if 'workid' in mp:
		a.append({'workid': mp['workid']})
	rejReason = pool.submitblock(*a)
	if not rejReason is None:
		currentwork[1] = 0
		raise RejectedShare('pool-' + rejReason)

def HandleLP():
	global server
	
	# FIXME: get path from gmp!
	pool = jsonrpc.ServiceProxy(sys.argv[1].rstrip('/') + '/LP')
	while True:
		try:
			mp = pool.getmemorypool()
			break
		except socket.timeout:
			pass
	jsonrpc_getwork._CheckForDupesHACK = {}
	makeMRD(mp)
	server.wakeLongpoll()

LPThread = None
LPTrackReal = jsonrpcserver.JSONRPCHandler.LPTrack
class LPHook:
	def LPTrack(self):
		global LPThread
		if LPThread is None or not LPThread.is_alive():
			LPThread = threading.Thread(target=HandleLP)
			LPThread.daemon = True
			LPThread.start()
		return LPTrackReal(self)
jsonrpcserver.JSONRPCHandler.LPTrack = LPHook.LPTrack

server = jsonrpcserver.JSONRPCServer()
server.getBlockHeader = MakeWork
server.receiveShare = SubmitShare
jsonrpcserver.JSONRPCListener(server, ('', 9332))

server.serve_forever()



from typing import Optional
import sys
import time

import dpkt

import cozmoai


class ReplayApp(object):

    def __init__(self, log_messages: Optional[list] = None, replay_messages: Optional[list] = None):
        self.log_messages = log_messages
        self.frame_count = 0
        self.pkts = []
        self.first_ts = None
        self.packet_id_filter = cozmoai.filter.Filter()
        if replay_messages:
            for i in replay_messages:
                self.packet_id_filter.deny_ids(cozmoai.protocol_encoder.PACKETS_BY_GROUP[i])

    def load_engine_pkts(self, fspec):
        self.pkts = []

        self.frame_count = 0
        with open(fspec, "rb") as f:
            self.first_ts = None
            for ts, frame in dpkt.pcap.Reader(f):
                if self.first_ts is None:
                    self.first_ts = ts
                eth = dpkt.ethernet.Ethernet(frame)
                if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                    
                    continue
                ip = eth.data
                if ip.p != dpkt.ip.IP_PROTO_UDP:
                    
                    continue
                udp = ip.data
                if udp.data[:7] != cozmoai.protocol_declaration.FRAME_ID:
                    
                    continue
                frame = cozmoai.Frame.from_bytes(udp.data)
                if frame.type not in (cozmoai.protocol_declaration.FrameType.ENGINE,
                                      cozmoai.protocol_declaration.FrameType.ENGINE_ACT):
                    
                    continue
                for pkt in frame.pkts:
                    if pkt.type not in [cozmoai.protocol_declaration.PacketType.COMMAND,
                                        cozmoai.protocol_declaration.PacketType.KEYFRAME]:
                        
                        continue
                    self.pkts.append((ts, pkt))
                self.frame_count += 1

        print("Loaded {} engine packets from {} frames.".format(
            len(self.pkts), self.frame_count))

    def replay(self, fspec):
        self.load_engine_pkts(fspec)

        cozmoai.setup_basic_logging(log_level="DEBUG", protocol_log_level="DEBUG")
        cli = cozmoai.Client(protocol_log_messages=self.log_messages)
        cli.start()
        cli.connect()
        cli.wait_for_robot()

        try:
            for i, v in enumerate(self.pkts):
                
                
                ts, pkt = v
                if self.packet_id_filter.filter(pkt.id):
                    continue
                input()
                print("{}, time={:.06f}".format(i, ts - self.first_ts))
                cli.conn.send(pkt)
        except KeyboardInterrupt:
            pass

        cli.disconnect()
        time.sleep(1)


def main():
    fspec = sys.argv[1]
    log_messages = []   
    replay_messages = []    

    app = ReplayApp(log_messages=log_messages, replay_messages=replay_messages)
    app.replay(fspec)


if __name__ == '__main__':
    main()

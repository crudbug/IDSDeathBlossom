#!/usr/bin/python
# -*- coding: utf-8 -*-

#*************************************************************
#  Copyright (c) 2003-2012, Emerging Threats
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the 
#  following conditions are met:
#  
#  * Redistributions of source code must retain the above copyright notice, this list of conditions and the following 
#    disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the 
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#  * Neither the name of the nor the names of its contributors may be used to endorse or promote products derived 
#    from this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES, 
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
#  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
#
#*************************************************************

import re
import sys
import os

oinkcode = None
engines = {}
engines["suricata121"] = {"type":"suricata", "version":"1.2", "eversion":"1.2.1"}
engines["suricata13"] = {"type":"suricata", "version":"1.3", "eversion":"1.3"}
engines["suricata13JIT"] = {"type":"suricata", "version":"1.3", "eversion":"1.3JIT"}
engines["suricata131"] = {"type":"suricata", "version":"1.3.1", "eversion":"1.3.1"}
engines["suricata131JIT"] = {"type":"suricata", "version":"1.3.1", "eversion":"1.3.1JIT"}
engines["snort2841"] = {"type":"snort", "version":"2.8.4", "eversion":"2.8.4.1"}
engines["snort2861"] = {"type":"snort", "version":"2.8.6", "eversion":"2.8.6.1"}
engines["snort2904"] = {"type":"snort", "version":"2.9.0", "eversion":"2.9.0.4"}
engines["snort2905"] = {"type":"snort", "version":"2.9.0", "eversion":"2.9.0.5"}
engines["snort2922"] = {"type":"snort", "version":"2.9.0", "eversion":"2.9.2.2"}
engines["snort2923"] = {"type":"snort", "version":"2.9.0", "eversion":"2.9.2.3"}
engines["snort293"] = {"type":"snort", "version":"2.9.0", "eversion":"2.9.3"}
engines["snort2931"] = {"type":"snort", "version":"2.9.0", "eversion":"2.9.3.1"}
rule_sets = {}

rule_sets["all"] = ["ftp.rules","policy.rules","trojan.rules","games.rules","pop3.rules","user_agents.rules","activex.rules","rpc.rules","virus.rules","attack_response.rules","icmp.rules","scan.rules","scada.rules","voip.rules","chat.rules","icmp_info.rules","info.rules","shellcode.rules","web_client.rules","imap.rules","web_server.rules","current_events.rules","inappropriate.rules","smtp.rules","web_specific_apps.rules","deleted.rules","malware.rules","snmp.rules","worm.rules","dns.rules","misc.rules","sql.rules","dos.rules","netbios.rules","telnet.rules","exploit.rules","p2p.rules","tftp.rules","mobile_malware.rules","botcc.rules","compromised.rules","drop.rules","dshield.rules","rbn.rules","rbn-malvertisers.rules","tor.rules","ciarmy.rules"]

rule_sets["base"] = ["ftp.rules","policy.rules","trojan.rules","games.rules","pop3.rules","user_agents.rules","rpc.rules","virus.rules","attack_response.rules","icmp.rules","scan.rules","scada.rules","voip.rules","chat.rules","web_client.rules","imap.rules","web_server.rules","current_events.rules","smtp.rules","malware.rules","snmp.rules","worm.rules","dns.rules","misc.rules","sql.rules","dos.rules","netbios.rules","telnet.rules","exploit.rules","p2p.rules","tftp.rules","mobile_malware.rules"]

rule_sets["test"] = []
update_script_buf = ""

def make_pp_config(engine,feed_type):
    ocode = ""
    rules_file = ""
    global update_script_buf

    if feed_type == "etpro":
        rules_file = "etpro.rules.tar.gz"
        ocode = oinkcode
    elif feed_type == "etopen":
        rules_file = "emerging.rules.tar.gz"
        ocode = "open"
    else:
        print "Unkown feed type bailing\n";
        sys.exit(-1)
    
    ppconfig = "/opt/%s/etc/%s/pp-%s-%s.config" % (engine,feed_type,engine,feed_type)
    ppbuf="rule_url=https://rules.emergingthreatspro.com/|%s|%s\n\
ignore=local.rules\n\
temp_path=/tmp\n\
out_path=/opt/%s/etc/%s/\n\
sid_msg=/opt/%s/etc/%s/sid-msg.map\n\
sid_changelog=/opt/%s/var/log/%s_sid_changes.log\n\
engine=%s\n\
%s_version=%s\n\
version=0.6.0\n" % (rules_file, ocode, engine, feed_type, engine, feed_type, engine, feed_type,engines[engine]["type"],engines[engine]["type"], engines[engine]["version"])
    # write this buff to a file
    f = open(ppconfig,'w')
    f.write(ppbuf)
    f.close()

    #save the update command
    update_script_buf = update_script_buf + "/usr/local/bin/pulledpork.pl -c %s -o /opt/%s/etc/%s/ -k -K /opt/%s/etc/%s/\n" % (ppconfig,engine,feed_type,engine,feed_type)

def make_engine_config(engine,feed_type,rset):
    buff = ""
    tmp_list = []

    try:
        buff = open("engine-templates/%s.template" % (engine)).read()
    except:
        print "failed to open template engine-templates/%s.template" % (engine)
        sys.exit(-1)

    if engines[engine]["type"] == "snort":
        buff += "var RULE_PATH /opt/%s/etc/%s\n" % (engine,feed_type)
        rprefix = "include $RULE_PATH/";
    elif engines[engine]["type"] == "suricata":
        buff +="default-rule-path: /opt/%s/etc/%s/\nrule-files:\n" % (engine,feed_type)
        rprefix = " - "

    for rule_file in rule_sets[rset]:
        if feed_type == "etopen":
            if re.match(r"^(botcc|compromised|drop|dshield|rbn|rbn-malvertisers|tor|ciarmy)\.rules$",rule_file) != None and engines[engine]["type"] == "suricata":
                buff += "%sET-%s\n" % (rprefix,rule_file)
            else:
                buff += "%sET-emerging-%s\n" % (rprefix,rule_file)
        elif feed_type == "etpro":
            buff += "%sET-%s\n" % (rprefix,rule_file)
        elif feed_type != "test":
            print "unknown feed type"
            sys.exit(-1)

    local_rules = "/opt/%s/etc/%s/local.rules" % (engine,feed_type)
    if not os.path.exists(local_rules):
        file(local_rules, 'w').close()
    buff += "%slocal.rules\n" % (rprefix) 
    buff += "\n"

    f = None
    if engines[engine]["type"] == "snort":
        f = open("/opt/%s/etc/%s/%s-%s-%s.conf" % (engine,feed_type,engine,feed_type,rset),"w")
    elif engines[engine]["type"] == "suricata":
        f = open("/opt/%s/etc/%s/%s-%s-%s.yaml" % (engine,feed_type,engine,feed_type,rset),"w")
    f.write(buff)
    f.close()


    buff =" - engine: %s-%s-%s-%s\n\
   type: %s\n\
   version: %s\n\
   syntax_version: %s\n\
   summary: \"%s %s %s config with %s rules\"\n\
   path: \"/opt/%s/bin/%s\"\n\
   logdir: \"/opt/%s/var/log/\"\n\
   # For specifying custom rules, we use the following template\n\
   configtpl: \"/opt/%s/etc/%s.template\"\n\
   fastlog: \"alert\"\n\
   perflog: \"perf.txt\"\n\
   enable: yes\n" % (engines[engine]["type"],engines[engine]["eversion"],feed_type,rset,engines[engine]["type"],engines[engine]["eversion"],engines[engine]["version"],engines[engine]["type"],engines[engine]["eversion"],rset,feed_type,engine,engines[engine]["type"],engine,engine,engine)
    if engines[engine]["type"] == "snort":
        buff +="   config: \"/opt/%s/etc/%s/%s-%s-%s.conf\"\n\n" % (engine,feed_type,engine,feed_type,rset)
    elif engines[engine]["type"] == "suricata":
        buff +="   config: \"/opt/%s/etc/%s/%s-%s-%s.yaml\"\n\n" % (engine,feed_type,engine,feed_type,rset)
    return buff

oinkcode = raw_input("Enter Your Oinkcode if you Have/Want to test ETPro rules (optional): ")
m = re.search(r'(?P<oinkcode>[a-z0-9A-Z]+)',oinkcode)
if m != None:
    oinkcode = m.group("oinkcode")
else:
    oinkcode = None

print "You enter Oinkcode:%s" % (oinkcode)
for engine in engines:
    dblossom_config_buff = ""
    f = open("../config/engines/%s.yaml" % (engine),"w")
    f.write("#Configurations for %s %s\n\nengines:\n" % (engines[engine]["type"],engines[engine]["eversion"]))
    if oinkcode != None:
        dblossom_config_buff += make_engine_config(engine,"etpro","base")
        dblossom_config_buff += make_engine_config(engine,"etpro","all")
        make_pp_config(engine,"etpro")
    #always cook open
    dblossom_config_buff += make_engine_config(engine,"etopen","base")
    dblossom_config_buff += make_engine_config(engine,"etopen","all")
    dblossom_config_buff += make_engine_config(engine,"test","test")
    make_pp_config(engine,"etopen")
    f.write(dblossom_config_buff)
    f.close()
    
f = open("ruleupdates.sh",'w')
f.write(update_script_buf)
f.close()
 
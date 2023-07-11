# -*- coding: utf-8 -*-

import re
import time
import requests

# confs names in template/ and ../
# except sr_head and sr_foot
confs_names = [
    'sr_top500_banlist_ad',
    'sr_top500_banlist',
    'sr_top500_whitelist_ad',
    'sr_top500_whitelist',
    'sr_adb',
    'sr_direct_banad',
    'sr_proxy_banad',
    'sr_cnip', 'sr_cnip_ad',
    'sr_backcn', 'sr_backcn_ad',
    'sr_ad_only'
]


def getRulesStringFromFile(path, kind,getFromUrl=False):
    
    file = open(path, 'r', encoding='utf-8')
    contents = file.readlines()
    if getFromUrl:
        url='https://raw.githubusercontent.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever/build/factory/'
        r=requests.get(url+path)
        contents += r.text.split('\n')
        print('loading from Johnshall:'+path)
    ret = ''

    for content in contents:
        content = content.strip('\r\n')
        if not len(content):
            continue

        if content.startswith('#'):
            ret += content + '\n'
        else:
            prefix = 'DOMAIN-SUFFIX'
            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content):
                prefix = 'IP-CIDR'
                if '/' not in content:
                    content += '/32'
            elif '.' not in content and len(content) > 1:
                prefix = 'DOMAIN-KEYWORD'

            ret += prefix + ',%s,%s\n' % (content, kind)

    return ret
    

def getASNStringFromURL(url):
    r=requests.get(url)
    contents = r.text.split('\n')
    print('loading ASN from:'+url)
    ret = ''

    for content in contents:
        content = content.strip('\r\n')
        if not len(content):
            continue

        if content.startswith('#'):
            ret += content + '\n'
        else:
            content.replace(r' //',',DIRECT #')
            ret += '%s\n' % (content)
    return ret


# get head and foot
str_head = open('template/sr_head.txt', 'r', encoding='utf-8').read()
str_foot = open('template/sr_foot.txt', 'r', encoding='utf-8').read()


# make values
values = {}

values['build_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()+60*60*8))

values['top500_proxy']  = getRulesStringFromFile('resultant/top500_proxy.list', 'Proxy')
values['top500_direct'] = getRulesStringFromFile('resultant/top500_direct.list', 'Direct')
values['ASN_direct'] = getASNStringFromURL('https://raw.githubusercontent.com/VirgilClyne/GetSomeFries/main/ruleset/ASN.China.list')
values['ad'] = getRulesStringFromFile('resultant/ad.list', 'Reject')

values['manual_direct'] = getRulesStringFromFile('manual_direct.txt', 'Direct', True)
values['manual_proxy']  = getRulesStringFromFile('manual_proxy.txt', 'Proxy', True)
values['manual_reject'] = getRulesStringFromFile('manual_reject.txt', 'Reject', True)

values['gfwlist'] = getRulesStringFromFile('resultant/gfw.list', 'Proxy') \
                  + getRulesStringFromFile('manual_gfwlist.txt', 'Proxy',True)


# make confs
for conf_name in confs_names:
    file_template = open('template/'+conf_name+'.txt', 'r', encoding='utf-8')
    template = file_template.read()
  
    if conf_name != 'sr_ad_only':
        template = str_head + template + str_foot

    file_output = open('../'+conf_name+'.conf', 'w', encoding='utf-8')

    marks = re.findall(r'{{(.+)}}', template)

    for mark in marks:
        template = template.replace('{{'+mark+'}}', values[mark])

    file_output.write(template)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K | gautamajay52

import asyncio
import logging
import os
import sys
import time
import re
from re import search
import subprocess
import hashlib

import aria2p
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from tobrot import (
    ARIA_TWO_STARTED_PORT,
    AUTH_CHANNEL,
    CUSTOM_FILE_NAME,
    DOWNLOAD_LOCATION,
    EDIT_SLEEP_TIME_OUT,
    LOGGER,
    MAX_TIME_TO_WAIT_FOR_TORRENTS_TO_START,
)
from tobrot.helper_funcs.create_compressed_archive import (
    create_archive,
    get_base_name,
    unzip_me,
)
from tobrot.helper_funcs.extract_link_from_message import extract_link
from tobrot.helper_funcs.upload_to_tg import upload_to_gdrive, upload_to_tg
from tobrot.helper_funcs.direct_link_generator import direct_link_generator
from tobrot.helper_funcs.exceptions import DirectDownloadLinkException

sys.setrecursionlimit(10 ** 4)



async def aria_start():
    aria2_daemon_start_cmd = []
    # start the daemon, aria2c command
    aria2_daemon_start_cmd.append("aria2c")
    aria2_daemon_start_cmd.append("--conf-path=/app/aria2.conf")
    aria2_daemon_start_cmd.append("--allow-overwrite=true")
    aria2_daemon_start_cmd.append("--daemon=true")
    # aria2_daemon_start_cmd.append(f"--dir={DOWNLOAD_LOCATION}")
    # TODO: this does not work, need to investigate this.
    # but for now, https://t.me/TrollVoiceBot?start=858
    aria2_daemon_start_cmd.append("--enable-rpc")
    aria2_daemon_start_cmd.append("--disk-cache=0")
    aria2_daemon_start_cmd.append("--follow-torrent=mem")
    aria2_daemon_start_cmd.append("--max-connection-per-server=16")
    aria2_daemon_start_cmd.append("--min-split-size=10M")
    aria2_daemon_start_cmd.append("--rpc-listen-all=false")
    aria2_daemon_start_cmd.append(f"--rpc-listen-port={ARIA_TWO_STARTED_PORT}")
    aria2_daemon_start_cmd.append("--rpc-max-request-size=1024M")
    aria2_daemon_start_cmd.append("--seed-ratio=0.01")
    aria2_daemon_start_cmd.append("--seed-time=1")
    aria2_daemon_start_cmd.append("--max-overall-upload-limit=2M")
    aria2_daemon_start_cmd.append("--split=16")
    aria2_daemon_start_cmd.append(f"--bt-stop-timeout={MAX_TIME_TO_WAIT_FOR_TORRENTS_TO_START}")
    aria2_daemon_start_cmd.append("--user-agent=qBittorrent 4.2.2")
    aria2_daemon_start_cmd.append("--peer-agent=Transmission 2.94")
    aria2_daemon_start_cmd.append("--user-agent=Transmission 2.94")
    aria2_daemon_start_cmd.append("--bt-tracker=http://104.28.1.30:8080/announce,http://104.28.16.69/announce,http://104.28.16.69:80/announce,http://1337.abcvg.info:80/announce,http://185.148.3.231:80/announce,http://193.37.214.12:6969/announce,http://195.201.31.194:80/announce,http://51.15.55.204:1337/announce,http://51.79.71.167:80/announce,http://51.81.46.170:6969/announce,http://54.36.126.137:6969/announce,http://54.39.179.91:6699/announce,http://60-fps.org:80/bt:80/announce.php,http://78.30.254.12:2710/announce,http://95.107.48.115:80/announce,http://[2001:1b10:1000:8101:0:242:ac11:2]:6969/announce,http://[2001:470:1:189:0:1:2:3]:6969/announce,http://[2a04:ac00:1:3dd8::1:2710]:2710/announce,http://all4nothin.net:80/announce.php,http://alltorrents.net:80/bt:80/announce.php,http://atrack.pow7.com:80/announce,http://baibako.tv:80/announce,http://big-boss-tracker.net:80/announce.php,http://bithq.org:80/announce.php,http://bt-tracker.gamexp.ru:2710/announce,http://bt.3dmgame.com:2710/announce,http://bt.3kb.xyz:80/announce,http://bt.ali213.net:8080/announce,http://bt.edwardk.info:4040/announce,http://bt.firebit.org:2710/announce,http://bt.unionpeer.org:777/announce,http://bt.zlofenix.org:81/announce,http://bt2.edwardk.info:6969/announce,http://bttracker.debian.org:6969/announce,http://btx.anifilm.tv:80/announce.php,http://concen.org:6969/announce,http://data-bg.net:80/announce.php,http://datascene.net:80/announce.php,http://explodie.org:6969/announce,http://filetracker.xyz:11451/announce,http://finbytes.org:80/announce.php,http://h4.trakx.nibba.trade:80/announce,http://ipv4announce.sktorrent.eu:6969/announce,http://irrenhaus.dyndns.dk:80/announce.php,http://kaztorka.org:80/announce.php,http://kinorun.com:80/announce.php,http://mail2.zelenaya.net:80/announce,http://masters-tb.com:80/announce.php,http://mediaclub.tv:80/announce.php,http://music-torrent.net:2710/announce,http://mvgroup.org:2710/announce,http://ns3107607.ip-54-36-126.eu:6969/announce,http://open.acgnxtracker.com:80/announce,http://opentracker.i2p.rocks:6969/announce,http://opentracker.xyz:80/announce,http://pow7.com:80/announce,http://proaudiotorrents.org:80/announce.php,http://retracker.hotplug.ru:2710/announce,http://retracker.telecom.by:80/announce,http://rt.tace.ru:80/announce,http://secure.pow7.com:80/announce,http://share.camoe.cn:8080/announce,http://siambit.com:80/announce.php,http://t.acg.rip:6699/announce,http://t.nyaatracker.com:80/announce,http://t.overflow.biz:6969/announce,http://t1.pow7.com:80/announce,http://t2.pow7.com:80/announce,http://torrent-team.net:80/announce.php,http://torrent.arjlover.net:2710/announce,http://torrent.fedoraproject.org:6969/announce,http://torrent.mp3quran.net:80/announce.php,http://torrent.nwps.ws:80/announce,http://torrent.rus.ec:2710/announce,http://torrent.ubuntu.com:6969/announce,http://torrentsmd.com:8080/announce,http://tr.cili001.com:8070/announce,http://tracker-cdn.moeking.me:2095/announce,http://tracker.ali213.net:8080/announce,http://tracker.anirena.com:80/announce,http://tracker.anirena.com:80/b16a15d9a238d1f59178d3614b857290/announce,http://tracker.birkenwald.de:6969/announce,http://tracker.bt4g.com:2095/announce,http://tracker.dler.org:6969/announce,http://tracker.fdn.fr:6969/announce,http://tracker.files.fm:6969/announce,http://tracker.frozen-layer.net:6969/announce.php,http://tracker.gbitt.info:80/announce,http://tracker.gcvchp.com:2710/announce,http://tracker.gigatorrents.ws:2710/announce,http://tracker.ipv6tracker.ru:80/announce,http://tracker.lelux.fi:80/announce,http://tracker.loadbt.com:6969/announce,http://tracker.minglong.org:8080/announce,http://tracker.nighthawk.pw:2052/announce,http://tracker.noobsubs.net:80/announce,http://tracker.opentrackr.org:1337/announce,http://tracker.pow7.com:80/announce,http://tracker.pussytorrents.org:3000/announce,http://tracker.shittyurl.org:80/announce,http://tracker.skyts.cn:6969/announce,http://tracker.skyts.net:6969/announce,http://tracker.sloppyta.co:80/announce,http://tracker.tambovnet.org:80/announce.php,http://tracker.tasvideos.org:6969/announce,http://tracker.trackerfix.com:80/announce,http://tracker.uw0.xyz:6969/announce,http://tracker.xdvdz.com:2710/announce,http://tracker.yoshi210.com:6969/announce,http://tracker.zerobytes.xyz:1337/announce,http://tracker1.itzmx.com:8080/announce,http://tracker2.dler.org:80/announce,http://tracker3.dler.org:2710/announce,http://trk.publictracker.xyz:6969/announce,http://vpn.flying-datacenter.de:6969/announce,http://vps02.net.orel.ru:80/announce,http://www.all4nothin.net:80/announce.php,http://www.thetradersden.org/forums/tracker:80/announce.php,http://www.tribalmixes.com:80/announce.php,http://www.tvnihon.com:6969/announce,http://www.worldboxingvideoarchive.com:80/announce.php,http://www.xwt-classics.net:80/announce.php,https://1337.abcvg.info:443/announce,https://bt.nfshost.com:443/announce,https://opentracker.acgnx.se:443/announce,https://torrents.linuxmint.com:443/announce.php,https://tr.ready4.icu:443/announce,https://tr.steins-gate.moe:2096/announce,https://tracker.coalition.space:443/announce,https://tracker.foreverpirates.co:443/announce,https://tracker.gbitt.info:443/announce,https://tracker.hama3.net:443/announce,https://tracker.imgoingto.icu:443/announce,https://tracker.iriseden.eu:443/announce,https://tracker.iriseden.fr:443/announce,https://tracker.lelux.fi:443/announce,https://tracker.lilithraws.cf:443/announce,https://tracker.nanoha.org:443/announce,https://tracker.nitrix.me:443/announce,https://tracker.parrotsec.org:443/announce,https://tracker.sloppyta.co:443/announce,https://tracker.tamersunion.org:443/announce,https://trakx.herokuapp.com:443/announce,https://w.wwwww.wtf:443/announce,udp://103.196.36.31:6969/announce,udp://103.30.17.23:6969/announce,udp://104.238.159.144:6969/announce,udp://104.238.198.186:8000/announce,udp://104.244.153.245:6969/announce,udp://104.244.72.77:1337/announce,udp://109.248.43.36:6969/announce,udp://119.28.134.203:6969/announce,udp://138.68.171.1:6969/announce,udp://144.76.35.202:6969/announce,udp://144.76.82.110:6969/announce,udp://148.251.53.72:6969/announce,udp://149.28.47.87:1738/announce,udp://151.236.218.182:6969/announce,udp://156.234.201.18:80/announce,udp://157.90.161.74:6969/announce,udp://157.90.169.123:80/announce,udp://159.65.202.134:6969/announce,udp://159.69.208.124:6969/announce,udp://163.172.170.127:6969/announce,udp://167.179.77.133:1/announce,udp://173.212.223.237:6969/announce,udp://176.123.5.238:3391/announce,udp://178.159.40.252:6969/announce,udp://185.181.60.67:80/announce,udp://185.21.216.185:6969/announce,udp://185.243.215.40:6969/announce,udp://185.8.156.2:6969/announce,udp://193.34.92.5:80/announce,udp://195.201.94.195:6969/announce,udp://198.100.149.66:6969/announce,udp://198.50.195.216:7777/announce,udp://199.195.249.193:1337/announce,udp://199.217.118.72:6969/announce,udp://205.185.121.146:6969/announce,udp://208.83.20.20:6969/announce,udp://209.141.45.244:1337/announce,udp://209.141.59.16:6969/announce,udp://212.1.226.176:2710/announce,udp://212.83.181.109:6969/announce,udp://217.12.218.177:2710/announce,udp://37.1.205.89:2710/announce,udp://37.235.174.46:2710/announce,udp://37.59.48.81:6969/announce,udp://45.33.83.49:6969/announce,udp://45.56.65.82:54123/announce,udp://45.76.92.209:6969/announce,udp://45.77.100.109:6969/announce,udp://46.101.244.237:6969/announce,udp://46.148.18.250:2710/announce,udp://46.148.18.254:2710/announce,udp://47.ip-51-68-199.eu:6969/announce,udp://5.206.31.154:6969/announce,udp://51.15.2.221:6969/announce,udp://51.15.41.46:6969/announce,udp://51.68.199.47:6969/announce,udp://51.68.34.33:6969/announce,udp://51.77.134.13:6969/announce,udp://51.77.58.98:6969/announce,udp://51.79.81.233:6969/announce,udp://52.58.128.163:6969/announce,udp://62.168.229.166:6969/announce,udp://6ahddutb1ucc3cp.ru:6969/announce,udp://6rt.tace.ru:80/announce,udp://78.30.254.12:2710/announce,udp://88.99.142.4:8000/announce,udp://9.rarbg.me:2710/announce,udp://9.rarbg.to:2710/announce,udp://91.121.145.207:6969/announce,udp://91.149.192.31:6969/announce,udp://91.216.110.52:451/announce,udp://[2001:1b10:1000:8101:0:242:ac11:2]:6969/announce,udp://[2001:470:1:189:0:1:2:3]:6969/announce,udp://[2a03:7220:8083:cd00::1]:451/announce,udp://[2a04:ac00:1:3dd8::1:2710]:2710/announce,udp://admin.videoenpoche.info:6969/announce,udp://anidex.moe:6969/announce,udp://app.icon256.com:8000/announce,udp://bt.okmp3.ru:2710/announce,udp://bt2.3kb.xyz:6969/announce,udp://bubu.mapfactor.com:6969/announce,udp://cdn-1.gamecoast.org:6969/announce,udp://cdn-2.gamecoast.org:6969/announce,udp://code2chicken.nl:6969/announce,udp://concen.org:6969/announce,udp://cutiegirl.ru:6969/announce,udp://daveking.com:6969/announce,udp://discord.heihachi.pw:6969/announce,udp://edu.uifr.ru:6969/announce,udp://engplus.ru:6969/announce,udp://exodus.desync.com:6969/announce,udp://explodie.org:6969/announce,udp://fe.dealclub.de:6969/announce,udp://free-tracker.zooki.xyz:6969/announce,udp://free.publictracker.xyz:6969/announce,udp://inferno.demonoid.is:3391/announce,udp://ipv4.tracker.harry.lu:80/announce,udp://ipv6.tracker.harry.lu:80/announce,udp://ipv6.tracker.zerobytes.xyz:16661/announce,udp://johnrosen1.com:6969/announce,udp://line-net.ru:6969/announce,udp://ln.mtahost.co:6969/announce,udp://mail.realliferpg.de:6969/announce,udp://movies.zsw.ca:6969/announce,udp://mts.tvbit.co:6969/announce,udp://nagios.tks.sumy.ua:80/announce,udp://newtoncity.org:6969/announce,udp://open.demonii.com:1337/announce,udp://open.publictracker.xyz:6969/announce,udp://open.stealth.si:80/announce,udp://openbittorrent.com:80/announce,udp://opentor.org:2710/announce,udp://opentracker.i2p.rocks:6969/announce,udp://opentrackr.org:1337/announce,udp://p4p.arenabg.com:1337/announce,udp://peerfect.org:6969/announce,udp://peru.subventas.com:53/announce,udp://public-tracker.zooki.xyz:6969/announce,udp://public.popcorn-tracker.org:6969/announce,udp://public.publictracker.xyz:6969/announce,udp://public.tracker.vraphim.com:6969/announce,udp://qg.lorzl.gq:2710/announce,udp://qg.lorzl.gq:6969/announce,udp://retracker.hotplug.ru:2710/announce,udp://retracker.lanta-net.ru:2710/announce,udp://retracker.netbynet.ru:2710/announce,udp://retracker.nts.su:2710/announce,udp://retracker.sevstar.net:2710/announce,udp://sugoi.pomf.se:80/announce,udp://t1.leech.ie:1337/announce,udp://t2.leech.ie:1337/announce,udp://t3.leech.ie:1337/announce,udp://thetracker.org:80/announce,udp://torrentclub.online:54123/announce,udp://tr.bangumi.moe:6969/announce,udp://tr2.ysagin.top:2710/announce,udp://tracker.0x.tf:6969/announce,udp://tracker.altrosky.nl:6969/announce,udp://tracker.army:6969/announce,udp://tracker.beeimg.com:6969/announce,udp://tracker.birkenwald.de:6969/announce,udp://tracker.bittor.pw:1337/announce,udp://tracker.blacksparrowmedia.net:6969/announce,udp://tracker.btsync.gq:2710/announce,udp://tracker.coppersurfer.tk:6969/announce,udp://tracker.cyberia.is:6969/announce,udp://tracker.dler.org:6969/announce,udp://tracker.filemail.com:6969/announce,udp://tracker.flashtorrents.org:6969/announce,udp://tracker.grepler.com:6969/announce,udp://tracker.ilibr.org:80/announce,udp://tracker.internetwarriors.net:1337/announce,udp://tracker.kali.org:6969/announce,udp://tracker.kuroy.me:5944/announce,udp://tracker.lelux.fi:6969/announce,udp://tracker.moeking.me:6969/announce,udp://tracker.nighthawk.pw:2052/announce,udp://tracker.nrx.me:6969/announce,udp://tracker.open-internet.nl:6969/announce,udp://tracker.openbittorrent.com:80/announce,udp://tracker.opentrackr.org:1337/announce,udp://tracker.sbsub.com:2710/announce,udp://tracker.shkinev.me:6969/announce,udp://tracker.sktorrent.net:6969/announce,udp://tracker.skyts.net:6969/announce,udp://tracker.swateam.org.uk:2710/announce,udp://tracker.theoks.net:6969/announce,udp://tracker.tiny-vps.com:6969/announce,udp://tracker.torrent.eu.org:451/announce,udp://tracker.tricitytorrents.com:2710/announce,udp://tracker.tvunderground.org.ru:3218/announce,udp://tracker.uw0.xyz:6969/announce,udp://tracker.v6speed.org:6969/announce,udp://tracker.yoshi210.com:6969/announce,udp://tracker.zerobytes.xyz:1337/announce,udp://tracker0.ufibox.com:6969/announce,udp://tracker1.bt.moack.co.kr:80/announce,udp://tracker2.christianbro.pw:6969/announce,udp://tracker2.dler.org:80/announce,udp://tracker4.itzmx.com:2710/announce,udp://u.wwwww.wtf:1/announce,udp://udp-tracker.shittyurl.org:6969/announce,udp://us-tracker.publictracker.xyz:6969/announce,udp://valakas.rollo.dnsabr.com:2710/announce,udp://vibe.community:6969/announce,udp://vibe.sleepyinternetfun.xyz:1738/announce,udp://wassermann.online:6969/announce,udp://www.mvgroup.org:2710/announce,udp://www.torrent.eu.org:451/announce,udp://zephir.monocul.us:6969/announce,ws://tracker.nighthawk.pw:4201/announce,ws://tracker.sloppyta.co:80/announce,wss://tracker.btorrent.xyz:443/announce,wss://tracker.openwebtorrent.com:443/announce")
    #
    LOGGER.info(aria2_daemon_start_cmd)
    #
    process = await asyncio.create_subprocess_exec(
        *aria2_daemon_start_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    LOGGER.info(stdout)
    LOGGER.info(stderr)
    aria2 = aria2p.API(
        aria2p.Client(host="http://localhost", port=ARIA_TWO_STARTED_PORT, secret="")
    )
    return aria2


def add_magnet(aria_instance, magnetic_link, c_file_name):
    options = None
    # if c_file_name is not None:
    #     options = {
    #         "dir": c_file_name
    #     }
    try:
        download = aria_instance.add_magnet(magnetic_link, options=options)
    except Exception as e:
        return (
            False,
            "**FAILED** \n" + str(e) + " \nPlease do not send SLOW links. Read /help",
        )
    else:
        return True, "" + download.gid + ""


def add_torrent(aria_instance, torrent_file_path):
    if torrent_file_path is None:
        return (
            False,
            "**FAILED** \n"
            + str(e)
            + " \nsomething wrongings when trying to add <u>TORRENT</u> file",
        )
    if os.path.exists(torrent_file_path):
        # Add Torrent Into Queue
        try:
            download = aria_instance.add_torrent(
                torrent_file_path, uris=None, options=None, position=None
            )
        except Exception as e:
            return (
                False,
                "**FAILED** \n"
                + str(e)
                + " \nPlease do not send SLOW links. Read /help",
            )
        else:
            return True, "" + download.gid + ""
    else:
        return False, "**FAILED** \nPlease try other sources to get workable link"


def add_url(aria_instance, text_url, c_file_name):
    options = None
    # if c_file_name is not None:
    #     options = {
    #         "dir": c_file_name
    #     }
    if "zippyshare.com" in text_url \
        or "osdn.net" in text_url \
        or "mediafire.com" in text_url \
        or "cloud.mail.ru" in text_url \
        or "github.com" in text_url \
        or "yadi.sk" in text_url  \
        or "racaty.net" in text_url:
            try:
                urisitring = direct_link_generator(text_url)
                uris = [urisitring]
            except DirectDownloadLinkException as e:
                LOGGER.info(f'{text_url}: {e}')
    else:
        uris = [text_url]
    # Add URL Into Queue
    try:
        download = aria_instance.add_uris(uris, options=options)
    except Exception as e:
        return (
            False,
            "**FAILED** \n" + str(e) + " \nPlease do not send SLOW links. Read /help",
        )
    else:
        return True, "" + download.gid + ""


async def call_apropriate_function(
    aria_instance,
    incoming_link,
    c_file_name,
    sent_message_to_update_tg_p,
    is_zip,
    cstom_file_name,
    is_cloud,
    is_unzip,
    user_message,
    client,
):
    regexp = re.compile(r'^https?:\/\/.*(\.torrent|\/torrent|\/jav.php|nanobytes\.org).*')
    if incoming_link.lower().startswith("magnet:"):
        sagtus, err_message = add_magnet(aria_instance, incoming_link, c_file_name)
    elif incoming_link.lower().endswith(".torrent") and not incoming_link.lower().startswith("http"):
        sagtus, err_message = add_torrent(aria_instance, incoming_link)
    else:
        if regexp.search(incoming_link):
            var = incoming_link.encode('utf-8')
            file = hashlib.md5(var).hexdigest()
            subprocess.run(f"wget -O /app/{file}.torrent '{incoming_link}'", shell=True)
            sagtus, err_message = add_torrent(aria_instance, f"/app/{file}.torrent")
        else:
            sagtus, err_message = add_url(aria_instance, incoming_link, c_file_name)
    if incoming_link.lower().startswith("magnet:"):
        sagtus, err_message = add_magnet(aria_instance, incoming_link, c_file_name)
    elif incoming_link.lower().endswith(".torrent"):
        sagtus, err_message = add_torrent(aria_instance, incoming_link)
    else:
        sagtus, err_message = add_url(aria_instance, incoming_link, c_file_name)
    if not sagtus:
        return sagtus, err_message
    LOGGER.info(err_message)
    # https://stackoverflow.com/a/58213653/4723940
    await check_progress_for_dl(
        aria_instance, err_message, sent_message_to_update_tg_p, None
    )
    if incoming_link.startswith("magnet:"):
        #
        err_message = await check_metadata(aria_instance, err_message)
        #
        await asyncio.sleep(1)
        if err_message is not None:
            await check_progress_for_dl(
                aria_instance, err_message, sent_message_to_update_tg_p, None
            )
        else:
            return False, "can't get metadata \n\n#MetaDataError"
    await asyncio.sleep(1)
    file = aria_instance.get_download(err_message)
    to_upload_file = file.name
    com_g = file.is_complete
    #
    if is_zip:
        check_if_file = await create_archive(to_upload_file)
        if check_if_file is not None:
            to_upload_file = check_if_file
    #
    if is_unzip:
        try:
            check_ifi_file = get_base_name(to_upload_file)
            await unzip_me(to_upload_file)
            if os.path.exists(check_ifi_file):
                to_upload_file = check_ifi_file
        except Exception as ge:
            LOGGER.info(ge)
            LOGGER.info(
                f"Can't extract {os.path.basename(to_upload_file)}, Uploading the same file"
            )

    if to_upload_file:
        if CUSTOM_FILE_NAME:
            if os.path.isfile(to_upload_file):
                os.rename(to_upload_file, f"{CUSTOM_FILE_NAME}{to_upload_file}")
                to_upload_file = f"{CUSTOM_FILE_NAME}{to_upload_file}"
            else:
                for root, _, files in os.walk(to_upload_file):
                    LOGGER.info(files)
                    for org in files:
                        p_name = f"{root}/{org}"
                        n_name = f"{root}/{CUSTOM_FILE_NAME}{org}"
                        os.rename(p_name, n_name)
                to_upload_file = to_upload_file

    if cstom_file_name:
        os.rename(to_upload_file, cstom_file_name)
        to_upload_file = cstom_file_name
    #
    response = {}
    LOGGER.info(response)
    user_id = user_message.from_user.id
    if com_g:
        if is_cloud:
            await upload_to_gdrive(
                to_upload_file, sent_message_to_update_tg_p, user_message, user_id
            )
        else:
            final_response = await upload_to_tg(
                sent_message_to_update_tg_p, to_upload_file, user_id, response, client
            )
            if not final_response:
                return True, None
            try:
                message_to_send = ""
                for key_f_res_se in final_response:
                    local_file_name = key_f_res_se
                    message_id = final_response[key_f_res_se]
                    channel_id = str(sent_message_to_update_tg_p.chat.id)[4:]
                    private_link = f"https://t.me/c/{channel_id}/{message_id}"
                    message_to_send += "👉 <a href='"
                    message_to_send += private_link
                    message_to_send += "'>"
                    message_to_send += local_file_name
                    message_to_send += "</a>"
                    message_to_send += "\n"
                if message_to_send != "":
                    mention_req_user = (
                        f"<a href='tg://user?id={user_id}'>Your Requested Files</a>\n\n"
                    )
                    message_to_send = mention_req_user + message_to_send
                    message_to_send = message_to_send + "\n\n" + "#uploads"
                else:
                    message_to_send = "<i>FAILED</i> to upload files. 😞😞"
                await user_message.reply_text(
                    text=message_to_send, quote=True, disable_web_page_preview=True
                )
            except Exception as go:
                LOGGER.error(go)
    return True, None


#


# https://github.com/jaskaranSM/UniBorg/blob/6d35cf452bce1204613929d4da7530058785b6b1/stdplugins/aria.py#L136-L164
async def check_progress_for_dl(aria2, gid, event, previous_message):
    # g_id = event.reply_to_message.from_user.id
    try:
        file = aria2.get_download(gid)
        complete = file.is_complete
        is_file = file.seeder
        if not complete:
            if not file.error_message:
                msg = ""
                # sometimes, this weird https://t.me/c/1220993104/392975
                # error creeps up
                # TODO: temporary workaround
                downloading_dir_name = "N/A"
                try:
                    # another derp -_-
                    # https://t.me/c/1220993104/423318
                    downloading_dir_name = str(file.name)
                except:
                    pass
                #
                if is_file is None:
                    msgg = f"Conn: {file.connections} <b>|</b> GID: <code>{gid}</code>"
                else:
                    msgg = f"P: {file.connections} | S: {file.num_seeders} <b>|</b> GID: <code>{gid}</code>"
                msg = f"\n`{downloading_dir_name}`"
                msg += f"\n<b>Speed</b>: {file.download_speed_string()}"
                msg += f"\n<b>Status</b>: {file.progress_string()} <b>of</b> {file.total_length_string()} <b>|</b> {file.eta_string()} <b>|</b> {msgg}"
                # msg += f"\nSize: {file.total_length_string()}"

                # if is_file is None :
                # msg += f"\n<b>Conn:</b> {file.connections}, GID: <code>{gid}</code>"
                # else :
                # msg += f"\n<b>Info:</b>[ P : {file.connections} | S : {file.num_seeders} ], GID: <code>{gid}</code>"

                # msg += f"\nStatus: {file.status}"
                # msg += f"\nETA: {file.eta_string()}"
                # msg += f"\nGID: <code>{gid}</code>"
                inline_keyboard = []
                ikeyboard = []
                ikeyboard.append(
                    InlineKeyboardButton(
                        "Cancel 🚫", callback_data=(f"cancel {gid}").encode("UTF-8")
                    )
                )
                inline_keyboard.append(ikeyboard)
                reply_markup = InlineKeyboardMarkup(inline_keyboard)
                if msg != previous_message:
                    if not file.has_failed:
                        try:
                            await event.edit(msg, reply_markup=reply_markup)
                        except FloodWait as e_e:
                            LOGGER.warning(f"Trying to sleep for {e_e}")
                            time.sleep(e_e.x)
                        except MessageNotModified as e_p:
                            LOGGER.info(e_p)
                            await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
                        previous_message = msg
                    else:
                        LOGGER.info(
                            f"Cancelling downloading of {file.name} may be due to slow torrent"
                        )
                        await event.edit(
                            f"Download cancelled :\n<code>{file.name}</code>\n\n #MetaDataError"
                        )
                        file.remove(force=True, files=True)
                        return False
            else:
                msg = file.error_message
                LOGGER.info(msg)
                await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
                await event.edit(f"`{msg}`")
                return False
            await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
            await check_progress_for_dl(aria2, gid, event, previous_message)
        else:
            LOGGER.info(
                f"Downloaded Successfully: `{file.name} ({file.total_length_string()})` 🤒"
            )
            await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
            await event.edit(
                f"Downloaded Successfully: `{file.name} ({file.total_length_string()})` 🤒"
            )
            return True
    except aria2p.client.ClientException:
        await event.edit(
            f"Download cancelled :\n<code>{file.name} ({file.total_length_string()})</code>"
        )
    except MessageNotModified as ep:
        LOGGER.info(ep)
        await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
        await check_progress_for_dl(aria2, gid, event, previous_message)
    except FloodWait as e:
        LOGGER.info(e)
        time.sleep(e.x)
    except RecursionError:
        file.remove(force=True, files=True)
        await event.edit(
            "Download Auto Canceled :\n\n"
            "Your Torrent/Link is Dead.".format(file.name)
        )
        return False
    except Exception as e:
        LOGGER.info(str(e))
        if "not found" in str(e) or "'file'" in str(e):
            await event.edit(
                f"Download cancelled :\n<code>{file.name} ({file.total_length_string()})</code>"
            )
            return False
        else:
            LOGGER.info(str(e))
            await event.edit(
                "<u>error</u> :\n<code>{}</code> \n\n#error".format(str(e))
            )
            return False


# https://github.com/jaskaranSM/UniBorg/blob/6d35cf452bce1204613929d4da7530058785b6b1/stdplugins/aria.py#L136-L164


async def check_metadata(aria2, gid):
    file = aria2.get_download(gid)
    LOGGER.info(file)
    if not file.followed_by_ids:
        # https://t.me/c/1213160642/496
        return None
    new_gid = file.followed_by_ids[0]
    LOGGER.info("Changing GID " + gid + " to " + new_gid)
    return new_gid

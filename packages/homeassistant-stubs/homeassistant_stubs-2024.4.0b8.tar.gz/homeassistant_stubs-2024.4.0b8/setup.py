# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['homeassistant-stubs']

package_data = \
{'': ['*'],
 'homeassistant-stubs': ['auth/*',
                         'auth/mfa_modules/*',
                         'auth/permissions/*',
                         'auth/providers/*',
                         'backports/*',
                         'components/*',
                         'components/abode/*',
                         'components/accuweather/*',
                         'components/acer_projector/*',
                         'components/acmeda/*',
                         'components/actiontec/*',
                         'components/adax/*',
                         'components/adguard/*',
                         'components/aftership/*',
                         'components/air_quality/*',
                         'components/airly/*',
                         'components/airnow/*',
                         'components/airq/*',
                         'components/airthings/*',
                         'components/airthings_ble/*',
                         'components/airtouch5/*',
                         'components/airvisual/*',
                         'components/airvisual_pro/*',
                         'components/airzone/*',
                         'components/airzone_cloud/*',
                         'components/aladdin_connect/*',
                         'components/alarm_control_panel/*',
                         'components/alert/*',
                         'components/alexa/*',
                         'components/alpha_vantage/*',
                         'components/amazon_polly/*',
                         'components/amberelectric/*',
                         'components/ambiclimate/*',
                         'components/ambient_station/*',
                         'components/amcrest/*',
                         'components/ampio/*',
                         'components/analytics/*',
                         'components/analytics_insights/*',
                         'components/android_ip_webcam/*',
                         'components/androidtv/*',
                         'components/androidtv_remote/*',
                         'components/anel_pwrctrl/*',
                         'components/anova/*',
                         'components/anthemav/*',
                         'components/apache_kafka/*',
                         'components/apcupsd/*',
                         'components/api/*',
                         'components/apple_tv/*',
                         'components/apprise/*',
                         'components/aprs/*',
                         'components/aqualogic/*',
                         'components/aquostv/*',
                         'components/aranet/*',
                         'components/arcam_fmj/*',
                         'components/arris_tg2492lg/*',
                         'components/aruba/*',
                         'components/arwn/*',
                         'components/aseko_pool_live/*',
                         'components/assist_pipeline/*',
                         'components/asterisk_cdr/*',
                         'components/asterisk_mbox/*',
                         'components/asuswrt/*',
                         'components/auth/*',
                         'components/automation/*',
                         'components/awair/*',
                         'components/axis/*',
                         'components/axis/hub/*',
                         'components/backup/*',
                         'components/baf/*',
                         'components/bang_olufsen/*',
                         'components/bayesian/*',
                         'components/binary_sensor/*',
                         'components/bitcoin/*',
                         'components/blockchain/*',
                         'components/blue_current/*',
                         'components/blueprint/*',
                         'components/bluetooth/*',
                         'components/bluetooth_adapters/*',
                         'components/bluetooth_tracker/*',
                         'components/bmw_connected_drive/*',
                         'components/bond/*',
                         'components/braviatv/*',
                         'components/brother/*',
                         'components/browser/*',
                         'components/bthome/*',
                         'components/button/*',
                         'components/calendar/*',
                         'components/camera/*',
                         'components/canary/*',
                         'components/cert_expiry/*',
                         'components/clickatell/*',
                         'components/clicksend/*',
                         'components/climate/*',
                         'components/cloud/*',
                         'components/co2signal/*',
                         'components/command_line/*',
                         'components/config/*',
                         'components/configurator/*',
                         'components/counter/*',
                         'components/cover/*',
                         'components/cpuspeed/*',
                         'components/crownstone/*',
                         'components/date/*',
                         'components/datetime/*',
                         'components/deconz/*',
                         'components/deconz/hub/*',
                         'components/default_config/*',
                         'components/demo/*',
                         'components/derivative/*',
                         'components/device_automation/*',
                         'components/device_tracker/*',
                         'components/devolo_home_control/*',
                         'components/devolo_home_network/*',
                         'components/dhcp/*',
                         'components/diagnostics/*',
                         'components/discovergy/*',
                         'components/dlna_dmr/*',
                         'components/dlna_dms/*',
                         'components/dnsip/*',
                         'components/doorbird/*',
                         'components/dormakaba_dkey/*',
                         'components/downloader/*',
                         'components/dsmr/*',
                         'components/duckdns/*',
                         'components/dunehd/*',
                         'components/duotecno/*',
                         'components/easyenergy/*',
                         'components/ecovacs/*',
                         'components/ecowitt/*',
                         'components/efergy/*',
                         'components/electrasmart/*',
                         'components/electric_kiwi/*',
                         'components/elgato/*',
                         'components/elkm1/*',
                         'components/emulated_hue/*',
                         'components/energy/*',
                         'components/energyzero/*',
                         'components/enigma2/*',
                         'components/enphase_envoy/*',
                         'components/esphome/*',
                         'components/event/*',
                         'components/evil_genius_labs/*',
                         'components/evohome/*',
                         'components/faa_delays/*',
                         'components/fan/*',
                         'components/fastdotcom/*',
                         'components/feedreader/*',
                         'components/file_upload/*',
                         'components/filesize/*',
                         'components/filter/*',
                         'components/fitbit/*',
                         'components/flexit_bacnet/*',
                         'components/flux_led/*',
                         'components/forecast_solar/*',
                         'components/fritz/*',
                         'components/fritzbox/*',
                         'components/fritzbox_callmonitor/*',
                         'components/fronius/*',
                         'components/frontend/*',
                         'components/fully_kiosk/*',
                         'components/generic_hygrostat/*',
                         'components/generic_thermostat/*',
                         'components/geo_location/*',
                         'components/geocaching/*',
                         'components/gios/*',
                         'components/glances/*',
                         'components/goalzero/*',
                         'components/google/*',
                         'components/google_assistant_sdk/*',
                         'components/google_sheets/*',
                         'components/gpsd/*',
                         'components/greeneye_monitor/*',
                         'components/group/*',
                         'components/guardian/*',
                         'components/hardkernel/*',
                         'components/hardware/*',
                         'components/here_travel_time/*',
                         'components/history/*',
                         'components/history_stats/*',
                         'components/holiday/*',
                         'components/homeassistant/*',
                         'components/homeassistant/triggers/*',
                         'components/homeassistant_alerts/*',
                         'components/homeassistant_green/*',
                         'components/homeassistant_hardware/*',
                         'components/homeassistant_sky_connect/*',
                         'components/homeassistant_yellow/*',
                         'components/homekit/*',
                         'components/homekit_controller/*',
                         'components/homewizard/*',
                         'components/homeworks/*',
                         'components/http/*',
                         'components/huawei_lte/*',
                         'components/humidifier/*',
                         'components/hydrawise/*',
                         'components/hyperion/*',
                         'components/ibeacon/*',
                         'components/idasen_desk/*',
                         'components/image/*',
                         'components/image_processing/*',
                         'components/image_upload/*',
                         'components/imap/*',
                         'components/input_button/*',
                         'components/input_select/*',
                         'components/input_text/*',
                         'components/integration/*',
                         'components/intent/*',
                         'components/intent_script/*',
                         'components/ios/*',
                         'components/ipp/*',
                         'components/iqvia/*',
                         'components/islamic_prayer_times/*',
                         'components/isy994/*',
                         'components/jellyfin/*',
                         'components/jewish_calendar/*',
                         'components/jvc_projector/*',
                         'components/kaleidescape/*',
                         'components/knx/*',
                         'components/knx/helpers/*',
                         'components/kraken/*',
                         'components/lacrosse/*',
                         'components/lacrosse_view/*',
                         'components/lamarzocco/*',
                         'components/lametric/*',
                         'components/laundrify/*',
                         'components/lawn_mower/*',
                         'components/lcn/*',
                         'components/ld2410_ble/*',
                         'components/led_ble/*',
                         'components/lidarr/*',
                         'components/lifx/*',
                         'components/light/*',
                         'components/linear_garage_door/*',
                         'components/litejet/*',
                         'components/litterrobot/*',
                         'components/local_ip/*',
                         'components/local_todo/*',
                         'components/lock/*',
                         'components/logbook/*',
                         'components/logbook/queries/*',
                         'components/logger/*',
                         'components/london_underground/*',
                         'components/lookin/*',
                         'components/luftdaten/*',
                         'components/mailbox/*',
                         'components/map/*',
                         'components/mastodon/*',
                         'components/matrix/*',
                         'components/matter/*',
                         'components/media_extractor/*',
                         'components/media_player/*',
                         'components/media_source/*',
                         'components/met_eireann/*',
                         'components/metoffice/*',
                         'components/mikrotik/*',
                         'components/min_max/*',
                         'components/minecraft_server/*',
                         'components/mjpeg/*',
                         'components/modbus/*',
                         'components/modem_callerid/*',
                         'components/moon/*',
                         'components/mopeka/*',
                         'components/motionmount/*',
                         'components/mqtt/*',
                         'components/mqtt/light/*',
                         'components/my/*',
                         'components/mysensors/*',
                         'components/myuplink/*',
                         'components/nam/*',
                         'components/nanoleaf/*',
                         'components/neato/*',
                         'components/nest/*',
                         'components/netatmo/*',
                         'components/network/*',
                         'components/nextdns/*',
                         'components/nfandroidtv/*',
                         'components/nightscout/*',
                         'components/nissan_leaf/*',
                         'components/no_ip/*',
                         'components/notify/*',
                         'components/notion/*',
                         'components/number/*',
                         'components/nut/*',
                         'components/onboarding/*',
                         'components/oncue/*',
                         'components/onewire/*',
                         'components/open_meteo/*',
                         'components/openexchangerates/*',
                         'components/opensky/*',
                         'components/openuv/*',
                         'components/oralb/*',
                         'components/otbr/*',
                         'components/overkiz/*',
                         'components/overkiz/climate_entities/*',
                         'components/overkiz/cover_entities/*',
                         'components/overkiz/water_heater_entities/*',
                         'components/p1_monitor/*',
                         'components/peco/*',
                         'components/persistent_notification/*',
                         'components/pi_hole/*',
                         'components/ping/*',
                         'components/plugwise/*',
                         'components/poolsense/*',
                         'components/powerwall/*',
                         'components/private_ble_device/*',
                         'components/prometheus/*',
                         'components/proximity/*',
                         'components/prusalink/*',
                         'components/pure_energie/*',
                         'components/purpleair/*',
                         'components/pushbullet/*',
                         'components/pvoutput/*',
                         'components/qnap_qsw/*',
                         'components/rabbitair/*',
                         'components/radarr/*',
                         'components/rainforest_raven/*',
                         'components/rainmachine/*',
                         'components/raspberry_pi/*',
                         'components/rdw/*',
                         'components/recollect_waste/*',
                         'components/recorder/*',
                         'components/recorder/auto_repairs/*',
                         'components/recorder/auto_repairs/events/*',
                         'components/recorder/auto_repairs/states/*',
                         'components/recorder/auto_repairs/statistics/*',
                         'components/recorder/history/*',
                         'components/recorder/models/*',
                         'components/recorder/system_health/*',
                         'components/recorder/table_managers/*',
                         'components/remote/*',
                         'components/renault/*',
                         'components/repairs/*',
                         'components/rest/*',
                         'components/rest_command/*',
                         'components/rfxtrx/*',
                         'components/rhasspy/*',
                         'components/ridwell/*',
                         'components/rituals_perfume_genie/*',
                         'components/roku/*',
                         'components/romy/*',
                         'components/rpi_power/*',
                         'components/rss_feed_template/*',
                         'components/rtsp_to_webrtc/*',
                         'components/ruuvi_gateway/*',
                         'components/ruuvitag_ble/*',
                         'components/samsungtv/*',
                         'components/samsungtv/triggers/*',
                         'components/scene/*',
                         'components/schedule/*',
                         'components/scrape/*',
                         'components/search/*',
                         'components/select/*',
                         'components/sensibo/*',
                         'components/sensirion_ble/*',
                         'components/sensor/*',
                         'components/senz/*',
                         'components/sfr_box/*',
                         'components/shelly/*',
                         'components/shelly/bluetooth/*',
                         'components/shopping_list/*',
                         'components/simplepush/*',
                         'components/simplisafe/*',
                         'components/siren/*',
                         'components/skybell/*',
                         'components/slack/*',
                         'components/sleepiq/*',
                         'components/smhi/*',
                         'components/snooz/*',
                         'components/sonarr/*',
                         'components/speedtestdotnet/*',
                         'components/sql/*',
                         'components/ssdp/*',
                         'components/starlink/*',
                         'components/statistics/*',
                         'components/steamist/*',
                         'components/stookalert/*',
                         'components/stream/*',
                         'components/streamlabswater/*',
                         'components/stt/*',
                         'components/suez_water/*',
                         'components/sun/*',
                         'components/surepetcare/*',
                         'components/switch/*',
                         'components/switchbee/*',
                         'components/switchbot_cloud/*',
                         'components/switcher_kis/*',
                         'components/synology_dsm/*',
                         'components/system_health/*',
                         'components/system_log/*',
                         'components/systemmonitor/*',
                         'components/tag/*',
                         'components/tailscale/*',
                         'components/tailwind/*',
                         'components/tami4/*',
                         'components/tautulli/*',
                         'components/tcp/*',
                         'components/technove/*',
                         'components/tedee/*',
                         'components/text/*',
                         'components/threshold/*',
                         'components/tibber/*',
                         'components/tile/*',
                         'components/tilt_ble/*',
                         'components/time/*',
                         'components/time_date/*',
                         'components/timer/*',
                         'components/tod/*',
                         'components/todo/*',
                         'components/tolo/*',
                         'components/tplink/*',
                         'components/tplink_omada/*',
                         'components/trace/*',
                         'components/tractive/*',
                         'components/tradfri/*',
                         'components/trafikverket_camera/*',
                         'components/trafikverket_ferry/*',
                         'components/trafikverket_train/*',
                         'components/trafikverket_weatherstation/*',
                         'components/transmission/*',
                         'components/trend/*',
                         'components/tts/*',
                         'components/twentemilieu/*',
                         'components/unifi/*',
                         'components/unifi/hub/*',
                         'components/unifiprotect/*',
                         'components/upcloud/*',
                         'components/update/*',
                         'components/uptime/*',
                         'components/uptimerobot/*',
                         'components/usb/*',
                         'components/vacuum/*',
                         'components/vallox/*',
                         'components/valve/*',
                         'components/velbus/*',
                         'components/vlc_telnet/*',
                         'components/wake_on_lan/*',
                         'components/wake_word/*',
                         'components/wallbox/*',
                         'components/waqi/*',
                         'components/water_heater/*',
                         'components/watttime/*',
                         'components/weather/*',
                         'components/webhook/*',
                         'components/webostv/*',
                         'components/webostv/triggers/*',
                         'components/websocket_api/*',
                         'components/wemo/*',
                         'components/whois/*',
                         'components/withings/*',
                         'components/wiz/*',
                         'components/wled/*',
                         'components/worldclock/*',
                         'components/xiaomi_ble/*',
                         'components/yale_smart_alarm/*',
                         'components/yalexs_ble/*',
                         'components/youtube/*',
                         'components/zeroconf/*',
                         'components/zodiac/*',
                         'components/zone/*',
                         'components/zwave_js/*',
                         'components/zwave_js/scripts/*',
                         'components/zwave_js/triggers/*',
                         'generated/*',
                         'helpers/*',
                         'helpers/service_info/*',
                         'scripts/*',
                         'scripts/benchmark/*',
                         'scripts/macos/*',
                         'util/*',
                         'util/yaml/*']}

install_requires = \
['homeassistant==2024.4.0b8']

setup_kwargs = {
    'name': 'homeassistant-stubs',
    'version': '2024.4.0b8',
    'description': 'PEP 484 typing stubs for Home Assistant Core',
    'long_description': "[![CI](https://github.com/KapJI/homeassistant-stubs/actions/workflows/ci.yaml/badge.svg)](https://github.com/KapJI/homeassistant-stubs/actions/workflows/ci.yaml)\n[![PyPI version](https://img.shields.io/pypi/v/homeassistant-stubs)](https://pypi.org/project/homeassistant-stubs/)\n\n# PEP 484 stubs for Home Assistant Core\n\nThis is unofficial stub-only package generated from [Home Assistant Core](https://github.com/home-assistant/core) sources.\nYou can use it to enable type checks against Home Assistant code in your custom component or AppDaemon app.\n\n## How to use\n\nAdd it to dev dependencies of your project.\nI recommend to use [Poetry](https://python-poetry.org/) for managing dependencies:\n\n```shell\npoetry add --group dev homeassistant-stubs\n```\n\nPlease note that only stubs from strictly typed modules are added in this package.\nThis includes all core modules and some components.\nGeneric components like `sensor`, `light` or `media_player` are already typed.\n\nIf your project imports not yet typed components, `mypy` will be unable to find that module.\nThe best thing you can do to fix this is to submit PR to HA Core which adds type hints for these components.\nAfter that stubs for these components will become available in this package.\n\n## Motivation\n\nHome Assistant maintainers don't want to distribute typing information with `homeassistant` package\n([[1]](https://github.com/home-assistant/core/pull/28866),\n[[2]](https://github.com/home-assistant/core/pull/47796)).\nThe reason is that [PEP 561](https://www.python.org/dev/peps/pep-0561/#packaging-type-information)\nsays that `py.typed` marker is applied recursively and the whole package must support type checking.\nBut many of the Home Assistant components are currently not type checked.\n\n## How it works\n\n- `update_stubs.py` script extracts list of strictly typed modules from Home Assistant configs.\n- Then it runs `stubgen` which is shipped with `mypy` to generate typing stubs.\n- New versions are generated and published automatically every 12 hours.\n",
    'author': 'Ruslan Sayfutdinov',
    'author_email': 'ruslan@sayfutdinov.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/KapJI/homeassistant-stubs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.12,<3.13',
}


setup(**setup_kwargs)
